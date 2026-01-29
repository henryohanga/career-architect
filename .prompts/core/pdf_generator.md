# Role: Application Artifact Builder

## Objective: Generate Submission-Ready Application Documents

Transform validated markdown into **final submission artifacts** (PDF, DOCX, TXT) that can be uploaded to ATS systems or sent directly to employers.

This is a **MANDATORY FINAL STEP**. The pipeline is NOT complete until submission-ready files exist on disk.

---

## Inputs

- `applications/[folder]/resume.md`
- `applications/[folder]/cover_letter.md` (if present)
- `source_materials/identity.json`
- `.prompts/core/quality_gates.md` (Gate E)
- `templates/` (LaTeX templates for PDF generation)

## Required Output Artifacts

**MANDATORY** - Pipeline is incomplete without these files:

| Artifact          | Filename            | Purpose                          |
| ----------------- | ------------------- | -------------------------------- |
| Resume PDF        | `resume.pdf`        | Primary submission format        |
| Resume DOCX       | `resume.docx`       | ATS-friendly fallback            |
| Resume TXT        | `resume.txt`        | Plain text for copy-paste fields |
| Cover Letter PDF  | `cover_letter.pdf`  | If cover letter exists           |
| Cover Letter DOCX | `cover_letter.docx` | If cover letter exists           |

**Location**: All artifacts saved to `applications/[folder]/`

## Critical Template Rules

The LaTeX templates (`templates/style.tex`, etc.) define the visual styling. The markdown must be structured to work with these templates.

### Header Handling

**The template automatically generates the header.** The `\contactline` macro is injected from `identity.json`:

```latex
\contactline{NAME}{LOCATION}{PHONE}{EMAIL}{LINKEDIN}{GITHUB}{PORTFOLIO}
```

**Therefore, the markdown MUST NOT contain:**

