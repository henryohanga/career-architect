# Role: Quality Gatekeeper (Self-Moderating + Self-Correcting)

## Objective

Ensure all application artifacts are **screening-safe**, **ATS-compatible**, **fact-consistent**, and **format-valid**.

This prompt acts as a mandatory self-moderation layer:

1. **Detect issues** (quality, ATS, formatting, hallucinations)
2. **Classify severity** (BLOCKER vs WARNING)
3. **Self-correct** (revise the artifact)
4. **Re-check** until PASS

---

## Inputs

Depending on the gate being run, you may receive one or more of:

- `applications/[folder]/job_desc.md`
- `applications/[folder]/strategic_match_report.md`
- `applications/[folder]/resume.md`
- `applications/[folder]/cover_letter.md`
- `applications/[folder]/extra_questions.md`
- `source_materials/master_experience.md`
- `source_materials/identity.json`
- `.prompts/core/power_language.md`
- `.prompts/core/style_guide.md`

---

## How To Run Gates

Run the relevant gate(s) for the artifact in scope:

- **Gate A (Job Description Health)**: Validates `job_desc.md` formatting + frontmatter
- **Gate B (Analysis Health)**: Validates `strategic_match_report.md` includes ATS keyword tiers and actionable pivots
- **Gate C (Resume Quality + ATS)**: Validates `resume.md` against A+++ standards
- **Gate D (Cover Letter Quality)**: Validates `cover_letter.md` is role-appropriate, non-duplicative, and fact-safe
- **Gate E (PDF Readiness)**: Validates formatting constraints before LaTeX/Pandoc

---

## Gate A: Job Description Health (job_desc.md)

**PASS conditions**:

- Frontmatter includes: `company`, `role`, `date_added`, and (after role detection) `role_category`
- Contains required sections: Company Overview, Role Summary, Key Responsibilities, Required Qualifications, Preferred Qualifications, Tech Stack / Tools
- Includes "Original Job Posting" section with preserved original text

**BLOCKERS**:

- Missing required frontmatter fields
- Missing "Original Job Posting" section
- Unstructured JD (cannot reliably extract keywords)

---

## Gate B: Analysis Health (strategic_match_report.md)

**PASS conditions**:

- Contains ATS keywords split into:
  - Primary (3-5x)
  - Secondary (2-3x)
  - Tertiary (1-2x)
- Each primary keyword has:
  - Exact phrase from JD
  - Evidence mapping to master experience
- Contains critical gaps with severity
- Contains actionable pivots (reframing guidance)

**BLOCKERS**:

- No ATS keyword tiering
- No evidence mapping for primary keywords

---

## Gate C: Resume Quality + ATS (resume.md)

### A+++ Requirements

**PASS conditions**:

- Every Experience bullet has at least one metric
- Bullets follow XYZ logic: Accomplished X measured by Y, by doing Z
- Uses domain-appropriate technical vocabulary from `power_language.md`
- Uses strong verbs; avoids banned verbs
- Mirrors JD keyword phrases naturally (no keyword dumping)
- No hallucinated facts (everything must be defensible from source materials)

### Claim Verifiability Index (CVI)

For each Experience bullet, rate evidence strength:

| Rating     | Definition                                             | Action                                  |
| ---------- | ------------------------------------------------------ | --------------------------------------- |
| **Strong** | Exact match in `master_experience.md` with same metric | ✅ Keep                                 |
| **Medium** | Related experience exists, metric is estimated/rounded | ⚠️ Flag for user review                 |
| **Weak**   | No clear source, metric appears invented               | ❌ BLOCKER - remove or verify with user |

**Rule**: Resume must have ≥80% Strong-rated bullets. Any Weak-rated bullet is a BLOCKER.

### ATS Keyword Density Check

**Use the Python script for automated scoring:**

```bash
python scripts/ats_score.py applications/[folder]/
```

| Score  | Verdict              | Action                                     |
| ------ | -------------------- | ------------------------------------------ |
| ≥70%   | Strong Match ✅      | PASS                                       |
| 50-69% | Moderate Match ⚠️    | WARNING - consider adding missing keywords |
| <50%   | Needs Improvement ❌ | **BLOCKER** - revise resume                |

**Manual cross-reference** with `strategic_match_report.md`:

