"""
Neo4j Schema — Constraints and Indexes for the Legal Knowledge Graph.
"""
from app.db.neo4j_client import run_write_query


def create_constraints():
    """Create uniqueness constraints."""
    constraints = [
        "CREATE CONSTRAINT act_name IF NOT EXISTS FOR (a:Act) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT section_id IF NOT EXISTS FOR (s:Section) REQUIRE s.sectionId IS UNIQUE",
        "CREATE CONSTRAINT amendment_id IF NOT EXISTS FOR (am:Amendment) REQUIRE am.amendmentId IS UNIQUE",
        "CREATE CONSTRAINT rule_id IF NOT EXISTS FOR (r:Rule) REQUIRE r.ruleId IS UNIQUE",
        "CREATE CONSTRAINT part_id IF NOT EXISTS FOR (p:Part) REQUIRE p.partId IS UNIQUE",
        "CREATE CONSTRAINT chapter_id IF NOT EXISTS FOR (c:Chapter) REQUIRE c.chapterId IS UNIQUE",
        "CREATE CONSTRAINT schedule_id IF NOT EXISTS FOR (sc:Schedule) REQUIRE sc.scheduleId IS UNIQUE",
    ]
    for constraint in constraints:
        try:
            run_write_query(constraint)
        except Exception as e:
            if "already exists" not in str(e):
                print(f"Constraint warning: {e}")
    print("[OK] Constraints created")


def create_indexes():
    """Create indexes for performance."""
    indexes = [
        "CREATE INDEX section_number IF NOT EXISTS FOR (s:Section) ON (s.number)",
        "CREATE INDEX section_title IF NOT EXISTS FOR (s:Section) ON (s.title)",
        "CREATE INDEX rule_number IF NOT EXISTS FOR (r:Rule) ON (r.number)",
        "CREATE INDEX amendment_type IF NOT EXISTS FOR (am:Amendment) ON (am.type)",
        "CREATE FULLTEXT INDEX section_fulltext IF NOT EXISTS FOR (s:Section) ON EACH [s.title, s.text, s.effectiveText]",
        "CREATE FULLTEXT INDEX rule_fulltext IF NOT EXISTS FOR (r:Rule) ON EACH [r.title, r.text]",
    ]
    for index in indexes:
        try:
            run_write_query(index)
        except Exception as e:
            if "already exists" not in str(e):
                print(f"Index warning: {e}")
    print("[OK] Indexes created")


def init_schema():
    """Initialize constraints and indexes."""
    create_constraints()
    create_indexes()


def clear_database():
    """Delete all nodes and relationships."""
    run_write_query("MATCH (n) DETACH DELETE n")
    print("[OK] Database cleared")
