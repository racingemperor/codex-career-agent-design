# Codex Career Agent Design

这是一个面向 Codex 平台的求职与简历设计 pipeline 方案草稿。

目标不是先部署一个完整项目，而是先把 agent / skill 的边界、角色分工、数据来源、合规约束和后续技术路线写清楚。后续如果要落地，优先采用 **Codex 原生 Skill + Codex Custom Subagents + deterministic scripts**，而不是复刻 Claude Code / Cloud Code 风格的外部 dispatcher。

## 1. 项目目标

这个 agent 的目标不是简单“帮用户润色简历”，而是帮助用户完成一套可解释、可追溯的求职决策流程：

1. 从用户的简历、项目、作品集、GitHub、论文、经历描述中提取候选人画像。
2. 从岗位 JD 中拆解真实筛选标准，包括显性要求和隐性要求。
3. 从公开数据中分析目标公司、岗位方向、行业趋势和外部评价。
4. 判断用户与岗位、公司、方向之间的匹配度。
5. 设计针对目标岗位的简历结构、叙事主线和项目表达。
6. 审查事实风险、夸大风险、隐私风险和面试可防御性。
7. 输出可操作的岗位优先级、简历修改方案、投递策略和面试准备方向。

## 2. 非目标

第一阶段不做以下事情：

- 不部署在线服务。
- 不创建前端产品。
- 不自动投递简历。
- 不绕过招聘平台登录、反爬或权限控制。
- 不抓取未授权的个人简历、聊天记录、录用结果或求职状态。
- 不将匿名平台的单条评价当作事实。
- 不编造候选人经历、数据、项目成果、学历、证书或工作年限。

## 3. Codex 形态

建议的 Codex 原生结构如下：

```text
.agents/
  skills/
    career-pipeline/
      SKILL.md
      references/
        data-source-policy.md
        resume-writing-rules.md
        job-analysis-rubric.md
      scripts/
        parse_resume.py
        normalize_job_postings.py
        score_fit.py
        render_resume.py

.codex/
  agents/
    profile-extractor.toml
    jd-analyzer.toml
    job-scout.toml
    company-intelligence-analyst.toml
    market-sentiment-analyzer.toml
    match-strategist.toml
    resume-architect.toml
    factual-reviewer.toml
```

其中：

- `SKILL.md` 是主编排器，定义何时触发 pipeline、何时派 subagent、如何合并结果。
- `.codex/agents/*.toml` 定义具体角色，每个角色只负责一个清晰切面。
- `scripts/` 处理确定性任务，例如简历解析、JD 标准化、schema 校验、匹配分计算、文档渲染。
- `references/` 存放规则、rubric、数据来源政策和写作准则，避免把大量知识塞进主 prompt。

## 4. 总体 Pipeline

推荐主流程：

```text
User Input
  -> Career Orchestrator
  -> ProfileExtractor
  -> JDAnalyzer
  -> JobScout
  -> CompanyIntelligenceAnalyst
  -> MarketSentimentAnalyzer
  -> MatchStrategist
  -> ResumeArchitect
  -> FactualReviewer
  -> Final Decision Package
```

根据任务类型可以裁剪流程：

- 只分析简历：`ProfileExtractor -> ResumeArchitect -> FactualReviewer`
- 只分析岗位：`JDAnalyzer -> CompanyIntelligenceAnalyst -> MarketSentimentAnalyzer`
- 目标岗位定制简历：完整流程
- 找岗位：`ProfileExtractor -> JobScout -> JDAnalyzer -> MatchStrategist`

## 5. 角色设计

### 5.1 Career Orchestrator

主控角色，一般写在 `SKILL.md` 中，不一定单独作为 subagent。

职责：

