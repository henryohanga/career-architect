# Role: Resume Style Configurator

## Purpose

This prompt defines different resume styles. The AI should read `identity.json -> preferences.resume_style` and apply the corresponding style guide.

## Available Styles

---

### Style: `modern_builder`

**Best for**: Tech startups, AI companies, senior engineering roles

**Philosophy**: Emphasize systems thinking, ownership, and measurable impact.

**Section Names** (English):

- Summary → "Summary" or "Profile"
- Capabilities → "Modern Builder Capabilities"
- Experience → "Experience"
- Skills → "Technical Skills"

**Language Patterns**:

- "Locked architectural intent for X"
- "Constrained entropy in Y"
- "Improved decision throughput by Z%"
- "Steered AI exploration to achieve..."
- "Delivered system durability through..."

**Required Elements**:

- Every bullet MUST have a metric
- Include "Modern Builder Capabilities" section
- SAR format (Situation-Action-Result)

---

### Style: `traditional`

**Best for**: Enterprise companies, government, consulting, finance

**Philosophy**: Clear, professional, qualification-focused.

**Section Names**:

- Professional Summary
- Work Experience
- Education
- Skills

**Language Patterns**:

- "Led team of X to deliver Y"
- "Managed project with $X budget"
- "Increased revenue/efficiency by X%"
- "Collaborated with stakeholders to..."
- "Implemented solution resulting in..."

**Required Elements**:

- Reverse chronological order
- Formal tone
- Clear job titles and dates

---

### Style: `academic`

**Best for**: Research roles, universities, think tanks, R&D positions

**Philosophy**: Emphasize research, publications, and methodological rigor.

**Section Names**:

- Research Interests
- Education
- Publications
- Research Experience
- Teaching Experience
- Grants & Awards

**Language Patterns**:

- "Conducted research on..."
- "Published findings in..."
- "Developed novel methodology for..."
- "Supervised X graduate students"

**Required Elements**:

- Publications list with citations
- Research focus areas
- Academic appointments

---

### Style: `creative`

**Best for**: Design, marketing, product roles, agencies

**Philosophy**: Show personality while demonstrating competence.

**Section Names**:

- About Me
- What I Do
- Experience
- Projects
- Skills & Tools

**Language Patterns**:

- Storytelling approach
- First person acceptable
- Show personality
- Visual/portfolio references

**Required Elements**:

- Portfolio links
- Project highlights with visuals
- Brand voice consistency

---

## Language Localization

When `preferences.language` is not "en", adapt:

| English    | German (de)     | Spanish (es) | French (fr) | Portuguese (pt) |
| ---------- | --------------- | ------------ | ----------- | --------------- |
| Summary    | Zusammenfassung | Resumen      | Résumé      | Resumo          |
| Experience | Berufserfahrung | Experiencia  | Expérience  | Experiência     |
| Education  | Ausbildung      | Educación    | Formation   | Formação        |
| Skills     | Kenntnisse      | Habilidades  | Compétences | Competências    |

## Implementation

The AI should:

1. Read `identity.json -> preferences.resume_style`
2. Apply the corresponding style guide above
3. Read `identity.json -> preferences.language`
4. Translate section headers if not English
5. Maintain consistent tone throughout all documents
