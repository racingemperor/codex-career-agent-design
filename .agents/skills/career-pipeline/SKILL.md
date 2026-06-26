---
name: career-pipeline
description: Use when Codex needs to analyze Chinese majors or discipline domains, career direction, target companies, job descriptions, learning gaps, personal branding, or resumes for campus recruitment and early-career job search.
---

# Career Pipeline

This skill is the main entrypoint for the Codex-native career and resume agent design.

Use it to route user requests across specialized subagents, read the bundled static databases, and return a source-aware decision package. Do not deploy anything from this repository automatically; this repository is the design and prompt source of truth.

## Required References

Read these references as needed:

- `references/data-catalog.md` before using any static database.
- `references/source-policy.md` before analyzing job, company, HR, candidate, or social media information.
- `references/runtime-collaboration-protocol.md` before dispatching or merging role prompts.
- `references/role-output-contracts.md` before merging subagent outputs.

## Built-In Databases

Use repository-relative paths:

- `data/discipline_taxonomy/` for discipline-domain routing across engineering, science, humanities, social science, business, arts/design, medicine/health, agriculture, law/public affairs, and interdisciplinary backgrounds.
- `data/major_taxonomy/` for the currently implemented engineering major taxonomy, employment clusters, cross-tags, and major lookup.
- `data/runtime_parameters/` for deciding which parameters are user-owned, optional, researched by local subagents, or weighted at runtime.
- `data/school_signals/` for source policy and schema for school-company cooperation, campus recruiting, internship, and full-time opportunity signals.
- `data/company_signals/` for company-level hiring signals, source evidence, and company x major-cluster priors.
- `data/resume_formats/` for reusable resume section logic, format variants, and format accept/reject rules.

Never paste an entire database into the prompt. Load the smallest file and subset needed for the active role.

## Pipeline

Default full route:

```text
InputNormalizer
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
```

Short routes:

- Major positioning: `InputNormalizer -> MajorClusterClassifier`.
- Resume review: `InputNormalizer -> ProfileExtractor -> ResumeFormatGate -> ResumeArchitect -> FactualReviewer -> HRSupervisor`.
- Job analysis: `InputNormalizer -> JDAnalyzer -> CompanyIntelligenceAnalyst -> MarketSentimentAnalyzer`.
- Job search: `InputNormalizer -> MajorClusterClassifier -> ProfileExtractor -> JobScout -> JDAnalyzer -> MatchStrategist -> LearningPathStrategist`.

## Operating Rules

- Prefer user-provided materials and official/public sources over memory.
- Treat every `.codex/agents/*.toml` file as a role framework for runtime local subagents, not as a frozen decision engine.
- Normalize vague chats, Markdown, resumes, websites, links, and mixed materials through `InputNormalizer` before specialist agents.
- Ask the user for missing user-owned facts once in a compact batch. Do not ask the user for data that local subagents can research from allowed public sources.
- Treat concrete skill weights and external-display asset weights as runtime decisions. The repository provides schemas and examples, not universal requirements that every discipline must follow.
- For non-graduating candidates, split current internship analysis from future full-time preparation.
- School-company cooperation and school-specific hiring advantages require official or primary runtime evidence; never infer them from school name alone.
- Treat company-signal data as priors, not current role-specific requirements.
- For a concrete job, require fresh JD text or current public JD retrieval before final resume tailoring.
- Use candidate/social media information only as auxiliary preparation or risk signals unless it is verified by official sources.
- If runtime evidence is missing, return research tasks, evidence requirements, blocked outputs, conditional options, and handoff targets instead of a final judgment.
- Do not store or expose private resumes, private chats, IDs, addresses, or non-public HR/candidate information. Intermediate reports and logs should redact phone numbers and personal emails by default; final resume drafts may include user-authorized contact fields when the user explicitly provides them for the resume.
- Resume writing may improve structure, evidence, and wording, but must not create false experience, fake metrics, fake ownership, fake education, or fake awards.
- Complete resume drafts must pass `ResumeFormatGate` before drafting and `FactualReviewer` before being presented as final.
- If the user refuses to provide missing information, generate an incomplete resume draft only after explicit consent and after `ResumeFormatGate` marks the incomplete-draft exception. Omit missing sections, block application direction recommendations, and warn that targeted advice requires detailed information.
- The whole pipeline should remain under `HRSupervisor` review: personal branding, resume strategy, and final packages must be quickly understandable to HR and show credible competitive signals.
- Agents should debate conflicts through structured fields. If claims conflict, preserve the disagreement, request evidence, or hand back to the relevant agent instead of silently merging incompatible conclusions.

## Role Prompt Files

Role prompt frameworks live in `.codex/agents/*.toml`.

Each file contains:

- role identity and scope.
- database dependencies.
- professional prompt instructions.
- expected output contract.
- hard prohibitions.

When a role needs static data, read the dependency paths listed in its TOML first.
