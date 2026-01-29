# Role: Lead Career Operations Engineer

## Task: Initialize and execute the end-to-end "Job Application Build Pipeline."

---

## Prompt Architecture

This pipeline uses a **multi-profile prompt system** to support diverse career types:

```
.prompts/
├── core/                    # Shared prompts (all roles)
│   ├── role_detector.md     # Auto-classifies job type
│   ├── power_language.md    # A+++ screening language + ATS optimization
│   ├── quality_gates.md     # Self-checks + self-correction gates
│   ├── setup.md             # Experience extraction
│   ├── cover_letter.md      # Cover letter generation
│   ├── follow_up.md         # Follow-up emails
│   └── pdf_generator.md     # Build preparation
├── engineering/             # Technical roles
│   ├── manifesto_logic.md   # Modern Builder philosophy
│   ├── analyser.md          # Technical gap analysis
│   ├── tailor_resume.md     # Engineering resume
│   └── interview_prep.md    # Technical interviews
├── business/                # Non-technical roles
│   ├── business_capabilities.md  # Business Impact framework
│   ├── analyser.md          # Business gap analysis
│   ├── tailor_resume.md     # Business resume
│   └── interview_prep.md    # Business interviews
└── [legacy prompts]         # Original prompts (deprecated)
```

---

### Step 0: Load User Preferences

**CRITICAL**: Before any generation, read `source_materials/identity.json`:

```
preferences.language      → Output language (en, de, es, fr, pt, etc.)
preferences.resume_style  → Style guide to apply (modern_builder, traditional, academic, creative)
preferences.tone          → Overall tone (professional, conversational, formal)
```

Reference `.prompts/core/style_guide.md` for style-specific rules.

### Step 0.5: Workspace Initialization

- **Scan**: Identify Company Name and Role from the provided Job Description (JD).
- **Directory Creation**: Create `applications/YYYY-MM-DD-company-role/`.
- **Action**: If only JD text was provided, save it as `job_desc.md` inside that new directory.

### Step 0.6: Format Job Description (MANDATORY)

When saving `job_desc.md`, use this structured format:

```markdown
---
company: [Company Name]
role: [Role Title]
date_added: [YYYY-MM-DD]
status: draft
source_url: [URL if available]
---

# [Company Name] - [Role Title]

## Company Overview

[2-3 sentences about the company, industry, size, mission]

## Role Summary

[Brief description of what this role does and its impact]

## Key Responsibilities

- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

## Required Qualifications

- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Preferred Qualifications

- [Nice-to-have 1]
- [Nice-to-have 2]

## Tech Stack / Tools

- **Languages:** [List]
- **Frameworks:** [List]
- **Infrastructure:** [List]
- **Other:** [List]

## Compensation & Benefits

- **Salary Range:** [If provided]
- **Equity:** [If provided]
- **Benefits:** [Key benefits]

## Interview Process

[If mentioned in JD]

## Notes

- [Any additional observations]
- [Red flags or highlights]
- [Questions to research]

---

## Original Job Posting

> [Paste the complete, unmodified original job description here] > [Preserve all original formatting, bullet points, and text] > [This serves as the source of truth for reference]
```

**Formatting Rules:**

- Use H1 (`#`) only for the main title
- Use H2 (`##`) for major sections
- Use bullet lists (`-`) for items
- Bold key terms with `**term**`
- Keep sections even if empty (mark as "Not specified")
- Extract and organize scattered info into proper sections
- **ALWAYS preserve original JD** in the "Original Job Posting" section

### Step 0.65: Quality Gate (JD Health)

**Execute `.prompts/core/quality_gates.md` (Gate A)** on `applications/[folder]/job_desc.md`.

**STOP** if Gate A fails. Fix `job_desc.md` and rerun until **PASS**.

### Step 0.7: Vertical Classification

Classify the company size and adapt tone accordingly:

- **🚀 Startup (<50 people)**: Bold, ownership-focused, high-energy
- **📈 ScaleUp (50-1000 people)**: Process maturity, architectural stability, collaboration
- **🏢 Big Tech (1000+ people)**: Deep expertise, massive scale, methodical precision

