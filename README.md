# Codex Career Pipeline

**Codex-native career planning and resume design skill for Chinese early-career candidates.**

This repository contains a Codex Skill that helps users move from an incomplete self-introduction to a role-specific application plan: public job evidence, fit analysis, learning gaps, personal branding, and a resume designed backward from the target role.

Current planning scope is **engineering majors and engineering-adjacent backgrounds**. Other disciplines are reserved in the taxonomy and prompt framework, but engineering is the first usable MVP.

[Skill Entry](.agents/skills/career-pipeline/SKILL.md) | [Real User Flow](.agents/skills/career-pipeline/references/real-user-deployment-and-use-flow.md) | [Source Policy](.agents/skills/career-pipeline/references/source-policy.md) | [Reference Repo Gap Analysis](docs/reference-repo-gap-analysis-2026-06-28.md) | [Archived Old README](docs/archive/README.legacy-2026-06-27.md)

## News

- 2026-06-27: Added public-source recovery rules for login walls, CAPTCHA pages, app-only pages, and dynamic JavaScript shells.
- 2026-06-27: Added limited final-package support for `prepare-first` outputs when exact fit score, final priority, or company-specific tailoring is not yet supported by evidence.
- 2026-06-27: Added Codex Desktop built-in subagent adapter protocol for batched role execution.
- 2026-06-28: Added company-bound HR real-question sourcing and concrete project recommendation contracts.

## What It Does

Career Pipeline is not a generic resume beautifier. It is designed around one principle:

> **One role, one resume. Start from the target role, then design the candidate presentation backward.**

The skill can help with:

- **Personalized career positioning**: classify the user's major, stage, strengths, constraints, and possible engineering job families.
- **Target-job fit analysis**: compare the user's current evidence with a concrete internship or full-time role.
- **Learning-first planning**: when the user is not ready, propose skills, projects, proof artifacts, and resume-conversion conditions before applying.
- **Concrete project recommendation**: when project evidence is weak, suggest the easiest credible project path for the target role, including implementation steps, proof artifacts, and when it can truthfully enter the resume.
- **Project evidence toolchain**: score public project candidates, audit local source repositories, and generate project interview packs before turning project work into resume-ready claims.
- **Role-specific resume strategy**: design a resume around one company or one role family instead of producing a broad, generic resume.
- **Personal branding**: decide whether GitHub, Gitee, personal website, portfolio, paper page, project demo, blog, or other assets matter for the target direction.
- **Public-source job research**: use official career pages, school notices, public JDs, verified HR public posts, reports, local employer sources, small/mid-size company sources, school-local internship notices, and weak social signals with explicit confidence levels.
- **Company-bound HR question prep**: collect target-company or recommended-company HR public wording from official/verified sources; if no reliable public HR source exists, say so instead of generating fake HR talk.
- **HR-supervised output**: keep the final advice concise, credible, and easy for a recruiter to scan.

## Core Idea

Most resume tools start from "what the user already has." This skill starts from:

1. what the target role screens for;
2. what the target company or comparable companies value;
3. what the user can prove today;
4. what the user can realistically learn or build next;
5. how to express only truthful, interview-defensible evidence in the resume.

The result should be a compact decision package:

- recommended application targets with real public URLs;
- current fit and risks;
- missing skills and concrete learning path;
- concrete projects and proof artifacts to build before applying;
- one-role resume outline or draft;
- company-bound HR/面试可能追问 when supported by target or recommended company public sources;
- HR confirmation items such as city, deadline, headcount, or internship duration when the public page is silent.

The job pool should not be limited to big tech. When the user has no precise target, the skill should consider major companies, small/mid-size companies, startups, local/regional employers, school-recommended internships, industrial-park or incubator employers, and local public internship channels when public evidence exists.

## Pipeline

