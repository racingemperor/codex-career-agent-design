# Real User Deployment And Use Flow

This reference explains how a real user installs and uses the career pipeline skill, and what each subagent does during a complete engineering-MVP run.

## Install And Enable

1. Install Codex and sign in with an account that can run local tools.
2. Clone or download this repository.
3. Open Codex in the repository root so repo-scoped files are visible:
   - `.agents/skills/career-pipeline/SKILL.md`
   - `.codex/agents/*.toml`
   - `data/**`
4. Use the skill by asking Codex for career, resume, job-search, target-job fit, learning-path, or personal-branding help. Codex should load `career-pipeline` automatically from the skill metadata.
5. For a smoke run, use the deterministic local runner. This checks contracts only:

```bash
cd .agents/skills/career-pipeline
python scripts/career_pipeline_run.py --task-type target_job_fit --route target_job_fit --input-text "computer science senior, assess fit for Tencent backend role. JD: Java and MySQL" --run-root ../../../.career-pipeline-runs --source-adapter seed --subagent-adapter mock-blocked
```

6. For real career output, configure a real source adapter and a real subagent adapter. The seed source adapter is not live web search. The mock-blocked subagent adapter is not real subagent execution.
7. Runtime artifacts are written under `.career-pipeline-runs/<run_id>/` and should not be committed.

## User-Facing Invocation

The user can provide any of these in the first message:

- vague self-introduction.
- pasted resume or Markdown.
- PDF/DOCX resume.
- GitHub, Gitee, personal website, portfolio, paper page, or project link.
- target company, role family, JD text, or JD URL.
- constraints such as city, internship period, graduation time, salary preference, or uncertainty.

The pipeline should not force a questionnaire first. It normalizes current information, tells the user what is already known, names what can be generated now, and asks one compact batch of missing user-owned facts only when needed.

If the user has no clear target job, the pipeline returns direction clusters, learning gaps, public-source research tasks, and exploration URLs. It should not force exact company recommendations.

## Runtime Data Sources

Use these sources in priority order:

- user-provided facts, files, links, JD text, and user-authorized resume materials.
- company official career pages, official campus pages, official JD pages, official job-search pages.
- official school career center, department notices, employment reports, and school-company cooperation pages.
- public recruitment-platform JDs that do not require login.
- verified HR public posts and official-listed HR/social accounts.
- public reports, company news, product pages, finance/regulatory disclosures, and mainstream media.
- candidate interview experiences and social media as auxiliary weak signals.

Never use private resumes, private chats, recruiter backends, login-only candidate profiles, non-public HR messages, or platform-bypassed data.

## Judgment Basis

Every judgment must say what evidence supports it:

- taxonomy lookup: static major database only, marked as prior.
- current role requirement: current JD text or public JD URL.
- application readiness: user evidence plus current JD/public evidence.
- learning gap: JD requirements, role-family public evidence, and current user evidence.
- company direction: official company sources, public reports, and verified/public hiring signals.
- HR readability: role outputs, user evidence, company priors, and factual review.
- resume claim: original user material, extracted evidence, and FactualReviewer approval.

Scores, weights, rankings, confidence, application priority, and external-display priorities require hard-data provenance. If evidence is missing, return `not_available`, `needs_more_sources`, or blocked outputs.

## Role-by-Role Runtime Work

### InputNormalizer

Work:

- Accept chats, files, links, websites, GitHub, portfolios, JD text, and mixed inputs.
- Extract `first_round_user_profile`.
- Separate known user facts, missing user-owned facts, public research needs, privacy constraints, and blocked outputs.
- Split non-graduating users into current internship and future full-time scenarios.

Inputs:

- raw user message and uploaded/provided materials.
- `data/runtime_parameters/parameter_ownership.zh-CN.json`
- `data/school_signals/school_signal_policy.zh-CN.json`
- `data/discipline_taxonomy/discipline_registry.zh-CN.json`

Handoff:

- sends `runtime_context_packet` to CareerOrchestrator.
- asks the user one compact follow-up only for user-owned missing facts.

### CareerOrchestrator

Work:

- Choose route: major positioning, resume review, job search, target-job fit, learning plan, personal branding, or full pipeline.
- Convert `runtime_context_packet` into role-specific `secondary_prompt_injections`.
- Attach allowed user facts, database refs, public-source tasks, hard-data weight tasks, output contracts, handoff rules, and debate rules.
- Track `run_state`, blocked agents, recovery state, and final gates.

Inputs:

- `runtime_context_packet`.
- role TOML files.
- source policy, URL policy, runtime contracts, and output contracts.

Handoff:

- builds `subagent_invocation` or work orders for each role.
- prevents merging blocked or malformed final decision fields.

