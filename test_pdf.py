"""Quick test of the PDF service."""
from app.data.pdf_service import init_pdf_service, get_section_from_pdf, search_pdf_content, get_pdf_stats

init_pdf_service()
print()

# Test 1: Section NOT in sample_data.py (Section 230 - Mergers)
s = get_section_from_pdf(230)
print("Section 230:", s["title"] if s else "NOT FOUND")
if s:
    print(s["text"][:200])
print()

# Test 2: Section that IS in sample_data.py
s149 = get_section_from_pdf(149)
print("Section 149:", s149["title"] if s149 else "NOT FOUND")
print()

# Test 3: Search for a topic
results = search_pdf_content("merger amalgamation")
print("Search results for 'merger amalgamation':")
for r in results:
    num = r.get("number", r.get("clause", "?"))
    print(f"  - [{r['type']}] {num}: {r['title']} (relevance: {r['relevance']})")
print()

# Test 4: Stats
stats = get_pdf_stats()
print(f"Stats: {stats['act_sections_indexed']} sections, {stats['amendment_clauses']} amendments, {stats['rules_entries']} rules")
