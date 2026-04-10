"""
Ingest Data Script — Populate Neo4j with legal data from PDFs + curated sources.

Usage:
    python scripts/ingest_data.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.neo4j_client import verify_connection, close_driver
from app.db.schema import init_schema, clear_database
from app.db.ingest import ingest_all


def main():
    print("")
    print("=" * 42)
    print("  LexGraph AI -- Data Ingestion")
    print("  PDF -> Neo4j Knowledge Graph")
    print("=" * 42)
    print("")

    # Step 1: Verify connection
    if not verify_connection():
        print("\n[ERROR] Cannot connect to Neo4j. Please ensure it is running.")
        print("   Expected URI: bolt://127.0.0.1:7687")
        print("   Check your .env file for connection settings.")
        sys.exit(1)

    # Step 2: Clear existing data
    print("\n[STEP 2] Clearing existing data...")
    clear_database()

    # Step 3: Initialize schema
    print("\n[STEP 3] Initializing schema (constraints + indexes)...")
    init_schema()

    # Step 4: Ingest all data (PDF + curated)
    print("\n[STEP 4] Ingesting data...")
    ingest_all()

    # Done
    print("\n" + "=" * 42)
    print("  [DONE] Data ingestion complete!")
    print("  Run 'python run.py' to start the server.")
    print("=" * 42)
    print("")

    close_driver()


if __name__ == "__main__":
    main()
