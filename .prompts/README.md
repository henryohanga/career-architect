# Prompts Index

This directory contains AI instruction prompts for the Career Architect pipeline. Use these prompts with your AI assistant (Claude, GPT-4, etc.) to generate tailored job application materials.

## Multi-Profile Architecture

Career Architect supports **multiple career types** through role-specific prompt sets:

```
.prompts/
├── core/                    # Shared prompts (all role types)
│   ├── role_detector.md     # Auto-classifies job type from JD
│   ├── power_language.md    # A+++ screening language + ATS optimization
│   ├── quality_gates.md     # Self-checks + self-correction gates
│   ├── setup.md             # Experience extraction (role-agnostic)
│   ├── cover_letter.md      # Cover letter (adapts to role type)
│   ├── follow_up.md         # Email templates
│   ├── pdf_generator.md     # Build preparation
│   └── application_questions.md
│
├── engineering/             # Technical/Engineering roles
│   ├── manifesto_logic.md   # Modern Builder philosophy
│   ├── analyser.md          # Technical gap analysis
│   ├── tailor_resume.md     # Engineering resume generation
│   └── interview_prep.md    # Technical interview prep
│
├── business/                # Sales, Marketing, Ops, Finance, HR, PM
│   ├── business_capabilities.md  # Business Impact framework
│   ├── analyser.md          # Business gap analysis
│   ├── tailor_resume.md     # Business resume generation
│   └── interview_prep.md    # Business interview prep
│
├── creative/                # Design, Writing, Brand
│   ├── creative_capabilities.md  # Creative Portfolio framework
│   ├── analyser.md          # Creative gap analysis
│   ├── tailor_resume.md     # Creative resume generation
│   └── interview_prep.md    # Portfolio + creative interview prep
│
├── healthcare/              # Clinical roles
│   ├── clinical_outcomes.md # Clinical Outcomes framework
│   ├── analyser.md          # Healthcare gap analysis
│   ├── tailor_resume.md     # Healthcare resume generation
│   └── interview_prep.md    # Clinical interview prep
│
├── academic/                # Research/teaching roles
│   ├── academic_research.md # Academic Research framework
│   ├── analyser.md          # Academic gap analysis
│   ├── tailor_resume.md     # Academic resume/CV generation
│   └── interview_prep.md    # Research interview prep
│
└── [legacy prompts]         # Original prompts (for backward compatibility)
```

### Role Categories

| Category      | Example Roles                                 | Capability Framework |
| ------------- | --------------------------------------------- | -------------------- |
| `engineering` | Software Engineer, DevOps, Data Scientist     | Modern Builder       |
| `business`    | Sales, Marketing, Operations, Finance, HR, PM | Business Impact      |
| `creative`    | Designer, Writer, Brand Manager               | Creative Portfolio   |
| `healthcare`  | Nurse, Physician, Clinical roles              | Clinical Outcomes    |
| `academic`    | Professor, Researcher, Postdoc                | Academic Research    |

The pipeline **auto-detects** the role category from the job description and routes to the appropriate prompts.

---

## First-Time Setup (Do This Once)

Before using any prompts, you must add your source materials:

```
1. Edit identity.json          → Your contact info
2. Add resumes to resumes/     → Copy-paste your existing resumes as .md files
3. Add projects to projects/   → Document your key projects
4. Run core/setup.md           → AI builds your master_experience.md
```

Then for each job application, just paste the job description!

## Quick Reference

### Core Pipeline

| Prompt                     | Location                      | When to Use                     | Output                 |
| -------------------------- | ----------------------------- | ------------------------------- | ---------------------- |
| `role_detector.md`         | `core/`                       | Auto-run by orchestrator        | Role classification    |
| `setup.md`                 | `core/`                       | **First!** After adding resumes | `master_experience.md` |
| `main_orchestrator.md`     | root                          | For each new job application    | Full pipeline          |
| `analyser.md`              | `engineering/` or `business/` | Gap analysis (auto-routed)      | Strategic Match Report |
| `tailor_resume.md`         | `engineering/` or `business/` | Generate resume (auto-routed)   | `resume.md`            |
| `cover_letter.md`          | `core/`                       | Generate cover letter           | `cover_letter.md`      |
| `application_questions.md` | `core/`                       | Answer extra questions          | `extra_questions.md`   |
| `pdf_generator.md`         | `core/`                       | Prepare for PDF build           | Validated Markdown     |

### Role-Specific Prompts

