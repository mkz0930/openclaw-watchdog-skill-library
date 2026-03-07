# 怎么帮你把龙虾“改挂了”变成“自动自救”，一个能自动回滚配置的 OpenClaw Watchdog Skill

我把 OpenClaw 的 Watchdog 做成了一个可复用 Skill
作者：Horse
这次我做的，不是单纯修一个脚本，而是把一套 OpenClaw Watchdog 自恢复方案整理成了一个可以直接复用、直接分享的 Skill。
公开仓库：（帮点个小星星）
https://github.com/mkz0930/openclaw-watchdog-skill-library
它解决什么问题？
一句话：
当 OpenClaw gateway 因为坏配置起不来时，watchdog 会先尝试恢复；如果恢复失败，就自动把 openclaw.json 回滚到最后一个已知健康版本。
重点解决这几类问题：
- 改坏配置后，gateway 启动失败
- watchdog 误把 visibility restriction 当成系统故障
- 同时存在多个 watchdog / health-guard，导致重复告警、重复重启
- 出故障后，没有一个明确可退的稳定配置
这个 Skill 的核心能力
1. 单 watchdog 链路
只保留一条真正负责恢复的 watchdog 链，避免多个守护逻辑互相打架。
2. visibility restriction soft-fail
像 tools.sessions.visibility=tree 这类限制，不再误判成系统故障，也不会触发无意义重启。
3. 自动保存 last-known-good 配置
系统健康时，自动保存：
~/.openclaw/watchdog/openclaw.json.last-known-good
这让系统在“配置改坏”之后，始终有一个可回退的稳定点。
4. 自动回滚配置
如果 gateway 重启后还是不健康，watchdog 会自动把：
~/.openclaw/openclaw.json
回滚到最后一个健康版本，再尝试恢复。
这套东西为什么有价值？
因为很多系统真正难的，不是“跑起来”，而是：
出错之后，能不能自己恢复。
一个成熟的 watchdog，不只是会重启服务，而是要做到：
- 少误报
- 不乱重启
- 出错时保留现场
- 真恢复不了时，有回退路径
这也是这次把它做成 Skill 的原因：
不只是修一次，而是把经验变成别人也能直接拿去用的资产。
仓库里有什么？
- SKILL.md：Skill 主说明
- references/architecture.md：架构说明
- references/usage.md：使用说明
- scripts/openclaw-watchdog.sh：可直接部署的 watchdog 脚本
适合谁用？
如果你符合下面任一项，这个 Skill 就有用：
- 你在本地跑 OpenClaw gateway
- 你经常调整配置，担心一改就挂
- 你希望 watchdog 少误报、能自恢复
- 你想把这套方案直接分享给别人复用
项目地址
https://github.com/mkz0930/openclaw-watchdog-skill-library
最后
这次最重要的不是“多了一个脚本”，而是多了一条更可靠的恢复链：
系统被改坏时，不只是报错，而是有机会自己爬回来。
