# Codex Career Pipeline

Career Pipeline is a Codex Skill for career planning, job exploration, ability improvement, and resume design for early-career candidates in China.

It is built around one idea:

> **One role, one resume. Start from the job, then design the learning plan and resume backward.**

Current usable scope is **engineering majors and engineering-adjacent backgrounds**. Other disciplines are reserved in the framework and taxonomy, but the engineering path is the MVP.

## What Makes It Different

- **Tailored planning**: analyzes the user's major, stage, experience, constraints, and target direction.
- **Reverse-designed resumes**: starts from a role or JD, then decides what the resume should emphasize.
- **Learn before applying**: when the user is not ready, gives specific skills, projects, proof artifacts, and resume-conversion conditions.
- **One role, one resume**: avoids a generic resume when a concrete role or company is selected.
- **Two resume versions**: generates a current factual resume, plus a clearly labeled preview of how the resume could look after recommended skills/projects are completed.
- **Source-aware job research**: uses public job URLs, official pages, school notices, recruitment platforms, local opportunities, and verified HR public sources when available.
- **Truthfulness gate**: planned learning or projects cannot be written as completed experience until proof artifacts exist.

## What It Can Produce

- Current positioning and suitable direction clusters.
- Recommended role pool or application targets with public URLs.
- Fit reasoning, risks, and missing information.
- Learning path and project recommendations.
- HR-style preparation points when backed by target-company or recommended-company public sources.
- Current factual resume draft.
- After-learning/project resume preview.
- Resume artifacts in Word DOCX, PDF, and first-page PNG.
- Next 3 actions for the user.

## Typical Use

In Codex, open this repository and ask:

```text
Use the career-pipeline skill.
Computer-related junior, basic Python, looking for an internship but unsure what to apply for.
Please help me choose directions, plan skills/projects, and design the resume.
```

If the user has a concrete role:

```text
Use the career-pipeline skill.
Automation graduate student, C++, ROS, Python, robotics competition experience.
Target: DJI robotics/control algorithm internship.
Please judge whether I should apply now. If not, give a prepare-first plan and a better role-specific resume direction.
```

The intended product flow is plain chat. They should not need to understand subagents, JSON, runners, or adapters: the skill collects one compact batch of information, searches public sources, judges direction or fit, plans learning/projects, designs the resume, and exports files.

## Resume Output

The skill distinguishes two versions:

- **Current factual resume**: only uses what the user has provided or can prove now.
- **After-learning preview**: shows what the resume could look like after the recommended skills/projects are completed. This version must stay labeled as a preview and cannot be used as a factual resume before completion.

When a final package is ready, resume artifacts can be exported with:

```bash
cd .agents/skills/career-pipeline
python scripts/render_resume_artifacts.py --decision-package ../../../.career-pipeline-runs/<run_id>/final/decision_package.json --out-dir ../../../.career-pipeline-runs/<run_id>/final/resume_artifacts --basename general_resume --all-resume-versions
```

This exports DOCX, PDF, PNG, `resume_draft.md`, and, when available, `growth_resume_preview.md`.

## Developer Notes

For product-flow checks, use `scripts/run_product_flow.py`. If the main Codex controller has already gathered public URLs from browser search or visible web results, pass them through `scripts/collect_public_source_results.py` without hand-writing JSON. The notes can use simple URL lines or YAML-like blocks with `source_type_hint`; official homepages and search pages are exploration entrypoints until a concrete public JD supports stronger claims.

For real subagent execution in Codex Desktop, prefer the Codex Desktop built-in subagent adapter when available. `mock-blocked` remains only a local contract smoke mode and is not proof of real role execution.

For target-role checks, missing details such as city, deadline, headcount, or internship duration should go to `ask_hr_about`. The system can return a prepare-first / `prepare_first` plan while stronger evidence is still being collected.

## Current Status

Implemented:

- Repo-scoped Codex Skill entry.
- Engineering major taxonomy and role-cluster support.
- Public-source policy for official pages, recruitment platforms, school notices, local employers, and social/HR signals.
- Batched role prompt framework for Codex subagents.
- General resume generation when the user has no concrete target.
- Concrete learning/project recommendation contracts.
- Current resume plus after-learning/project preview.
- Local DOCX/PDF/PNG resume renderer.

Not packaged yet:

- This is not a `.codex-plugin` package yet.
- Live recruitment search still depends on the user's Codex environment and available browsing/search tools.
- Non-engineering disciplines are planned but not fully implemented.

## Key Files

- [Skill entry](.agents/skills/career-pipeline/SKILL.md)
- [Role prompts](.codex/agents)
- [Source policy](.agents/skills/career-pipeline/references/source-policy.md)
- [Real user flow](.agents/skills/career-pipeline/references/real-user-deployment-and-use-flow.md)
- [Detailed archived README](docs/archive/README.product-detailed-2026-06-28.md)

## Safety

- Do not fabricate education, internships, projects, awards, metrics, or ownership.
- Do not scrape private resumes, private candidate profiles, private HR messages, or login-only content.
- Do not bypass login, CAPTCHA, app-only, backend, or access-controlled pages.
- Do not treat social media as stronger than official JD or recruitment evidence.
- Do not recommend a concrete application target without a public URL.

## License

Add a license before public redistribution.
