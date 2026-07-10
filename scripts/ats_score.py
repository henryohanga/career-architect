#!/usr/bin/env python3
"""ATS (Applicant Tracking System) Keyword Scoring Tool.

Analyzes resume against job description to calculate keyword match score
and identify missing keywords for ATS optimization.

Matching pipeline: markdown-stripped tokenization (slash-aware, so "ci/cd"
survives), unigram + 2/3-gram phrase extraction, alias canonicalization
(k8s -> kubernetes, ml -> machine learning), light suffix stemming for
non-technical words, and weighting that favors technical keywords and
terms from the JD title/requirements sections.

Usage:
    python scripts/ats_score.py <job_desc.md> <resume.md>
    python scripts/ats_score.py applications/2025-01-01-company-role/

Thresholds (single source of truth for the whole repo):
    >= ATS_THRESHOLD_STRONG  (70) - strong match, ready to submit
    >= ATS_THRESHOLD_MINIMUM (50) - acceptable; below this the exit code is 1
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Single source of truth for ATS score gates. Referenced by quality_gates.md,
# README.md, the /career:* skills, and CI workflows - update those docs if
# these change.
ATS_THRESHOLD_STRONG = 70
ATS_THRESHOLD_MINIMUM = 50


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# Common stop words to exclude from analysis
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can", "need",
    "we", "you", "your", "our", "their", "this", "that", "these", "those",
    "it", "its", "they", "them", "he", "she", "his", "her", "who", "which",
    "what", "when", "where", "why", "how", "all", "each", "every", "both",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "just", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "over", "out", "up", "down", "off", "again",
    "further", "then", "once", "here", "there", "any", "also", "well",
    "work", "working", "worked", "experience", "years", "year", "team",
    "including", "using", "used", "use", "new", "help", "strong", "able",
    # JD boilerplate section words - not skills
    "requirements", "requirement", "qualifications", "qualification",
    "responsibilities", "responsibility", "preferred", "bonus", "benefits",
    "candidate", "candidates", "ideal", "looking", "seeking", "join",
}

# Technical keywords with higher weight. Multi-word entries are matched via
# n-gram extraction; short entries (go, r, ml, ai) bypass the length filter.
TECH_KEYWORDS = {
    # Languages
    "python", "javascript", "typescript", "java", "go", "rust", "c++",
    "c#", "ruby", "php", "swift", "kotlin", "scala", "r", "sql",
    # Frontend
    "react", "vue", "angular", "svelte", "next.js", "nuxt", "html", "css",
    "sass", "tailwind", "webpack", "vite",
    # Backend
    "node.js", "express", "fastapi", "django", "flask", "rails", "spring",
    "graphql", "rest", "api", "microservices", "grpc",
    # Data
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
    "rabbitmq", "dynamodb", "cassandra", "snowflake", "spark",
    # Cloud/DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins",
    "github", "gitlab", "ci/cd", "ansible", "prometheus", "grafana",
    # AI/ML
    "machine learning", "deep learning", "ml", "ai", "llm", "nlp",
    "tensorflow", "pytorch", "openai", "langchain", "embeddings", "rag",
}

# Alias map: canonical term -> variants. A JD term matches if the resume
# contains the term or any of its variants (and vice versa).
ALIASES = {
    "machine learning": {"ml"},
    "artificial intelligence": {"ai"},
    "deep learning": {"dl"},
    "natural language processing": {"nlp"},
    "kubernetes": {"k8s"},
    "go": {"golang"},
    "javascript": {"js"},
    "typescript": {"ts"},
    "python": {"py"},
    "postgresql": {"postgres", "psql"},
    "ci/cd": {"cicd", "ci-cd", "continuous integration", "continuous delivery",
              "continuous deployment"},
    "next.js": {"nextjs"},
    "node.js": {"nodejs", "node"},
    "c#": {"csharp"},
    "aws": {"amazon web services"},
    "gcp": {"google cloud platform", "google cloud"},
    "iac": {"infrastructure as code"},
    "tdd": {"test-driven development", "test driven development"},
    "oop": {"object-oriented", "object oriented"},
    "ux": {"user experience"},
    "ui": {"user interface"},
    "sre": {"site reliability engineering"},
    "llm": {"large language model", "large language models", "llms"},
    "rag": {"retrieval-augmented generation", "retrieval augmented generation"},
}

# variant -> canonical lookup (canonical maps to itself)
ALIAS_LOOKUP = {}
for _canon, _variants in ALIASES.items():
    ALIAS_LOOKUP[_canon] = _canon
    for _v in _variants:
        ALIAS_LOOKUP[_v] = _canon

# Curated multi-word phrases always extracted when present (in addition to
# data-driven n-grams and multi-word TECH_KEYWORDS/aliases).
CURATED_PHRASES = {
    "full stack", "front end", "back end", "data science", "data engineering",
    "software engineer", "software engineering", "distributed systems",
    "system design", "event-driven", "real-time", "open source",
    "cross-functional", "stakeholder management", "project management",
    "agile", "scrum", "unit testing", "code review", "technical leadership",
}

# Words the light stemmer must not touch (would produce wrong stems).
STEM_GUARD = {
    "less", "class", "css", "kubernetes", "series", "species", "analysis",
    "redis", "sales", "media", "data", "as", "its", "ios", "macos", "aws",
    "devops", "sass", "rails", "express", "postgres",
}

_TOKEN_RE = re.compile(r"[a-z][a-z0-9+#./-]*")


def _stem(word: str) -> str:
    """Light suffix stripping for non-technical words (no external deps)."""
    if word in STEM_GUARD or word in TECH_KEYWORDS or word in ALIAS_LOOKUP:
        return word
    for suffix, replacement in (
        ("ies", "y"), ("sses", "ss"), ("ing", ""), ("ed", ""), ("es", ""), ("s", ""),
    ):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)] + replacement
    return word


def _canonical(term: str) -> str:
    """Map a term to its canonical form via the alias table, then stem."""
    term = ALIAS_LOOKUP.get(term, term)
    if " " not in term and "/" not in term:
        term = _stem(term)
        term = ALIAS_LOOKUP.get(term, term)
    return term


def _clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)  # frontmatter
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[#*_`\[\](){}|>~,;:!?\"']", " ", text)
    return text


def _tokenize(text: str) -> list:
    """Tokenize cleaned text; keeps c++, c#, next.js, ci/cd as single tokens."""
    tokens = []
    for tok in _TOKEN_RE.findall(text):
        tok = tok.strip(".-/")
        if tok:
            tokens.append(tok)
    return tokens