- 识别用户输入类型：简历、岗位链接、JD 文本、目标公司、作品集、GitHub、LinkedIn、论文、项目材料。
- 判断用户目标：提取画像、找岗位、分析公司、定制简历、准备面试、生成投递策略。
- 选择需要派发的 subagent。
- 控制隐私边界和合规边界。
- 合并所有 subagent 输出。
- 发现冲突信息时标记不确定性，而不是强行下结论。

重点工作面：

- 输入路由
- 子任务拆分
- 数据最小化
- 结果合并
- 证据链维护
- 用户确认点管理

输出：

```json
{
  "task_type": "resume_review|job_search|jd_analysis|company_research|tailored_resume",
  "agents_to_run": [],
  "privacy_constraints": [],
  "final_package": {}
}
```

### 5.2 ProfileExtractor

候选人画像提取员。负责回答：“这个人到底能做什么，有哪些可证明的证据？”

输入：

- 简历 PDF / DOCX / Markdown / LaTeX
- 自我介绍
- 项目经历
- 实习经历
- GitHub / 作品集 / 论文 / 博客
- 教育背景、竞赛、证书

工作方面：

- 基础画像：学历、专业、毕业时间、地区、求职身份、语言能力。
- 目标约束：目标岗位、城市、远程/线下、行业偏好、薪资、实习/全职。
- 技能抽取：语言、框架、模型、工具链、工程能力、研究能力、数据能力、产品能力。
- 经历拆解：每段经历拆成场景、任务、动作、结果、证据。
- 项目类型判断：课程项目、研究项目、业务项目、开源项目、个人 demo、比赛项目。
- 量化信息提取：用户量、准确率、速度提升、成本降低、收入、排名、论文指标。
- 证据等级：明确事实、可推断信息、用户需要确认的信息。
- 短板识别：缺少结果、目标不清、项目价值弱、技能堆砌、经历断层。

输出：

```json
{
  "candidate_profile": {},
  "skills": [],
  "experience_units": [],
  "evidence_map": [],
  "strengths": [],
  "risks_or_gaps": [],
  "needs_user_confirmation": []
}
```

禁止事项：

- 不改写简历。
- 不编造数据。
- 不把推断当事实。
- 不决定投递优先级。

### 5.3 JDAnalyzer

岗位分析员。负责回答：“这个岗位真正筛选什么人？”

输入：

- 岗位链接
- JD 文本
- 公司招聘页
- 用户指定的岗位方向

工作方面：

- 硬性门槛：学历、年限、地点、签证、语言、实习周期、必须技术栈。
- 核心职责：日常工作实际在做什么。
- 显性技能：JD 明确写出的技能、工具、框架、业务能力。
- 隐性技能：JD 未明说但实际需要的能力，如沟通、owner 意识、实验设计、工程落地。
- 岗位类型：研究型、工程型、产品型、数据型、运营型、增长型、算法型。
- 优先级拆分：must-have、nice-to-have、加分项、无关噪声。
- ATS 关键词：简历中应自然出现的关键词。
- 风险识别：高级岗伪装初级岗、外包/派遣、泛人才池、title 与职责不一致、JD 大而空。

输出：

```json
{
  "job_profile": {},
  "must_have": [],
  "nice_to_have": [],
  "hidden_requirements": [],
  "ats_keywords": [],
  "risk_flags": [],
  "confidence": "high|medium|low"
}
```

禁止事项：

- 不判断用户是否适合。
- 不改简历。
- 不把招聘宣传语当事实。

### 5.4 JobScout

岗位侦察员。负责回答：“有哪些岗位值得进入候选池？”

输入：

- 用户目标方向
- 候选人画像
- 城市、远程、薪资、行业偏好
- 公司名单
- 平台范围

工作方面：

