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
- `references/role-output-contracts.md` before merging subagent outputs.

## Built-In Databases

Use repository-relative paths:

- `data/discipline_taxonomy/` for discipline-domain routing across engineering, science, humanities, social science, business, arts/design, medicine/health, agriculture, law/public affairs, and interdisciplinary backgrounds.
- `data/major_taxonomy/` for the currently implemented engineering major taxonomy, employment clusters, cross-tags, and major lookup.
- `data/company_signals/` for company-level hiring signals, source evidence, and company x major-cluster priors.
- `data/resume_formats/` for reusable resume section logic, format variants, and format accept/reject rules.

Never paste an entire database into the prompt. Load the smallest file and subset needed for the active role.

## Pipeline

Default full route:

```text
Career Orchestrator
  -> MajorClusterClassifier
  -> ProfileExtractor
  -> JDAnalyzer
  -> JobScout
  -> CompanyIntelligenceAnalyst
  -> MarketSentimentAnalyzer
  -> MatchStrategist
  -> LearningPathStrategist
  -> PersonalBrandingStrategist
  -> ResumeFormatGate
  -> ResumeArchitect
  -> FactualReviewer
```

Short routes:

- Major positioning: `MajorClusterClassifier`.
- Resume review: `ProfileExtractor -> ResumeFormatGate -> ResumeArchitect -> FactualReviewer`.
- Job analysis: `JDAnalyzer -> CompanyIntelligenceAnalyst -> MarketSentimentAnalyzer`.
- Job search: `MajorClusterClassifier -> ProfileExtractor -> JobScout -> JDAnalyzer -> MatchStrategist -> LearningPathStrategist`.

## Operating Rules

- Prefer user-provided materials and official/public sources over memory.
- Treat company-signal data as priors, not current role-specific requirements.
- For a concrete job, require fresh JD text or current public JD retrieval before final resume tailoring.
- Use candidate/social media information only as auxiliary preparation or risk signals unless it is verified by official sources.
- Do not store or expose private resumes, private chats, IDs, addresses, or non-public HR/candidate information. Intermediate reports and logs should redact phone numbers and personal emails by default; final resume drafts may include user-authorized contact fields when the user explicitly provides them for the resume.
- Resume writing may improve structure, evidence, and wording, but must not create false experience, fake metrics, fake ownership, fake education, or fake awards.
- Any generated resume must pass `ResumeFormatGate` before drafting and `FactualReviewer` before being presented as final.

## Role Prompt Files

Role prompt frameworks live in `.codex/agents/*.toml`.

Each file contains:

- role identity and scope.
- database dependencies.
- professional prompt instructions.
- expected output contract.
- hard prohibitions.

When a role needs static data, read the dependency paths listed in its TOML first.
