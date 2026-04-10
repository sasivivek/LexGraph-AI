"""
Data Ingestion — Populates Neo4j with legal data.

Two-phase pipeline:
  Phase 1: Load ALL sections from PDF extraction (421 sections, full coverage)
  Phase 2: Enrich with curated sample_data.py (subsections, cross-references, precise text)
"""
from app.db.neo4j_client import run_write_query, run_query
from app.data.sample_data import act_data, amendment_data, rules_data, cross_references


# ============================================================
# PHASE 1: PDF-SOURCED DATA (full coverage)
# ============================================================

def ingest_from_pdf():
    """
    Ingest ALL sections, amendments, and rules extracted from the actual PDFs.
    This gives full coverage of the Companies Act (421 sections).
    """
    from app.data.pdf_service import (
        init_pdf_service,
        _act_sections,
        _amendment_clauses,
        _rules_entries,
        is_ready,
    )

    if not is_ready():
        print("  [PDF] Initializing PDF service...")
        init_pdf_service()

    print(f"  [PDF] Ingesting {len(_act_sections)} sections from PDF...")

    # Create Act node
    run_write_query(
        """
        MERGE (a:Act {name: 'Companies Act'})
        SET a.year = 2013,
            a.fullTitle = 'The Companies Act, 2013',
            a.dateEnacted = '2013-08-29',
            a.shortDescription = 'An Act to consolidate and amend the law relating to companies.',
            a.source = 'pdf'
        """
    )

    # Batch-create all sections from PDF
    batch_size = 50
    section_list = list(_act_sections.values())

    for i in range(0, len(section_list), batch_size):
        batch = section_list[i : i + batch_size]
        for section in batch:
            section_id = f"Companies Act_S{section['number']}"
            run_write_query(
                """
                MERGE (s:Section {sectionId: $sectionId})
                ON CREATE SET
                    s.number = $number,
                    s.title = $title,
                    s.text = $text,
                    s.effectiveText = $text,
                    s.isAmended = false,
                    s.actName = 'Companies Act',
                    s.source = 'pdf'
                """,
                {
                    "sectionId": section_id,
                    "number": section["number"],
                    "title": section["title"],
                    "text": section["text"],
                },
            )

    print(f"    -> {len(section_list)} sections created from PDF")

    # Ingest amendment clauses from PDF
    if _amendment_clauses:
        print(f"  [PDF] Ingesting {len(_amendment_clauses)} amendment clauses from PDF...")

        # Create Amendment Act node
        run_write_query(
            """
            MERGE (aa:Act:AmendmentAct {name: 'Corporate Laws (Amendment) Act'})
            SET aa.year = 2026,
                aa.fullTitle = 'The Corporate Laws (Amendment) Bill, 2026',
                aa.dateEnacted = '2026-01-15',
                aa.shortDescription = 'A Bill further to amend the LLP Act, 2008 and the Companies Act, 2013.',
                aa.source = 'pdf'
            """
        )

        for clause in _amendment_clauses:
            amend_id = f"PDF_Amendment_Clause_{clause['clause']}"
            try:
                target_num = int(clause["targetSection"])
            except ValueError:
                continue

            target_section_id = f"Companies Act_S{target_num}"

            run_write_query(
                """
                MERGE (am:Amendment {amendmentId: $amendId})
                SET am.clause = $clause,
                    am.targetSection = $targetSection,
                    am.text = $text,
                    am.year = 2026,
                    am.source = 'pdf'
                WITH am
                MATCH (aa:AmendmentAct {name: 'Corporate Laws (Amendment) Act'})
                MERGE (aa)-[:CONTAINS_AMENDMENT]->(am)
                """,
                {
                    "amendId": amend_id,
                    "clause": clause["clause"],
                    "targetSection": target_num,
                    "text": clause["text"][:2000],
                },
            )

            # Link to target section if it exists
            run_write_query(
                """
                MATCH (am:Amendment {amendmentId: $amendId})
                MATCH (s:Section {sectionId: $targetSectionId})
                MERGE (am)-[:AMENDS]->(s)
                MERGE (s)-[:AMENDED_BY]->(am)
                SET s.isAmended = true
                """,
                {"amendId": amend_id, "targetSectionId": target_section_id},
            )

        print(f"    -> {len(_amendment_clauses)} amendment clauses ingested")

    # Ingest rules from PDF
    if _rules_entries:
        print(f"  [PDF] Ingesting {len(_rules_entries)} rules from PDF...")
        for rule in _rules_entries:
            rule_id = f"PDF_Rule_{rule['number']}"
            run_write_query(
                """
                MERGE (r:Rule {ruleId: $ruleId})
                SET r.number = $number,
                    r.text = $text,
                    r.year = 2014,
                    r.source = 'pdf'
                """,
                {
                    "ruleId": rule_id,
                    "number": rule["number"],
                    "text": rule["text"][:2000],
                },
            )
        print(f"    -> {len(_rules_entries)} rules ingested")