```text
User Input
  -> InputNormalizer
  -> CareerOrchestrator
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

Subagents are dispatched in batches and pass artifacts forward. Completed subagents can be closed; their information is preserved in local JSON artifacts, not in chat memory.

## Key Features

### Role-Specific Resume Design

The resume is not written as a universal document. The pipeline first analyzes the target role, then decides:

- which experiences should be foregrounded;
- which skills should be treated as must-have evidence;
- which projects should be reframed;
- which weak or unsupported claims must be removed;
- which version to generate: broad campus resume, target-company resume, target-role resume, internship resume, or incomplete resume with user consent.

### Learning Before Applying

If a user has useful foundations but is missing a key direction, the skill does not simply reject the target. It can produce a `prepare-first` plan:

- skills to learn;
- projects to build;
- public proof artifacts to create;
- when the new work can truthfully enter the resume;
- what to apply to now versus what to delay.

Example: a student with Python and Java but weak LLM knowledge can be guided toward AI application projects, RAG/Agent basics, evaluation artifacts, and resume bullets only after those artifacts exist.

When a user lacks project experience, the project advice should be specific enough to execute:

- target role or role family;
- recommended project mode: `interview-only`, `smoke-test`, `local-full-run`, or `remote-full-run`;
- implementation steps;
- proof artifacts such as GitHub/Gitee, README, demo screenshots, logs, tests, or evaluation notes;
- resume-conversion conditions.

Planned project work is preparation. It must not be written as completed resume experience until the user actually finishes the proof artifacts and can explain personal contribution.

For open-source or public project paths, the bundled MVP scripts can support the evidence chain:

- `discover_project_candidates.py`: scores a public candidate pool, caps star-count influence, and filters shallow wrappers, templates, browser extensions, SDK/framework-only projects, and missing public repo URLs.
- `audit_project_repository.py`: scans a locally cloned repository for README, dependencies, Docker/deploy files, tests, API/backend signals, state/database evidence, async jobs, AI/agent signals, and source evidence points.
- `build_project_interview_pack.py`: turns source audit evidence and a recommendation into a project positioning, existing-capability/modification/resume-ready split, STAR outline, interviewer follow-ups, core-code explanation path, and proof-artifact list.

Without local source audit evidence, project recommendations remain preparation guidance and should not become completed resume claims.

### HR Questions From Public Sources

HR/面试可能追问 must be company-bound. The source should be the target company, a recommended company, or that company's official/verified recruiting source:

- official company recruitment or campus page;
- enterprise-certified recruiting account;
- official-listed recruiter or verified HR public post;
- public recruitment-platform process notes.

Candidate experience and social media can only support preparation notes. If no reliable target-company or recommended-company HR wording is found, the skill should say that clearly and create a research task. It should not invent HR wording.

### Public Evidence And Source Accuracy

Every job or internship recommendation shown to the user must include an inspectable public URL. Sources are ranked:

| Tier | Sources | Can Support |
|---|---|---|
| A | Official JD, official career/campus page, school official notice, user original material | Strong claims, job requirements, school signals, weights |
| B | Public recruitment-platform JD, verified HR public post, credible public report | Role/company signals with recency limits |
| C | Candidate experience, offer review, public referral, multi-source social consensus | Preparation notes and risk signals only |
| D | Login wall, CAPTCHA, app-only/private/backend page, screenshot-only claim, JavaScript shell without public rendered text | Not usable evidence |

If a source hits a login wall, CAPTCHA, app-only page, or dynamic shell, the pipeline should automatically search for a public replacement. It must not ask the user to log in, paste private screenshots, or bypass platform controls.

### HR And Factual Review

`HRSupervisor` checks whether the output is recruiter-readable:

- target role is clear;
- strongest 2-4 competitive signals are visible;
- evidence chain is credible;
- recommendation has public URLs;
- company or big-tech priors do not override current JD evidence.

`FactualReviewer` blocks fake or overclaimed resume content:

- no invented education, awards, projects, papers, metrics, internships, or ownership;
- no planned learning written as completed skill;
- no private or non-public data leakage;
- no weak social source used as a final application basis.

## Repository Layout

```text
.agents/skills/career-pipeline/
  SKILL.md                         # Main Codex Skill entry
  references/                      # Runtime, source, URL, adapter, and user-flow policies
  scripts/                         # Contract validation, simulation, source, and adapter helpers

.codex/agents/
  *.toml                           # Role prompt frameworks for local subagents

data/
  discipline_taxonomy/             # Discipline routing; future non-engineering expansion
  major_taxonomy/                  # Engineering major and employment-cluster database
  company_signals/                 # Company priors, source targets, official entrypoints
  runtime_parameters/              # User-owned vs subagent-researched parameters
  school_signals/                  # School-company signal policy
  resume_formats/                  # Resume section and format rules

tests/
  test_runtime_tools.py            # Runtime contract and prompt-policy regression tests

