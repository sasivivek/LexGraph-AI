"""
Cypher Queries — Pre-built queries for the Legal Knowledge Graph.
"""

# ============================================================
# SECTION QUERIES
# ============================================================

GET_CURRENT_SECTION = """
    MATCH (s:Section {number: $sectionNumber})
    OPTIONAL MATCH (s)-[:HAS_SUBSECTION]->(ss:SubSection)
    OPTIONAL MATCH (p:Part)-[:HAS_SECTION]->(s)
    RETURN s.sectionId AS id,
           s.number AS number,
           s.title AS title,
           s.text AS originalText,
           s.effectiveText AS effectiveText,
           s.isAmended AS isAmended,
           p.number AS partNumber,
           p.title AS partTitle,
           collect(DISTINCT {number: ss.number, text: ss.text}) AS subsections
"""

GET_ALL_SECTIONS = """
    MATCH (s:Section)
    OPTIONAL MATCH (p:Part)-[:HAS_SECTION]->(s)
    RETURN s.sectionId AS id,
           s.number AS number,
           s.title AS title,
           s.isAmended AS isAmended,
           p.number AS partNumber,
           p.title AS partTitle
    ORDER BY s.number
"""

# ============================================================
# AMENDMENT QUERIES
# ============================================================

GET_AMENDMENTS_FOR_SECTION = """
    MATCH (s:Section {number: $sectionNumber})-[:AMENDED_BY]->(am:Amendment)
    OPTIONAL MATCH (aa:AmendmentAct)-[:CONTAINS_AMENDMENT]->(am)
    RETURN am.amendmentId AS id,
           am.type AS type,
           am.description AS description,
           am.originalText AS originalText,
           am.newText AS newText,
           am.insertedText AS insertedText,
           am.year AS year,
           aa.fullTitle AS amendmentAct
    ORDER BY am.year
"""

GET_ALL_AMENDMENTS = """
    MATCH (am:Amendment)
    OPTIONAL MATCH (am)-[r]->(s:Section)
    WHERE type(r) IN ['SUBSTITUTES', 'INSERTS', 'DELETES']
    RETURN am.amendmentId AS id,
           am.type AS type,
           am.description AS description,
           am.targetSection AS targetSection,
           s.title AS sectionTitle,
           type(r) AS relationship,
           am.year AS year
    ORDER BY am.targetSection
"""

# ============================================================
# RULE QUERIES
# ============================================================

GET_RULES_FOR_SECTION = """
    MATCH (s:Section {number: $sectionNumber})<-[:DERIVED_FROM]-(r:Rule)
    RETURN r.ruleId AS id,
           r.number AS number,
           r.title AS title,
           r.text AS text,
           r.category AS category,
           r.year AS year
    ORDER BY r.number
"""

GET_ALL_RULES = """
    MATCH (r:Rule)
    OPTIONAL MATCH (r)-[:DERIVED_FROM]->(s:Section)
    RETURN r.ruleId AS id,
           r.number AS number,
           r.title AS title,
           r.text AS text,
           r.category AS category,
           s.number AS sectionNumber,
           s.title AS sectionTitle
    ORDER BY r.number
"""

# ============================================================
# EXPLANATION / CONTEXT QUERIES
# ============================================================

GET_SECTION_EXPLANATION = """
    MATCH (s:Section {number: $sectionNumber})
    OPTIONAL MATCH (p:Part)-[:HAS_SECTION]->(s)
    OPTIONAL MATCH (s)-[:HAS_SUBSECTION]->(ss:SubSection)
    OPTIONAL MATCH (s)-[:AMENDED_BY]->(am:Amendment)
    OPTIONAL MATCH (s)<-[:DERIVED_FROM]-(r:Rule)
    OPTIONAL MATCH (s)-[:REFERS_TO]->(ref:Section)
    OPTIONAL MATCH (refBy:Section)-[:REFERS_TO]->(s)
    RETURN s.number AS number,
           s.title AS title,
           s.text AS originalText,
           s.effectiveText AS effectiveText,
           s.isAmended AS isAmended,
           p.number AS partNumber,
           p.title AS partTitle,
           collect(DISTINCT {number: ss.number, text: ss.text}) AS subsections,
           collect(DISTINCT {id: am.amendmentId, type: am.type, description: am.description, year: am.year}) AS amendments,
           collect(DISTINCT {number: r.number, title: r.title, text: r.text}) AS rules,
           collect(DISTINCT {number: ref.number, title: ref.title}) AS referencesTo,
           collect(DISTINCT {number: refBy.number, title: refBy.title}) AS referencedBy
"""