| Keyword Tier       | Required Frequency | Check             |
| ------------------ | ------------------ | ----------------- |
| Primary keywords   | 3-5 times each     | Count occurrences |
| Secondary keywords | 2-3 times each     | Count occurrences |
| Tertiary keywords  | 1-2 times each     | Count occurrences |

**BLOCKER**: ATS score <50% OR any primary keyword with <2 occurrences.
**WARNING**: ATS score 50-69% OR any primary keyword with <3 occurrences.

### Banned Phrase Detector

The following phrases are BANNED unless backed by specific metrics:

| Banned Phrase             | Why                  | Fix                                |
| ------------------------- | -------------------- | ---------------------------------- |
| "Results-driven"          | Empty buzzword       | Remove or add specific result      |
| "Team player"             | Vague                | Replace with collaboration example |
| "Detail-oriented"         | Tell don't show      | Replace with accuracy metric       |
| "Fast learner"            | Unverifiable         | Replace with ramp-up example       |
| "Passionate about"        | Subjective           | Replace with action/outcome        |
| "Go-getter"               | Cliché               | Replace with initiative example    |
| "Self-starter"            | Vague                | Replace with ownership example     |
| "Hard worker"             | Everyone claims this | Replace with output metric         |
| "Excellent communication" | Vague                | Replace with stakeholder example   |
| "Strong leadership"       | Vague                | Replace with team size/outcome     |

**BLOCKER**: Any banned phrase without accompanying metric/evidence.

### ATS & Formatting Requirements

**PASS conditions**:

- No tables/columns
- No `#` H1 headers
- Sections are `##`, subsections are `###`
- No contact info in markdown
- Dates are consistent

### BLOCKERS

- Any Experience role with a bullet lacking a metric
- Banned verbs used as the lead verb (Helped/Assisted/Worked on/Participated/Responsible for)
- Missing required sections or wrong heading levels
- Contact info present in markdown
- Claims not supported by `master_experience.md` (hallucination)
- Any Weak-rated bullet in CVI check
- Any primary ATS keyword with <2 occurrences
- Any banned phrase without supporting evidence

---

## Gate D: Cover Letter Quality (cover_letter.md)

**PASS conditions**:

- Role-aligned tone and vocabulary (role_category aware)
- Does not duplicate the resume; adds narrative + fit
- Mentions 2-3 role-specific requirements and ties them to evidence
- No hallucinations; no new employers/titles/metrics not in source
- Uses domain vocabulary from `power_language.md`

### ATS Keyword Integration Check

Verify cover letter includes:

| Requirement                                                        | Check                        |
| ------------------------------------------------------------------ | ---------------------------- |
| At least 2-3 primary ATS keywords from `strategic_match_report.md` | Count and list               |
| Keywords used naturally (not forced/dumped)                        | Read for flow                |
| Company name spelled correctly                                     | Verify against `job_desc.md` |
| Role title matches JD exactly                                      | Verify against `job_desc.md` |

**WARNING**: <2 primary keywords used.

### Claim Verification Check

Every factual claim must trace to source:

| Claim Type         | Source Required                       | BLOCKER if Missing |
| ------------------ | ------------------------------------- | ------------------ |
| Employer names     | `master_experience.md` or `resume.md` | ✅ Yes             |
| Job titles         | `master_experience.md` or `resume.md` | ✅ Yes             |
| Metrics/numbers    | `master_experience.md` or `resume.md` | ✅ Yes             |
| Skills/tools       | `master_experience.md` or `resume.md` | ✅ Yes             |
| Personal narrative | `identity.json` narrative_hooks       | ⚠️ Warning only    |

### Anti-Pattern Check

| Anti-Pattern                   | Detection                                     | Fix                   |
| ------------------------------ | --------------------------------------------- | --------------------- |
| "I am writing to apply for..." | Opening line check                            | Rewrite with hook     |
| Resume bullet copy-paste       | >80% word overlap with resume bullet          | Rephrase as narrative |
| Generic company praise         | No specific product/initiative mentioned      | Add specifics         |
| Desperation language           | "really want/need", "would be honored"        | Rewrite confidently   |
| Salary mention                 | Any compensation discussion                   | Remove entirely       |
| Gap/weakness apology           | "Although I lack...", "Despite not having..." | Remove or reframe     |

**BLOCKERS**:

