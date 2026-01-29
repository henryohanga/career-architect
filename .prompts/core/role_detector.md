# Role: Job Classification Specialist

## Objective

Analyze a job description and classify it into the appropriate role category to enable role-specific resume optimization.

## Input

- `applications/[folder]/job_desc.md`

## Instructions

1. Read the job description carefully
2. Identify key signals: job title, responsibilities, required skills, tools mentioned
3. Classify into ONE primary category
4. Output the classification for downstream prompts

---

## Role Categories

### `engineering`

**Signals:**

- Titles: Engineer, Developer, Architect, SRE, DevOps, Data Scientist, ML Engineer
- Skills: Programming languages, frameworks, system design, algorithms, infrastructure
- Tools: Git, AWS, Kubernetes, databases, CI/CD, IDEs
- Responsibilities: Build, deploy, debug, architect, code review

### `business`

**Signals:**

- Titles: Manager, Director, VP, Analyst, Coordinator, Specialist, Consultant
- Subcategories:
  - **Sales**: Account Executive, BDR, Sales Manager, Revenue
  - **Marketing**: Marketing Manager, Growth, Demand Gen, Brand, Content
  - **Operations**: Operations Manager, Supply Chain, Logistics, Process
  - **Finance**: Financial Analyst, Controller, FP&A, Accountant
  - **HR**: Recruiter, HR Manager, People Operations, Talent Acquisition
  - **Project/Program**: Project Manager, Program Manager, Scrum Master
- Skills: Stakeholder management, budgeting, forecasting, strategy, communication
- Tools: Salesforce, HubSpot, Excel, Tableau, SAP, Workday

### `creative`

**Signals:**

- Titles: Designer, Writer, Content Creator, Brand Manager, Art Director
- Skills: Design thinking, copywriting, visual design, storytelling, UX
- Tools: Figma, Adobe Creative Suite, Canva, CMS platforms

### `healthcare`

**Signals:**

- Titles: Nurse, Physician, Therapist, Clinical, Medical, Pharmacist
- Skills: Patient care, clinical protocols, medical terminology, compliance
- Certifications: RN, MD, NP, PA, HIPAA

### `academic`

**Signals:**

- Titles: Professor, Researcher, Postdoc, Fellow, Lecturer
- Skills: Research, publishing, grant writing, teaching, peer review
- Context: University, research institution, think tank

---

## Output Format

**CRITICAL ACTION REQUIRED**: You MUST edit `applications/[folder]/job_desc.md` to add classification fields to its YAML frontmatter.

### Step-by-Step Instructions

1. **Read** `applications/[folder]/job_desc.md`
2. **Analyze** the job description using the role categories and signals above
3. **Edit** the file's YAML frontmatter to ADD these fields (do not remove existing fields):

```yaml
---
company: [existing]
role: [existing]
date_added: [existing]
# ADD THESE FIELDS:
role_category: engineering # or business|creative|healthcare|academic
subcategory: backend # specific type (e.g., sales, marketing, product_design, nursing, postdoc)
role_confidence: high # high|medium|low
recommended_framework: modern_builder # modern_builder|business_impact|creative_portfolio|clinical_outcomes|academic_research
interview_focus: technical # technical|behavioral|case_study|portfolio|clinical|research
---
```

4. **Save** the edited file

### Verification (MANDATORY)

After editing, confirm:

- [ ] `role_category` field exists in frontmatter
- [ ] `subcategory` field exists in frontmatter
- [ ] File was saved (not just displayed)

**BLOCKER**: If `role_category` is missing from `job_desc.md` after this step, the orchestrator cannot route correctly. Gate A will fail.

### Subcategory Reference

| role_category | Valid subcategories                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------- |
| `engineering` | backend, frontend, fullstack, devops, sre, data, ml, mobile, security, platform                         |
| `business`    | sales, marketing, operations, finance, hr, project_management, product_management, strategy, consulting |
| `creative`    | product_design, ux, ui, brand, content, copywriting, art_direction, video                               |
| `healthcare`  | nursing, physician, allied_health, clinical_ops, pharmacy, administration                               |
| `academic`    | postdoc, lecturer, researcher, professor, lab_manager                                                   |

### Signals to Capture (for downstream use)

Also record in frontmatter (optional but recommended):

```yaml
signals_detected:
  - "[Signal 1 from JD]"
  - "[Signal 2 from JD]"
  - "[Signal 3 from JD]"
```

---

## Decision Rules

1. **If ambiguous between engineering and product**: Check if coding/technical implementation is required → engineering; if strategy/roadmap focused → business
2. **If "Technical" appears in business title** (e.g., Technical Account Manager): Still classify as business unless coding is a core responsibility
3. **If startup with vague title**: Look at responsibilities, not just title
4. **If multiple categories apply**: Choose the one with >60% of responsibilities

---

## Examples

**Input**: "Senior Software Engineer - Backend"

```yaml
role_category: engineering
subcategory: backend
role_confidence: high
recommended_framework: modern_builder
interview_focus: technical
signals_detected:
  - "Software Engineer" in title
  - Python, Go, PostgreSQL mentioned
  - System design responsibilities
```

**Input**: "Marketing Manager - Demand Generation"

```yaml
role_category: business
subcategory: marketing
role_confidence: high
recommended_framework: business_impact
interview_focus: case_study
signals_detected:
  - "Marketing Manager" in title
  - Campaign management, MQL targets
  - HubSpot, Google Analytics mentioned
```

**Input**: "Product Designer"

```yaml
role_category: creative
subcategory: product_design
role_confidence: high
recommended_framework: creative_portfolio
interview_focus: portfolio
signals_detected:
  - "Designer" in title
  - Figma, user research mentioned
  - Portfolio required
```
