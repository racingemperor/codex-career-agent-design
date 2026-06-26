# Runtime Collaboration Protocol

This repository stores role frameworks, static schemas, source policies, and seed databases. It must not act as a frozen judge of a user's career fit.

## Core Rule

Every role prompt is a framework for runtime local subagents:

- Define what to collect, how to evaluate evidence, how to share findings, and when to hand off.
- Do not make final fit, company, market, learning, branding, HR, or resume decisions from repository priors alone.
- If current user materials or runtime public evidence are missing, output research tasks, evidence requirements, blocked fields, and handoff targets instead of a conclusion.
- Static databases are priors, templates, and schemas. Runtime local subagents collect current evidence and set weights.

## Shared Context Envelope

Every role should preserve these fields when possible:

```json
{
  "judgment_status": "framework_only|runtime_evidence_required|ready_for_runtime_judgment|evidence_bound_judgment|blocked",
  "decision_owner": "local_subagent|user|factual_reviewer|hr_supervisor|orchestrator|none",
  "runtime_research_tasks": [],
  "evidence_requirements": [],
  "shared_context_refs": [],
  "handoff_to": []
}
```

Field meanings:

- `framework_only`: the role only prepared a protocol, schema, or task list.
- `runtime_evidence_required`: the role cannot judge until local subagents collect current evidence.
- `ready_for_runtime_judgment`: the role has enough structured inputs for a runtime subagent to judge.
- `evidence_bound_judgment`: a limited judgment was made only from supplied user materials or runtime evidence.
- `blocked`: user-owned facts, consent, or required public evidence are missing.

## Evidence Ownership

- User-owned facts: ask once in a compact batch.
- Public or official facts: assign to local subagents as `runtime_research_tasks`.
- Skill and external-display weights: configure at runtime from current JD, company, school, discipline, and source evidence.
- Resume truthfulness: `FactualReviewer` has final authority.
- HR readability and first-screen coherence: `HRSupervisor` supervises presentation, not factual truth.

## Debate And Handoff

Roles should challenge claims through shared fields rather than overwriting each other:

```json
{
  "agent_claims": [],
  "evidence_challenges": [],
  "disagreements_with": [],
  "handoff_questions": []
}
```

Use debate when:

- A claim lacks user evidence or current source evidence.
- Repository priors conflict with a current JD or official source.
- HR presentation is strong but factual support is weak.
- A learning, branding, or resume recommendation depends on uncollected runtime evidence.

Do not loop indefinitely. If the conflict depends on user-owned facts, stop and ask once. If it depends on public evidence, hand off to the responsible local subagent.

## Limited Evidence-Bound Judgments

Some roles may make narrow judgments only from provided materials:

- `InputNormalizer`: whether a field is present, missing, or needs confirmation.
- `ProfileExtractor`: whether a claim is explicit, inferred, or unsupported.
- `MajorClusterClassifier`: taxonomy lookup when the major exists in the static database.
- `JDAnalyzer`: requirements extraction from a provided/current JD.
- `ResumeFormatGate`: whether supplied materials satisfy the resume format schema.
- `FactualReviewer`: whether a resume claim is supported, overclaimed, private, or indefensible.

These judgments must be marked as `evidence_bound_judgment` and must not become final career recommendations without the downstream runtime evidence packet.
