---
name: openclaw-watchdog-rollback
description: Package, install, and maintain a reusable OpenClaw watchdog with soft-fail visibility handling, single-watchdog consolidation, timer cleanup, and automatic openclaw.json rollback to a last-known-good config after failed restart recovery. Use when creating or applying a watchdog/health-guard recovery setup for OpenClaw gateway hosts, especially after false watchdog alerts, duplicate watchdog services, timer misconfiguration, or config-induced gateway failures.
---

# OpenClaw Watchdog Rollback

Use this skill to deploy a reusable single-watchdog setup for OpenClaw gateway.

## Workflow

1. Read `references/architecture.md` for the intended service/timer/script layout.
2. Copy `scripts/openclaw-watchdog.sh` to the target host path that runs the watchdog.
3. Ensure only one active watchdog chain remains:
   - keep `openclaw-watchdog.timer -> openclaw-watchdog.service`
   - disable duplicate health-guard timers/services if present
4. Ensure timer override files do not contain empty `OnBootSec=` / `OnUnitActiveSec=` / `AccuracySec=` values.
5. Reload systemd user daemon and restart the retained watchdog timer.
6. Verify:
   - watchdog timer is active/waiting
   - watchdog service exits successfully on schedule
   - retired health-guard timer is disabled/inactive
   - watchdog state file shows healthy or explicit recovery reason

## Script behavior

The bundled watchdog script provides:
- health check via systemd active state + HTTP health endpoint
- file lock to prevent concurrent runs
- threshold + cooldown protections
- visibility soft-fail handling
- last-known-good `openclaw.json` snapshots
- pre-restart config snapshot
- automatic rollback of `~/.openclaw/openclaw.json` if restart does not recover health

## Manual rollback command

Use this on the target host when a manual rollback is needed:

```bash
cp -a ~/.openclaw/watchdog/openclaw.json.last-known-good ~/.openclaw/openclaw.json && systemctl --user restart openclaw-gateway.service && openclaw gateway status
```

## Files

- Script: `scripts/openclaw-watchdog.sh`
- Reference: `references/architecture.md`

Keep SKILL.md concise. Put detailed reasoning and file layout notes in the reference file.
