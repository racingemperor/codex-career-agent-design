# Source Policy

Use this policy for job, company, HR, candidate, and social media information.

## Source Priority

1. Company official website, official career page, official campus page, official JD.
2. Verified HR public account or official-listed HR social account.
3. Public recruitment-platform JD, including BOSS, Lagou, Liepin, Nowcoder enterprise pages, LinkedIn, Indeed.
4. Candidate interview experience, offer review, public referral post, multi-source social media consensus.
5. Single anonymous post, screenshot, comment, or unverified rumor.

For school-company cooperation and campus channels, use this priority:

1. Official school career center, official employment report, official campus recruitment calendar.
2. Official college or department notice, internship-base announcement, school-enterprise cooperation announcement.
3. Official employer campus page or target-company school event page.
4. Public recruitment-platform campus event or public JD.
5. Candidate or social media signal.

School-specific advantages require priority 1-3 evidence. Candidate or social media signals can only support preparation notes.

## Access-Wall And Dynamic-Page Recovery

If a recruitment source lands on a login wall, CAPTCHA, app-only page, access-denied page, private backend, candidate profile gate, or JavaScript shell without public rendered text, treat it as unusable evidence for the current run. Do not ask the user to log in, solve a CAPTCHA, provide private screenshots, or export platform-only data. Do not use a URL that only proves "the platform exists" as a job, company, HR, or candidate fact.

Use automatic source substitution before interrupting the user. Try replacement public sources in this order:

1. Official company career page, campus page, job-search entrypoint, or current official JD.
2. Official school career center, department notice, or school-company channel.
3. Public recruitment-platform JD that is visible without login.
4. Verified HR public recruiting post or official-listed HR/social account.
5. Public report, mainstream media, technical blog, or public product/company page.
6. Candidate experience or social-media weak signal only for preparation and risk notes.

For dynamic public pages, a browser-rendered public text snapshot may be used only when the text is visible without login, private messages, backend access, or access-control bypass. Keep the inspectable public URL as the source ref and mark the extraction method as browser-rendered public text. A JavaScript shell without a public rendered snapshot is not evidence.

Record a `source_attempt_log` when access fails: attempted URL, failure type, source type, replacement attempted, replacement URL if found, and which claims the replacement may support. If no replacement public source exists, return a research task or blocked field instead of guessing.

## Accuracy Tiers

Use `source_accuracy_tier` in role outputs when a source supports a job, company, HR, candidate, school, weight, score, priority, or resume-tailoring claim.

- Accuracy Tier A: user-provided original material, current official JD, official career page, official campus page, official school notice, official report, or official company disclosure. May support role requirements, public application targets, school signals, and hard-data weights when current and relevant.
- Accuracy Tier B: public recruitment-platform JD visible without login, verified HR public recruiting post, credible public report, mainstream media, or official-listed HR/social account. May support role requirements or company/HR signals with source notes and recency limits.
- Accuracy Tier C: candidate interview experience, offer review, public referral post, multi-source social-media consensus, or technical community discussion. May support preparation notes, risk flags, hidden expectations, and interview strategy, but cannot support role requirements as a standalone source.
- Accuracy Tier D: single anonymous post, screenshot, comment, rumor, login-only page, CAPTCHA page, app-only page, private/backend page, non-public candidate profile, or JavaScript shell without public rendered text. Cannot support role requirements, final recommendations, weights, priorities, company-specific claims, or resume tailoring.

If sources conflict, keep the higher tier as the primary source and preserve lower-tier disagreement as a risk or preparation note.

## Conflict Handling

- Official JD and official career pages override social media claims.
- Verified HR public posts can clarify official process but should not override a current JD.
- Candidate experiences can inform preparation, interview risk, and hidden expectations, but cannot become company requirements alone.
- Social media signals need source type, date, platform, confidence, and whether identity is verified.
- When sources conflict, preserve the conflict and state which source is primary.
- Skill weights, external-display asset weights, school-signal weights, fit scores, priorities, and strategy weights must be set from hard evidence at runtime. Valid evidence includes current JD text, official company/campus pages, recruitment-platform public JDs, verified HR public posts, official school notices, public reports, multi-source candidate signals, or user-provided materials.
- Local subagents must verify weight-setting evidence through public/official network information whenever the information is not already supplied by the user. They must not set weights from intuition, repository examples, or model-only reasoning.
- Every weight must include `weight_provenance`: source refs, source types, dates, source count or sample size, evidence strength, and confidence. If provenance is weak or missing, the weight must be `not_available` or `needs_more_sources`.
- If a local subagent can research a public or official source, do not ask the user to manually provide that source unless the user volunteers it.

## Privacy

Do not store or reveal:

- private resumes.
- private chat logs or screenshots.
- phone numbers, personal emails, IDs, addresses, WeChat IDs in intermediate reports, logs, or evidence databases.
- non-public HR/candidate information.
- details that identify a candidate without consent.

Allowed:

- public URL.
- paraphrased source summary.
- source type and confidence.
- de-identified aggregate candidate signal.
- user-authorized contact fields in the final resume draft only.

## Resume Truthfulness

Allowed:

- clarify structure.
- improve evidence order.
- translate real work into stronger professional language.
- mark claims that need user confirmation.
- generate an incomplete resume draft only after explicit user consent, omitting missing sections and blocking application direction recommendations.

Forbidden:

- invent education, awards, internships, projects, papers, users, metrics, or ownership.
- turn "participated" into "led" without evidence.
- describe unfinished learning as mastered skill.
- expose confidential project data.
