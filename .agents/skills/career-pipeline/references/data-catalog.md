# Data Catalog

Use this catalog to decide which static database to load for each role.

## Discipline Taxonomy

Path: `data/discipline_taxonomy/`

Purpose: route a user's major into the correct discipline-domain logic before detailed employment classification.

Core files:

- `discipline_registry.zh-CN.json`: domain registry, implementation status, evidence focus, and runtime contract.
- `README.md`: human-readable explanation of why each discipline domain needs different classification logic.

Usage:

- `MajorClusterClassifier` must read this registry before using any domain-specific taxonomy.
- If a domain is not implemented, return `taxonomy_status = "pending_static_database"` and do not force engineering clusters.
- Use `interdisciplinary` as a bridge layer, not as a final single employment category.

## Major Taxonomy

Path: `data/major_taxonomy/`

Purpose: classify Chinese undergraduate engineering majors into employment-oriented clusters.

Core files:

- `engineering_major_index.zh-CN.csv`: concrete major lookup table.
- `engineering_employment_clusters.zh-CN.json`: cluster definitions, typical roles, core skills, bridge skills, and major mappings.
- `engineering_employment_clusters.zh-CN.md`: human-readable cluster summary.
- `engineering_related_interdisciplinary_majors_2026.zh-CN.json`: engineering-related interdisciplinary majors.
- `summary.json`: counts and coverage.

Usage:

- `MajorClusterClassifier` reads this database only after the discipline registry selects `engineering` or an engineering-related bridge path.
- `LearningPathStrategist` and `PersonalBrandingStrategist` may use cluster skill lists and bridge skills only as broad priors. Concrete skill importance and external display importance must be set by runtime subagent research.
- `ResumeArchitect` should use cluster and target role labels when selecting format variants and section emphasis.

## Runtime Parameters

Path: `data/runtime_parameters/`

Purpose: define which parameters should be provided by the user, which are optional, which should be researched by local subagents, and which weights should be configured at runtime.

Core files:

- `parameter_ownership.zh-CN.json`: ownership groups, one-round question policy, and incomplete-resume policy.
- `summary.json`: group counts and status.

Usage:

- `InputNormalizer` reads this before asking follow-up questions.
- `CareerOrchestrator` uses it to avoid repeated questioning and to route public-source research to local subagents.
- `MatchStrategist`, `LearningPathStrategist`, and `PersonalBrandingStrategist` use it to avoid hard-coding skill or external-asset weights from repository priors.
- `ResumeFormatGate` and `ResumeArchitect` use it for incomplete-resume consent and omission rules.

Important: concrete skill weights and external display requirements are runtime outputs, not static repository requirements.

## School Signals

Path: `data/school_signals/`

Purpose: define source priority and schema for school-company cooperation, campus recruiting, internship-base, employment-report, and grade-specific opportunity analysis.

Core files:

- `school_signal_policy.zh-CN.json`: source priority, research fields, stage rules, hard rules, and output shape.
- `summary.json`: source priority and stage rule counts.

Usage:

- `InputNormalizer` extracts school and grade context and marks school-signal research needs.
- `MatchStrategist` uses runtime school signals as opportunity priors for internship and full-time scenarios.
- `HRSupervisor` checks that school-specific claims are supported by official or primary evidence.

Important: this directory does not assert any school-company partnership. Local subagents must collect current evidence on the user's device.

## Company Hiring Signals

Path: `data/company_signals/`

Purpose: provide company-level and major-cluster-level hiring signal priors for engineering employers.

Core files:

- `company_hiring_signal_seed.zh-CN.json`: company summaries, major-cluster templates, and source evidence.
- `covered_companies.zh-CN.json`: company coverage list.
- `source_collection_targets.zh-CN.json`: source collection plan and search templates.
- `default_recruitment_source_matrix.zh-CN.json`: default public recruitment source matrix automatically injected into recruitment-information roles.
- `official_application_entrypoints.zh-CN.json`: curated official application and campus entrypoint candidates. These are public URL entrypoints, not proof that a concrete role is currently open.
- `company_hiring_signals.schema.json`: schema.
- `summary.json`: coverage counts and status.

Usage:

- `CompanyIntelligenceAnalyst` reads company summaries and source evidence.
- `MarketSentimentAnalyzer` reads source evidence and collection targets.
- `JDAnalyzer` may use major-cluster requirement templates only as broad priors.
- `JobScout`, `JDAnalyzer`, `CompanyIntelligenceAnalyst`, `MarketSentimentAnalyzer`, and `HRSupervisor` use `default_recruitment_source_matrix.zh-CN.json` as the automatic source-discovery matrix; users do not need to name recruitment websites.
- `JobScout`, `MatchStrategist`, `HRSupervisor`, and `FactualReviewer` use `official_application_entrypoints.zh-CN.json` with `references/application-url-output-policy.md` to ensure recommended application targets include inspectable public URLs or remain blocked.
- `MatchStrategist`, `LearningPathStrategist`, and `ResumeArchitect` may use company x cluster priors only after marking them as priors.
- `HRSupervisor` may read company summaries, source evidence, and collection targets to simulate big-company HR screening bias for a target company or comparable company family.

Important: this is a seed database with expanded public source links, not a complete evidence corpus. Official entrypoints can support exploration or "inspect here" actions, but specific role analysis still requires current JD text or a current public JD URL.

## Resume Formats

Path: `data/resume_formats/`

Purpose: store reusable resume section logic, format variants, and accept/reject rules.

Core files:

- `resume_format_database.zh-CN.json`: section rules, variants, scoring dimensions, and reject rules.
- `resume_format_schema.json`: schema.
- `summary.json`: version and coverage summary.

Usage:

- `ResumeFormatGate` must read this database before deciding whether resume drafting is allowed.
- `ResumeArchitect` must read this database and the gate output before generating a resume draft.
- `FactualReviewer` must read accept/reject rules before approving a resume.
- `PersonalBrandingStrategist` should use section and variant logic to keep resume claims consistent with external assets.