| Role Category | Analyser                  | Resume                         | Interview Prep                  | Framework                           |
| ------------- | ------------------------- | ------------------------------ | ------------------------------- | ----------------------------------- |
| Engineering   | `engineering/analyser.md` | `engineering/tailor_resume.md` | `engineering/interview_prep.md` | `engineering/manifesto_logic.md`    |
| Business      | `business/analyser.md`    | `business/tailor_resume.md`    | `business/interview_prep.md`    | `business/business_capabilities.md` |
| Creative      | `creative/analyser.md`    | `creative/tailor_resume.md`    | `creative/interview_prep.md`    | `creative/creative_capabilities.md` |
| Healthcare    | `healthcare/analyser.md`  | `healthcare/tailor_resume.md`  | `healthcare/interview_prep.md`  | `healthcare/clinical_outcomes.md`   |
| Academic      | `academic/analyser.md`    | `academic/tailor_resume.md`    | `academic/interview_prep.md`    | `academic/academic_research.md`     |

### Supporting Prompts

| Prompt                  | When to Use                   | Output                         |
| ----------------------- | ----------------------------- | ------------------------------ |
| `power_language.md`     | **A+++ Resume Quality**       | Domain-specific vocabulary     |
| `quality_gates.md`      | Self-checks + self-correction | Gate report (PASS/FAIL)        |
| `style_guide.md`        | Reference for resume styles   | Style configuration            |
| `mock_interview.md`     | Practice interview responses  | Feedback & coaching            |
| `salary_negotiation.md` | Negotiate offers              | Negotiation playbook           |
| `linkedin_optimizer.md` | Optimize LinkedIn profile     | Profile content                |
| `gap_filler.md`         | Fill experience gaps          | Updated `master_experience.md` |

### Configuration

Set your preferences in `source_materials/identity.json`:

```json
"preferences": {
  "language": "en",              // en, de, es, fr, pt, etc.
  "resume_style": "traditional", // modern_builder, traditional, academic, creative
  "tone": "professional"         // professional, conversational, formal
}
```

---

## A+++ Resume Quality System

The pipeline is optimized to produce resumes that pass every screening stage.

### Power Language Guide (`core/power_language.md`)

Provides domain-specific technical vocabulary for:

| Domain          | Key Elements                                                    |
| --------------- | --------------------------------------------------------------- |
| **Engineering** | Architecture patterns, P95 latency, distributed systems, DevOps |
| **Sales**       | ARR, MEDDIC, quota attainment, pipeline velocity                |
| **Marketing**   | CAC, MQLs, ABM, attribution models, ROAS                        |
| **Operations**  | Cycle time, Six Sigma, SLA compliance, process mapping          |
| **Finance**     | Variance analysis, forecast accuracy, SOX, EBITDA               |
| **HR**          | Time-to-hire, eNPS, retention rate, succession planning         |
| **PM**          | On-time delivery, RACI, sprint velocity, risk mitigation        |

### Quality Standards Enforced

1. **XYZ Bullet Formula**: "Accomplished [X] measured by [Y], by doing [Z]"
2. **Metrics in every bullet**: No exceptions
3. **Power verbs only**: Banned words list (Helped, Assisted, Worked on, Participated)
4. **ATS keyword optimization**: 3-tier extraction (Primary/Secondary/Tertiary)
5. **Technical precision**: Domain-specific vocabulary required
6. **Front-loaded impact**: Results first, methods second

### Example Transformations

| ❌ Before                   | ✅ After                                                                                         |
| --------------------------- | ------------------------------------------------------------------------------------------------ |
| Built microservices         | Architected event-driven microservices handling 2M daily transactions with 99.97% uptime         |
| Managed marketing campaigns | Generated $2.4M in attributable pipeline at $38 CAC via integrated ABM across 6sense and Marketo |
| Led sales team              | Directed team of 8 AEs to $12M ARR (118% of target), ranking #1 globally                         |

---

## Workflow Diagram

### Setup Phase (One-Time)

```
+--------------+     +--------------+     +--------------+
|   Resumes    | --> |   Projects   | --> |  setup.md    |
|  resumes/    |     |  projects/   |     |              |
+--------------+     +--------------+     +------+-------+
                                                 |
                                                 v
                                         +---------------+
                                         |   master_     |
                                         | experience.md |
                                         +---------------+
```

### Application Phase (Per Job)