### MajorClusterClassifier

Work:

- Route the major into discipline domain and engineering employment clusters.
- Allow cross-tags, such as computer plus electronics, automation, math, or robotics.
- Mark engineering taxonomy matches as priors, not final personal fit.

Data Sources:

- `data/discipline_taxonomy/discipline_registry.zh-CN.json`
- `data/major_taxonomy/engineering_major_index.zh-CN.csv`
- `data/major_taxonomy/engineering_employment_clusters.zh-CN.json`

Judgment Basis:

- static taxonomy lookup plus user major.
- no final job recommendation without runtime user evidence and public job evidence.

### ProfileExtractor

Work:

- Build an evidence map of education, projects, internships, competitions, research, coursework, skills, and external assets.
- Separate explicit facts, inferred facts, unsupported claims, and questions for user confirmation.
- Do not rewrite the resume or decide fit.

Data Sources:

- user-provided materials.
- normalized profile from InputNormalizer.

Judgment Basis:

- only user-provided or extracted evidence.
- output is candidate evidence, not application priority.

### JDAnalyzer

Work:

- Extract hard gates, responsibilities, must-have skills, nice-to-have skills, hidden requirements, ATS keywords, and risk flags.
- When no JD text is supplied, use automatic recruitment-source injection to retrieve or request public JD evidence.
- Record `application_url_candidates` and current JD public URL status.

Data Sources:

- user-provided JD text or JD URL.
- company official job pages and public recruitment-platform JDs.
- `data/company_signals/default_recruitment_source_matrix.zh-CN.json`

Judgment Basis:

- current JD text or accepted public JD URL.
- company priors never override current JD.

### JobScout

Work:

- Build the candidate job pool.
- Search official career pages, official campus pages, official school notices, public recruitment-platform JDs, and verified HR posts.
- Normalize `application_url_candidates`.
- Reject login-only, private, backend, or non-public candidate URLs.
- Put missing targets into `blocked_application_targets_without_public_url`.

Data Sources:

- `data/company_signals/source_collection_targets.zh-CN.json`
- `data/company_signals/default_recruitment_source_matrix.zh-CN.json`
- `data/company_signals/official_application_entrypoints.zh-CN.json`
- runtime search/fetch/backfill evidence.

Judgment Basis:

- public URL validity, source priority, freshness, current/open risk, and user constraints.
- does not make final apply/skip decisions alone.

### CompanyIntelligenceAnalyst

Work:

- Summarize target-company development, business direction, hiring direction, product/technology signals, and organization risk.
- Mark seed company data as priors.
- Request runtime public evidence for current conditions.

Data Sources:

- official company pages, product pages, news, reports, public filings, public hiring pages.
- `data/company_signals/company_hiring_signal_seed.zh-CN.json`
- `data/company_signals/source_collection_targets.zh-CN.json`

Judgment Basis:

- official/current company evidence outranks social media and stale priors.

### MarketSentimentAnalyzer

Work:

- Collect outside evaluation, candidate experiences, interview patterns, risk signals, and social-media weak signals.
- De-identify candidate signals.
- Keep social media as auxiliary unless corroborated by stronger sources.

Data Sources:

- verified HR public posts, public candidate experiences, public reports, social media, technical communities.
- default recruitment source matrix.

Judgment Basis:

- source type, recency, multi-source consistency, verification status, and conflict with official/JD evidence.

### MatchStrategist

Work:

- Merge profile, major cluster, JD, company intelligence, market sentiment, school signals, and constraints.
- Separate current suitability, learnable gaps, project evidence gaps, interview risks, internship scenario, and future full-time scenario.
- Produce `recommended_application_targets` only when valid `application_url_candidates` exist.
- If no concrete public URL exists, block concrete application recommendation and create research tasks.

Data Sources:

- ProfileExtractor evidence map.
- JDAnalyzer requirements.
- JobScout URL candidates.
- CompanyIntelligenceAnalyst and MarketSentimentAnalyzer outputs.
- school-signal runtime evidence.

Judgment Basis:

- user evidence plus current/public JD and source-policy-valid URL evidence.
- fit score and application priority remain unavailable without hard-data provenance.

### LearningPathStrategist

Work:

- Turn gaps into learnable skills, projects, proof artifacts, timeline, and resume-conversion conditions.
- For target jobs, separate "not ready now" from "can become competitive after these proofs."
- Do not write unfinished learning as mastered skill.

Data Sources:

- MatchStrategist gaps.
- JDAnalyzer must-have/nice-to-have requirements.
- public role-family evidence and user baseline.

Judgment Basis:

