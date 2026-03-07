# 怎么帮你把龙虾“改挂了”变成“自动自救”
## 一个能自动回滚配置的 OpenClaw Watchdog Skill

**作者：Horse**

这次我做的，不是单纯修一个脚本，而是把一套 **OpenClaw Watchdog 自恢复方案** 整理成了一个可以直接复用、直接分享的 **Skill**。

## 项目仓库

> 帮点个小星星 ⭐  
> https://github.com/mkz0930/openclaw-watchdog-skill-library

---

## 它解决什么问题？

一句话：

> 当 OpenClaw gateway 因为坏配置起不来时，watchdog 会先尝试恢复；如果恢复失败，就自动把 `openclaw.json` 回滚到最后一个已知健康版本。

它重点解决以下几类问题：

- 改坏配置后，gateway 启动失败
- watchdog 误把 visibility restriction 当成系统故障
- 同时存在多个 watchdog / health-guard，导致重复告警、重复重启
- 出故障后，没有一个明确可退回的稳定配置

---

## 这个 Skill 的核心能力

### 1. 单 watchdog 链路

只保留一条真正负责恢复的 watchdog 链，避免多个守护逻辑互相打架。

### 2. visibility restriction soft-fail

像 `tools.sessions.visibility=tree` 这类限制，不再误判成系统故障，也不会触发无意义重启。

### 3. 自动保存 last-known-good 配置

系统健康时，自动保存：

```bash
~/.openclaw/watchdog/openclaw.json.last-known-good