# ============================================================
# PHASE 2: CURATED SAMPLE DATA (enrichment layer)
# ============================================================

def ingest_act(act: dict):
    """Ingest the curated Act data with Parts, Sections, and SubSections."""
    print(f"  [CURATED] Ingesting Act: {act['fullTitle']}")

    # Update Act node
    run_write_query(
        """
        MERGE (a:Act {name: $name})
        SET a.year = $year,
            a.fullTitle = $fullTitle,
            a.dateEnacted = $dateEnacted,
            a.shortDescription = $shortDescription
        """,
        act,
    )

    # Create/update Parts and Sections with curated data
    for part in act["parts"]:
        part_id = f"{act['name']}_Part_{part['number']}"
        run_write_query(
            """
            MERGE (p:Part {partId: $partId})
            SET p.number = $number, p.title = $title
            WITH p
            MATCH (a:Act {name: $actName})
            MERGE (a)-[:HAS_PART]->(p)
            """,
            {"partId": part_id, "number": part["number"], "title": part["title"], "actName": act["name"]},
        )

        for section in part.get("sections", []):
            section_id = f"{act['name']}_S{section['number']}"
            # MERGE so we update PDF-created sections with curated data
            run_write_query(
                """
                MERGE (s:Section {sectionId: $sectionId})
                SET s.number = $number,
                    s.title = $title,
                    s.text = $text,
                    s.effectiveText = $text,
                    s.isAmended = false,
                    s.actName = $actName,
                    s.partNumber = $partNumber
                WITH s
                MATCH (p:Part {partId: $partId})
                MERGE (p)-[:HAS_SECTION]->(s)
                """,
                {
                    "sectionId": section_id,
                    "number": section["number"],
                    "title": section["title"],
                    "text": section["text"],
                    "actName": act["name"],
                    "partNumber": part["number"],
                    "partId": part_id,
                },
            )

            # Create SubSections (only from curated data)
            for sub in section.get("subsections", []):
                sub_id = f"{section_id}_Sub{sub['number']}"
                run_write_query(
                    """
                    MERGE (ss:SubSection {subSectionId: $subId})
                    SET ss.number = $number,
                        ss.text = $text,
                        ss.sectionNumber = $sectionNumber
                    WITH ss
                    MATCH (s:Section {sectionId: $sectionId})
                    MERGE (s)-[:HAS_SUBSECTION]->(ss)
                    """,
                    {
                        "subId": sub_id,
                        "number": sub["number"],
                        "text": sub["text"],
                        "sectionNumber": section["number"],
                        "sectionId": section_id,
                    },
                )

    print(f"    -> Act enriched with {len(act['parts'])} parts (curated)")


def ingest_amendments(amendments: dict):
    """Ingest curated amendments and link to target sections."""
    print(f"  [CURATED] Ingesting Amendments: {amendments['fullTitle']}")

    # Create/update Amendment Act node
    run_write_query(
        """
        MERGE (aa:Act:AmendmentAct {name: $name})
        SET aa.year = $year,
            aa.fullTitle = $fullTitle,
            aa.dateEnacted = $dateEnacted,
            aa.shortDescription = $shortDescription
        """,
        amendments,
    )

    for i, amend in enumerate(amendments["amendments"]):
        amend_id = f"Amendment_{amendments['year']}_{i + 1}"
        target_section_id = f"Companies Act_S{amend['targetSection']}"

        # Create Amendment node
        run_write_query(
            """
            MERGE (am:Amendment {amendmentId: $amendId})
            SET am.type = $type,
                am.description = $description,
                am.targetSection = $targetSection,
                am.targetSubsection = $targetSubsection,
                am.year = $year,
                am.actName = $actName
            """,
            {
                "amendId": amend_id,
                "type": amend["type"],
                "description": amend["description"],
                "targetSection": amend["targetSection"],
                "targetSubsection": amend.get("targetSubsection"),
                "year": amendments["year"],
                "actName": amendments["name"],
            },
        )

        # Link Amendment to Amendment Act
        run_write_query(
            """
            MATCH (aa:AmendmentAct {name: $actName})
            MATCH (am:Amendment {amendmentId: $amendId})
            MERGE (aa)-[:CONTAINS_AMENDMENT]->(am)
            """,
            {"actName": amendments["name"], "amendId": amend_id},
        )

        # Create relationship based on amendment type
        rel_type = {
            "substitution": "SUBSTITUTES",
            "insertion": "INSERTS",
            "deletion": "DELETES",
        }.get(amend["type"], "AMENDS")

        run_write_query(
            f"""
            MATCH (am:Amendment {{amendmentId: $amendId}})
            MATCH (s:Section {{sectionId: $targetSectionId}})
            MERGE (am)-[:{rel_type}]->(s)
            MERGE (s)-[:AMENDED_BY]->(am)
            SET s.isAmended = true
            """,
            {"amendId": amend_id, "targetSectionId": target_section_id},
        )

        # Update effective text if substitution
        if amend["type"] == "substitution" and amend.get("newText"):
            run_write_query(
                """
                MATCH (am:Amendment {amendmentId: $amendId})
                SET am.originalText = $originalText, am.newText = $newText
                WITH am
                MATCH (s:Section {sectionId: $targetSectionId})
                SET s.effectiveText = $newText
                """,
                {
                    "amendId": amend_id,
                    "originalText": amend.get("originalText", ""),
                    "newText": amend["newText"],
                    "targetSectionId": target_section_id,
                },
            )

        if amend["type"] == "insertion" and amend.get("newText"):
            run_write_query(
                """
                MATCH (am:Amendment {amendmentId: $amendId})
                SET am.insertedText = $newText
                WITH am
                MATCH (s:Section {sectionId: $targetSectionId})
                SET s.effectiveText = s.text + ' ' + $newText
                """,
                {
                    "amendId": amend_id,
                    "newText": amend["newText"],
                    "targetSectionId": target_section_id,
                },
            )

    print(f"    -> {len(amendments['amendments'])} curated amendments ingested")