- 搜索策略：生成中文、英文、同义岗位关键词组合。
- 岗位来源选择：公司官网、招聘平台公开页面、校招官网、实习招聘页、公众号、行业社区。
- 岗位去重：合并同公司同岗位在不同平台的重复信息。
- 基础过滤：地点、年限、学历、实习周期、全职/实习、签证限制。
- 岗位分类：冲刺岗、匹配岗、保底岗、探索岗、暂缓岗。
- 时效判断：发布时间、是否还开放、是否疑似过期。
- 投递价值初筛：公司质量、岗位清晰度、成长空间、与用户背景关系。
- 岗位结构化：为 JDAnalyzer 和 MatchStrategist 准备统一输入。

输出：

```json
{
  "job_candidates": [
    {
      "title": "",
      "company": "",
      "url": "",
      "location": "",
      "source": "",
      "category": "",
      "why_relevant": "",
      "risk_flags": []
    }
  ]
}
```

禁止事项：

- 不绕登录、不破反爬、不批量抓取权限内数据。
- 不抓取未授权的个人简历。
- 不虚构岗位。
- 不深度改写简历。

### 5.5 CompanyIntelligenceAnalyst

公司情报分析员。负责回答：“这家公司现在处在什么状态，这个岗位有没有战略价值？”

输入：

- 公司名称
- 岗位 JD
- 公司官网
- 新闻、财报、融资、招聘趋势、技术博客等公开信息

工作方面：

- 公司基本面：主营业务、产品线、商业模式、客户类型、收入来源。
- 发展阶段：初创、成长期、成熟期、收缩期、转型期。
- 融资/财务：融资轮次、上市状态、财报、现金流、营收增长、亏损情况。
- 业务动向：新产品、新市场、新合作、新战略、区域扩张。
- 组织信号：扩招、裁员、招聘冻结、部门调整、管理层变化。
- 岗位战略价值：核心业务、边缘支持、实验性团队、替补性岗位、不明。
- 风险识别：业务下滑、频繁裁员、战略摇摆、监管压力、负面舆情。
- 机会识别：候选人背景是否能切中公司当前需求。

数据源：

- 公司官网、新闻中心、博客。
- 财报、招股书、SEC / 港交所 / 上交所 / 深交所文件。
- 融资新闻、投资机构公告。
- 公司技术博客、开源项目、GitHub 活跃度。
- 主流媒体、行业报告。
- 公开招聘数量变化。
- 裁员或组织调整的公开报道。

输出：

```json
{
  "company_stage": "startup|growth|mature|declining|turnaround|unknown",
  "business_health": [],
  "recent_signals": [],
  "hiring_signals": [],
  "role_strategic_value": "core|adjacent|experimental|unclear",
  "risks": [],
  "opportunities_for_candidate": [],
  "source_notes": []
}
```

禁止事项：

- 不把单篇营销稿当作公司真实状态。
- 不把匿名爆料直接当事实。
- 不做投资建议。
- 不输出未经来源支持的强判断。

### 5.6 MarketSentimentAnalyzer

外部评价与风向分析员。负责回答：“外界如何评价这家公司、岗位和行业方向？”

输入：

- 公司名称
- 岗位方向
- 行业关键词
- 公开评价、面经、新闻、社区讨论

工作方面：

- 员工评价：工作强度、管理风格、晋升、薪资、技术氛围、稳定性。
- 候选人评价：面试体验、HC 真实性、流程速度、压价风险、面试难度。
- 行业风向：方向是在扩张、泡沫、收缩，还是稳定期。
- 舆论风险：劳动争议、产品争议、监管风险、商业模式争议。
- 技术趋势：LLM Agent、RAG、AI Infra、具身智能、机器人、自动驾驶等方向的招聘热度。
- 平台差异校正：知乎、脉脉、小红书、牛客、Glassdoor、Blind、Reddit 的可信度不同。
- 时间衰减：旧评价降低权重，最近 6-12 个月信号优先。
- 证据分级：官方公告 > 财报 > 多源媒体 > 多人一致评价 > 单条匿名吐槽。

数据源：

