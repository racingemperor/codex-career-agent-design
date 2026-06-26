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
- `LearningPathStrategist` and `PersonalBrandingStrategist` should use cluster skill lists and bridge skills.
- `ResumeArchitect` should use cluster and target role labels when selecting format variants and section emphasis.

## Company Hiring Signals

Path: `data/company_signals/`

Purpose: provide company-level and major-cluster-level hiring signal priors for engineering employers.

Core files:

- `company_hiring_signal_seed.zh-CN.json`: company summaries, major-cluster templates, and source evidence.
- `covered_companies.zh-CN.json`: company coverage list.
- `source_collection_targets.zh-CN.json`: source collection plan and search templates.
- `company_hiring_signals.schema.json`: schema.
- `summary.json`: coverage counts and status.

Usage:

- `CompanyIntelligenceAnalyst` reads company summaries and source evidence.
- `MarketSentimentAnalyzer` reads source evidence and collection targets.
- `JDAnalyzer` may use major-cluster requirement templates only as broad priors.
- `MatchStrategist`, `LearningPathStrategist`, and `ResumeArchitect` may use company x cluster priors only after marking them as priors.

Important: this is a seed database with expanded public source links, not a complete evidence corpus. Specific role analysis still requires current JD text.

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
