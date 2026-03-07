#!/usr/bin/env bash
set -euo pipefail

UNIT="openclaw-gateway.service"
URL="http://127.0.0.1:18789/health"
TIMEOUT=3

STATE_DIR="/home/claw/.openclaw/watchdog"
FAIL_FILE="$STATE_DIR/fail_count"
SUCCESS_STREAK_FILE="$STATE_DIR/success_streak"
LAST_RESTART_FILE="$STATE_DIR/last_restart_epoch"
SOFTFAIL_STAMP="$STATE_DIR/softfail_visibility_epoch"
STATE_JSON="$STATE_DIR/state.json"
LOCK_FILE="$STATE_DIR/lock"

CONFIG="/home/claw/.openclaw/openclaw.json"
CONFIG_LAST_GOOD="$STATE_DIR/openclaw.json.last-known-good"
CONFIG_PRE_RESTART="$STATE_DIR/openclaw.json.pre-restart"

THRESHOLD=3
COOLDOWN_SEC=900
SOFTFAIL_DEDUP_SEC=1800
POST_RESTART_WAIT_SEC=5

mkdir -p "$STATE_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then exit 0; fi

now=$(date +%s)

fail_count=0
[[ -f "$FAIL_FILE" ]] && fail_count="$(cat "$FAIL_FILE" 2>/dev/null || echo 0)"

success_streak=0
[[ -f "$SUCCESS_STREAK_FILE" ]] && success_streak="$(cat "$SUCCESS_STREAK_FILE" 2>/dev/null || echo 0)"

last_restart=0
[[ -f "$LAST_RESTART_FILE" ]] && last_restart="$(cat "$LAST_RESTART_FILE" 2>/dev/null || echo 0)"

last_soft=0
[[ -f "$SOFTFAIL_STAMP" ]] && last_soft="$(cat "$SOFTFAIL_STAMP" 2>/dev/null || echo 0)"

write_state() {
  local reason="$1"
  cat > "$STATE_JSON" <<JSON
{"ts":$now,"unit":"$UNIT","fail_count":$fail_count,"success_streak":$success_streak,"last_restart":$last_restart,"reason":"$reason"}
JSON
}

save_last_known_good_config() {
  if [[ -f "$CONFIG" ]]; then
    cp -a "$CONFIG" "$CONFIG_LAST_GOOD"
  fi
}

save_pre_restart_config() {
  if [[ -f "$CONFIG" ]]; then
    cp -a "$CONFIG" "$CONFIG_PRE_RESTART"
  fi
}

rollback_config() {
  if [[ -f "$CONFIG_LAST_GOOD" ]]; then
    cp -a "$CONFIG_LAST_GOOD" "$CONFIG"
    logger -t openclaw-watchdog "[rollback] restored openclaw.json from last-known-good backup"
    return 0
  fi
  return 1
}

is_healthy() {
  local code unit_ok
  code="$(curl -sS -m "$TIMEOUT" -o /dev/null -w '%{http_code}' "$URL" || true)"
  unit_ok=0
  systemctl --user is-active --quiet "$UNIT" && unit_ok=1
  [[ "$unit_ok" -eq 1 && "$code" =~ ^[234] ]]
}

restart_unit() {
  if systemctl --user restart "$UNIT" >/dev/null 2>&1; then
    echo "$now" > "$LAST_RESTART_FILE"
    last_restart="$now"
    return 0
  fi
  return 1
}

# 1) 健康直接通过
if is_healthy; then
  fail_count=0
  success_streak=$((success_streak + 1))
  echo "$fail_count" > "$FAIL_FILE"
  echo "$success_streak" > "$SUCCESS_STREAK_FILE"
  save_last_known_good_config
  write_state "healthy"
  exit 0
fi

# 2) visibility 软失败：不重启不计失败
status_out="$(openclaw status 2>&1 || true)"
if echo "$status_out" | grep -qiE "Cannot read main session history|tools\.sessions\.visibility=tree|visibility restrictions"; then
  if (( now - last_soft > SOFTFAIL_DEDUP_SEC )); then
    logger -t openclaw-watchdog "[soft-fail] visibility restricted, skip restart"
    echo "$now" > "$SOFTFAIL_STAMP"
  fi
  write_state "softfail_visibility"
  exit 0
fi

# 3) 真失败计数
success_streak=0
fail_count=$((fail_count + 1))
echo "$fail_count" > "$FAIL_FILE"
echo "$success_streak" > "$SUCCESS_STREAK_FILE"

if [[ "$fail_count" -lt "$THRESHOLD" ]]; then
  write_state "hardfail_hold_${fail_count}_${THRESHOLD}"
  exit 0
fi

# 4) 冷却保护
if (( now - last_restart < COOLDOWN_SEC )); then
  write_state "cooldown_skip_restart"
  exit 0
fi

# 5) 重启前二次确认（1秒快速复检）
TIMEOUT=1
if is_healthy; then
  fail_count=0
  success_streak=1
  echo "$fail_count" > "$FAIL_FILE"
  echo "$success_streak" > "$SUCCESS_STREAK_FILE"
  save_last_known_good_config
  write_state "recheck_recovered"
  exit 0
fi

# 6) 真重启 + 重启后失败则回滚配置
save_pre_restart_config
logger -t openclaw-watchdog "[hard-fail] threshold reached, restart $UNIT"
if ! restart_unit; then
  write_state "restart_failed"
  exit 1
fi

sleep "$POST_RESTART_WAIT_SEC"
TIMEOUT=2
if is_healthy; then
  fail_count=0
  success_streak=0
  echo "$fail_count" > "$FAIL_FILE"
  echo "$success_streak" > "$SUCCESS_STREAK_FILE"
  save_last_known_good_config
  write_state "restart_triggered"
  exit 0
fi

if rollback_config; then
  logger -t openclaw-watchdog "[rollback] restart did not recover service, applying config rollback"
  if restart_unit; then
    sleep "$POST_RESTART_WAIT_SEC"
    TIMEOUT=2
    if is_healthy; then
      fail_count=0
      success_streak=0
      echo "$fail_count" > "$FAIL_FILE"
      echo "$success_streak" > "$SUCCESS_STREAK_FILE"
      save_last_known_good_config
      write_state "config_rollback_recovered"
      exit 0
    fi
    write_state "config_rollback_failed"
    exit 1
  fi
  write_state "config_rollback_restart_failed"
  exit 1
fi

write_state "restart_failed_no_rollback"
exit 1
