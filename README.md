# Codex Career Agent Design

## User-Side Smoke Run

This repository now includes a deterministic local runner for checking whether the Codex skill wiring works on a user's machine. It is a contract/smoke run, not a final career-advice run:

```bash
cd .agents/skills/career-pipeline
python scripts/career_pipeline_run.py --task-type target_job_fit --route target_job_fit --input-text "computer science senior, assess fit for Tencent backend role. JD: Java and MySQL" --run-root ../../../.career-pipeline-runs --source-adapter seed --subagent-adapter mock-blocked
```

Expected response for this mock smoke run:

- `exit_status = "blocked"` because this command uses `mock-blocked`, not a real Codex subagent adapter.
- `real_subagent_execution = false` because `mock-blocked` only writes schema-valid blocked role outputs.
- `source_discovery_ready = true` when the deterministic `seed` source adapter generated public source candidates and `discover_public_sources.py` accepted at least one allowed URL.
- Runtime artifacts are written under `.career-pipeline-runs/<run_id>/`, which is gitignored.

For real user-side execution in Codex Desktop, prefer the Codex Desktop built-in subagent adapter when current-session `multi_agent_v1.spawn_agent` is available. The main Codex controller reads `subagent_work_orders.json`, dispatches role agents by batch, persists strict JSON role outputs, backfills with `execute_subagent_plan.py --manual-controller-execution`, and finalizes with `finalize_runtime_run.py --execution-mode manual-controller`. See `.agents/skills/career-pipeline/references/codex-desktop-subagent-adapter.md`.

The `seed` source adapter is local and deterministic. It is useful for proving the pipeline can build public-source query plans and filter allowed URLs automatically, but it is not live recruitment-platform search and should not be treated as fresh evidence. Replace it with a real browser/search/API adapter before producing current job or company judgments.

Concrete recommended jobs, internships, or application targets must include real public URLs. The pipeline can use official entrypoints in `data/company_signals/official_application_entrypoints.zh-CN.json` for exploration, but apply-now decisions, role-specific fit claims, and tailored resume advice require current JD text or a current public JD URL gathered by the runtime source adapter. See `.agents/skills/career-pipeline/references/application-url-output-policy.md` and `.agents/skills/career-pipeline/references/real-user-deployment-and-use-flow.md`.

For engineering-only MVP tests with external adapters, the runner can accept externally collected search results and an external command adapter:

```bash
python scripts/career_pipeline_run.py --task-type job_search --route job_search --input-text "computer science sophomore, Python, looking for AI internship" --run-root ../../../.career-pipeline-runs --source-adapter external-json --search-results-json <search_results.json> --subagent-adapter external-command --adapter-command <adapter-executable> --adapter-arg <adapter-script-or-config> --finalize
```

This path may return `success` only when the external command writes valid `done` or `done_with_warnings` role outputs for every required work order. Search results still need source-policy filtering and evidence backfill before they can support weights or final judgments.

这是一个面向 Codex 平台的求职与简历设计 pipeline 方案草稿。

目标不是先部署一个完整项目，而是先把 agent / skill 的边界、角色分工、数据来源、合规约束和后续技术路线写清楚。后续如果要落地，优先采用 **Codex 原生 Skill + Codex Custom Subagents + deterministic scripts**，而不是复刻 Claude Code / Cloud Code 风格的外部 dispatcher。

## 1. 项目目标

这个 agent 的目标不是简单“帮用户润色简历”，而是帮助用户完成一套可解释、可追溯的求职决策流程：

1. 从用户的简历、项目、作品集、GitHub、论文、经历描述中提取候选人画像。
2. 从岗位 JD 中拆解真实筛选标准，包括显性要求和隐性要求。
3. 从公开数据中分析目标公司、岗位方向、行业趋势和外部评价。
4. 为用户与岗位、公司、方向之间的运行时匹配判断准备证据、条件和缺口。
5. 设计针对目标岗位的简历结构、叙事主线和项目表达。
6. 审查事实风险、夸大风险、隐私风险和面试可防御性。
7. 输出可操作的条件化岗位选项、简历修改方案、投递策略前置条件和面试准备方向；最终优先级由运行时 subagent 基于当前证据生成。

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
        data-catalog.md
        source-policy.md
        runtime-collaboration-protocol.md
        runtime-execution-layer.md
        runtime-subagent-injection-protocol.md
        subagent-invocation-contract.md
        runtime-orchestration-protocol.md
        runtime-artifact-schema.md
        error-recovery-protocol.md
        user-interaction-flow.md
        runtime-weight-engine.md
        role-output-contracts.md
      scripts/                  # local contract validation and simulation helpers
        validate_runtime_contracts.py
        simulate_runtime_run.py
        build_subagent_plan.py
        build_subagent_prompt_bundle.py
        build_public_source_plan.py
        execute_subagent_plan.py
        continue_runtime_run.py

.codex/
  agents/
    career-orchestrator.toml
    input-normalizer.toml
    major-cluster-classifier.toml
    profile-extractor.toml
    jd-analyzer.toml
    job-scout.toml
    company-intelligence-analyst.toml
    market-sentiment-analyzer.toml
    match-strategist.toml
    learning-path-strategist.toml
    personal-branding-strategist.toml
    hr-supervisor.toml
    resume-format-gate.toml
    resume-architect.toml
    factual-reviewer.toml

data/
  discipline_taxonomy/
    discipline_registry.zh-CN.json
    README.md
  major_taxonomy/
    engineering_official_majors_2026.zh-CN.json
    engineering_employment_clusters.zh-CN.json
    engineering_employment_clusters.zh-CN.md
    engineering_major_index.zh-CN.csv
    engineering_related_interdisciplinary_majors_2026.zh-CN.json
    engineering_related_interdisciplinary_majors_2026.zh-CN.csv
    summary.json
  company_signals/
    company_hiring_signal_seed.zh-CN.json
    covered_companies.zh-CN.json
    source_collection_targets.zh-CN.json
    company_hiring_signals.schema.json
    summary.json
  runtime_parameters/
    parameter_ownership.zh-CN.json
    summary.json
  school_signals/
    school_signal_policy.zh-CN.json
    summary.json
  resume_formats/
    resume_format_database.zh-CN.json
    resume_format_schema.json
    summary.json