docs/archive/
  README.legacy-2026-06-27.md      # Previous detailed README preserved for reference
```

## Quick Start

Clone the repository and open Codex in the repo root. The Skill entry is repo-scoped:

```text
.agents/skills/career-pipeline/SKILL.md
```

For normal users, the intended experience is plain chat. They should not need to understand subagents, JSON, runners, adapters, or internal artifacts. A standard run starts from the user's first sentence, introduces the skill, asks one compact batch of missing user-owned facts, searches public job sources, judges fit, gives learning guidance, runs the resume gate, generates a general or targeted resume draft, and returns a concise Chinese report.

A user can invoke it naturally:

```text
Use the career-pipeline skill.
我是软件工程大三，本科，做过一个 Java 后端项目和一个 Python 数据分析项目。
我想找互联网后端或 AI 应用实习，但还不确定投哪个公司。
请帮我规划岗位方向、需要补什么能力、简历应该怎么设计。
```

For a target role:

```text
Use the career-pipeline skill.
我是自动化研一，会 C++、ROS、Python，有机器人竞赛经历。
目标是大疆机器人/控制算法实习。请判断现在适不适合投，
如果不适合，告诉我先补什么项目和技能，再设计一版更贴合这个岗位的简历。
```

For product-flow testing from one plain user sentence:

```bash
cd .agents/skills/career-pipeline
python scripts/run_product_flow.py --task-type job_search --route job_search --input-text "我是计算机相关专业大三，会一点 Python，想找实习但不知道投什么。" --run-root ../../../.career-pipeline-runs
```

This produces a user-facing status report plus controller handoff artifacts for public-source search and batched role execution. It does not pretend to be a final career judgment before real public sources and real role outputs exist.

When Codex or the browser has collected public URLs, convert them without hand-writing JSON:

```bash
python scripts/collect_public_source_results.py --run-dir ../../../.career-pipeline-runs/<run_id> --notes-md <public_source_notes.md>
```

The notes file can be simple URL lines or YAML-like blocks. Use blocks when the controller has a title, snippet, task id, or source type hint from visible public search results:

```md
- task_id: recruitment-platform-public-jd
  url: https://www.nowcoder.com/jobs/detail/123
  title: Python backend intern public JD
  source_type_hint: recruitment_platform_jd
  snippet: Python, SQL, API, Linux.