- 牛客面经、OfferShow、脉脉公开讨论。
- Glassdoor、Levels.fyi、Blind、Reddit。
- 知乎、小红书、公众号文章。
- 新闻媒体、行业报告。
- 技术社区讨论、GitHub activity。
- 招聘平台公开岗位数量变化。
- 用户主动提供的面经、截图或聊天记录。

输出：

```json
{
  "external_reputation": {},
  "candidate_experience_signals": [],
  "employee_sentiment": [],
  "industry_trend": "rising|stable|declining|mixed",
  "confidence": "high|medium|low",
  "source_notes": []
}
```

禁止事项：

- 不人肉、不挖个人隐私。
- 不抓取非公开讨论区或登录后受限内容。
- 不把情绪性评价当事实。
- 不输出诽谤性或无法来源支撑的结论。

### 5.7 MatchStrategist

匹配策略师。负责回答：“这个人该不该投这个岗位，应该怎么打？”

输入：

- Candidate profile
- Job profile
- Company intelligence
- Market sentiment
- 用户偏好与约束

工作方面：

- 硬门槛匹配：学历、年限、地点、签证、语言、技术栈。
- 技能匹配：用户技能与 must-have / nice-to-have 的重合和差距。
- 经历匹配：哪些项目、实习、论文、开源贡献最能证明岗位所需能力。
- 公司匹配：公司阶段、团队价值、行业方向是否适合用户。
- 风险收益判断：成长空间、稳定性、竞争激烈程度、简历转化概率。
- 投递优先级：High / Medium / Low / Skip。
- 简历打法：突出工程、研究、产品、业务、数据、开源或跨学科能力。
- 补救建议：补项目、补关键词、补量化结果、补作品链接、补面试故事。
- 面试风险预测：大概率会被追问的问题。

输出：

```json
{
  "fit_score": 0.0,
  "priority": "high|medium|low|skip",
  "matched_evidence": [],
  "gaps": [],
  "company_fit": {},
  "resume_angle": "",
  "application_strategy": "",
  "interview_risks": []
}
```

禁止事项：

- 不把低匹配硬说成高匹配。
- 不忽略硬性门槛。
- 不做最终简历改写。
- 不替用户做人生选择，只给可解释建议。

### 5.8 ResumeArchitect

简历架构师。负责回答：“如何把真实经历组织成最适合这个岗位的表达？”

输入：

- 候选人画像
- 岗位分析
- 匹配策略
- 当前简历
- 用户目标版本，例如中文、英文、实习、全职、科研、工程、产品

工作方面：

- 简历结构设计：教育、技能、项目、实习、论文、奖项的顺序。
- 版本定位：算法版、工程版、产品版、研究版、实习版、海外版。
- 项目排序：哪个项目放前面，哪个压缩，哪个删除。
- bullet 改写：动作、技术、结果、影响、证据。
- 关键词布局：ATS 关键词自然嵌入。
- 叙事主线：让用户看起来像适合这个岗位的人，而不是经历散乱的人。
- 弱项处理：没有实习、转专业、GPA 不高、项目结果弱、经历过杂。
- 输出格式：Markdown、DOCX、LaTeX、中文简历、英文 resume。

输出：

```json
{
  "resume_strategy": "",
  "section_order": [],
  "rewritten_bullets": [],
  "delete_or_compress": [],
  "keyword_placement": [],
  "final_resume_draft": ""
}
```

禁止事项：

- 不创造不存在的经历。
- 不把“参与”写成“主导”，除非材料有证据。
- 不为了 ATS 牺牲可读性。
- 不绕过 FactualReviewer。

### 5.9 FactualReviewer

事实与风险审查员。负责回答：“这份简历和建议是否真实、合规、可防御？”

输入：

- 原始候选人材料
- 改写后的简历
- 匹配报告
- 岗位 JD

工作方面：