- ❌ `# Name` (H1 header with person's name)
- ❌ Contact information (email, phone, location, links)
- ❌ Any header-like content before `## Summary`

### Required Structure

The markdown should follow this exact structure:

```markdown
---
company: [Company]
role: [Role]
date: [YYYY-MM-DD]
---

## Summary

[Summary paragraph]

## Experience

### Company Name

**Role Title** | Start - End

- Achievement with metric
- Achievement with metric

## Education

### University

**Degree** | Year

## Skills

**Category:** Skill1, Skill2, Skill3
```

---

## Validation Checklist

Before generating PDF, verify:

1. **No H1 Headers**: Document should NOT contain `# ` (single hash headers)
2. **No Contact Info**: Email, phone, LinkedIn URLs should NOT appear in markdown
3. **Sections Use H2**: All sections use `## ` (double hash)
4. **Subsections Use H3**: Company names, schools use `### `
5. **Lists Properly Formatted**:
   - Blank line before each list
   - Consistent bullet style (`-` or `1.`)
   - Each item on its own line
6. **Special Characters Escaped**: `%`, `$`, `&`, `#` in content (not headers)
7. **No Citations**: Remove any `:40-44` style references

---

## Error Conditions

**ABORT with CRITICAL ERROR if:**

- Phone/email in markdown doesn't match `identity.json`
- H1 header (`#`) found in document
- Contact information duplicated in content
- Missing required sections (Summary, Experience)
- `.prompts/core/quality_gates.md` Gate E returns **STATUS = FAIL**

---

## Instructions

0. **Quality Gate (Mandatory)**: Execute `.prompts/core/quality_gates.md` using **Gate E (PDF Readiness)** on:
   - `applications/[folder]/resume.md`
   - `applications/[folder]/cover_letter.md` (if present)

   If Gate E fails, self-correct the artifacts and rerun Gate E until **STATUS = PASS**.

1. **Sanitize**: Escape special characters (%, $, &) outside of headers
2. **Remove Headers**: Delete any `# Name` or contact block at top
3. **Validate Structure**: Ensure H2 for sections, H3 for subsections
4. **Check Lists**: Verify blank lines before lists, proper numbering
5. **Identity Match**: Confirm any contact info matches `identity.json`
6. **Clean Citations**: Remove internal file references

## Build Commands

After validation passes, use the Python build scripts (NOT raw pandoc):

### Primary Build: `scripts/build_resume.py`

```bash
# Build all formats (PDF, DOCX, TXT) for resume
python scripts/build_resume.py applications/[folder]/resume.md

# Build with specific template
python scripts/build_resume.py applications/[folder]/resume.md --template default

# Build cover letter
python scripts/build_resume.py applications/[folder]/cover_letter.md
```

**Available templates**: `default`, `minimal`, `creative`, `executive`

The script automatically:

- ✅ Uses correct LaTeX template from `templates/`
- ✅ Validates contact info against `identity.json`
- ✅ Builds PDF, DOCX, TXT in parallel
- ✅ Reports success/failure with colors

---

## Template Selection (MANDATORY)

You MUST select the appropriate template. Priority order:

1. **Check `job_desc.md` frontmatter** for explicit `template:` field
2. **Check `identity.json -> preferences.template`** for user default
3. **Auto-select based on `role_category`** (see table below)

### Template Routing by Role Category

| role_category | Default Template         | Rationale                                          |
| ------------- | ------------------------ | -------------------------------------------------- |
| `engineering` | `default`                | Modern, tech-forward, professional                 |
| `business`    | `default` or `executive` | Professional; use `executive` for Director+ titles |
| `creative`    | `creative`               | Bold, memorable, design-conscious                  |
| `healthcare`  | `minimal`                | Clean, conservative, clinical                      |
| `academic`    | `minimal`                | Traditional, no-frills, scholarly                  |

### Seniority Override

If role title contains senior indicators, consider upgrading:

| Title Contains                            | Upgrade To            |
| ----------------------------------------- | --------------------- |
| Director, VP, C-level, Head of, Principal | `executive`           |
| Lead, Senior, Staff                       | Keep category default |
| Junior, Associate, Entry                  | Keep category default |

### Enforcement

Before building, verify template selection:

```bash
# Build with explicit template
python scripts/build_resume.py applications/[folder]/resume.md --template [selected]
```

**BLOCKER**: If no template is specified and role_category is missing, STOP and run role detection first.

---

### ATS Score Check: `scripts/ats_score.py`

```bash
# Score resume against job description
python scripts/ats_score.py applications/[folder]/

# Output as JSON for programmatic use
python scripts/ats_score.py applications/[folder]/ --json
```

**Score interpretation**:

- ≥70%: Strong match ✅
- 50-69%: Moderate match ⚠️ (consider adding missing keywords)
- <50%: Needs improvement ❌ (BLOCKER - revise resume)

### Export Formats: `scripts/export_resume.py`

```bash
# Export to plain text (ATS-optimized)
python scripts/export_resume.py txt [folder]

# Export to JSON Resume schema
python scripts/export_resume.py json [folder]

# Export all formats
python scripts/export_resume.py all [folder]
```

---

## Artifact Verification Checklist (MANDATORY)

After build, verify ALL artifacts exist and are valid:

| Check                   | Command                      | Expected                     |
| ----------------------- | ---------------------------- | ---------------------------- |
| Resume PDF exists       | `ls -la resume.pdf`          | File size > 10KB             |
| Resume PDF opens        | `open resume.pdf` (Mac)      | No errors, renders correctly |
| Resume DOCX exists      | `ls -la resume.docx`         | File size > 5KB              |
| Resume TXT exists       | `ls -la resume.txt`          | File size > 1KB              |
| Cover Letter PDF exists | `ls -la cover_letter.pdf`    | If cover_letter.md exists    |
| No build errors         | Check pandoc/pdflatex output | Exit code 0                  |

### BLOCKERS (Pipeline Incomplete)

- ❌ Any required artifact missing from disk
- ❌ PDF file size < 10KB (likely empty or corrupted)
- ❌ Build command returns non-zero exit code
- ❌ PDF contains Lorem ipsum or placeholder text
- ❌ Contact info in PDF doesn't match `identity.json`

---

## Final Artifact Summary

After successful build, report to user:

```markdown
## ✅ Application Artifacts Generated

**Location**: `applications/[folder]/`

| File              | Size   | Status   |
| ----------------- | ------ | -------- |
| resume.pdf        | [X] KB | ✅ Ready |
| resume.docx       | [X] KB | ✅ Ready |
| resume.txt        | [X] KB | ✅ Ready |
| cover_letter.pdf  | [X] KB | ✅ Ready |
| cover_letter.docx | [X] KB | ✅ Ready |

**Next Steps**:

1. Review PDF visually for formatting issues
2. Upload to ATS or send to recruiter
3. Run interview prep if needed
```

---

## Metadata

```yaml
---
title: "Resume - [Company]"
author: "[Name]"
date: "2025"
---
```