- current JD and public role evidence plus user evidence.
- output includes conditions for when a skill/project may be written into the resume.

### PersonalBrandingStrategist

Work:

- Decide which external assets matter for the user's discipline and target direction: GitHub, project README, personal website, portfolio, paper page, blog, demo, LinkedIn, or other assets.
- Package the user honestly so HR can see evidence quickly.
- Respect discipline differences and privacy/NDA constraints.

Data Sources:

- user external assets.
- target discipline, role, company, JD, and public evidence.
- runtime external-asset weight evidence.

Judgment Basis:

- hard-data provenance for external asset priority.
- no fake persona or unsupported positioning.

### HRSupervisor

Work:

- Supervise the whole pipeline from big-company HR first-screen perspective.
- Check 10-second readability, competitive signal density, target clarity, school/stage clarity, evidence chain, public URL availability, and debate resolution.
- Use company hiring-signal database as big-company priors when target company or comparable company family exists.
- Require public URLs for final recommended application targets.

Data Sources:

- all role outputs.
- `data/company_signals/company_hiring_signal_seed.zh-CN.json`
- `data/company_signals/source_collection_targets.zh-CN.json`
- `data/company_signals/default_recruitment_source_matrix.zh-CN.json`
- `data/company_signals/official_application_entrypoints.zh-CN.json`

Judgment Basis:

- HR-readable process status: `pass`, `revise`, or `required_user_confirmation`.
- cannot override FactualReviewer on truthfulness.

### ResumeFormatGate

Work:

- Decide whether resume drafting is procedurally allowed.
- Check required base sections: school information, personal contact, skills, project/competition experience, personality/potential.
- Select broad campus version when no target company or JD is specified.
- If input is incomplete and the user consents, allow an incomplete draft that omits missing sections and blocks application direction.

Data Sources:

- `data/resume_formats/resume_format_database.zh-CN.json`
- InputNormalizer and ProfileExtractor outputs.

Judgment Basis:

- resume-format database and available user facts.

### ResumeArchitect

Work:

- Draft resume structure and wording from user facts only.
- Use target role/JD/company evidence only when current evidence exists.
- Create broad campus, target-company, target-role, internship, or incomplete versions as allowed.

Data Sources:

- ResumeFormatGate output.
- ProfileExtractor evidence.
- JD/Match/HR outputs when evidence exists.

Judgment Basis:

- supported facts and format gate.
- no fake metrics, ownership, awards, education, papers, internships, or completed skills.

### FactualReviewer

Work:

- Review resume and recommendation claims for factual support, privacy, overclaiming, and interview defensibility.
- Check that application recommendations do not treat entrypoints, stale pages, or weak social posts as current concrete JDs.
- Check `application_url_fact_review` before final package presentation.

Data Sources:

- original user facts and extracted evidence.
- ResumeArchitect draft.
- JobScout/JDAnalyzer/MatchStrategist URL fields.
- source policy and URL policy.

Judgment Basis:

- truthfulness and defensibility only.
- has final authority on resume claim safety, not career fit.

## Subagent Cooperation And Debate

Subagents coordinate through structured fields:

- `evidence_basis`
- `weight_provenance`
- `application_url_candidates`
- `blocked_application_targets_without_public_url`
- `agent_claims`
- `evidence_challenges`
- `disagreements_with`
- `handoff_questions`
- `runtime_research_tasks`

Common debate paths:

- MatchStrategist says fit is high but ProfileExtractor evidence is weak: HRSupervisor asks for evidence or lowers confidence.
- PersonalBrandingStrategist proposes GitHub/personal site but role evidence does not value it: return to runtime research or reframe.
- JDAnalyzer lacks current JD URL: MatchStrategist blocks apply-now and asks JobScout/JDAnalyzer to retrieve current public JD.
- ResumeArchitect writes a strong claim but FactualReviewer flags it: revise or ask user for proof.
- School-company cooperation is claimed without official school/company evidence: HRSupervisor rejects that claim.

Debate should not loop indefinitely. Missing user facts trigger one compact user follow-up. Missing public evidence triggers runtime research tasks.

## Full Run Shape

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

## Final User Output

The final package should include:

- known candidate summary.
- major/discipline cluster and cross-tags.
- current target or no-target exploration state.
- public evidence index and source confidence.
- target role/JD analysis when available.
- recommended_application_targets with real public URLs.
- blocked_application_targets_without_public_url.
- current fit and learnable gaps.
- learning plan and proof artifacts.
- personal branding plan.
- HR readability review.
- resume format gate result.
- resume draft only when allowed.
- factual review and risk notes.
- next actions.

If a required source, URL, subagent, or user fact is missing, return a blocked or degraded package instead of guessing.

