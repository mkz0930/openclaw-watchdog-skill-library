# Usage Guide

## What this skill solves

Use this skill when an OpenClaw gateway host needs a single reusable watchdog that:
- checks gateway health through systemd + HTTP health endpoint
- suppresses false alerts caused by session visibility restrictions
- prevents duplicate watchdog chains from fighting each other
- automatically rolls back `~/.openclaw/openclaw.json` to a last-known-good version if a bad config keeps the gateway unhealthy after restart

## Recommended target layout

Keep this retained chain:
- `openclaw-watchdog.timer`
- `openclaw-watchdog.service`
- `/home/claw/.local/bin/openclaw-watchdog.sh`

Retire duplicate chain if present:
- `openclaw-health-guard.timer`
- `openclaw-health-guard.service`
- `/home/claw/.local/bin/openclaw-health-guard.sh`

## Install steps

### 1) Copy the watchdog script

Copy the bundled script to the target path:

```bash
cp openclaw-watchdog-rollback/scripts/openclaw-watchdog.sh ~/.local/bin/openclaw-watchdog.sh
chmod +x ~/.local/bin/openclaw-watchdog.sh
```

### 2) Verify the service and timer point to the retained watchdog script

Check the user systemd unit files and confirm the service runs:

```bash
systemctl --user cat openclaw-watchdog.service
systemctl --user cat openclaw-watchdog.timer
```

If the service points to another script, update it so the retained service executes:

```bash
~/.local/bin/openclaw-watchdog.sh
```

### 3) Disable duplicate health-guard chain if present

```bash
systemctl --user disable --now openclaw-health-guard.timer || true
systemctl --user disable --now openclaw-health-guard.service || true
```

### 4) Check timer override files for empty values

Empty values like these can trigger parse warnings and break timer behavior:
- `OnBootSec=`
- `OnUnitActiveSec=`
- `AccuracySec=`

Inspect overrides with:

```bash
systemctl --user cat openclaw-watchdog.timer
systemctl --user cat openclaw-health-guard.timer
```

Remove empty assignments if they exist.

### 5) Reload systemd and restart the retained timer

```bash
systemctl --user daemon-reload
systemctl --user enable --now openclaw-watchdog.timer
systemctl --user restart openclaw-watchdog.timer
```

## How automatic rollback works

The watchdog keeps state under:

```bash
~/.openclaw/watchdog/
```

Important files:
- `openclaw.json.last-known-good` — last config seen while gateway health was good
- `openclaw.json.pre-restart` — snapshot taken just before a restart attempt
- `state.json` — current watchdog state and reason

Recovery flow:
1. detect repeated unhealthy state
2. wait until threshold is reached
3. restart `openclaw-gateway.service`
4. re-check health
5. if still unhealthy, restore `openclaw.json.last-known-good`
6. restart again
7. record whether rollback recovered service

## Verify installation

Run these checks:

```bash
systemctl --user status openclaw-watchdog.timer
systemctl --user status openclaw-watchdog.service
journalctl --user -u openclaw-watchdog.service -n 30 --no-pager
cat ~/.openclaw/watchdog/state.json
openclaw gateway status
```

Expected steady state:
- timer is active/waiting
- service exits successfully each run
- gateway status probe is healthy
- `state.json` usually shows `reason: healthy`

## Manual rollback

### Roll back to last-known-good config

```bash
cp -a ~/.openclaw/watchdog/openclaw.json.last-known-good ~/.openclaw/openclaw.json && \
systemctl --user restart openclaw-gateway.service && \
openclaw gateway status
```

### Compare current config with last-known-good first

```bash
diff -u ~/.openclaw/openclaw.json ~/.openclaw/watchdog/openclaw.json.last-known-good
```

### Roll back to pre-restart snapshot instead

Use this only when you intentionally want the exact config that existed before the last restart attempt:

```bash
cp -a ~/.openclaw/watchdog/openclaw.json.pre-restart ~/.openclaw/openclaw.json && \
systemctl --user restart openclaw-gateway.service && \
openclaw gateway status
```

## Notes

- Prefer `last-known-good` over `pre-restart` for normal recovery.
- Session visibility restrictions should be treated as soft-fail, not gateway failure.
- If the real problem is not config-related (port conflict, broken runtime, bad service file, missing dependencies), config rollback may not recover the gateway.