- Duplicates resume bullet lists (>80% overlap)
- Introduces unverified claims (employer/title/metric not in source)
- Uses banned opening ("I am writing to apply...")
- Mentions salary or compensation
- Company name misspelled

---

## Gate E: PDF Readiness (Pre-Build)

**PASS conditions**:

- Escapes LaTeX-breaking characters where needed (`%`, `$`, `&`)
- Correct headings and list formatting
- No citations, no file paths, no line-number references
- No H1 headers (`#`) in document
- No contact info duplicated in markdown (template handles it)
- Required sections present (Summary, Experience, Education, Skills)

**BLOCKERS**:

- H1 header found in document
- Contact info present in markdown body
- Missing required sections
- Unescaped special characters that break LaTeX

---

## Gate F: Final Artifact Verification (Post-Build)

**This is the FINAL gate. Pipeline is incomplete until this gate PASSES.**

### Artifact Existence Check

| Artifact            | Required                  | Check                       |
| ------------------- | ------------------------- | --------------------------- |
| `resume.pdf`        | ✅ Always                 | File exists AND size > 10KB |
| `resume.docx`       | ✅ Always                 | File exists AND size > 5KB  |
| `resume.txt`        | ✅ Always                 | File exists AND size > 1KB  |
| `cover_letter.pdf`  | If cover_letter.md exists | File exists AND size > 5KB  |
| `cover_letter.docx` | If cover_letter.md exists | File exists                 |

### Artifact Quality Check

| Check                | Method                     | PASS Criteria                             |
| -------------------- | -------------------------- | ----------------------------------------- |
| PDF renders          | Open file                  | No error, content visible                 |
| Contact info correct | Compare to `identity.json` | Exact match on name, email, phone         |
| No placeholder text  | Search PDF content         | No "Lorem ipsum", "[PLACEHOLDER]", "TODO" |
| Company name correct | Search PDF content         | Matches `job_desc.md` company field       |
| Role title correct   | Search PDF content         | Matches `job_desc.md` role field          |

### BLOCKERS (Pipeline Incomplete)

- ❌ Any required artifact missing from `applications/[folder]/`
- ❌ PDF file corrupted or empty (size < 10KB)
- ❌ Contact info mismatch between PDF and `identity.json`
- ❌ Placeholder text found in any artifact
- ❌ Build command failed (non-zero exit code)

### PASS Output

When Gate F passes, output:

```markdown
## ✅ GATE F: PASS - Artifacts Ready for Submission

| Artifact          | Size  | Verified |
| ----------------- | ----- | -------- |
| resume.pdf        | [X]KB | ✅       |
| resume.docx       | [X]KB | ✅       |
| resume.txt        | [X]KB | ✅       |
| cover_letter.pdf  | [X]KB | ✅       |
| cover_letter.docx | [X]KB | ✅       |

**Pipeline Status**: COMPLETE
**Ready for**: ATS upload, recruiter email, job portal submission
```

**BLOCKERS**:

- Any structural rule broken that would fail LaTeX/Pandoc

---

## Output Format (MANDATORY)

Return a gate report in this exact format:

```markdown
# Quality Gate Report

## Artifact

- **Artifact**: [job_desc|strategic_match_report|resume|cover_letter|extra_questions]
- **Path**: applications/[folder]/[file].md

## Gate Results

- **Gate A (JD Health)**: PASS|FAIL|N/A
- **Gate B (Analysis Health)**: PASS|FAIL|N/A
- **Gate C (Resume Quality + ATS)**: PASS|FAIL|N/A
- **Gate D (Cover Letter Quality)**: PASS|FAIL|N/A
- **Gate E (PDF Readiness)**: PASS|FAIL|N/A

## Blocking Issues (Must Fix)

- [BLOCKER] [issue]
- [BLOCKER] [issue]

## Warnings (Should Fix)

- [WARN] [issue]

## Required Corrections

Provide concrete edits the assistant must apply. If you can correct immediately, do so and then rerun the relevant gate(s).

## Final Status

- **STATUS**: PASS|FAIL
```

---

## Self-Correction Loop (Mandatory)

If **STATUS = FAIL**:

1. Revise the artifact(s) to address **all BLOCKERS**
2. Rerun the same gate(s)
3. Repeat until **STATUS = PASS**

Do not proceed to the next pipeline step until PASS.
