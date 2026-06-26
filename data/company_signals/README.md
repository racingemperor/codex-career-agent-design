# 大厂招聘信号数据库

这个目录用于保存工程类求职 pipeline 的第二个静态数据库：大厂招聘信号库。

它的定位不是替代实时 JD 分析，也不是收集个人简历或私域消息；它只提供“公司 x 工科就业大类”的先验信息，帮助后续 Codex skill 在用户还没有确定具体岗位时，先判断哪些能力、作品、学习路径和个人包装方向更值得准备。

## 文件

- `company_hiring_signal_seed.zh-CN.json`：主数据库。包含公司清单、专业大类要求模板、公司级种子信号和第一批公开来源 evidence。
- `covered_companies.zh-CN.json`：覆盖公司清单。它是覆盖计划，不是证据库。
- `source_collection_targets.zh-CN.json`：后续采集计划。包含每家公司应查的官方入口、招聘平台关键词、HR/内推关键词、候选人面经关键词。
- `company_hiring_signals.schema.json`：主数据库 schema。
- `summary.json`：数据库规模和状态摘要。

## 当前状态

当前版本是 `0.2.1`，覆盖 85 家工程热门就业公司，包含 12 个工程就业大类要求模板和 51 条初始公开来源 evidence。

这仍然是 seed database，不是完整 evidence corpus。已有来源可以证明“官方入口、招聘流程、岗位族入口或候选人面经聚合页存在”，但不能直接推导某个具体岗位的完整任职要求。

## 来源优先级

使用时必须按以下顺序采信：

1. 公司官网、官方招聘页、校招官网、官方 JD。
2. 已验证身份的 HR 公开账号或官方列出的 HR 社媒账号。
3. 招聘软件公开 JD，例如 BOSS 直聘、拉勾、猎聘、牛客企业招聘页、LinkedIn、Indeed。
4. 候选人面经、offer 复盘、公开内推贴、多平台社媒共识。
5. 单条匿名帖子、截图、评论区传闻。

第 4-5 类只能用于补充面试准备、隐性要求、团队氛围、风险提示和 JD 模糊处解释，不能覆盖官方 JD 或已验证 HR 信号。

## 隐私和合规边界

数据库禁止保存：

- 个人简历原文。
- 私聊记录、内推聊天截图、非公开录用结果。
- 手机号、私人邮箱、微信号、身份证、住址等个人信息。
- 未授权抓取的招聘平台登录后内容。
- 可反向识别单个候选人的完整经历样本。

允许保存：

- 公开 URL。
- 来源类型、采集日期、发布者类型、HR 是否已验证。
- 对公开内容的短摘要。
- 去标识化、聚合后的候选人经验标签。

## 使用方式

未来 Codex skill 应按这个顺序使用本库：

1. 读取 `data/major_taxonomy/`，确认用户专业的主就业大类和交叉标签。
2. 读取 `company_hiring_signal_seed.zh-CN.json`，筛出相关公司和专业大类要求模板。
3. 只把 `source_evidence` 中已标明 `primary`、`high` 或 `verified_hr_public_post` 的内容作为强信号。
4. 把候选人面经和社媒内容标记为“辅助准备信号”。
5. 用户确定具体岗位后，必须重新获取当前 JD，并由 JDAnalyzer 在用户设备上做岗位级分析。

## 维护规则

新增 evidence 时至少填写：

- `company_id`
- `source_type`
- `source_priority`
- `publisher_type`
- `publisher_or_account`
- `hr_verified`
- `url`
- `captured_on`
- `recruiting_season`
- `title`
- `evidence_summary`
- `claim_summary`
- `major_cluster_refs`
- `role_family`
- `verification_status`
- `confidence`
- `privacy_checked`

如果来源是 HR 个人账号，必须能从公司官方招聘页、官方公众号、认证企业号或公开企业认证信息反向验证身份，否则只能标记为 `public_referral_or_hr_post_unverified`。
