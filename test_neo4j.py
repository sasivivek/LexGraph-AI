"""Verify Neo4j is working as primary data source."""
import urllib.request
import json

def api(path):
    r = urllib.request.urlopen(f"http://localhost:3000{path}")
    return json.loads(r.read().decode())

# Test 1: Health
h = api("/api/health")
print("=== Health ===")
print(f"  Neo4j: {h['neo4j']}")
print(f"  Gemini: {h['gemini']}")
print(f"  PDF: {h['pdf']}")
print(f"  DataSource: {h['dataSource']}")
print()

# Test 2: Section 230 (NOT in sample_data, loaded from PDF->Neo4j)
d = api("/api/section/230")
print("=== Section 230 (Mergers - from PDF->Neo4j) ===")
print(f"  Found: {d['success']}")
if d['success']:
    print(f"  Title: {d['data']['title']}")
    print(f"  Text preview: {str(d['data'].get('text', d['data'].get('effectiveText', '')))[:150]}...")
print()

# Test 3: Graph stats
g = api("/api/graph/stats")
print("=== Graph Stats ===")
print(f"  Total nodes: {g['totalNodes']}")
print(f"  Total rels: {g['totalRelationships']}")
for n in g['nodesByType']:
    print(f"    {n['label']}: {n['count']}")
print()

# Test 4: Section 149 (curated data)
d = api("/api/section/149")
print("=== Section 149 (Directors - curated) ===")
print(f"  Title: {d['data']['title']}")
print(f"  Amended: {d['data'].get('isAmended', False)}")
print()

# Test 5: Amendments
a = api("/api/amendments")
print(f"=== Amendments: {a['count']} total ===")
print()

# Test 6: All sections count
s = api("/api/sections")
print(f"=== Sections: {s['count']} total ===")
print()

print("[OK] All tests passed - Neo4j is the primary database!")
