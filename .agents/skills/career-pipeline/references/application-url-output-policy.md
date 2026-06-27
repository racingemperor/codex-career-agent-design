# Application URL Output Policy

Use this policy whenever the pipeline recommends jobs, internships, companies to inspect, or concrete application targets.

## Core Rule

Every recommended jobs, internships, or application targets item must include at least one real, public, inspectable URL candidate. If no public URL candidate is available, block the concrete application recommendation and return a research task instead.

If the JD or URL does not state opening status, freshness, city, work location, arrival time, onsite days, deadline, or headcount, do not block the recommendation for that reason alone. Keep the target visible as `prepare_first` or `explore` when the role family is relevant, and add the missing operational details to `ask_hr_about`.

This rule applies to:

- job-search results.
- target-job fit decisions.
- application priority lists.
- resume-tailoring targets.
- HR-supervised final packages.

## URL Candidate Schema

Use this shape in role outputs:

```json
{
  "application_url_candidates": [
    {
      "url": "",
      "source_type": "official_or_primary|official_school_notice|recruitment_platform_jd|verified_hr_public_post",
      "source_priority": 1,
      "title": "",
      "company": "",
      "role_family": "",
      "current_or_entrypoint": "current_jd|official_search_entrypoint|campus_entrypoint|school_notice|public_jd",
      "retrieved_or_verified_at": "",
      "requires_login": false,
      "may_support_apply_recommendation": false,
      "confidence": "high|medium|low",
      "notes": "",
      "ask_hr_about": []
    }
  ],
  "blocked_application_targets_without_public_url": [
    {
      "company": "",
      "role_family": "",
      "reason": "",
      "required_research_task": ""
    }
  ]
}
```

## Source Priority For Application URLs

1. Current official JD or company official job detail page.
2. Company official career, campus, or job-search entrypoint.
3. Official school career notice, school-company channel, or department career notice.
4. Public recruitment-platform JD that does not require login.
5. Verified HR public recruiting post, only when the post itself is public and recruiting-related.

Candidate posts, social media comments, screenshots, and unverified HR/referral posts must not be the application URL. They may support preparation notes only.

## Entrypoint Versus Current JD

An official search entrypoint or campus entrypoint can support "inspect/apply through this official channel." It cannot support role-specific claims such as must-have skills, deadline, headcount, city, salary, or current openness unless the current JD text or current JD URL has also been retrieved.

For a concrete application recommendation:

- `apply_now` requires a current JD or public JD URL plus user evidence.
- `prepare_first` can use a current JD, public JD, or official entrypoint plus explicit evidence gaps.
- `explore` can use an official entrypoint when no concrete JD is available.
- `skip` should cite hard gates from current JD/public evidence or user constraints, not repository priors alone.

If the best available URL is only an official entrypoint, the recommendation should be an exploration target, not a final role-specific apply-now decision.

Missing HR-operational fields should be handled as user-facing confirmation notes, not repeated user questions. Suggested `ask_hr_about` values include:

- `opening_status`
- `city_or_work_location`
- `onsite_days_or_arrival`
- `deadline`
- `headcount`
- `internship_duration`

The final wording should tell the user to confirm these details with HR or the recruiter if they are not written on the public page.

## Role Responsibilities

- `JobScout` collects and normalizes `application_url_candidates`, rejects login-only or private URLs, and records blocked targets without public URLs.
- `JDAnalyzer` retrieves or asks for current JD text from public JD URLs before extracting role requirements.
- `MatchStrategist` may name concrete recommended application targets only when source-policy-valid URL candidates exist.
- `HRSupervisor` checks that every user-facing recommended application target has a public URL and an HR-readable source note.
- `FactualReviewer` blocks final wording that treats an entrypoint, stale URL, weak social signal, or planned learning outcome as a current concrete job fact.
- `CareerOrchestrator` keeps blocked targets visible in the final package instead of converting them into guessed recommendations.

## Final Package Requirements

User-facing final packages should expose:

```json
{
  "recommended_application_targets": [
    {
      "company": "",
      "title_or_role_family": "",
      "scenario": "apply_now|prepare_first|explore|skip",
      "public_urls": [],
      "why_this_target": "",
      "evidence_basis": [],
      "blocked_claims": [],
      "ask_hr_about": []
    }
  ],
  "blocked_application_targets_without_public_url": [],
  "runtime_research_tasks": []
}
```

If `public_urls` is empty for a target, the target must not appear as a recommended application target.

## User-Facing Style

Final recommendations should read like a professional career tool or resume review: concise, structured, and easy to scan. Prefer:

- conclusion first.
- 2-4 evidence points.
- clear recommendation status: `apply_now`, `prepare_first`, `explore`, or `skip`.
- public URL list.
- `ask_hr_about` as short confirmation bullets.
- next 3 actions.

Do not expose internal fields such as raw `blocked_outputs`, run directories, execution logs, or schema names unless the user is debugging the pipeline.
