"""
In-Memory Store — Fallback data store when Neo4j is unavailable.
Provides the same query interface using in-memory Python data structures.
Falls back to PDF extraction for sections not in the hardcoded sample data.
"""
from app.data.sample_data import act_data, amendment_data, rules_data, cross_references

_sections = {}
_amendments = []
_rules = []
_cross_refs = []
_loaded = False


def load():
    """Load all data into memory."""
    global _sections, _amendments, _rules, _cross_refs, _loaded

    if _loaded:
        return

    # Load sections
    for part in act_data["parts"]:
        for section in part.get("sections", []):
            _sections[section["number"]] = {
                "number": section["number"],
                "title": section["title"],
                "text": section["text"],
                "effectiveText": section["text"],
                "isAmended": False,
                "partNumber": part["number"],
                "partTitle": part["title"],
                "subsections": section.get("subsections", []),
            }

    # Apply amendments
    for amend in amendment_data["amendments"]:
        target = amend["targetSection"]
        _amendments.append({
            "type": amend["type"],
            "description": amend["description"],
            "targetSection": target,
            "targetSubsection": amend.get("targetSubsection"),
            "year": amendment_data["year"],
            "originalText": amend.get("originalText", ""),
            "newText": amend.get("newText", ""),
            "sectionTitle": _sections.get(target, {}).get("title", ""),
            "relationship": {
                "substitution": "SUBSTITUTES",
                "insertion": "INSERTS",
                "deletion": "DELETES",
            }.get(amend["type"], "AMENDS"),
        })

        if target in _sections:
            _sections[target]["isAmended"] = True
            if amend["type"] == "substitution" and amend.get("newText"):
                _sections[target]["effectiveText"] = amend["newText"]
            elif amend["type"] == "insertion" and amend.get("newText"):
                _sections[target]["effectiveText"] += " " + amend["newText"]

    # Load rules
    for rule in rules_data["rules"]:
        _rules.append({
            "number": rule["number"],
            "title": rule["title"],
            "text": rule["text"],
            "category": rule["category"],
            "relatedSection": rule["relatedSection"],
            "sectionNumber": rule["relatedSection"],
            "sectionTitle": _sections.get(rule["relatedSection"], {}).get("title", ""),
            "year": rules_data["year"],
        })

    # Load cross-references
    _cross_refs = cross_references[:]

    _loaded = True
    print(f"📦 Memory store loaded: {len(_sections)} sections, {len(_amendments)} amendments, {len(_rules)} rules")


# ============================================================
# Query Functions
# ============================================================

def get_all_sections():
    return [
        {
            "number": s["number"],
            "title": s["title"],
            "isAmended": s["isAmended"],
            "partNumber": s["partNumber"],
            "partTitle": s["partTitle"],
        }
        for s in sorted(_sections.values(), key=lambda x: x["number"])
    ]


def get_section(number: int):
    s = _sections.get(number)
    if not s:
        # Fallback: try PDF service for sections not in hardcoded data
        try:
            from app.data.pdf_service import get_section_from_pdf
            pdf_section = get_section_from_pdf(number)
            if pdf_section:
                return {
                    "number": pdf_section["number"],
                    "title": pdf_section["title"],
                    "originalText": pdf_section["text"],
                    "effectiveText": pdf_section["text"],
                    "isAmended": False,
                    "partNumber": "",
                    "partTitle": "",
                    "subsections": [],
                    "source": "pdf",
                }
        except Exception:
            pass
        return None
    return {
        "number": s["number"],
        "title": s["title"],
        "originalText": s["text"],
        "effectiveText": s["effectiveText"],
        "isAmended": s["isAmended"],
        "partNumber": s["partNumber"],
        "partTitle": s["partTitle"],
        "subsections": s.get("subsections", []),
    }


def get_amendments_for_section(number: int):
    return [a for a in _amendments if a["targetSection"] == number]


def get_all_amendments():
    return _amendments[:]