- 事实一致性：改写内容是否能从原始材料找到依据。
- 夸大检测：主导、负责、提升、优化、SOTA、生产环境、用户量等词是否过度。
- 数字审查：百分比、用户量、排名、准确率有没有来源。
- 责任边界：团队项目中用户到底做了哪部分。
- 隐私风险：手机号、身份证、地址、客户名、公司内部数据、机密项目。
- 合规风险：虚假学历、虚假年限、违反 NDA、伪造论文/奖项。
- 表达风险：太营销、太空泛、太像 AI、关键词堆砌。
- 面试可防御性：如果面试官追问，用户能否讲清楚。

输出：

```json
{
  "verdict": "pass|revise|required_user_confirmation",
  "unsupported_claims": [],
  "overclaim_risks": [],
  "privacy_risks": [],
  "recommended_edits": [],
  "questions_for_user": []
}
```

禁止事项：

- 不帮用户编合理化解释。
- 不通过没有证据的强 claim。
- 不为了好看牺牲真实性。

## 6. 数据来源设计

数据来源应分层处理，不同来源具有不同可信度和合规边界。

### 6.1 公开岗位信息

用途：JDAnalyzer、JobScout、MatchStrategist。

可用来源：

- 公司官网招聘页。
- 公开岗位 JD 页面。
- 用户粘贴的岗位描述。
- 校招官网、实习招聘页。
- 招聘公众号、学校 career portal。
- 招聘平台公开可访问的职位信息。

约束：

- 遵守平台协议、robots、频率限制。
- 不绕登录。
- 不破反爬。
- 不抓取非公开数据。

### 6.2 公司基本面与发展状况

用途：CompanyIntelligenceAnalyst、MatchStrategist。

可用来源：

- 公司官网、新闻中心、产品页。
- 财报、招股书、监管披露。
- 融资新闻、投资机构公告。
- 行业报告。
- 主流媒体报道。
- 技术博客、开源仓库、开发者文档。
- 招聘数量变化。

核心指标：

- 业务增长信号。
- 现金流和融资信号。
- 产品发布节奏。
- 招聘扩张或收缩信号。
- 组织稳定性。
- 岗位是否处于核心业务。

### 6.3 外界评价与市场风向

用途：MarketSentimentAnalyzer、MatchStrategist。

可用来源：

- 牛客面经、OfferShow。
- Glassdoor、Blind、Levels.fyi、Reddit。
- 知乎、小红书、公众号。
- 脉脉公开讨论。
- 技术社区和开源社区。
- 新闻媒体。
- 用户主动提供的面经或截图。

处理规则：

- 匿名评价降权。
- 单条吐槽不作为事实。
- 多源一致信号提高置信度。
- 最近 6-12 个月信息优先。
- 输出必须带来源说明、时间和置信度。

### 6.4 用户授权样本

用途：构建“成功候选人画像”的合规替代方案。

允许方式：

- 用户或受访者主动上传已脱敏简历。
- 明确告知用途。
- 明确获得授权。
- 去标识化后只保留结构化特征。

可保留字段：

- 岗位方向。
- 学历层级。
- 技能组合。
- 项目类型。
- 实习类型。
- 作品链接类型。
- 面试反馈类型。
- offer 类型。

不应保留：

- 姓名、电话、邮箱、身份证。
- 精确住址。
- 未公开公司内部项目。
- 私聊记录。
- 未授权录用结果。
- 可反推出个人身份的组合信息。

### 6.5 不建议或禁止的数据

不应爬取：

- 招聘平台上未授权的成功受聘人简历。
- 登录后才能看到的求职者简历。
- 私聊记录。
- HR 后台候选人信息。
- 录用结果、薪酬、求职状态等个人敏感信息。
- 绕过平台访问控制取得的数据。

原则：

岗位分析可以来自公开 JD、公司公开信息、外界公开评价和用户授权样本；不能依赖未经授权的个人简历抓取。

## 7. 证据与可信度分级

建议所有输出都带证据等级：

