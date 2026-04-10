"""
PDF Service — Dynamic extraction and indexing of legal PDF content.

Parses the three legal PDFs at startup:
  - Companies Act, 2013 (370 pages, ~470 sections)
  - Companies Rules, 2014 (195 pages)
  - Corporate Laws (Amendment) Act, 2026 (98 pages)

Provides lookup functions so the AI can pull full legal text on-demand
for any section/rule, even those not in the hardcoded sample_data.py.
"""

import re
import os
import sys
from pathlib import Path
from functools import lru_cache

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# ============================================================
# STATE
# ============================================================
_initialized = False

# Indexed content
_act_sections: dict[int, dict] = {}       # section_number → {number, title, text, page}
_act_full_text: str = ""                   # full raw text of the Act
_rules_text: str = ""                      # full raw text of the Rules
_amendment_text: str = ""                  # full raw text of the Amendment Act
_amendment_clauses: list[dict] = []        # parsed amendment clauses
_rules_entries: list[dict] = []            # parsed rule entries

# PDF file paths (relative to project root)
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_PDF_FILES = {
    "act": _PROJECT_ROOT / "Companies Act, 2013.pdf",
    "rules": _PROJECT_ROOT / "Companies Rules, 2014.pdf",
    "amendment": _PROJECT_ROOT / "Corporate Laws (Amendment) Act, 2026 - converted.pdf",
}


# ============================================================
# INITIALIZATION
# ============================================================
def init_pdf_service() -> bool:
    """Parse all PDFs and build the search index. Call once at startup."""
    global _initialized

    if pdfplumber is None:
        print("[WARN] pdfplumber not installed -- PDF features disabled")
        sys.stdout.flush()
        return False

    missing = [name for name, path in _PDF_FILES.items() if not path.exists()]
    if missing:
        print(f"[WARN] Missing PDF files: {', '.join(missing)} -- PDF features partially available")
        sys.stdout.flush()

    success = True
    try:
        if _PDF_FILES["act"].exists():
            _parse_act_pdf()
        else:
            success = False

        if _PDF_FILES["rules"].exists():
            _parse_rules_pdf()

        if _PDF_FILES["amendment"].exists():
            _parse_amendment_pdf()

        _initialized = True
        print(
            f"[PDF] PDF service ready: "
            f"{len(_act_sections)} act sections, "
            f"{len(_rules_entries)} rules entries, "
            f"{len(_amendment_clauses)} amendment clauses"
        )
        sys.stdout.flush()
        return success

    except Exception as e:
        print(f"[ERROR] PDF service init error: {e}")
        sys.stdout.flush()
        _initialized = True  # Mark initialized even on partial failure
        return False


def is_ready() -> bool:
    return _initialized


# ============================================================
# PDF PARSING — Companies Act, 2013
# ============================================================
def _parse_act_pdf():
    """Extract and index sections from the Companies Act PDF."""
    global _act_full_text, _act_sections

    print("  [PDF] Parsing Companies Act, 2013...")
    sys.stdout.flush()
    pdf_path = _PDF_FILES["act"]

    pages_text = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

    _act_full_text = "\n\n".join(pages_text)

    # Index sections using regex patterns
    # Pattern: section number followed by title followed by content
    # The Act uses patterns like:
    #   "1. Short title, extent, commencement and application.—(1) This Act may be..."
    #   "149. Company to have Board of Directors.—(1) Every company shall..."
    section_pattern = re.compile(
        r'(?:^|\n)'                                    # start or newline
        r'(\d{1,3}[A-Z]?)\.\s+'                       # section number (e.g., "1.", "3A.", "149.")
        r'([A-Z][^.—\n]{5,120})'                      # title (starts with capital, 5-120 chars)
        r'[.—]+'                                       # separator (period, em-dash)
        r'(.*?)(?=\n\d{1,3}[A-Z]?\.\s+[A-Z]|\Z)',     # body text until next section or end
        re.DOTALL
    )

    for match in section_pattern.finditer(_act_full_text):
        raw_num = match.group(1).strip()
        title = match.group(2).strip().rstrip(".")
        body = match.group(3).strip()

        # Extract integer section number (skip lettered sections like 3A for now)
        try:
            num = int(raw_num)
        except ValueError:
            # Handle sections like "3A" — store with base number
            base = int(re.match(r'(\d+)', raw_num).group(1))
            _act_sections.setdefault(base, {
                "number": base,
                "title": title,
                "text": body[:3000],  # Cap at 3000 chars per section
                "source": "pdf",
                "pdf_file": "Companies Act, 2013",
                "raw_section_id": raw_num,
            })
            continue

        # Clean up body text
        body = re.sub(r'\s+', ' ', body).strip()
        if len(body) > 5000:
            body = body[:5000]  # Cap very long sections

        _act_sections[num] = {
            "number": num,
            "title": title,
            "text": body,
            "source": "pdf",
            "pdf_file": "Companies Act, 2013",
            "raw_section_id": raw_num,
        }

    print(f"    -> Indexed {len(_act_sections)} sections from Act PDF")
    sys.stdout.flush()