def get_rules_for_section(number: int):
    return [r for r in _rules if r["relatedSection"] == number]


def get_all_rules():
    return _rules[:]


def get_acts():
    """Return Act-level information."""
    return [
        {
            "name": act_data["name"],
            "year": act_data["year"],
            "fullTitle": act_data["fullTitle"],
            "dateEnacted": act_data["dateEnacted"],
            "shortDescription": act_data["shortDescription"],
            "partCount": len(act_data["parts"]),
            "sectionCount": len(_sections),
        },
        {
            "name": amendment_data["name"],
            "year": amendment_data["year"],
            "fullTitle": amendment_data["fullTitle"],
            "dateEnacted": amendment_data["dateEnacted"],
            "shortDescription": amendment_data["shortDescription"],
            "amendmentCount": len(amendment_data["amendments"]),
        },
    ]


def get_parts():
    """Return all Parts with their section counts."""
    parts = []
    for part in act_data["parts"]:
        parts.append({
            "number": part["number"],
            "title": part["title"],
            "sectionCount": len(part.get("sections", [])),
            "sections": [
                {"number": s["number"], "title": s["title"]}
                for s in part.get("sections", [])
            ],
        })
    return parts


def get_sections_by_topic(topic: str):
    """Search for sections relevant to a topic using keyword matching."""
    topic_lower = topic.lower()
    # Extract meaningful keywords (remove stop words)
    stop_words = {
        "what", "is", "are", "the", "a", "an", "in", "of", "to", "for",
        "and", "or", "by", "on", "at", "from", "with", "about", "how",
        "which", "that", "this", "it", "its", "has", "have", "had",
        "do", "does", "did", "can", "could", "will", "would", "shall",
        "should", "may", "might", "be", "been", "being", "was", "were",
        "hi", "hello", "hey", "tell", "me", "show", "please", "give",
        "explain", "describe", "list", "find", "get", "all", "any",
        "related", "regarding", "under", "per", "as", "so", "if",
    }
    keywords = [w for w in topic_lower.split() if w not in stop_words and len(w) > 1]

    if not keywords:
        return []

    scored_sections = []
    for s in _sections.values():
        score = 0
        title_lower = s["title"].lower()
        text_lower = s["effectiveText"].lower()
        part_lower = s["partTitle"].lower()

        for kw in keywords:
            if kw in title_lower:
                score += 3  # Title match is strong
            if kw in part_lower:
                score += 2  # Part title match
            if kw in text_lower:
                score += 1  # Text match

        if score > 0:
            scored_sections.append((score, s))

    scored_sections.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "number": s["number"],
            "title": s["title"],
            "text": s["effectiveText"][:300],
            "isAmended": s["isAmended"],
            "partNumber": s["partNumber"],
            "partTitle": s["partTitle"],
            "relevanceScore": score,
        }
        for score, s in scored_sections[:10]
    ]


def get_section_explanation(number: int):
    s = get_section(number)
    if not s:
        return None
    s["amendments"] = get_amendments_for_section(number)
    s["rules"] = get_rules_for_section(number)
    s["referencesTo"] = get_cross_references(number)
    s["referencedBy"] = get_referenced_by(number)
    return s


def get_cross_references(number: int):
    results = []
    for ref in _cross_refs:
        if ref["fromSection"] == number:
            target = _sections.get(ref["toSection"])
            if target:
                results.append({
                    "number": target["number"],
                    "title": target["title"],
                    "context": ref["context"],
                })
    return results


def get_referenced_by(number: int):
    results = []
    for ref in _cross_refs:
        if ref["toSection"] == number:
            source = _sections.get(ref["fromSection"])
            if source:
                results.append({
                    "number": source["number"],
                    "title": source["title"],
                    "context": ref["context"],
                })
    return results