| 等级 | 来源类型 | 处理方式 |
|---|---|---|
| A | 官方公告、财报、招聘官网、用户原始材料 | 可作为强证据 |
| B | 主流媒体、多源一致报道、行业报告 | 可作为较强证据 |
| C | 多人一致的公开面经或社区评价 | 可作为趋势信号 |
| D | 单条匿名评价、论坛吐槽、无法核实截图 | 只能作为弱信号 |
| E | 模型推断 | 必须标记为推断，不能当事实 |

时间权重：

- 0-6 个月：高权重。
- 6-12 个月：中权重。
- 1-3 年：低权重。
- 3 年以上：仅作背景参考。

## 8. 输出产品形态

最终输出不应该只有一份改写后的简历，而应包括一个 decision package：

```text
1. 候选人画像摘要
2. 目标岗位画像
3. 公司情报摘要
4. 外界评价与市场风向
5. 人岗匹配与差距分析
6. 投递优先级
7. 简历设计方案
8. 简历改写草稿
9. 风险审查结果
10. 面试准备建议
```

示例结构：

```json
{
  "candidate_summary": {},
  "job_summary": {},
  "company_intelligence": {},
  "market_sentiment": {},
  "fit_analysis": {},
  "resume_plan": {},
  "resume_draft": "",
  "factual_review": {},
  "next_actions": []
}
```

## 9. MVP 建议

第一版不做全网岗位搜索，先支持用户提供材料：

输入：

- 用户简历。
- 一个或多个岗位 JD。
- 一个或多个目标公司。
- 用户偏好。

MVP 流程：

```text
ProfileExtractor
  -> JDAnalyzer
  -> CompanyIntelligenceAnalyst
  -> MarketSentimentAnalyzer
  -> MatchStrategist
  -> ResumeArchitect
  -> FactualReviewer
```

MVP 输出：

- 候选人画像。
- 岗位拆解。
- 公司与风向摘要。
- 匹配分和投递优先级。
- 简历结构建议。
- 针对岗位的简历草稿。
- 风险审查清单。

MVP 验收标准：

- 所有强判断必须有来源或用户材料依据。
- 简历改写不能引入无证据事实。
- 岗位匹配必须区分硬门槛和软匹配。
- 公司评价必须带置信度。
- 输出能让用户明确知道下一步该做什么。

## 10. 后续扩展

### 10.1 Job Search 扩展

增加自动岗位搜索：

- 公司官网职位抓取。
- 招聘平台公开页面解析。
- 岗位去重。
- 岗位时效判断。
- 关键词策略生成。

### 10.2 Talent Benchmark 扩展

增加授权样本库：

- 成功候选人匿名画像。
- 按岗位方向聚合特征。
- 生成岗位成功画像。
- 比较用户与成功画像的差距。

### 10.3 Resume Rendering 扩展

增加输出格式：

- Markdown。
- DOCX。
- LaTeX。
- 中文简历。
- 英文 resume。
- 一页版与详细版。

### 10.4 Interview Preparation 扩展

增加面试准备：

- 根据简历生成追问清单。
- 根据 JD 生成技术面题。
- 根据公司业务生成业务理解题。
- 根据项目经历生成 STAR 故事。

### 10.5 Plugin 分发

当 skill 和 subagents 稳定后，可以打包为 Codex plugin：

```text
codex-career-plugin/
  .codex-plugin/plugin.json
  skills/
    career-pipeline/
      SKILL.md
      references/
      scripts/
  agents/
    openai.yaml
```

插件适合团队分发；本地迭代阶段先用 repo-scoped skill 即可。

## 11. 核心原则

1. 求职建议必须可解释。
2. 简历改写必须可追溯到用户原始材料。
3. 公司和市场判断必须带来源、时间和置信度。
4. 不抓取未授权个人简历。
5. 不把匿名情绪当事实。
6. 不为提高匹配度编造经历。
7. 先做本地 Codex workflow，再考虑 plugin 化。