### Step 0.8: Role Detection (NEW - CRITICAL)

**Execute `.prompts/core/role_detector.md`** to classify the job into a role category.

This determines which prompt set to use:

| Role Category | Prompt Directory        | Capability Framework |
| ------------- | ----------------------- | -------------------- |
| `engineering` | `.prompts/engineering/` | Modern Builder       |
| `business`    | `.prompts/business/`    | Business Impact      |
| `creative`    | `.prompts/creative/`    | Creative Portfolio   |
| `healthcare`  | `.prompts/healthcare/`  | Clinical Outcomes    |
| `academic`    | `.prompts/academic/`    | Academic Research    |

**Output**: Save classification to `job_desc.md` frontmatter:

```yaml
role_category: [engineering|business|creative|healthcare|academic]
subcategory: [specific type]
```

### Step 0.9: Framework Alignment

Based on `role_category`:

- If `engineering`: Execute `.prompts/engineering/manifesto_logic.md`
- If `business`: Execute `.prompts/business/business_capabilities.md`
- If `creative`: Execute `.prompts/creative/creative_capabilities.md`
- If `healthcare`: Execute `.prompts/healthcare/clinical_outcomes.md`
- If `academic`: Execute `.prompts/academic/academic_research.md`

### Step 1: Deep Analysis

**Route based on role_category**:

- If `engineering`: Execute `.prompts/engineering/analyser.md`
- If `business`: Execute `.prompts/business/analyser.md`
- If `creative`: Execute `.prompts/creative/analyser.md`
- If `healthcare`: Execute `.prompts/healthcare/analyser.md`
- If `academic`: Execute `.prompts/academic/analyser.md`

**Execute `.prompts/core/quality_gates.md` (Gate B)** on `applications/[folder]/strategic_match_report.md`.

**STOP** if Gate B fails. Fix `strategic_match_report.md` and rerun until **PASS**.

**Gap Check**: If critical gaps are identified, pause and ask: _"I've found gaps in [Skills/Tools]. Do you have unrecorded experience here?"_ - If User provides info, run `.prompts/core/gap_filler.md` to update `source_materials/master_experience.md` before proceeding.

**STOP**: Present the **Strategic Match Report**. Wait for User to say "GO."

### Step 2: Generation (Core Documents)

**Route based on role_category**:

- If `engineering`: Execute `.prompts/engineering/tailor_resume.md`
- If `business`: Execute `.prompts/business/tailor_resume.md`
- If `creative`: Execute `.prompts/creative/tailor_resume.md`
- If `healthcare`: Execute `.prompts/healthcare/tailor_resume.md`
- If `academic`: Execute `.prompts/academic/tailor_resume.md`

Then execute `.prompts/core/cover_letter.md` to generate cover letter (shared prompt, adapts to role_category).

**Execute `.prompts/core/quality_gates.md` (Gate C)** on `applications/[folder]/resume.md`.

**STOP** if Gate C fails. Fix `resume.md` and rerun until **PASS**.

**Execute `.prompts/core/quality_gates.md` (Gate D)** on `applications/[folder]/cover_letter.md`.

**STOP** if Gate D fails. Fix `cover_letter.md` and rerun until **PASS**.

### Step 2.5: Handle Extra Questions (Logistics & Narrative)

- **Scan**: Prompt user for application questions.
- **Data Load**: Explicitly read `source_materials/identity.json` for the `logistics` object.
- **Execution**: Run `.prompts/core/application_questions.md`.
- **Validation**: If the AI detects a question about salary or visa but the user hasn't provided those in `identity.json`, it must pause and ask: _"I noticed a question about [Salary/Notice]. What values should I use?"_
- **Save**: Write to `applications/[folder]/extra_questions.md`.

### Step 3: Lint & Build Preparation (Pre-Build)

- **Execute `.prompts/core/quality_gates.md` (Gate E)** on the final `resume.md` and `cover_letter.md`.
- **STOP** if Gate E fails. Fix artifacts and rerun until **PASS**.
- **Identity Check**: Validate that contact info matches `source_materials/identity.json` exactly. Flag as **CRITICAL ERROR** if a hallucination or old number is detected.