# ============================================================
# PDF PARSING — Companies Rules, 2014
# ============================================================
def _parse_rules_pdf():
    """Extract text from the Companies Rules PDF."""
    global _rules_text, _rules_entries

    print("  [PDF] Parsing Companies Rules, 2014...")
    sys.stdout.flush()
    pdf_path = _PDF_FILES["rules"]

    pages_text = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Filter out Hindi/non-English content
                # Keep lines that have >50% ASCII characters
                lines = text.split('\n')
                english_lines = []
                for line in lines:
                    if not line.strip():
                        continue
                    ascii_count = sum(1 for c in line if ord(c) < 128)
                    if len(line) > 0 and (ascii_count / len(line)) > 0.6:
                        english_lines.append(line)
                if english_lines:
                    pages_text.append('\n'.join(english_lines))

    _rules_text = "\n\n".join(pages_text)

    # Parse individual rules
    # Pattern: "Rule X." or numbered rules like "3. ..." within rule context
    rule_pattern = re.compile(
        r'(?:Rule|RULE)\s+(\d+[A-Za-z]?)\b[.:\-—]?\s*(.*?)(?=(?:Rule|RULE)\s+\d+|\Z)',
        re.DOTALL | re.IGNORECASE
    )

    for match in rule_pattern.finditer(_rules_text):
        rule_num = match.group(1).strip()
        rule_body = match.group(2).strip()
        rule_body = re.sub(r'\s+', ' ', rule_body)

        if len(rule_body) > 50:  # Skip very short/empty matches
            _rules_entries.append({
                "number": rule_num,
                "text": rule_body[:3000],
                "source": "pdf",
                "pdf_file": "Companies Rules, 2014",
            })

    print(f"    -> Extracted {len(_rules_entries)} rule entries from Rules PDF")
    sys.stdout.flush()


# ============================================================
# PDF PARSING — Corporate Laws (Amendment) Act, 2026
# ============================================================
def _parse_amendment_pdf():
    """Extract text from the Amendment Act PDF."""
    global _amendment_text, _amendment_clauses

    print("  [PDF] Parsing Corporate Laws (Amendment) Act, 2026...")
    sys.stdout.flush()
    pdf_path = _PDF_FILES["amendment"]

    pages_text = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

    _amendment_text = "\n\n".join(pages_text)

    # Parse amendment clauses
    # Pattern: "X. In section Y of the principal Act..." or "X. Section Y..."
    clause_pattern = re.compile(
        r'(\d+)\.\s+'                                          # clause number
        r'(?:In\s+)?[Ss]ection\s+(\d+[A-Z]?)\s+'             # target section
        r'(?:of\s+the\s+(?:principal\s+)?Act[,.]?\s*)?'        # optional "of the principal Act"
        r'(.*?)(?=\n\d+\.\s+(?:In\s+)?[Ss]ection|\Z)',        # body until next clause
        re.DOTALL
    )

    for match in clause_pattern.finditer(_amendment_text):
        clause_num = match.group(1).strip()
        target_section = match.group(2).strip()
        body = match.group(3).strip()
        body = re.sub(r'\s+', ' ', body)

        if len(body) > 30:
            _amendment_clauses.append({
                "clause": clause_num,
                "targetSection": target_section,
                "text": body[:3000],
                "source": "pdf",
                "pdf_file": "Corporate Laws (Amendment) Act, 2026",
            })

    print(f"    -> Extracted {len(_amendment_clauses)} amendment clauses")
    sys.stdout.flush()


# ============================================================
# LOOKUP FUNCTIONS
# ============================================================

def get_section_from_pdf(number: int) -> dict | None:
    """Get a specific section's full text from the Act PDF."""
    if not _initialized:
        return None
    section = _act_sections.get(number)
    if section:
        return {
            "number": section["number"],
            "title": section["title"],
            "text": section["text"],
            "effectiveText": section["text"],
            "isAmended": False,
            "source": "pdf",
            "partNumber": "",
            "partTitle": "",
        }
    return None


def get_amendments_for_section_from_pdf(section_number: int) -> list[dict]:
    """Get amendment clauses targeting a specific section from the Amendment PDF."""
    target = str(section_number)
    return [
        c for c in _amendment_clauses
        if c["targetSection"] == target
    ]