def search(term: str):
    """Smart search with keyword tokenization and scoring. Falls back to PDF content."""
    term_lower = term.lower()

    # First try exact substring match
    sections = [
        {"number": s["number"], "title": s["title"], "text": s["effectiveText"][:300], "isAmended": s["isAmended"]}
        for s in _sections.values()
        if term_lower in s["title"].lower() or term_lower in s["effectiveText"].lower()
    ][:10]

    # If no exact match, try keyword-based topic search
    if not sections:
        topic_results = get_sections_by_topic(term)
        sections = [
            {"number": r["number"], "title": r["title"], "text": r["text"], "isAmended": r["isAmended"]}
            for r in topic_results
        ]

    # If still no results, try PDF search
    if not sections:
        try:
            from app.data.pdf_service import search_pdf_content
            pdf_results = search_pdf_content(term, max_results=5)
            for r in pdf_results:
                if r["type"] == "section":
                    sections.append({
                        "number": r["number"],
                        "title": r["title"],
                        "text": r["text"][:300],
                        "isAmended": False,
                        "source": "pdf",
                    })
        except Exception:
            pass

    rules_result = [
        {"number": r["number"], "title": r["title"], "text": r["text"]}
        for r in _rules
        if term_lower in r["title"].lower() or term_lower in r["text"].lower()
    ][:10]

    # If no exact rule match, try keyword matching
    if not rules_result:
        stop_words = {"what", "is", "are", "the", "a", "an", "in", "of", "to", "for", "and", "or", "hi", "hello", "tell", "me", "show", "please"}
        keywords = [w for w in term_lower.split() if w not in stop_words and len(w) > 1]
        if keywords:
            for r in _rules:
                for kw in keywords:
                    if kw in r["title"].lower() or kw in r["text"].lower():
                        rules_result.append({"number": r["number"], "title": r["title"], "text": r["text"]})
                        break
            rules_result = rules_result[:10]

    return {"sections": sections, "rules": rules_result}


def get_graph_stats():
    section_count = len(_sections)
    amendment_count = len(_amendments)
    rule_count = len(_rules)
    sub_count = sum(len(s.get("subsections", [])) for s in _sections.values())
    total_nodes = section_count + amendment_count + rule_count + sub_count + 2  # +2 for Act nodes

    # Count relationships
    ref_count = len(_cross_refs)
    amended_by_count = sum(1 for s in _sections.values() if s["isAmended"])
    derived_from_count = rule_count
    total_rels = ref_count + amended_by_count + derived_from_count + section_count + sub_count + amendment_count + rule_count

    return {
        "totalNodes": total_nodes,
        "totalRelationships": total_rels,
        "nodesByType": [
            {"label": "Section", "count": section_count},
            {"label": "SubSection", "count": sub_count},
            {"label": "Amendment", "count": amendment_count},
            {"label": "Rule", "count": rule_count},
            {"label": "Part", "count": len(act_data["parts"])},
            {"label": "Act", "count": 2},
        ],
        "relationshipsByType": [
            {"type": "HAS_SECTION", "count": section_count},
            {"type": "HAS_SUBSECTION", "count": sub_count},
            {"type": "AMENDED_BY", "count": amended_by_count},
            {"type": "DERIVED_FROM", "count": derived_from_count},
            {"type": "REFERS_TO", "count": ref_count},
            {"type": "CONTAINS_AMENDMENT", "count": amendment_count},
            {"type": "HAS_RULE", "count": rule_count},
        ],
    }


def get_amendment_chain(number: int):
    s = _sections.get(number)
    if not s:
        return None
    amendments = get_amendments_for_section(number)
    return {
        "sectionNumber": number,
        "sectionTitle": s["title"],
        "originalText": s["text"],
        "currentText": s["effectiveText"],
        "amendmentHistory": [
            {
                "type": a["type"],
                "description": a["description"],
                "originalText": a.get("originalText", ""),
                "newText": a.get("newText", ""),
                "year": a["year"],
                "relationship": a["relationship"],
            }
            for a in amendments
        ],
    }
