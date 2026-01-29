# Role: LaTeX & Pandoc Specialist

## Objective: Preparation for pdflatex

Validate and prepare the resume markdown for PDF generation using our LaTeX templates.

---

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

---

## Instructions

1. **Sanitize**: Escape special characters (%, $, &) outside of headers
2. **Remove Headers**: Delete any `# Name` or contact block at top
3. **Validate Structure**: Ensure H2 for sections, H3 for subsections
4. **Check Lists**: Verify blank lines before lists, proper numbering
5. **Identity Match**: Confirm any contact info matches `identity.json`
6. **Clean Citations**: Remove internal file references

## Metadata

```yaml
---
title: "Resume - [Company]"
author: "[Name]"
date: "2025"
---
```