```

The collector maps `source_type_hint` into the normal `source_type` field and still sends every URL through source-policy filtering, fetch/degrade handling, and final gates.

Official recruiting homepages, campus entrypoints, job-search pages, and report search entrypoints can be shown as useful public URLs, but they are exploration entrypoints. They must not be treated as concrete JD evidence, role requirements, final application priority, or resume-tailoring proof unless the fetched public text contains duties, qualifications, skill requirements, or other claim-specific evidence.

After a final decision package contains a factual-reviewed resume draft, export the resume files locally:

```bash
python scripts/render_resume_artifacts.py --decision-package ../../../.career-pipeline-runs/<run_id>/final/decision_package.json --out-dir ../../../.career-pipeline-runs/<run_id>/final/resume_artifacts --basename general_resume
```

This produces an editable Word DOCX, printable PDF, first-page PNG preview, and `resume_draft.md` copy in the artifact directory. The renderer can also accept a direct Markdown draft through `--draft-md`.

For incomplete-user delivery validation, the repository includes a bounded Manual Controller helper:

```bash
python scripts/build_incomplete_user_manual_outputs.py --run-dir ../../../.career-pipeline-runs/<run_id> --out-dir ../../../.career-pipeline-runs/<run_id>/manual-controller-outputs
```

Use it only to verify that a vague first message can flow into safe exploration guidance, a broad campus/internship resume draft, and DOCX/PDF/PNG artifacts. It is not a live subagent adapter and should not be treated as proof of exact fit scores, final application priority, or company-specific tailoring.

## Contract Smoke Run

This command checks local wiring only. It does not call real subagents and does not browse live recruitment sites:

```bash
cd .agents/skills/career-pipeline
python scripts/career_pipeline_run.py --task-type target_job_fit --route target_job_fit --input-text "computer science senior, assess fit for Tencent backend role. JD: Java and MySQL" --run-root ../../../.career-pipeline-runs --source-adapter seed --subagent-adapter mock-blocked
```

Expected behavior:

- `mock-blocked` produces schema-valid blocked role outputs.
- `real_subagent_execution = false`.
- `.career-pipeline-runs/<run_id>/` stores local artifacts.
- The `seed` source adapter is deterministic and local, not fresh web evidence.

Run verification:

```bash
python .agents/skills/career-pipeline/scripts/validate_runtime_contracts.py --repo-root .
pytest -q
```

For product-flow review without running the full test suite, use the manual user-flow checklist:

- [Incomplete undergraduate user flow](docs/manual-tests/incomplete-undergrad-user-flow-2026-06-28.md)

## Real User-Side Execution

For real output in Codex Desktop, prefer the **Codex Desktop built-in subagent adapter** when current-session `multi_agent_v1.spawn_agent` is available.

High-level flow:

1. Normalize the user's first-round profile.
2. Build a runtime context packet and secondary prompt injections.
3. Generate subagent work orders.
4. Search public sources from the source matrix.
5. Dispatch role subagents by batch.
6. Persist strict JSON role outputs.
7. Run HR and factual review gates.
8. Return a final or degraded decision package.

See:

- [Codex Desktop Subagent Adapter](.agents/skills/career-pipeline/references/codex-desktop-subagent-adapter.md)
- [Manual Controller Runtime Flow](.agents/skills/career-pipeline/references/manual-controller-runtime-flow.md)
- [Runtime Network And Adapter Setup](.agents/skills/career-pipeline/references/runtime-network-and-adapter-setup.md)

## Output Style

The final user-facing answer should be professional and compact:

```text
1. 当前定位
2. 推荐方向/岗位池
3. 为什么适合
4. 还差什么
5. 先学什么/做什么项目
6. 简历怎么写
7. 通用简历草稿 / 定制简历草稿
8. 简历交付物
9. HR/面试可能追问
10. 推荐查看的公开 URL
11. 需要问 HR 的事项
12. 下一步 3 个动作
```

If public evidence is incomplete, the output should still give safe planning advice, but exact fit score, final application priority, apply-now decision, company-specific skill weights, and targeted resume tailoring remain unavailable until evidence supports them.

If a JD or URL does not state opening status, freshness, city, work location, onsite days, arrival time, deadline, headcount, or internship duration, do not block the recommendation only for that reason. Add those fields to `ask_hr_about` and tell the user to confirm with HR or the recruiter.

## Current Status

Implemented:

- Codex Skill entry and role prompt frameworks.
- Engineering major taxonomy and employment clusters.
- Company, school, runtime-parameter, and resume-format seed databases.
- Public-source policy, URL policy, local/small-company source coverage, access-wall recovery, and accuracy tiers.
- Deterministic local simulation and contract validation scripts.
- Batched subagent work-order protocol.
- Manual Controller MVP and Codex Desktop adapter documentation.
- General resume generation gate for users without a concrete target role.
- Resume delivery contract for Word DOCX, PDF, and one-page image artifacts after factual and HR review.
- Local resume renderer for DOCX, PDF, and PNG exports from Markdown or `final/decision_package.json`.
- Incomplete-user delivery validation path from plain chat to broad general resume artifacts.

Not yet packaged:

- No `.codex-plugin/plugin.json` yet.
- No marketplace-style plugin distribution yet.
- Real live recruitment search depends on the user's Codex environment and adapter path.

## Roadmap

- Productize the repo-scoped Skill into a Codex plugin after the user-side workflow stabilizes.
- Add stronger real-source adapters for public JD and official career-page discovery.
- Strengthen DOCX/PDF/image visual QA and template styling for final resume files.
- Expand beyond engineering into science, humanities, social science, business, arts/design, medicine, agriculture, law/public affairs, and interdisciplinary users.
- Add interview preparation from the final resume and target JD.

## Safety Principles

- Do not fabricate experience.
- Do not scrape private resumes or candidate profiles.
- Do not bypass login, CAPTCHA, anti-scraping, or platform access controls.
- Do not treat social media as stronger than official JD evidence.
- Do not write planned learning as completed skill.
- Do not recommend a concrete application target without a public URL.

## Citation

This is currently a design and runtime-contract repository for a Codex-native Skill. If you use or extend it, cite the repository URL and the `career-pipeline` Skill entry.

## License

Add a license before public redistribution.