.career-pipeline-runs/       # runtime-only, gitignored; planned local run manifests, artifacts, logs, caches
```

其中：

- `SKILL.md` 是主编排器，定义何时触发 pipeline、何时派 subagent、如何合并结果。
- `.codex/agents/*.toml` 定义具体角色，每个角色只负责一个清晰切面。
- `scripts/` 当前提供本地合同验证、无网络模拟运行、plan-only subagent 调用队列、subagent prompt bundle、公开来源研究计划、安全执行外壳、角色输出回填校验和同一 run 的用户补充信息继续流程，用来检查 prompt、二次注入、subagent invocation、manifest、source policy、blocked/final gate 是否符合协议；这些脚本不代表真实 subagent 已执行。简历解析、JD 标准化、匹配证据矩阵和文档渲染仍是后续确定性脚本扩展。
- `references/` 存放规则、rubric、数据来源政策、运行层协议和写作准则，避免把大量知识塞进主 prompt。
- `data/discipline_taxonomy/` 提供学科域注册表，用于先判断工科、理科、文科、社科、商科、艺术设计、医学健康、农学、法学公共事务或跨专业桥接，再进入对应分类逻辑。
- `data/` 提供项目自带的静态数据库。第一批完整数据库是中国本科工科专业目录与就业导向大类映射；后续会扩展理科、文科、社科、商科和跨专业数据库。第二批数据库是大厂招聘信号库，用于按公司和工科就业大类整理官方 JD、官方招聘页、已验证 HR 公开信息、招聘软件公开 JD、候选人面经和社媒共识的采信规则。
- `data/runtime_parameters/` 定义参数归属：哪些由用户提供，哪些可选，哪些交给用户设备上的 subagent 调研，哪些在运行时配权重。
- `data/school_signals/` 定义学校与企业合作、校招宣讲、实习基地、就业报告等学校信号的来源优先级和 schema；仓库不预设任何学校天然适合某企业。
- `data/resume_formats/` 提供简历格式数据库，保存基础五板块、岗位方向 overlay、HR 信任评分、多版本选择和格式提交/驳回规则，供 ResumeFormatGate 和 ResumeArchitect 调用。

## 4. 总体 Pipeline

推荐主流程：

```text
User Input
  -> InputNormalizer
  -> Career Orchestrator
  -> MajorClusterClassifier
  -> ProfileExtractor
  -> JDAnalyzer
  -> JobScout
  -> CompanyIntelligenceAnalyst
  -> MarketSentimentAnalyzer
  -> MatchStrategist
  -> LearningPathStrategist
  -> PersonalBrandingStrategist
  -> HRSupervisor
  -> ResumeFormatGate
  -> ResumeArchitect
  -> FactualReviewer
  -> HRSupervisor
  -> Final Decision Package
```

根据任务类型可以裁剪流程：

- 只做专业定位：`InputNormalizer -> MajorClusterClassifier`
- 只分析简历：`InputNormalizer -> ProfileExtractor -> ResumeFormatGate -> ResumeArchitect -> FactualReviewer -> HRSupervisor`
- 只分析岗位：`InputNormalizer -> JDAnalyzer -> CompanyIntelligenceAnalyst -> MarketSentimentAnalyzer`
- 目标岗位定制简历：完整流程
- 找岗位：`InputNormalizer -> MajorClusterClassifier -> ProfileExtractor -> JobScout -> JDAnalyzer -> MatchStrategist -> LearningPathStrategist`

用户端实际运行时，第一步不是直接把静态角色 prompt 派给各个 subagent，而是先把用户第一轮自述的个人画像、状态、学校专业年级、实习/项目/竞赛/技能、目标方向、约束、当前困惑以及上传的链接或文件，统一归一化为 `first_round_user_profile`。`InputNormalizer` 再把它压缩为可共享的 `runtime_context_packet`，由 `CareerOrchestrator` 按每个角色的职责生成 `secondary_prompt_injections`。这些二次注入提示词必须只携带该角色需要的用户事实、数据库子集、公开调研任务、权重硬数据要求、禁止输出项、交接字段和辩论字段，保证用户设备上的 subagent 能围绕用户当前情况工作，而不是泛泛执行静态框架。

运行时还需要显式维护 `run_state` 和 `execution_manifest`，用状态机保证不会跳过归一化、上下文包、二次注入、子智能体调用、合并、辩论、HR 监督、事实审查和用户确认。每个 `secondary_prompt_injection` 要转换成可追踪的 `subagent_invocation`，运行过程要写入本地 `artifact_refs`、`execution_log_refs`、`role_output_packet` 和 `error_recovery_state`。用户端交互遵循“一轮补充”原则：先告诉用户已知信息、现在能做什么、暂时不能做什么，再只询问用户本人才能提供的缺失事实。所有技能、外部展示、学校信号、投递策略和 HR 初筛权重都通过 `runtime_weights` 表达，证据不足时必须是 `not_available` 或 `needs_more_sources`。

本地运行产物默认进入 `.career-pipeline-runs/<run_id>/`，该目录不进入 git。推荐结构包括 `manifest.json`、归一化后的 `first_round_user_profile`、`runtime_context_packet`、各角色的二次注入和调用包、子智能体输出、证据包、脱敏日志、合并结果、HR/事实审查报告、最终 decision package 或 blocked package。中间日志默认脱敏，不能保存未授权私人简历、私聊、HR 后台信息或登录后才能看到的候选人资料。

这个 pipeline 不应只做静态匹配。对于有潜力但当前条件不完全满足的用户，系统应输出一条“成长型匹配”路线：先学习、补项目、补证据，再决定是否投递和如何包装简历。例如用户会 Python、Java 和工程基础，但缺少 LLM 相关知识时，不应简单判定“不匹配 LLM 应用岗”，而应给出可执行的 AI / LLM 学习路径、项目建议、产出证据和简历转化方式。

同时，pipeline 也应包含“个人包装”能力。不同专业和行业看待候选人的方式不同：计算机相关岗位可能更认可 GitHub、项目 demo、技术博客、个人网站或开源贡献；设计岗位可能更重作品集；科研岗位可能更重论文、主页和 Google Scholar；产品和运营岗位可能更重案例、数据结果和业务分析。这些不是仓库写死的硬要求，而是运行时由用户设备上的 subagent 根据学科、目标岗位、目标公司、当前 JD、招聘平台和公开评价设置权重。系统应根据目标行业设计个人展示面，而不是只改一份简历。

整套 pipeline 应在大厂 HR 初筛/校招筛选视角下运行。HR 角色不替代事实审查，也不帮助用户造假，而是检查所有子智能体输出是否能让招聘方快速看懂：目标岗位是什么、候选人的 2-4 个核心竞争力是什么、证据在哪里、为什么值得约面。尤其在个人包装环节，包装不是“美化人设”，而是让真实优势以 HR 能一目了然的方式呈现出来。必要时，HRSupervisor 应读取 `data/company_signals/` 中的大厂招聘信号库，用目标公司或同类大厂的官方 JD、校招页、已验证 HR 公开信息和岗位族先验来校准筛选偏好。

流程起点应先根据用户专业判断学科域，再做就业导向的大类归并。每类学科的求职逻辑不同：工科看工程交付和工具链，理科看科研训练、数学建模和实验方法，文科看写作、研究、语言和内容判断，商科看业务指标和商业场景，艺术设计看作品集和设计过程，跨专业则看桥接证据。当前已落地的是工科数据库，其他学科先通过 `data/discipline_taxonomy/discipline_registry.zh-CN.json` 预留框架。一个专业可以有多个标签：系统应输出“学科域 + 主就业大类 + 交叉标签 + 权重 + 推荐岗位方向”。例如人工智能在求职建议中通常可主归“计算机与 AI 软件类”，同时带有电子信息、自动化、数学建模等副标签；机器人工程则可能横跨自动化、机械、电子信息和计算机。用户输入具体专业后，系统先判断学科域、大类和交叉标签，再在相近专业群中横向比较能力差距，推荐更适合补齐的技能和岗位方向。

## 5. 角色设计

### 5.1 InputNormalizer

输入归一化员。负责回答：“用户到底提供了什么材料、哪些事实可以直接提取、哪些缺失信息需要用户补充、哪些信息应该交给本地 subagent 调研？”

这个角色运行在所有专业角色之前。用户可能只在聊天框写几句模糊简介，也可能给完整简历、Markdown 文件、个人网站、GitHub、作品集、论文页、JD 链接或混合材料。InputNormalizer 不做岗位判断和简历美化，只把材料变成结构化 evidence packet。

默认应读取：

- `data/runtime_parameters/parameter_ownership.zh-CN.json`
- `data/school_signals/school_signal_policy.zh-CN.json`
- `data/discipline_taxonomy/discipline_registry.zh-CN.json`

工作方面：

- 输入类型识别：聊天简介、简历文本、Markdown、PDF/DOCX、个人网站、GitHub/作品集、JD 文本、JD 链接、混合材料。
- 证据拆解：明确事实、文档证据、公开链接、推断、缺失项。
- 学校与年级提取：学校、学院、专业、学历、年级、入学/毕业时间、当前身份。
- 阶段判断：非毕业生、毕业年级、已毕业、未知。
- 非毕业生双场景：当前实习可行性和未来全职准备路径分开交给后续角色分析。
- 参数归属：把字段分为 `user_required_minimal`、`user_optional`、`subagent_research`、`runtime_weight_config`。
- 下一步说明：先用自然语言告诉用户基于已知信息能如何生成简历、能否分析投递方向、哪些场景因缺失信息暂时不能做。
- 一轮补充：把用户本人才能提供的缺失事实合并成一次性问题，避免多轮打扰。
- 信息不全处理：用户拒绝补充时，必须征得同意才允许生成信息不完整版简历；缺失板块不写，投递方向不提供。

输出：

```json
{
  "input_type": "chat_brief|resume_text|markdown_file|pdf_docx|personal_website|github_or_portfolio|jd_text|jd_link|mixed|unknown",
  "first_round_user_profile": {
    "identity_and_contact": {},
    "education_status": {},
    "major_and_discipline": {},
    "internship_experience": [],
    "project_competition_research_experience": [],
    "skills_and_tools": [],
    "external_assets": [],
    "target_direction": {},
    "preferences_constraints": [],
    "current_concerns": [],
    "materials_provided": []
  },
  "runtime_context_packet": {
    "packet_id": "",
    "created_from": "first_round_user_profile",
    "first_round_user_profile_ref": "",
    "known_user_facts": [],
    "missing_user_owned_facts": [],
    "public_research_needed": [],
    "runtime_weight_questions": [],
    "privacy_constraints": [],
    "blocked_outputs": [],
    "next_possible_actions": []
  },
  "known_information_summary": "",
  "next_possible_actions": [],
  "candidate_stage": "non_graduating|graduating|graduate|unknown",
  "school_context": {},
  "application_scenarios": {
    "internship": {},
    "future_full_time": {},
    "current_full_time": {}
  },
  "parameter_ownership": {
    "user_required_minimal": [],
    "user_optional": [],
    "subagent_research": [],
    "runtime_weight_config": []
  },
  "missing_user_owned_facts": [],
  "one_round_followup_prompt": "",
  "incomplete_resume_consent_required": false,
  "job_direction_blocked": false
}
```

禁止事项：

- 不把缺失字段脑补成事实。
- 不向用户反复追问可以由本地 subagent 调研的公开信息。
- 不在用户未同意时生成信息不完整简历。
- 不在信息不足时给出岗位投递方向。

### 5.2 Career Orchestrator

主控角色，一般写在 `SKILL.md` 中，不一定单独作为 subagent。

职责：

- 识别用户输入类型：简历、岗位链接、JD 文本、目标公司、作品集、GitHub、LinkedIn、论文、项目材料。
- 判断用户目标：提取画像、找岗位、分析公司、定制简历、准备面试、生成投递策略。
- 选择需要派发的 subagent。
- 控制隐私边界和合规边界。
- 合并所有 subagent 输出。
- 发现冲突信息时标记不确定性，而不是强行下结论。
- 使用 InputNormalizer 输出的参数归属，决定哪些问用户、哪些交给本地 subagent 调研、哪些留给运行时权重配置。
- 基于 `runtime_context_packet` 为每个本地角色生成 `secondary_prompt_injections`，让用户端 subagent 带着用户画像、角色范围、调研任务、数据库子集和辩论字段工作。

重点工作面：

- 输入路由
- 子任务拆分
- 数据最小化
- 结果合并
- 证据链维护
- 用户确认点管理，且尽量合并为一轮补充

输出：

```json
{
  "task_type": "resume_review|job_search|jd_analysis|company_research|tailored_resume",
  "runtime_context_packet_ref": "",
  "secondary_prompt_injections": [
    {
      "target_agent": "",
      "base_prompt_ref": ".codex/agents/<agent>.toml",
      "runtime_context_packet_ref": "",
      "role_specific_context": {},
      "allowed_user_facts": [],
      "research_tasks": [],
      "hard_data_weight_tasks": [],
      "database_files_to_read": [],
      "source_policy_refs": [],
      "blocked_outputs": [],
      "required_output_fields": [],
      "handoff_contract": [],
      "debate_contract": []
    }
  ],
  "secondary_injection_status": "ready|blocked",
  "secondary_injection_blockers": [],
  "agents_to_run": [],
  "privacy_constraints": [],
  "known_information_summary": "",
  "next_possible_actions": [],
  "one_round_followup_prompt": "",
  "job_direction_blocked": false,
  "final_package": {}
}
```

### 5.3 MajorClusterClassifier

专业大类分类员。负责回答：“用户的具体专业属于哪个学科域，在就业上应归入哪些能力大类，应和哪些相近专业横向比较？”

这个角色用于 pipeline 的最前置分类。它先读取学科域注册表，判断用户属于工科、理科、文科、社科、商科、艺术设计、医学健康、农学、法学公共事务或跨专业桥接，再进入对应学科逻辑。当前只有工科具备完整静态数据库；其他学科应返回 `taxonomy_status = "pending_static_database"`，并基于用户课程、作品、项目和目标岗位给出谨慎的临时判断，不能硬套工科分类。

默认应读取仓库自带数据库：

- `data/discipline_taxonomy/discipline_registry.zh-CN.json`
- `data/major_taxonomy/engineering_employment_clusters.zh-CN.json`
- `data/major_taxonomy/engineering_major_index.zh-CN.csv`

输入：

- 用户专业名称，例如人工智能、机器人工程、电子信息工程、机械设计制造及其自动化，也可能是数学、物理、汉语言文学、新闻学、金融、法学、视觉传达设计等后续扩展学科。
- 学校、学院、培养方案、课程列表、项目经历。
- 用户目标行业和岗位方向。
- 用户已有技能和作品。

工作方面：

- 学科域识别：先判断 `discipline_domain`，决定使用已实现数据库还是 pending 框架。
- 标准化专业名称：处理简称、旧专业名、实验班、交叉学院、方向班。
- 主就业大类判断：给出最适合用于求职匹配的主类。
- 交叉标签识别：给出 2-5 个副标签，例如计算机、电子信息、自动化、机械、材料、能源、土木、数学建模。
- 权重分配：标记每个标签对就业匹配的影响权重。
- 相近专业横向对比：指出应和哪些专业一起比较能力，例如人工智能可和计算机、软件工程、数据科学横向比较。
- 能力底座判断：判断用户专业天然具备哪些基础，例如数学、编程、电路、控制、机械设计、材料实验、工艺流程。
- 岗位方向初筛：给出该专业群常见岗位、相邻岗位、转向岗位。
- 补齐方向建议：指出如果用户想进入某类岗位，需要补哪些能力。

输出：

```json
{
  "discipline_domain": "engineering|science|humanities|social_science|business|arts_design|medicine_health|agriculture|law_public_affairs|interdisciplinary|unknown",
  "taxonomy_status": "implemented|pending_static_database|bridge_layer",
  "normalized_major": "",
  "primary_cluster": "",
  "cross_tags": [
    {"tag": "", "weight": 0.0, "reason": ""}
  ],
  "peer_majors": [],
  "natural_strengths": [],
  "likely_role_families": [],
  "adjacent_role_families": [],
  "skill_gaps_by_target": {}
}
```

禁止事项：

- 不把一个专业强行塞进唯一大类。
- 不把非工科专业硬套进工科分类。
- 不完全照搬官方专业类；官方分类只作为参考。
- 不把专业名称等同于个人能力，必须结合课程、项目和技能。
- 不把热门方向强推给所有专业。

### 5.4 ProfileExtractor

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
- 技能归属：只抽取用户已提供或材料能证明的技能，不在仓库阶段判断某专业必须掌握哪些具体技能。
- 运行时研究标记：把具体技能权重、外部展示认可度、学校企业合作等交给用户设备上的 subagent 调研。
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
  "skill_weight_research_needed": [],
  "external_asset_weight_research_needed": [],
  "missing_user_owned_facts": [],
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
- 不把仓库中的技能示例当成用户必须掌握的技能。

### 5.5 JDAnalyzer

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
- 信息来源校准：公司官网、招聘软件公开 JD、校招官网和用户粘贴 JD 是岗位要求主证据；小红书、脉脉、牛客、知乎等社交媒体只能作为补充信号，尤其用于解释非大厂岗位中模糊的职责和隐性要求。
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
- 不用社交媒体传闻覆盖招聘软件或公司官网中的明确岗位要求。

### 5.6 JobScout

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

### 5.7 CompanyIntelligenceAnalyst

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

### 5.8 MarketSentimentAnalyzer

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

### 5.9 MatchStrategist

匹配证据策略师。负责回答：“运行时需要哪些证据才能比较候选人与岗位，证据齐全后有哪些条件化投递选项？”

输入：

- Candidate profile
- Job profile
- Company intelligence
- Market sentiment
- 用户偏好与约束

工作方面：

- 硬门槛状态：学历、年限、地点、签证、语言、技术栈是否已有证据支持。
- 技能证据矩阵：用户技能与 must-have / nice-to-have 的重合、差距和证据来源。
- 运行时技能权重：由当前 JD、公司信号、招聘平台公开 JD、已验证 HR 公开信息和学科证据决定，不由仓库写死。
- 学校机会信号：学校与企业合作、校招宣讲、实习基地、就业报告只能作为来源分级后的机会信号。
- 非毕业生双场景：当前实习可投性和未来全职准备路径分开输出。
- 经验证据：哪些项目、实习、论文、开源贡献能证明岗位所需能力，哪些还缺证据。
- 公司与岗位证据：公司阶段、团队价值、行业方向只在有运行时来源时进入条件化选项。
- 风险收益前置条件：成长空间、稳定性、竞争激烈程度、简历转化概率必须带来源和置信度。
- 条件化投递优先级：High / Medium / Low / Skip 只能在当前 JD、用户约束、公司/学校信号和证据矩阵齐全后输出；证据不足时返回 `not_available`。
- 简历角度选项：突出工程、研究、产品、业务、数据、开源或跨学科能力的候选角度及所需证据。
- 补救交接：把补项目、补关键词、补量化结果、补作品链接、补面试故事交给 LearningPathStrategist、PersonalBrandingStrategist 和 ResumeArchitect。
- 面试风险预测：大概率会被追问的问题。

输出：

```json
{
  "judgment_status": "framework_only|runtime_evidence_required|ready_for_runtime_judgment|evidence_bound_judgment|blocked",
  "fit_score": null,
  "priority": "high|medium|low|skip|not_available",
  "job_direction_blocked": false,
  "evidence_basis": [],
  "blocked_outputs": [],
  "conditional_options": [],
  "runtime_weight_config": {
    "skill_weights": [],
    "external_asset_weights": [],
    "school_signal_weights": []
  },
  "scenario_analysis": {
    "internship": {},
    "future_full_time": {},
    "current_full_time": {}
  },
  "matched_evidence": [],
  "gaps": [],
  "company_fit": {},
  "resume_angle": "",
  "application_strategy": "",
  "runtime_research_tasks": [],
  "evidence_requirements": [],
  "interview_risks": []
}
```

禁止事项：

- 不把低匹配硬说成高匹配。
- 不忽略硬性门槛。
- 不做最终简历改写。
- 不替用户做人生选择，只给可解释建议。
- 当用户拒绝补充关键个人事实且只同意信息不全简历时，不给投递方向。

### 5.10 LearningPathStrategist

学习路径策略师。负责回答：“如果运行时证据显示用户与目标岗位存在可学习差距，应该评估哪些学习路径、项目产出和证据标准？”

这个角色解决一个关键问题：求职推荐不应只基于用户现有条件做静态筛选。很多用户具备可迁移基础，例如会 Python、Java、后端开发、数据处理、科研实验或工程部署，但缺少目标岗位中的某一块知识。系统应该识别这些可迁移能力，给出短期可执行的学习和项目路径，再把真实完成的成果转化为简历材料。

输入：

- 候选人画像。
- 岗位分析。
- 匹配差距。
- 公司和行业趋势。
- 用户可投入时间，例如 1 周、2 周、1 个月、3 个月。
- 用户偏好，例如工程、算法、产品、研究、数据、全栈。

工作方面：

- 差距分层：硬门槛差距、技能差距、项目证据差距、叙事差距。
- 技能优先级研究：具体先学什么由运行时目标岗位、公司、JD 和公开招聘信号决定。
- 可迁移能力识别：已有语言、工程、数据、论文、业务、系统设计能力能否迁移到目标岗位。
- 学习优先级：先补最影响投递转化率的知识，而不是列一个泛泛课程清单。
- 学习路径设计：按 7 天、14 天、30 天、90 天给出具体路线。
- 项目化建议：学习必须转化为可展示项目、demo、GitHub、报告、博客、实验结果或部署链接。
- 简历转化规则：只有真实完成、能解释、能展示、能被追问的学习成果才允许写进简历。
- 岗位再选择：如果短期无法补齐，则推荐更合理的过渡岗位或相邻岗位。
- 面试可防御性：学习路径中每个成果都要能回答“为什么做、怎么做、效果如何、局限是什么”。

示例：

用户会 Python、Java、Web 后端和数据库，但 LLM 经验不足，目标是 LLM 应用工程师。该角色不应直接推荐放弃，而应输出：

- 先学：prompt engineering、RAG、embedding、向量数据库、function calling / tool use、LLM eval、API 成本与延迟优化。
- 再做：一个可部署的 RAG 问答项目，包含文档解析、chunking、retrieval、reranking、回答引用、评测集和错误分析。
- 再包装：把原有后端能力与 LLM 应用结合，写成“构建可评测、可部署的 LLM 应用系统”，而不是空泛写“熟悉大模型”。
- 再投递：优先投 LLM 应用工程、AI 产品工程、RAG 工程、Agent 工具链实习，而不是一开始冲纯算法研究岗。

输出：

```json
{
  "gap_taxonomy": {
    "hard_blockers": [],
    "learnable_gaps": [],
    "evidence_gaps": [],
    "narrative_gaps": []
  },
  "transferable_strengths": [],
  "learning_plan": {
    "7_days": [],
    "14_days": [],
    "30_days": [],
    "90_days": []
  },
  "project_recommendations": [],
  "resume_conversion": [],
  "ready_to_apply_when": [],
  "alternative_roles": []
}
```

禁止事项：

- 不建议把“正在学习”包装成“熟练掌握”。
- 不把没有完成的课程、项目或实验写成简历成果。
- 不推荐和目标岗位无关的泛泛学习清单。
- 不让用户为了热门方向强行转向完全不适合的岗位。
- 不承诺学习后一定获得 offer。
- 不把仓库种子技能表当作固定学习顺序。

### 5.11 PersonalBrandingStrategist

个人包装策略师。负责回答：“除简历外，哪些外部展示资产已有事实支撑，哪些需要运行时调研后才能推荐？”

这个角色不只是“美化人设”，而是根据目标行业、岗位类型和候选人基础，设计一套可被招聘方快速验证的个人展示面。不同专业和行业的评价方式不同，计算机、设计、科研、产品、运营、金融、咨询等方向需要展示的证据形态不同。

输入：

- 候选人画像。
- 目标岗位和行业。
- 用户已有外部资产，例如 GitHub、个人网站、博客、论文主页、作品集、LinkedIn、脉脉、公众号、Notion、Behance。
- 学习路径和项目建议。
- 用户隐私偏好。

工作方面：

- 行业展示标准判断：不同岗位可能需要哪些展示资产，但具体认可度由运行时调研决定。
- GitHub 包装：仅在目标学科、岗位、公司或 JD 证据显示其有价值，且用户有真实可展示内容时建议。
- 个人网站设计：仅在需要综合展示项目、研究、作品、博客、联系方式，且隐私风险可控时建议。
- 作品集设计：适用于设计、产品、内容、运营、数据分析、咨询案例等方向，但仍需运行时判断认可度。
- 技术博客/项目文档：把学习路径和项目结果沉淀成可读证据。
- LinkedIn / 脉脉 / 个人主页优化：统一 title、summary、项目描述、关键词。
- 资产优先级：根据目标岗位、公司信号、学科认可度和用户已有证据判断先做 GitHub、个人网站、作品集，还是先改简历。
- 可信度设计：每个展示资产都要有真实项目、代码、截图、demo、实验报告或案例支撑。
- 隐私与边界：隐藏个人敏感信息、内部项目细节、未公开客户信息。

展示资产候选池，不是固定要求：

- 计算机 / AI / 数据岗位：GitHub、项目 README、demo 链接、技术博客、个人网站、开源贡献。
- 前端 / 全栈岗位：个人网站、在线 demo、组件库、项目截图、性能优化说明。
- 设计岗位：作品集网站、Behance / Dribbble、设计过程、用户研究和落地结果。
- 产品岗位：产品案例、PRD 摘要、竞品分析、增长实验、指标结果。
- 运营 / 市场岗位：活动案例、内容作品、数据复盘、增长指标、渠道策略。
- 科研岗位：个人学术主页、Google Scholar、论文、代码复现、实验报告。
- 金融 / 咨询岗位：项目案例、行业研究、建模文件摘要、商业分析报告。

输出：

```json
{
  "branding_strategy": "",
  "external_asset_research_needed": [],
  "external_asset_weights": [],
  "recommended_assets": [],
  "asset_priority": [],
  "github_plan": {},
  "personal_website_plan": {},
  "portfolio_plan": {},
  "profile_copy": {},
  "privacy_checks": [],
  "done_definition": []
}
```

禁止事项：

- 不把个人包装变成虚假人设。
- 不建议展示未完成、不可解释或无法证明的项目。
- 不公开隐私信息、内部资料或违反 NDA 的材料。
- 不把所有行业都套用同一套 GitHub / 个人网站模板。
- 不为了视觉包装牺牲内容真实性。
- 不把仓库示例当成某学科必须具备的外部资产。

### 5.12 HRSupervisor

HR 监督员。负责回答：“大厂 HR 是否能快速看懂这个候选人的目标、可信优势和约面理由？”

这个角色贯穿整个 pipeline，尤其监督 PersonalBrandingStrategist、ResumeFormatGate、ResumeArchitect 和最终 decision package。它不替代 FactualReviewer，不创造新经历，也不负责写最终简历；它负责从大厂招聘初筛视角检查信息是否清晰、有竞争力、可信、能被快速扫描。

当用户提供目标公司、目标岗位族或目标行业时，它可以读取大厂招聘信号库：

- `data/company_signals/company_hiring_signal_seed.zh-CN.json`
- `data/company_signals/source_collection_targets.zh-CN.json`

读取规则：

- 公司官网、官方招聘页、校招官网、官方 JD 和已验证 HR 公开信息优先。
- 招聘软件公开 JD 是较强岗位证据。
- 候选人面经和社媒信号只能作为辅助准备信号。
- 没有目标公司时，只按岗位族和学科域使用同类大厂先验。
- 大厂库不能覆盖当前 JD、用户原始材料或 FactualReviewer 的事实审查结论。

工作方面：

- 10 秒清晰度：目标岗位、学历状态、核心竞争力和最强证据是否能快速看到。
- 竞争力信号密度：是否突出 2-4 个最能打动 HR 的优势，而不是信息堆砌。
- 证据链一致性：简历、项目、GitHub、个人网站、作品集、论文、案例之间是否互相支撑。
- 学科/行业适配：展示标准是否符合 discipline_domain 和目标行业。
- HR 风险识别：目标不明、经历过散、技术自嗨、空泛性格、过度包装、隐私泄露、无法验证。
- 子智能体辩论裁决：当匹配策略、个人包装、简历写作和事实审查冲突时，要求补证据、降置信度或退回对应角色重写。

输出：

```json
{
  "hr_readability_score": 0,
  "company_hr_signal_refs": [],
  "target_company_screening_bias": [],
  "big_tech_hr_screening_notes": [],
  "competitive_signal_summary": [],
  "hr_first_screen_risks": [],
  "positioning_verdict": "pass|revise|required_user_confirmation",
  "debate_summary": {
    "agreements": [],
    "conflicts": [],
    "resolution": []
  },
  "agent_feedback": [],
  "recommended_reframe": [],
  "pass_to_next_stage": false
}
```

禁止事项：

- 不为提高吸引力编造经历、指标、奖项、学历或项目结果。
- 不用 HR 视角压过事实审查；事实冲突时以 FactualReviewer 为准。
- 不把个人包装变成夸张人设或营销话术。
- 不用单一行业标准评价所有学科背景。

### 5.13 ResumeFormatGate

简历格式门禁。负责回答：“用户当前材料是否已经满足简历生成格式，应该进入哪个简历版本？”

这个角色运行在 ResumeArchitect 之前，不负责写简历，只负责提交与驳回。它读取 `data/resume_formats/resume_format_database.zh-CN.json`，检查基础五板块是否可解析、证据密度是否足够、是否存在隐私或真实性风险，并选择默认或定向简历版本。

基础五板块：

- 学校信息。
- 个人联系方式。
- 掌握技能。
- 项目竞赛经历。
- 个人性格和潜力。

工作方面：

- 板块映射：判断用户材料能否映射到基础五板块。
- 格式门槛：检查每个板块是否只有标题、口号或空泛描述。
- 版本选择：无明确目标公司时默认校招通用版；有岗位族时选择软件/AI、硬件/嵌入式/IC、新能源/车辆/电池、科研/算法、实习短版、ATS 纯文本版等。
- HR 信任评分：按信息完整度、证据强度、岗位相关度、可读性、真实性风险和成长潜力表达评分。
- 驳回判断：缺联系方式、缺学校/专业/毕业时间、无项目证据、技能无支撑、隐私泄露、夸大责任等情况应驳回或要求用户确认。
- 生成许可：只有 `format_gate_status = pass` 时，ResumeArchitect 才能生成完整简历草稿；用户拒绝补充但明确同意时，只能进入信息不完整版草稿。
- 信息不全处理：缺失板块不写，不用占位符，不提供岗位投递方向，并再次告知详细信息才能做针对性建议。
- 权重边界：掌握技能和外部展示资产的具体权重由运行时 subagent 调研，不由格式库硬编码。

输出：

```json
{
  "format_gate_status": "pass|revise_required|user_confirmation_required",
  "primary_resume_version": "",
  "secondary_resume_version": "",
  "section_status": {},
  "hr_trust_score": 0,
  "score_breakdown": {},
  "reject_reasons": [],
  "missing_materials": [],
  "questions_for_user": [],
  "one_round_followup_prompt": "",
  "resume_architect_allowed": true,
  "incomplete_resume_allowed_with_user_consent": false,
  "job_direction_blocked": false
}
```

禁止事项：

- 不写最终简历。
- 不为缺失板块编造内容。
- 不把空泛性格描述直接塞进简历。
- 不批准有隐私、NDA 或事实风险的材料进入生成。
- 不因为仓库示例提到某项技能或外部资产，就把它当作所有用户的硬门槛。

### 5.14 ResumeArchitect

简历架构师。负责回答：“如何把真实经历组织成最适合这个岗位的表达？”

输入：

- 候选人画像
- 岗位分析
- 匹配策略
- 当前简历
- 用户目标版本，例如中文、英文、实习、全职、科研、工程、产品

工作方面：

- 读取 ResumeFormatGate 输出；如果格式未通过，不生成简历，只返回补材料清单。
- 如果用户明确同意信息不完整版草稿，只写已有事实能支撑的板块，缺失板块直接省略。
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
  "incomplete_resume": false,
  "job_direction_blocked": false,
  "incomplete_resume_warning": "",
  "final_resume_draft": ""
}
```

禁止事项：

- 不创造不存在的经历。
- 不把“参与”写成“主导”，除非材料有证据。
- 不为了 ATS 牺牲可读性。
- 不绕过 ResumeFormatGate 和 FactualReviewer。
- 不在信息不全草稿中写用户没有提到的板块。
- 不在信息不全草稿中提供投递方向。

### 5.15 FactualReviewer

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

## 6. 学科域与专业就业大类预分类

长期版本会覆盖工科、理科、文科、社科、商科、艺术设计、医学健康、农学、法学公共事务和跨专业背景。不同学科不能共用同一套评价逻辑，所以专业分类先进入 `data/discipline_taxonomy/discipline_registry.zh-CN.json`，再选择具体学科域数据库。

当前实现状态：

| 学科域 | 状态 | 核心评价逻辑 |
|---|---|---|
| 工科 | 已实现 | 工程项目、工具链、实验/仿真/制造/部署、可验证交付 |
| 理科 | 预留 | 数学建模、实验方法、科研训练、数据分析、工程化迁移 |
| 文科 | 预留 | 研究、写作、语言、内容判断、文本分析、文化/历史/政策理解 |
| 社科 | 预留 | 调研、统计、政策分析、组织理解、用户研究、咨询与公共事务 |
| 商科与管理 | 预留 | 财务、运营、市场、战略、投研、数据分析和商业结果 |
| 艺术与设计 | 预留 | 作品集、审美判断、设计过程、表达媒介、用户/品牌理解 |
| 医学与健康 | 预留 | 专业资质、实验/临床/法规、医疗器械、生物医药和健康数据 |
| 农学与生态产业 | 预留 | 实验田/养殖/食品/生态/资源、生产流程和产业链理解 |
| 法学与公共事务 | 预留 | 法律检索、案例分析、合规、政策、文书和表达 |
| 跨专业与复合背景 | 桥接层 | 原专业域、目标岗位域、桥接课程、项目、作品、证书或实习证据 |

未实现学科域不能输出伪完整分类。分类器应返回 `pending_static_database`，说明当前可用依据、需要补充的数据，以及临时岗位方向建议。

### 6.1 中国工科专业就业大类预分类

这套分类用于求职匹配，不是官方专业目录的替代品。官方专业类用于识别专业背景，求职大类用于判断岗位能力和补齐路径。一个专业可以拥有多个交叉标签。

仓库已经提供一份静态数据库，不需要每次运行时重新抓取或重新分类：

- `data/major_taxonomy/engineering_official_majors_2026.zh-CN.json`
- `data/major_taxonomy/engineering_employment_clusters.zh-CN.json`
- `data/major_taxonomy/engineering_employment_clusters.zh-CN.md`
- `data/major_taxonomy/engineering_major_index.zh-CN.csv`
- `data/major_taxonomy/engineering_related_interdisciplinary_majors_2026.zh-CN.json`
- `data/major_taxonomy/engineering_related_interdisciplinary_majors_2026.zh-CN.csv`
- `data/major_taxonomy/summary.json`

数据来源为教育部《普通高等学校本科专业目录（2026年）》中 `08 学科门类：工学`。当前版本抽取了 31 个官方工学专业类、293 个工科专业，并归并为 17 个就业导向大类。每个具体专业只有一个 `primary_cluster`，以降低不同大类之间的专业重合；但可以有多个 `cross_tags`，用于表示交叉分类和相邻岗位方向。

另外，目录中的 `14 学科门类：交叉学科` 包含一批与工科就业强相关的新专业，例如未来机器人、低空技术与工程、具身智能、工程互联网、集成电路科学与工程等。它们不属于 `08 工学` 门类，但多项授予工学学士学位，因此单独放入 `engineering_related_interdisciplinary_majors_2026.zh-CN.*`，作为 MajorClusterClassifier 的补充查询库。

### 6.2 工科分类原则

- 使用“主就业大类 + 交叉标签 + 权重”的形式。
- 主就业大类表示最常见、最直接的就业方向。
- 交叉标签表示该专业可迁移到的相邻能力域。
- 权重应结合用户课程、项目、技能和目标岗位动态调整。
- 相同专业在不同学校可能方向不同，例如自动化可能偏控制、机器人、嵌入式、工业过程或 AI。
- 专业分类只做初筛，不能替代个人能力画像。

输出示例：

```json
{
  "normalized_major": "人工智能",
  "primary_cluster": "计算机与 AI 软件类",
  "cross_tags": [
    {"tag": "电子信息", "weight": 0.25, "reason": "专业设置与智能感知、信号处理、嵌入式方向相关"},
    {"tag": "自动化与控制", "weight": 0.20, "reason": "机器人、控制、智能系统方向可迁移"},
    {"tag": "数学与数据建模", "weight": 0.20, "reason": "机器学习、优化、统计建模是能力底座"}
  ],
  "peer_majors": ["计算机科学与技术", "软件工程", "数据科学与大数据技术", "智能科学与技术"],
  "likely_role_families": ["AI 应用工程", "算法工程", "数据科学", "后端/平台工程"],
  "skill_gaps_by_target": {
    "LLM 应用工程": ["RAG", "向量数据库", "LLM eval", "工程部署"]
  }
}
```

### 6.3 工科预分类摘要

完整专业清单见 `data/major_taxonomy/engineering_employment_clusters.zh-CN.md`。下表只展示就业大类摘要，具体专业归属以静态数据库为准。

| 就业大类 | 覆盖专业数 | 官方专业类 | 典型岗位 |
|---|---:|---|---|
| 计算机与 AI 软件类 | 20 | 0809 | 后端开发、前端/全栈、客户端开发、AI 应用工程、算法工程、数据工程 |
| 电子信息、通信与集成电路类 | 22 | 0807 | 硬件工程师、嵌入式工程师、通信算法、FPGA、芯片设计、半导体工艺 |
| 自动化、控制与机器人工程类 | 8 | 0808 | 控制算法、机器人工程、嵌入式控制、PLC/工业自动化、运动控制、系统集成 |
| 机械、车辆与智能制造类 | 21 | 0802 | 机械设计、结构工程、车辆工程、制造工艺、设备工程、CAE 仿真 |
| 仪器、测控与智能感知类 | 3 | 0803 | 测试测量工程师、传感器工程师、仪器研发、硬件测试、智能感知工程师 |
| 材料、半导体材料与新能源材料类 | 23 | 0804 | 材料研发、工艺工程、质量工程、半导体材料、电池材料、检测分析 |
| 能源动力、电气与电力系统类 | 18 | 0805, 0806 | 电气工程师、电力系统、新能源工程、储能工程、热能工程、电控工程 |
| 土木、建筑、水利与空间基础设施类 | 34 | 0810, 0811, 0812, 0828 | 结构工程、施工管理、BIM 工程、水利工程、测绘/GIS、城市规划支持 |
| 化工、制药与过程工程类 | 9 | 0813 | 化工工艺、制药工艺、生产工程、过程安全、质量检测、研发助理 |
| 资源、地质、矿业、环境与安全类 | 28 | 0814, 0815, 0825, 0829 | 地质工程、资源勘查、矿业工程、环境工程、EHS、安全工程 |
| 交通运输、轨道与航运运行类 | 13 | 0818 | 交通规划、运输管理、轨道交通、航运技术、智慧交通、交通设备控制 |
| 航空航天、海洋、兵器与核工程类 | 31 | 0819, 0820, 0821, 0822 | 飞行器设计、航天系统、船舶设计、海洋装备、无人系统、制导控制 |
| 农业、林业与生态装备工程类 | 13 | 0823, 0824 | 农业装备、农业自动化、林业工程、木材加工、家具工程、生态装备 |
| 纺织、轻工、食品与消费品制造类 | 26 | 0816, 0817, 0827 | 纺织工程、服装工程、包装工程、食品研发、食品质量、轻工工艺 |
| 生物医学、生物工程与健康工程类 | 9 | 0826, 0830 | 医疗器械、生物工程、生物制药、合成生物、临床工程、康复工程 |
| 工程力学、仿真与基础建模类 | 2 | 0801 | CAE 仿真、结构分析、力学工程、工程建模、科研助理、仿真软件应用 |
| 公安技术、消防与公共安全工程类 | 13 | 0831 | 公安技术、消防工程、安全防范、网络安全执法、数据警务、应急救援 |


### 6.4 工科交叉分类示例

- 人工智能：主类可为“计算机与 AI 软件类”；交叉标签可为电子信息、自动化、数学建模。
- 机器人工程：主类可为“自动化、控制与机器人工程类”；交叉标签可为机械、电子信息、计算机、AI。
- 物联网工程：主类默认为“计算机与 AI 软件类”；若学校培养明显偏硬件、通信或嵌入式，可提升电子信息、嵌入式、通信等交叉标签权重。
- 智能制造工程：主类可为“机械、车辆与制造类”；交叉标签可为自动化、工业工程、数据分析。
- 生物医学工程：主类可为“生物医学、生物工程与健康工程类”；交叉标签可为电子信息、医学、算法、医疗器械。
- 新能源科学与工程：主类可为“电气与能源动力类”；交叉标签可为材料、化工、数据、设备工程。
- 工业设计：主类可随目标岗位变化；硬件产品方向偏机械与制造，互联网产品方向可交叉产品、设计、用户研究。
- 具身智能：来自交叉学科补充库；主类可为“计算机与 AI 软件类”，交叉标签可为机器人、自动化控制、数据与 AI。

### 6.5 基于专业大类的横向对比

用户输入具体专业后，系统应在同类和交叉类中横向比较，而不是直接给所有岗位打分。

对比维度：

- 同专业常见就业方向。
- 相近专业更强的能力，例如软件工程强工程实践，自动化强控制和系统，电子信息强硬件和信号。
- 用户相比同类候选人的优势和短板。
- 目标岗位需要补齐的最短路径。
- 哪些岗位适合立即投，哪些岗位适合学习 2-8 周后投，哪些岗位不建议当前阶段投入。

示例：

- 人工智能专业但工程项目弱：优先补 GitHub 项目、后端部署、LLM 应用工程，而不是只写机器学习课程。
- 机械专业想转机器人软件：补 Python/C++、ROS、控制基础、传感器、仿真项目，再投机器人应用/测试/系统集成岗位。
- 电子信息专业想转后端：补 Web 后端、数据库、分布式基础、项目部署，同时保留嵌入式/IoT 作为差异化标签。
- 材料专业想去新能源企业：强化电池材料、工艺、实验数据分析、质量体系，而不是泛泛转互联网。

### 6.6 大厂招聘信号数据库

仓库还提供第二个静态数据库：

- `data/company_signals/company_hiring_signal_seed.zh-CN.json`
- `data/company_signals/covered_companies.zh-CN.json`
- `data/company_signals/source_collection_targets.zh-CN.json`
- `data/company_signals/company_hiring_signals.schema.json`
- `data/company_signals/summary.json`

它的目的不是存储每个岗位的详细 JD，而是按“公司 + 工科就业大类”保存招聘信号先验。比如计算机与 AI 软件类在字节、腾讯、智谱、月之暗面等公司常见的准备方向；自动化、电子信息和机械制造类在大疆、比亚迪、宁德时代、汇川、海康等公司的准备方向；材料、电气、化工类在新能源、半导体、能源央企中的准备方向。

当前版本覆盖互联网、AI 大模型、通信 ICT、消费电子、机器人、汽车、新能源、半导体、智能制造、医疗器械、基础设施、运营商和央国企等 85 家工程热门就业公司。每家公司记录：

- 适配的工科就业大类。
- 适用的岗位族要求模板。
- 公司级考察方向 seed。
- HR 话术应采集主题。
- 候选人面经和社媒信号应采集主题。
- 简历和个人展示包装重点。
- 已有公开来源 evidence。
- 是否仍处于 `seed_unverified_requires_collection`。

来源优先级必须固定为：

1. 公司官网、官方招聘页、校招官网、官方 JD。
2. 已验证身份的 HR 公开账号或官方列出的 HR 社媒账号。
3. 招聘软件公开 JD，例如 BOSS 直聘、拉勾、猎聘、牛客企业招聘页、LinkedIn、Indeed。
4. 候选人面经、offer 复盘、公开内推贴、多平台社媒共识。
5. 单条匿名帖子、截图、评论区传闻。

第 4-5 类来源只能作为辅助信号，用于解释实际工作内容、面试体验、团队氛围、隐性要求、风险提示和 JD 模糊处。它们不能覆盖官方 JD，也不能被写成“公司确定要求”。如果招聘软件 JD 与社媒反馈冲突，输出应保留冲突，并以 JD 或官方来源为主证据、社媒为风险提示。

这个库也不保存个人简历、私聊记录、录用截图、手机号、私人邮箱、微信号或可反向识别个人的完整经历。成功候选人条件只能做去标识化、聚合化总结，例如“多个候选人面经都提到项目深挖、算法题和实习产出”，不能保存某个人的完整履历。

具体岗位分析仍然放在用户设备上实时运行。用户确定岗位后，pipeline 必须重新读取或让用户粘贴当前 JD，再由 JDAnalyzer 做岗位级 `must-have / nice-to-have / hidden_requirements / ats_keywords` 分析；大厂招聘信号库只提供先验和准备方向。

## 7. 数据来源设计

数据来源应分层处理，不同来源具有不同可信度和合规边界。

### 7.1 公开岗位信息

用途：JDAnalyzer、JobScout、MatchStrategist。

可用来源：

- 公司官网招聘页。
- 公开岗位 JD 页面。
- 用户粘贴的岗位描述。
- 校招官网、实习招聘页。
- 招聘公众号、学校 career portal。
- 招聘平台公开可访问的职位信息。

岗位信息来源优先级：

1. 公司官网、校招官网、官方招聘页。
2. 招聘软件公开 JD，例如 Boss 直聘、拉勾、猎聘、LinkedIn、Indeed 等公开职位页面。
3. 用户直接提供的 JD、HR 邮件、宣讲会材料、内推信息。
4. 招聘公众号、学校就业平台、行业社区的职位转发。
5. 小红书、脉脉、牛客、知乎、论坛、公众号评论等社交媒体讨论。

处理规则：

- 岗位要求、职责、学历年限、地点、薪资范围、技能关键词，应优先以第 1-3 类来源为准。
- 第 5 类社交媒体来源主要用于补充判断：非大厂岗位 JD 模糊处、实际工作内容、面试体验、团队氛围、加班强度、HC 真实性、隐性要求。
- 社交媒体来源不能单独推翻明确 JD；只有多平台、多时间点、多用户一致时，才可作为中等置信度趋势信号。
- 对非大厂、创业公司、小团队、岗位 title 模糊的情况，应主动用社交媒体和公开评价补充背景，但输出时必须标记为“补充信号”而非“岗位要求事实”。
- 若招聘软件 JD 与社交媒体反馈冲突，应同时呈现冲突，并以 JD 作为主证据、社交媒体作为风险提示。

约束：

- 遵守平台协议、robots、频率限制。
- 不绕登录。
- 不破反爬。
- 不抓取非公开数据。

### 7.2 公司基本面与发展状况

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

### 7.3 外界评价与市场风向

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
- 对岗位职责和任职要求的判断，优先以招聘软件公开 JD、公司官网、校招官网和用户提供 JD 为准；小红书、脉脉、牛客、知乎等只用于补充“实际工作内容、面试体验、团队氛围、隐性要求、非大厂 JD 模糊处的解释”。

### 7.4 用户授权样本

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

### 7.5 不建议或禁止的数据

不应爬取：

- 招聘平台上未授权的成功受聘人简历。
- 登录后才能看到的求职者简历。
- 私聊记录。
- HR 后台候选人信息。
- 录用结果、薪酬、求职状态等个人敏感信息。
- 绕过平台访问控制取得的数据。

原则：

岗位分析可以来自公开 JD、公司公开信息、外界公开评价和用户授权样本；不能依赖未经授权的个人简历抓取。

## 8. 证据与可信度分级

建议所有输出都带证据等级：

| 等级 | 来源类型 | 处理方式 |
|---|---|---|
| A | 公司官网、校招官网、官方招聘页、官方财报、用户原始材料 | 可作为强证据 |
| B | 招聘软件公开 JD、主流媒体、多源一致报道、行业报告 | 可作为较强证据 |
| C | 多人一致的公开面经、牛客/脉脉/小红书/知乎等多源一致评价 | 可作为趋势信号或补充解释 |
| D | 单条匿名评价、论坛吐槽、无法核实截图、单一社交媒体帖子 | 只能作为弱信号 |
| E | 模型推断 | 必须标记为推断，不能当事实 |

时间权重：

- 0-6 个月：高权重。
- 6-12 个月：中权重。
- 1-3 年：低权重。
- 3 年以上：仅作背景参考。

## 9. 子智能体协作与辩论协议

子智能体之间需要能相互配合和辩论，而不是各自独立输出结论。仓库里的各角色 prompt 只提供框架：定义要收集什么、证据如何分级、哪些字段共享、何时交给运行时本地 subagent 判断。所有角色输出都应保留共同字段、证据说明、置信度和需要用户确认的问题。涉及简历、包装、匹配和 HR 监督的角色还应显式输出冲突点和反驳理由。

协作规则：

- 每个角色只能在自己的职责内提交证据绑定的流程状态、条件化选项或运行时研究任务，不能替代其他角色做最终推荐。
- 每个角色输出都需要能被运行层追踪：保留 `invocation_ref`、`artifact_refs`、`execution_log_refs`、`role_output_packet_ref` 和必要的 `error_recovery_state_ref`。
- 任何强结论都必须来自用户材料、当前 JD、官方/公开来源或运行时 subagent 收集的证据，并明确标记推断。
- 下游角色可以挑战上游角色，但必须指出冲突字段、证据差异和希望重跑的角色。
- `HRSupervisor` 负责把子智能体冲突转化为 HR 可读性和展示准备度的 `pass|revise|required_user_confirmation` 流程状态；它不是最终求职裁判。
- `FactualReviewer` 对事实真实性拥有最高优先级；HR 认为表达强但事实不足时，必须退回补证据。
- 当 `MatchStrategist` 输出高优先级条件但 `ProfileExtractor` 证据弱，必须进入辩论状态，不能直接生成强包装。
- 当 `PersonalBrandingStrategist` 输出展示资产选项但无法支撑简历主线，必须退回补证据或重构包装方案。
- 当某个子智能体失败、输出格式错误或只返回安全部分结果，Orchestrator 只能合并 `evidence_basis`、`blocked_outputs`、`runtime_research_tasks`、`evidence_requirements`、`needs_user_confirmation` 等安全字段；不能合并 fit score、投递优先级、HR 通过状态、最终简历草稿或应用策略。

建议所有关键角色输出：

```json
{
  "execution_manifest": {},
  "artifact_refs": [],
  "execution_log_refs": [],
  "error_recovery_state": {},
  "agent_claims": [],
  "evidence_challenges": [],
  "disagreements_with": [
    {
      "agent": "",
      "field": "",
      "reason": "",
      "requested_resolution": ""
    }
  ],
  "handoff_questions": []
}
```

辩论不应该变成多轮空转。若冲突来自缺少用户材料，应停止生成最终简历或包装，输出补材料清单；若冲突来自来源优先级，应以官方 JD、用户原始材料、已验证 HR 公开信息和 FactualReviewer 结论为高优先级依据。

## 10. 输出产品形态

最终输出不应该只有一份改写后的简历，而应包括一个 decision package：

```text
1. 候选人画像摘要
2. 目标岗位画像
3. 公司情报摘要
4. 外界评价与市场风向
5. 人岗匹配证据与差距分析
6. 条件化投递选项与优先级前置条件
7. 学习路径与能力补齐方案
8. 个人展示与包装方案
9. HR 监督与首筛可读性结果
10. 子智能体辩论与冲突裁决
11. 简历格式门禁结果
12. 简历设计方案
13. 简历改写草稿
14. 风险审查结果
15. 面试准备建议
```

示例结构：

```json
{
  "candidate_summary": {},
  "job_summary": {},
  "company_intelligence": {},
  "market_sentiment": {},
  "fit_analysis": {},
  "learning_plan": {},
  "personal_branding": {},
  "hr_supervision": {},
  "agent_debate": {},
  "resume_format_gate": {},
  "resume_plan": {},
  "resume_draft": "",
  "factual_review": {},
  "next_actions": []
}
```

## 11. 参数归属与运行时权重

pipeline 的参数不应该全部向用户追问，也不应该全部写死在仓库里。当前分成四类：

```json
{
  "user_required_minimal": [
    "学校/专业/学历/年级或毕业时间",
    "当前目标：实习、全职、校招、社招、目标岗位或方向",
    "生成简历时需要的姓名或称呼、邮箱或电话",
    "项目、实习、竞赛、科研、课程等能证明能力的材料"
  ],
  "user_optional": [
    "GPA/排名",
    "奖项证书",
    "语言成绩",
    "城市/薪资/稳定性偏好",
    "作品链接或公开主页",
    "简历语言和格式偏好"
  ],
  "subagent_research": [
    "目标岗位当前技能权重",
    "目标学科和岗位对 GitHub/个人网站/作品集/论文页等外部展示资产的认可度",
    "学校与企业合作、宣讲、实习基地、就业报告",
    "目标公司的发展状态、招聘风向、HR 公开话术和候选人面经"
  ],
  "runtime_weight_config": [
    "skill_weight",
    "external_asset_weight",
    "school_signal_weight",
    "application_strategy_weight"
  ],
  "runtime_weights": [
    {
      "parameter": "",
      "weight_scope": "skill_weight|external_asset_weight|school_signal_weight|application_strategy_weight|hr_screening_weight",
      "proposed_weight": null,
      "weight_status": "verified|needs_more_sources|not_available",
      "evidence_basis": [],
      "source_count": 0,
      "source_mix": [],
      "freshness": "",
      "conflict_notes": [],
      "cannot_decide_alone": true
    }
  ]
}
```

关键规则：

- 仓库只提供 schema、证据规则、来源优先级和提示词框架，不固定某专业必须掌握哪些具体技能。
- 第 7 类“掌握技能”只作为简历板块和证据索引存在；具体技能要求与权重由用户设备上的 subagent 根据当前 JD、招聘平台、企业官网、已验证 HR 公开信息和学科证据调查。
- 第 10 类“外部展示”同样不写死。GitHub、个人网站、作品集、论文页、demo、博客、报告等由运行时判断是否值得做、优先级多高、是否适合该学科。
- 所有参数权重、分数、优先级、排序、阈值和置信度调整都必须有硬数据支撑：当前 JD、企业/学校官方页面、招聘平台公开 JD、已验证 HR 公开信息、公开报告、多源候选人信号或用户提供材料。子智能体不能凭直觉、仓库示例或模型推理直接设权重；证据不足时必须标记 `not_available` 或 `needs_more_sources`，并生成网络验证任务。
- 权重合并不能把冲突弱信号平均成精确分数。单条匿名社媒只能作为弱信号；仓库先验只能指导调研，不能单独设定最终权重。
- 能从用户材料提取的，不问用户；能由 subagent 查公开信息的，不问用户；只有用户本人事实才集中问一次。
- 用户拒绝补充时，只有在用户明确同意后才能生成信息不全版简历；未提到的板块不写，投递方向不提供。

## 12. MVP 建议

第一版不做全网岗位搜索，先支持用户提供材料：

输入：

- 用户简历。
- 一个或多个岗位 JD。
- 一个或多个目标公司。
- 用户偏好。

MVP 流程：

```text
InputNormalizer
  -> ProfileExtractor
  -> JDAnalyzer
  -> CompanyIntelligenceAnalyst
  -> MarketSentimentAnalyzer
  -> MatchStrategist
  -> LearningPathStrategist
  -> PersonalBrandingStrategist
  -> HRSupervisor
  -> ResumeFormatGate
  -> ResumeArchitect
  -> FactualReviewer
  -> HRSupervisor
```

MVP 输出：

- 候选人画像。
- 岗位拆解。
- 公司与风向摘要。
- 条件化匹配证据矩阵、blocked outputs 和投递优先级前置条件。
- 学习路径和能力补齐建议。
- GitHub、个人网站、作品集等个人展示建议，但必须说明这些建议来自运行时学科/岗位/公司证据，而不是仓库固定要求。
- HR 首筛视角下的竞争力摘要和可读性评分。
- 子智能体冲突点、裁决结果和需要用户补充的材料。
- 简历格式门禁结果。
- 简历结构建议。
- 针对岗位的简历草稿。
- 风险审查清单。

MVP 验收标准：

- 所有强判断必须有来源或用户材料依据。
- 简历改写不能引入无证据事实。
- 岗位匹配证据必须区分硬门槛和软匹配，优先级只能在运行时证据齐全后输出。
- 对于可学习差距，必须给出具体学习路径、项目产出和可写入简历的证据标准。
- 对于需要外部展示的行业，必须说明推荐展示资产、完成标准、来源依据和运行时权重。
- 公司评价必须带置信度。
- 输出能让用户明确知道下一步该做什么。

## 13. 后续扩展

### 13.1 Job Search 扩展

增加自动岗位搜索：

- 公司官网职位抓取。
- 招聘平台公开页面解析。
- 岗位去重。
- 岗位时效判断。
- 关键词策略生成。

### 13.2 Talent Benchmark 扩展

增加授权样本库：

- 成功候选人匿名画像。
- 按岗位方向聚合特征。
- 生成岗位成功画像。
- 比较用户与成功画像的差距。

### 13.3 Resume Rendering 扩展

增加输出格式：

- Markdown。
- DOCX。
- LaTeX。
- 中文简历。
- 英文 resume。
- 一页版与详细版。

### 13.4 Interview Preparation 扩展

增加面试准备：

- 根据简历生成追问清单。
- 根据 JD 生成技术面题。
- 根据公司业务生成业务理解题。
- 根据项目经历生成 STAR 故事。

### 13.5 Learning Roadmap 扩展

增加面向目标岗位的学习路线生成：

- 从岗位群中抽取高频技能差距。
- 根据用户已有基础识别可迁移能力。
- 生成 7 天、14 天、30 天、90 天学习路线。
- 将学习任务转化为可展示项目。
- 输出“完成到什么程度才可以写进简历”的证据标准。
- 生成学习后的简历 bullet 草稿，但必须经过 FactualReviewer 审查。

### 13.6 Personal Branding 扩展

增加个人展示资产生成和审查：

- GitHub profile README。
- 项目 README 模板。
- 个人网站结构。
- 作品集目录。
- LinkedIn / 脉脉 summary。
- 技术博客选题。
- 项目 demo 展示清单。
- 隐私和 NDA 风险检查。

### 13.7 Plugin 分发

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

## 14. 核心原则

1. 求职建议必须可解释。
2. 简历改写必须可追溯到用户原始材料。
3. 公司和市场判断必须带来源、时间和置信度。
4. 不抓取未授权个人简历。
5. 不把匿名情绪当事实。
6. 不为提高匹配度编造经历。
7. 不把未完成的学习或项目包装成既有成果。
8. 对可学习差距给出成长路径，而不是只做静态岗位过滤。
9. 根据行业设计个人展示资产，不把所有人都套进同一套包装模板。
10. 技能权重和外部展示权重由运行时 subagent 调研设置，仓库不写死。
11. 只集中询问用户本人事实，尽量减少用户补充次数。
12. 先做本地 Codex workflow，再考虑 plugin 化。