def extract_terms(text: str, surfaces: dict | None = None) -> Counter:
    """Extract canonical unigram and phrase terms with counts.

    Unigrams: kept if technical/aliased (any length) or a non-stopword of
    length > 2. Phrases (2-3 grams of non-stopwords): kept if technical,
    aliased, or curated; generic bigrams are kept when they repeat, since a
    phrase used twice in a JD is signal rather than prose.

    If `surfaces` is given, it is filled with canonical -> original surface
    form for readable reports (e.g. "pipelin" -> "pipelines").
    """
    if surfaces is None:
        surfaces = {}
    tokens = _tokenize(_clean_text(text))
    terms = Counter()

    def _add(canon, surface):
        terms[canon] += 1
        surfaces.setdefault(canon, surface)
        # An alias hit on a multi-word canonical (e.g. "ml" -> "machine
        # learning") also credits the component words so unigram counts on
        # the other side still match.
        if " " in canon:
            for part in canon.split():
                if part not in STOP_WORDS and len(part) > 2:
                    part_canon = _canonical(part)
                    terms[part_canon] += 1
                    surfaces.setdefault(part_canon, part)

    for tok in tokens:
        if tok in ALIAS_LOOKUP or tok in TECH_KEYWORDS:
            _add(_canonical(tok), tok)
        elif tok not in STOP_WORDS and len(tok) > 2:
            _add(_canonical(tok), tok)

    generic_bigrams = Counter()
    for n in (2, 3):
        for i in range(len(tokens) - n + 1):
            gram_tokens = tokens[i:i + n]
            if any(t in STOP_WORDS or len(t) < 2 for t in gram_tokens):
                continue
            gram = " ".join(gram_tokens)
            canon = _canonical(gram)
            if (
                canon in TECH_KEYWORDS
                or gram in ALIAS_LOOKUP
                or canon in CURATED_PHRASES
                or gram in CURATED_PHRASES
            ):
                _add(canon, gram)
            elif n == 2:
                generic_bigrams[gram] += 1

    for gram, count in generic_bigrams.items():
        if count >= 2:
            canon = _canonical(gram)
            terms[canon] += count
            surfaces.setdefault(canon, gram)

    return terms


