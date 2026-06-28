# Codex 职业规划 Pipeline

Career Pipeline 是一个面向中国早期求职者的 Codex Skill，用来做职业方向判断、岗位探索、能力提升规划和简历设计。

它围绕一个核心思路设计：

> **一个岗位，一份简历。先从岗位出发，再反向设计学习计划和简历表达。**

当前可用范围是**工科专业和工科交叉背景**。文科、理科、商科和跨专业路径已经在框架与分类中预留，但现阶段 MVP 以工科路径为主。

## 核心特点

- **量身定制规划**：综合分析用户的专业、年级、经历、限制条件和目标方向。
- **反向设计简历**：先看目标岗位或 JD，再决定简历应该突出什么。
- **先补能力再投递**：如果用户暂时不适合直接投递，会给出具体技能、项目、证明材料和写入简历的条件。
- **一个岗位一份简历**：当用户有明确公司或岗位时，避免生成泛泛而谈的通用简历。
- **两版简历输出**：生成当前真实简历，并额外给出完成推荐技能或项目后的简历预览版。
- **多子智能体协作**：协调 15 个角色 prompts/subagents，并使用覆盖 85 家工科热门雇主的种子公司信号数据库。
- **重视公开来源**：优先使用公开岗位 URL、企业官网、学校就业信息、招聘平台、地方机会和可验证的 HR 公开信息。
- **真实性门禁**：计划学习的技能或项目不能提前写成已完成经历，必须等用户有可证明材料后再转入正式简历。

## 可以产出什么

- 当前个人定位和适合的方向簇。
- 推荐岗位池或投递目标，并附公开 URL。
- 匹配理由、风险点和缺失信息。
- 学习路径和项目实践建议。
- 有公开来源支撑时，提供目标公司或推荐公司的 HR 风格准备重点。
- 当前真实简历草稿。
- 完成学习或项目后的简历预览版。
- Word DOCX、PDF 和首页 PNG 简历文件。
- 用户接下来最应该做的 3 个动作。

## 部署

克隆仓库，并在仓库根目录打开 Codex：

```bash
git clone https://github.com/racingemperor/codex-career-agent-design.git
cd codex-career-agent-design
```

仓库级 Skill 入口是：

```text
.agents/skills/career-pipeline/SKILL.md
```

常用本地检查命令：

```bash
python .agents/skills/career-pipeline/scripts/validate_runtime_contracts.py --repo-root .
python -m pytest tests/test_runtime_tools.py -q
```

## 在 Codex 中运行

在 Codex 中从本仓库目录打开一个新对话，然后这样开始：

```text
使用 career-pipeline skill。
我是计算机相关专业大三，本科，会一点 Python，想找实习但不知道投什么。
请帮我判断方向、规划技能和项目，并设计简历。
```

如果用户已经有目标岗位，可以这样输入：

```text
使用 career-pipeline skill。
我是自动化方向研究生，会 C++、ROS、Python，有机器人竞赛经历。
目标：DJI 机器人/控制算法实习。
请判断我现在是否适合投递；如果暂时不适合，请给我先准备再投递的计划，以及更贴合该岗位的简历方向。
```

如果需要做确定性的本地合约冒烟运行：

```bash
cd .agents/skills/career-pipeline
python scripts/career_pipeline_run.py --task-type target_job_fit --route target_job_fit --input-text "computer science senior, assess fit for Tencent backend role. JD: Java and MySQL" --run-root ../../../.career-pipeline-runs --source-adapter seed --subagent-adapter mock-blocked
```

`seed` 和 `mock-blocked` 只是本地冒烟测试模式，不会浏览实时招聘网站，也不能证明真实子智能体已经执行。

## 典型使用方式

在 Codex 中打开这个仓库后，可以直接说：

```text
使用 career-pipeline skill。
我是计算机相关专业大三，本科，会一点 Python，想找实习但不知道投什么。
请帮我判断方向、规划技能和项目，并设计简历。
```