def ingest_rules(rules: dict):
    """Ingest curated rules and link to sections."""
    print(f"  [CURATED] Ingesting Rules: {rules['fullTitle']}")

    for rule in rules["rules"]:
        rule_id = f"Rule_{rule['number']}"
        target_section_id = f"Companies Act_S{rule['relatedSection']}"

        run_write_query(
            """
            MERGE (r:Rule {ruleId: $ruleId})
            SET r.number = $number,
                r.title = $title,
                r.text = $text,
                r.category = $category,
                r.year = $year
            """,
            {
                "ruleId": rule_id,
                "number": rule["number"],
                "title": rule["title"],
                "text": rule["text"],
                "category": rule["category"],
                "year": rules["year"],
            },
        )

        run_write_query(
            """
            MATCH (r:Rule {ruleId: $ruleId})
            MATCH (s:Section {sectionId: $targetSectionId})
            MERGE (r)-[:DERIVED_FROM]->(s)
            MERGE (s)-[:HAS_RULE]->(r)
            """,
            {"ruleId": rule_id, "targetSectionId": target_section_id},
        )

    print(f"    -> {len(rules['rules'])} curated rules ingested")


def ingest_cross_references(refs: list):
    """Ingest cross-references between sections."""
    print("  [CURATED] Ingesting cross-references...")

    for ref in refs:
        from_id = f"Companies Act_S{ref['fromSection']}"
        to_id = f"Companies Act_S{ref['toSection']}"

        run_write_query(
            """
            MATCH (fromNode:Section {sectionId: $fromId})
            MATCH (toNode:Section {sectionId: $toId})
            MERGE (fromNode)-[:REFERS_TO {context: $context}]->(toNode)
            """,
            {"fromId": from_id, "toId": to_id, "context": ref["context"]},
        )

    print(f"    -> {len(refs)} cross-references ingested")


# ============================================================
# MAIN INGESTION PIPELINE
# ============================================================

def ingest_all():
    """
    Run the complete two-phase ingestion pipeline:
      Phase 1: PDF extraction -> Neo4j (full coverage, 421 sections)
      Phase 2: Curated sample_data -> Neo4j (enrich with subsections, cross-refs)
    """
    print("\n--- Phase 1: PDF Extraction (full coverage) ---")
    try:
        ingest_from_pdf()
    except Exception as e:
        print(f"  [WARN] PDF ingestion failed: {e}")
        print("  Continuing with curated data only...")

    print("\n--- Phase 2: Curated Data (enrichment) ---")
    ingest_act(act_data)
    ingest_amendments(amendment_data)
    ingest_rules(rules_data)
    ingest_cross_references(cross_references)

    # Print summary
    stats = run_query(
        """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
        """
    )
    print("\n--- Graph Statistics ---")
    for s in stats:
        print(f"   {s['label']}: {s['count']} nodes")

    rel_stats = run_query(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY count DESC
        """
    )
    print("\n--- Relationships ---")
    for s in rel_stats:
        print(f"   {s['type']}: {s['count']}")