def extract_priority_terms(jd_text: str) -> set:
    """Terms from the JD title/first heading and requirements-type sections."""
    priority_chunks = []

    fm_match = re.match(r"^---\n(.*?)\n---\n", jd_text, flags=re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if line.split(":", 1)[0].strip() in {"role", "title", "company"}:
                priority_chunks.append(line.split(":", 1)[1])

    body = re.sub(r"^---\n.*?\n---\n", "", jd_text, flags=re.DOTALL)
    heading_re = re.compile(r"^#{1,4}\s+(.+)$")
    section_re = re.compile(r"require|qualif|must[- ]have|skills|what you", re.I)
    in_priority = False
    first_heading_seen = False
    for line in body.splitlines():
        m = heading_re.match(line)
        if m:
            if not first_heading_seen:
                priority_chunks.append(m.group(1))
                first_heading_seen = True
            in_priority = bool(section_re.search(m.group(1)))
            continue
        if in_priority:
            priority_chunks.append(line)

    return set(extract_terms("\n".join(priority_chunks)).keys())


def _term_weight(term: str, jd_terms: Counter, priority_terms: set) -> int:
    weight = 2 if term in TECH_KEYWORDS else 1
    if term in priority_terms:
        weight *= 2
    weight *= min(jd_terms[term], 3)  # cap so repetition doesn't dominate
    return weight


def calculate_score(
    jd_terms: Counter,
    resume_terms: Counter,
    priority_terms: set | None = None,
    surfaces: dict | None = None,
) -> dict:
    """Calculate ATS match score. `surfaces` maps canonical terms back to a
    readable form (from the JD) for report display."""
    if priority_terms is None:
        priority_terms = set()
    if surfaces is None:
        surfaces = {}

    jd_unique = set(jd_terms.keys())
    resume_unique = set(resume_terms.keys())

    matched = jd_unique & resume_unique
    missing = jd_unique - resume_unique

    total_weight = 0
    matched_weight = 0
    for term in jd_unique:
        weight = _term_weight(term, jd_terms, priority_terms)
        total_weight += weight
        if term in matched:
            matched_weight += weight

    score = (matched_weight / total_weight * 100) if total_weight > 0 else 0

    missing_ranked = [
        (
            surfaces.get(term, term),
            _term_weight(term, jd_terms, priority_terms),
            jd_terms[term],
        )
        for term in missing
    ]
    missing_ranked.sort(key=lambda x: (-x[1], x[0]))

    return {
        "score": round(score, 1),
        "matched": len(matched),
        "total_jd": len(jd_unique),
        "missing": missing_ranked[:20],
        "matched_keywords": sorted(surfaces.get(t, t) for t in matched),
        "threshold_strong": ATS_THRESHOLD_STRONG,
        "threshold_minimum": ATS_THRESHOLD_MINIMUM,
        "pass": score >= ATS_THRESHOLD_MINIMUM,
    }


def score_texts(jd_text: str, resume_text: str) -> dict:
    """Score a resume against a JD (both as raw markdown text)."""
    surfaces = {}
    jd_terms = extract_terms(jd_text, surfaces)
    resume_terms = extract_terms(resume_text)
    priority_terms = extract_priority_terms(jd_text)
    return calculate_score(jd_terms, resume_terms, priority_terms, surfaces)


def print_report(result: dict, jd_path: str, resume_path: str):
    """Print the ATS score report."""
    score = result["score"]

    if score >= ATS_THRESHOLD_STRONG:
        score_color = Colors.GREEN
        verdict = "Strong Match"
    elif score >= ATS_THRESHOLD_MINIMUM:
        score_color = Colors.YELLOW
        verdict = "Moderate Match"
    else:
        score_color = Colors.RED
        verdict = "Needs Improvement"

    print(f"\n{Colors.BOLD}ATS Keyword Analysis{Colors.RESET}")
    print("=" * 50)
    print(f"Job Description: {jd_path}")
    print(f"Resume: {resume_path}")
    print()

    print(f"{Colors.BOLD}Match Score:{Colors.RESET} ", end="")
    print(f"{score_color}{score}%{Colors.RESET} - {verdict}")
    print(f"Keywords Matched: {result['matched']}/{result['total_jd']}")
    print(
        f"Targets: >={ATS_THRESHOLD_STRONG}% strong, "
        f">={ATS_THRESHOLD_MINIMUM}% minimum"
    )
    print()

    if result["missing"]:
        print(f"{Colors.BOLD}Top Missing Keywords:{Colors.RESET}")
        print(f"{Colors.YELLOW}(Consider adding these to your resume){Colors.RESET}")
        print()
        for keyword, _weight, freq in result["missing"][:15]:
            indicator = "⚡" if keyword in TECH_KEYWORDS else "•"
            print(f"  {indicator} {keyword} (appears {freq}x in JD)")
        print()

    if result["matched_keywords"]:
        print(f"{Colors.BOLD}Matched Keywords:{Colors.RESET}")
        matched_display = ", ".join(result["matched_keywords"][:30])
        if len(result["matched_keywords"]) > 30:
            matched_display += f" ... (+{len(result['matched_keywords']) - 30} more)"
        print(f"  {Colors.GREEN}{matched_display}{Colors.RESET}")
        print()

    print(f"{Colors.BOLD}Recommendations:{Colors.RESET}")
    if score < ATS_THRESHOLD_MINIMUM:
        print("  1. Add more technical keywords from the job description")
        print("  2. Mirror the exact terminology used in the JD")
        print("  3. Include specific tools and technologies mentioned")
    elif score < ATS_THRESHOLD_STRONG:
        print("  1. Good foundation - add a few more key terms")
        print("  2. Ensure skills section matches JD requirements")
    else:
        print("  ✓ Strong keyword match! Focus on tailoring bullet points.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="ATS Keyword Scoring - Analyze resume against job description"
    )
    parser.add_argument(
        "path",
        help="Path to application folder or job_desc.md file",
    )
    parser.add_argument(
        "resume",
        nargs="?",
        help="Path to resume.md (optional if path is a folder)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Print only the numeric score (for CI/scripting)",
    )

    args = parser.parse_args()

    path = Path(args.path)

    if path.is_dir():
        jd_path = path / "job_desc.md"
        resume_path = path / "resume.md"
    elif args.resume:
        jd_path = path
        resume_path = Path(args.resume)
    else:
        print(
            f"{Colors.RED}Error: Provide either a folder or both JD and resume paths{Colors.RESET}",
            file=sys.stderr,
        )
        return 1

    if not jd_path.exists():
        print(
            f"{Colors.RED}Error: Job description not found: {jd_path}{Colors.RESET}",
            file=sys.stderr,
        )
        return 1

    if not resume_path.exists():
        print(
            f"{Colors.RED}Error: Resume not found: {resume_path}{Colors.RESET}",
            file=sys.stderr,
        )
        return 1

    jd_text = jd_path.read_text(encoding="utf-8")
    resume_text = resume_path.read_text(encoding="utf-8")

    result = score_texts(jd_text, resume_text)

    if args.score_only:
        print(result["score"])
    elif args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result, str(jd_path), str(resume_path))

    return 0 if result["score"] >= ATS_THRESHOLD_MINIMUM else 1


if __name__ == "__main__":
    sys.exit(main())