如果用户有明确岗位，可以直接给出岗位：

```text
使用 career-pipeline skill。
我是自动化方向研究生，会 C++、ROS、Python，有机器人竞赛经历。
目标：DJI 机器人/控制算法实习。
请判断我现在是否适合投递；如果暂时不适合，请给我先准备再投递的计划，以及更贴合该岗位的简历方向。
```

预期产品流程是自然聊天。用户不需要理解 subagent、JSON、runner 或 adapter：系统会用一轮紧凑的信息收集完成公开来源搜索、方向或岗位匹配判断、学习和项目规划、简历设计以及文件导出。

## 简历输出

Skill 会区分两种版本：

- **当前真实简历**：只使用用户已经提供、且现在可以证明的信息。
- **成长后预览版**：展示用户完成推荐技能或项目后，简历可以如何呈现。这个版本必须明确标注为预览，不能在完成前当作真实简历使用。

最终包准备好后，可以用下面的命令导出简历文件：

```bash
cd .agents/skills/career-pipeline
python scripts/render_resume_artifacts.py --decision-package ../../../.career-pipeline-runs/<run_id>/final/decision_package.json --out-dir ../../../.career-pipeline-runs/<run_id>/final/resume_artifacts --basename general_resume --all-resume-versions
```

该命令会导出 DOCX、PDF、PNG、`resume_draft.md`，如果有成长后版本，也会导出 `growth_resume_preview.md`。

## 开发说明

产品流程检查使用 `scripts/run_product_flow.py`。如果主 Codex 控制器已经通过浏览器搜索或可见网页结果收集到公开 URL，可以通过 `scripts/collect_public_source_results.py` 传入，不需要手写 JSON。记录文件可以使用简单 URL 行，也可以使用类似 YAML 的块结构并带上 `source_type_hint`；企业官网和搜索页只作为探索入口，只有具体公开 JD 才能支撑更强结论。

真实子智能体执行时，如果 Codex Desktop 可用，优先使用 Codex Desktop 内置 subagent adapter。`mock-blocked` 只保留为本地合约冒烟模式，不能作为真实角色执行证明。

目标岗位判断中，如果城市、截止时间、招聘人数或实习周期等细节缺失，应进入 `ask_hr_about`。系统可以在继续收集更强证据的同时，先返回 prepare-first / `prepare_first` 计划。

## 更新记录

- 2026-06-28：新增 MIT 许可证，并将仓库设为公开。
- 2026-06-28：简化 README 的公开展示内容，详细旧版已归档到 `docs/archive/`。
- 2026-06-28：新增两版简历输出：当前真实简历和完成学习/项目后的预览版。
- 2026-06-28：新增 DOCX、PDF、PNG、`resume_draft.md` 和 `growth_resume_preview.md` 导出支持。
- 2026-06-28：当前可用范围是工科专业和工科交叉背景，非工科方向后续补齐。
- 包装状态：当前仍是仓库级 Codex Skill，还不是 `.codex-plugin` 插件包。

## 关键文件

- [Skill 入口](.agents/skills/career-pipeline/SKILL.md)
- [角色 prompts](.codex/agents)
- [来源策略](.agents/skills/career-pipeline/references/source-policy.md)
- [真实用户流程](.agents/skills/career-pipeline/references/real-user-deployment-and-use-flow.md)
- [已归档详细 README](docs/archive/README.product-detailed-2026-06-28.md)

## 安全边界

- 不伪造教育经历、实习经历、项目、奖项、数据指标或个人贡献。
- 不抓取私人简历、私人候选人资料、私人 HR 消息或需要登录才能查看的内容。
- 不绕过登录、验证码、仅 App 可见页面、后端接口或访问控制页面。
- 不把社交媒体信息看得比官方 JD 或招聘证据更可靠。
- 没有公开 URL 时，不推荐具体投递目标。

## 许可证

MIT 许可证。详见 [LICENSE](LICENSE)。