def search_pdf_content(query: str, max_results: int = 5) -> list[dict]:
    """
    Search across all PDF content for relevant text.
    Returns a list of relevant chunks with source info.
    """
    if not _initialized:
        return []

    results = []
    query_lower = query.lower()

    # Extract keywords (remove stop words)
    stop_words = {
        "what", "is", "are", "the", "a", "an", "in", "of", "to", "for",
        "and", "or", "by", "on", "at", "from", "with", "about", "how",
        "which", "that", "this", "it", "its", "has", "have", "had",
        "do", "does", "did", "can", "could", "will", "would", "shall",
        "should", "may", "might", "be", "been", "being", "was", "were",
        "tell", "me", "show", "please", "explain", "describe", "give",
    }
    keywords = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]

    if not keywords:
        return []

    # Search Act sections
    scored = []
    for num, section in _act_sections.items():
        score = 0
        title_lower = section["title"].lower()
        text_lower = section["text"].lower()

        for kw in keywords:
            if kw in title_lower:
                score += 5
            if kw in text_lower:
                score += 1
                # Bonus for multiple keyword matches
                score += text_lower.count(kw) * 0.5

        if score > 0:
            scored.append((score, {
                "type": "section",
                "number": num,
                "title": section["title"],
                "text": section["text"][:1500],
                "source": "pdf",
                "pdf_file": section["pdf_file"],
                "relevance": round(score, 1),
            }))

    # Search Rules
    for rule in _rules_entries:
        score = 0
        text_lower = rule["text"].lower()
        for kw in keywords:
            if kw in text_lower:
                score += 1
                score += text_lower.count(kw) * 0.3
        if score > 0:
            scored.append((score, {
                "type": "rule",
                "number": rule["number"],
                "title": f"Rule {rule['number']}",
                "text": rule["text"][:1500],
                "source": "pdf",
                "pdf_file": rule["pdf_file"],
                "relevance": round(score, 1),
            }))

    # Search Amendment clauses
    for clause in _amendment_clauses:
        score = 0
        text_lower = clause["text"].lower()
        for kw in keywords:
            if kw in text_lower:
                score += 1.5
                score += text_lower.count(kw) * 0.3
        if score > 0:
            scored.append((score, {
                "type": "amendment",
                "clause": clause["clause"],
                "targetSection": clause["targetSection"],
                "title": f"Amendment to Section {clause['targetSection']}",
                "text": clause["text"][:1500],
                "source": "pdf",
                "pdf_file": clause["pdf_file"],
                "relevance": round(score, 1),
            }))

    # Sort by relevance and return top results
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [item for _, item in scored[:max_results]]
    return results


def get_pdf_context_for_query(question: str, max_chars: int = 4000) -> str:
    """
    Build a context string from PDF content relevant to the user's question.
    This is designed to be injected into the AI prompt for grounding.
    """
    if not _initialized:
        return ""

    context_parts = []
    q_lower = question.lower()

    # Check for specific section reference
    section_match = re.search(r'section\s+(\d+)', q_lower)
    if section_match:
        num = int(section_match.group(1))
        section = _act_sections.get(num)
        if section:
            context_parts.append(
                f"[From Companies Act, 2013 — Section {num}: {section['title']}]\n"
                f"{section['text'][:2000]}"
            )
            # Also check amendments for this section
            amendments = get_amendments_for_section_from_pdf(num)
            for am in amendments[:2]:
                context_parts.append(
                    f"[From Corporate Laws (Amendment) Act, 2026 — Clause {am['clause']} amending Section {am['targetSection']}]\n"
                    f"{am['text'][:800]}"
                )

    # If no specific section, do a keyword search
    if not context_parts:
        results = search_pdf_content(question, max_results=3)
        for r in results:
            header = f"[From {r['pdf_file']}"
            if r.get("number"):
                header += f" — {r['title']}"
            header += "]"
            context_parts.append(f"{header}\n{r['text'][:1200]}")

    if not context_parts:
        return ""

    # Assemble and cap total length
    context = "\n\n---\n\n".join(context_parts)
    if len(context) > max_chars:
        context = context[:max_chars] + "\n...[truncated]"

    return context


def get_all_indexed_section_numbers() -> list[int]:
    """Return all section numbers that were successfully indexed from the PDF."""
    return sorted(_act_sections.keys())


def get_pdf_stats() -> dict:
    """Return stats about the PDF extraction."""
    return {
        "initialized": _initialized,
        "act_sections_indexed": len(_act_sections),
        "rules_entries": len(_rules_entries),
        "amendment_clauses": len(_amendment_clauses),
        "act_text_chars": len(_act_full_text),
        "rules_text_chars": len(_rules_text),
        "amendment_text_chars": len(_amendment_text),
        "pdf_files_found": {
            name: path.exists()
            for name, path in _PDF_FILES.items()
        },
    }