```
+--------------+     +--------------+     +--------------+
|   Job Desc   | --> | analyser.md  | --> | Match Report |
|  (Paste it!) |     |              |     |   (Review)   |
+--------------+     +--------------+     +------+-------+
                                                 |
                     +---------------------------+---------------------------+
                     |                           |                           |
                     v                           v                           v
              +--------------+           +--------------+           +--------------+
              | gap_filler   |           | tailor_resume|           | cover_letter |
              | (if needed)  |           |     .md      |           |     .md      |
              +--------------+           +------+-------+           +------+-------+
                                                |                          |
                                                +------------+-------------+
                                                             |
                                                             v
                                                     +--------------+
                                                     | pdf_generator|
                                                     |     .md      |
                                                     +------+-------+
                                                            |
                                                            v
                                                     +--------------+
                                                     |    OUTPUT    |
                                                     |  resume.pdf  |
                                                     |  cover.pdf   |
                                                     +--------------+
```

## Prompt Descriptions

### 🎯 main_orchestrator.md

**The Master Controller** - Orchestrates the entire pipeline from job description to final PDF. Use this when you want the AI to run the complete workflow automatically.

**Usage**: Provide a job description and say "Run the main orchestrator"

### 📊 setup.md

**Experience Extraction** - Analyzes your existing resumes and creates a comprehensive `master_experience.md` file. Run this once at the start, then update periodically.

**Usage**: "Analyze my resumes in source_materials/resumes/ and create master_experience.md"

### 🔍 analyser.md

**Gap Analysis** - Compares your experience against job requirements. Outputs a Strategic Match Report with scores and recommendations.

**Usage**: "Analyze the gap between my experience and this job description"

### ✍️ tailor_resume.md

**Resume Generation** - Creates a targeted resume respecting your style preferences. Every bullet includes metrics. Saves to `applications/[folder]/resume.md`.

**Usage**: "Create a tailored resume for this position"

### 💌 cover_letter.md

**Cover Letter Generation** - Creates a compelling cover letter that complements (not duplicates) your resume. Saves to `applications/[folder]/cover_letter.md`.

**Usage**: "Write a cover letter for this application"

### 📝 application_questions.md

**Extra Questions** - Handles both narrative questions (using SAR framework) and logistics questions (from identity.json).

**Usage**: "Answer these application questions: [paste questions]"

### 🎤 interview_prep.md

**Interview Coaching** - Generates technical, behavioral, and role-specific questions with model answers. Includes mock interview mode. Saves to `applications/[folder]/interview_prep.md`.

**Usage**: "Help me prepare for the interview at [Company]"

### 🔧 gap_filler.md

**Experience Updates** - Converts informal experience descriptions into structured entries. Asks clarifying questions to extract metrics, then updates `source_materials/master_experience.md`.

**Usage**: "I have this experience that's not in my master file: [describe]"

### 📄 pdf_generator.md

**Build Preparation** - Validates and sanitizes Markdown for PDF generation. Checks contact info against identity.json.

**Usage**: "Prepare resume.md for PDF generation"

### 🔗 linkedin_optimizer.md

**LinkedIn Optimization** - Generates optimized headline, about section, and experience bullets for LinkedIn profile.

**Usage**: "Optimize my LinkedIn profile for [target role]"

### 📧 follow_up.md

**Professional Communications** - Generates follow-up emails, thank you notes, rejection responses, and networking outreach.

**Usage**: "Write a thank you email after my interview with [Company]"

### 🎨 style_guide.md

**Style Configuration** - Defines resume styles (modern_builder, traditional, academic, creative) and language localization.

**Usage**: Referenced by other prompts based on `identity.json -> preferences.resume_style`

### 💡 manifesto_logic.md

**Philosophy Guide** - Defines the "Modern Builder" language transformations. Referenced when `resume_style = "modern_builder"`.

### 🏗️ career_architect.md

**Core Directives** - Establishes fundamental rules like SAR framework and no-hallucination policy.

## Best Practices

1. **Start with setup.md** to build your experience lake
2. **Keep identity.json updated** with current contact info
3. **Run analyser.md first** before generating documents
4. **Review AI output** - verify all metrics and claims
5. **Use gap_filler.md** when analysis finds missing experience

## Customization

To add new prompts:

1. Create a new `.md` file in this directory
2. Follow the structure:

   ```markdown
   # Role: [Role Name]

   ## Objective

   [Clear goal]

   ## Inputs

   [What files/data are needed]

   ## Instructions

   [Step-by-step process]

   ## Output Format

   [Expected structure]
   ```

3. Update this README with the new prompt