### Step 4: Generate Submission Artifacts (MANDATORY)

**⚠️ PIPELINE IS INCOMPLETE WITHOUT THIS STEP**

Execute `.prompts/core/pdf_generator.md` to generate artifacts using the Python scripts:

| Artifact            | Required  | Format             |
| ------------------- | --------- | ------------------ |
| `resume.pdf`        | ✅ Always | Primary submission |
| `resume.docx`       | ✅ Always | ATS fallback       |
| `resume.txt`        | ✅ Always | Copy-paste fields  |
| `cover_letter.pdf`  | If exists | Primary            |
| `cover_letter.docx` | If exists | ATS fallback       |

**Template Selection** (MANDATORY - select based on role_category):

| role_category | Template   | Override for Director+/VP/C-level |
| ------------- | ---------- | --------------------------------- |
| `engineering` | `default`  | `executive`                       |
| `business`    | `default`  | `executive`                       |
| `creative`    | `creative` | `executive`                       |
| `healthcare`  | `minimal`  | `minimal`                         |
| `academic`    | `minimal`  | `minimal`                         |

**Build Commands** (use Python scripts, NOT raw pandoc):

```bash
# Build resume with role-appropriate template
python scripts/build_resume.py applications/[folder]/resume.md --template [selected]

# Build cover letter
python scripts/build_resume.py applications/[folder]/cover_letter.md

# Run ATS keyword score check
python scripts/ats_score.py applications/[folder]/
```

**ATS Score Gate**: If `ats_score.py` returns <50%, **STOP** and revise resume to add missing keywords.

### Step 5: Final Artifact Verification (Gate F)

**Execute `.prompts/core/quality_gates.md` (Gate F)** - Final artifact verification.

Verify:

- [ ] `resume.pdf` exists and size > 10KB
- [ ] `resume.docx` exists and size > 5KB
- [ ] `resume.txt` exists and size > 1KB
- [ ] Cover letter artifacts exist (if cover_letter.md exists)
- [ ] Contact info in PDF matches `identity.json`
- [ ] No placeholder text in any artifact

**STOP** if Gate F fails. Rebuild artifacts and rerun until **PASS**.

### Step 6: Registry Update

- Update the `README.md` dashboard table with the current date, company, role, and a status of "� Ready to Submit."
- **Only mark as 🟢 Ready if Gate F PASSED.**

## 💎 Operational Constraints (Non-Negotiable)

1. **Identity Source of Truth**: Pull all contact data (Phone, Email, Links) **exclusively** from `source_materials/identity.json`. Never use info from old resume files.
2. **Role-Appropriate Framework**: Use the capability framework matching the detected role_category:
   - `engineering` → Modern Builder Capabilities
   - `business` → Business Impact Capabilities
   - `creative` → Portfolio & Creative Impact
   - `healthcare` → Clinical Outcomes
   - `academic` → Academic Research
3. **Industry Analogy Rule**: If the target industry is new, pivot achievements using the domain translation map from the role-specific analyser.
4. **No Citations**: Remove all file paths or line numbers (e.g., :40-44) from final documents.
5. **Prompt Routing**: Always use prompts from the detected role category directory. Never mix frameworks across categories.

## 📐 Template Formatting Rules (MANDATORY)

All generated documents must follow these rules for proper PDF generation:

### Resume Markdown Structure

```markdown
---
company: [Company]
role: [Role]
date: [YYYY-MM-DD]
---

## Summary

[content]

## Experience

### Company Name

**Role** | Dates

- Bullet points

## Education

## Skills
```

```

### Critical Rules

- **NO H1 headers** (`#`) - The LaTeX template handles the name/header
- **NO contact info** in markdown - Template injects from `identity.json`
- **Use H2** (`##`) for sections, **H3** (`###`) for subsections
- **Blank line before lists** - Required for proper rendering
- **Numbered lists on separate lines** - Each `1.` `2.` `3.` on its own line
```
