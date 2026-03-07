# Architecture

## Target layout

Canonical retained chain:
- `openclaw-watchdog.timer`
- `openclaw-watchdog.service`
- `/home/claw/.local/bin/openclaw-watchdog.sh`

Retired duplicate chain:
- `openclaw-health-guard.timer`
- `openclaw-health-guard.service`
- `/home/claw/.local/bin/openclaw-health-guard.sh`

## Consolidation principles

1. Keep a single watchdog chain.
2. Treat session visibility restrictions as soft-fail, not service failure.
3. Avoid duplicate alerts and duplicate restart attempts.
4. Record watchdog state in `~/.openclaw/watchdog/state.json`.
5. Keep a last-known-good `openclaw.json` snapshot for rollback.

## Verification checklist

- `systemctl --user status openclaw-watchdog.timer`
- `systemctl --user status openclaw-watchdog.service`
- `journalctl --user -u openclaw-watchdog.service -n 30 --no-pager`
- `systemctl --user status openclaw-health-guard.timer`
- `cat ~/.openclaw/watchdog/state.json`

Expected steady state:
- watchdog timer active/waiting
- watchdog service exits with success each run
- health-guard timer disabled/inactive
- no fresh parse warnings from timer override files
- state reason typically `healthy`
