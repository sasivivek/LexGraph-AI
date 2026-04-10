"""
Neo4j Client — Connection management singleton.
Handles driver lifecycle, connection verification, and query execution
with robust error handling for when Neo4j is unavailable.
"""
import time
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from app.config import settings

_driver = None
_last_connect_attempt = 0
_RECONNECT_COOLDOWN = 30  # seconds between reconnection attempts


def get_driver():
    """
    Get or create the Neo4j driver singleton.
    Returns None if the driver cannot be created (e.g. bad URI config).
    Applies a cooldown to avoid hammering a down server.
    """
    global _driver, _last_connect_attempt

    if _driver is not None:
        return _driver

    # Don't retry too frequently
    now = time.time()
    if now - _last_connect_attempt < _RECONNECT_COOLDOWN:
        return None

    _last_connect_attempt = now

    uri = settings.NEO4J_URI
    user = settings.NEO4J_USER
    password = settings.NEO4J_PASSWORD

    if not uri:
        print("[WARN] NEO4J_URI not configured")
        return None

    try:
        _driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_lifetime=3 * 60 * 60,
            max_connection_pool_size=50,
            connection_acquisition_timeout=10,
        )
        return _driver
    except Exception as e:
        print(f"[ERROR] Failed to create Neo4j driver: {e}")
        _driver = None
        return None


def run_query(cypher: str, params: dict = None, mode: str = "READ") -> list[dict]:
    """Execute a Cypher query and return results as list of dicts."""
    driver = get_driver()
    if driver is None:
        raise ConnectionError("Neo4j driver is not available")

    with driver.session(
        default_access_mode="r" if mode == "READ" else "w"
    ) as session:
        result = session.run(cypher, parameters=params or {})
        records = []
        for record in result:
            obj = {}
            for key in record.keys():
                val = record[key]
                if hasattr(val, "labels") and hasattr(val, "items"):
                    # Node
                    obj[key] = {**dict(val.items()), "_labels": list(val.labels)}
                elif hasattr(val, "type") and hasattr(val, "items"):
                    # Relationship
                    obj[key] = {**dict(val.items()), "_type": val.type}
                else:
                    obj[key] = val
            records.append(obj)
        return records


def run_write_query(cypher: str, params: dict = None) -> list[dict]:
    """Execute a write Cypher query."""
    return run_query(cypher, params, mode="WRITE")


def verify_connection() -> bool:
    """
    Verify the Neo4j connection is working.
    Returns True if connected, False otherwise.
    Cleans up a broken driver so the next call can retry.
    """
    global _driver
    try:
        driver = get_driver()
        if driver is None:
            return False
        driver.verify_connectivity()
        info = driver.get_server_info()
        print(f"[OK] Neo4j connected: {info.address}")
        return True
    except AuthError as e:
        print(f"[ERROR] Neo4j authentication failed: {e}")
        print("   -> Check NEO4J_USER and NEO4J_PASSWORD in your .env file")
        _close_and_reset()
        return False
    except ServiceUnavailable as e:
        print(f"[ERROR] Neo4j service unavailable: {e}")
        print("   -> Is Neo4j running? Start it with: neo4j console")
        _close_and_reset()
        return False
    except Exception as e:
        print(f"[ERROR] Neo4j connection failed: {e}")
        _close_and_reset()
        return False


def _close_and_reset():
    """Close and reset the driver so the next call can retry."""
    global _driver, _last_connect_attempt
    if _driver:
        try:
            _driver.close()
        except Exception:
            pass
    _driver = None
    _last_connect_attempt = time.time()


def close_driver():
    """Close the Neo4j driver."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None


def reset_driver():
    """
    Force reset the driver (e.g., after config change).
    Next call to get_driver() will create a fresh connection.
    """
    global _last_connect_attempt
    _last_connect_attempt = 0
    _close_and_reset()