# ============================================================
# GRAPH TRAVERSAL QUERIES
# ============================================================

GET_GRAPH_STATS = """
    MATCH (n)
    WITH labels(n)[0] AS label, count(n) AS count
    RETURN label, count
    ORDER BY count DESC
"""

GET_RELATIONSHIP_STATS = """
    MATCH ()-[r]->()
    WITH type(r) AS type, count(r) AS count
    RETURN type, count
    ORDER BY count DESC
"""

GET_SECTION_GRAPH = """
    MATCH (s:Section {number: $sectionNumber})
    OPTIONAL MATCH (s)-[r1]-(connected)
    RETURN s, r1, connected
"""

SEARCH_SECTIONS = """
    CALL db.index.fulltext.queryNodes("section_fulltext", $searchTerm)
    YIELD node, score
    RETURN node.number AS number,
           node.title AS title,
           node.effectiveText AS text,
           node.isAmended AS isAmended,
           score
    ORDER BY score DESC
    LIMIT 10
"""

SEARCH_RULES = """
    CALL db.index.fulltext.queryNodes("rule_fulltext", $searchTerm)
    YIELD node, score
    RETURN node.number AS number,
           node.title AS title,
           node.text AS text,
           score
    ORDER BY score DESC
    LIMIT 10
"""

GET_CROSS_REFERENCES = """
    MATCH (s:Section {number: $sectionNumber})-[r:REFERS_TO]->(ref:Section)
    RETURN ref.number AS number,
           ref.title AS title,
           r.context AS context
    ORDER BY ref.number
"""

GET_REFERENCED_BY = """
    MATCH (ref:Section)-[r:REFERS_TO]->(s:Section {number: $sectionNumber})
    RETURN ref.number AS number,
           ref.title AS title,
           r.context AS context
    ORDER BY ref.number
"""

GET_AMENDMENT_CHAIN = """
    MATCH (s:Section {number: $sectionNumber})
    OPTIONAL MATCH path = (am:Amendment)-[r]->(s)
    WHERE type(r) IN ['SUBSTITUTES', 'INSERTS', 'DELETES']
    RETURN s.number AS sectionNumber,
           s.title AS sectionTitle,
           s.text AS originalText,
           s.effectiveText AS currentText,
           collect({
             type: am.type,
             description: am.description,
             originalText: am.originalText,
             newText: am.newText,
             insertedText: am.insertedText,
             year: am.year,
             relationship: type(r)
           }) AS amendmentHistory
"""

# Fallback search queries (when fulltext index not available)
SEARCH_SECTIONS_FALLBACK = """
    MATCH (s:Section)
    WHERE toLower(s.title) CONTAINS toLower($searchTerm)
       OR toLower(s.effectiveText) CONTAINS toLower($searchTerm)
    RETURN s.number AS number, s.title AS title, s.effectiveText AS text, s.isAmended AS isAmended
    ORDER BY s.number
    LIMIT 10
"""

SEARCH_RULES_FALLBACK = """
    MATCH (r:Rule)
    WHERE toLower(r.title) CONTAINS toLower($searchTerm)
       OR toLower(r.text) CONTAINS toLower($searchTerm)
    RETURN r.number AS number, r.title AS title, r.text AS text
    ORDER BY r.number
    LIMIT 10
"""
