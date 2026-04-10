"""
FastAPI Application — Main entry point for LexGraph AI.
REST API endpoints for the Legal Knowledge Graph.
"""
import json
import re
import time
import uuid
from pathlib import Path
import asyncio

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.neo4j_client import verify_connection, run_query
from app.db import memory_store
from app.ai.llm_service import (
    init_llm,
    process_natural_language_query,
    generate_explanation,
    generate_response,
    chat_with_context,
    clear_chat_session,
)
from app.queries import cypher_queries as queries
from app.data.pdf_service import (
    init_pdf_service,
    get_pdf_context_for_query,
    search_pdf_content,
    get_section_from_pdf,
    get_pdf_stats,
)

# ============================================================
# APP SETUP
# ============================================================
app = FastAPI(title="LexGraph AI", version="1.0.0", description="Legal Knowledge Graph for Accurate Querying")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State
_use_neo4j = False
_gemini_ready = False
_pdf_ready = False


# ============================================================
# STARTUP
# ============================================================
@app.on_event("startup")
async def startup():
    global _use_neo4j, _gemini_ready, _pdf_ready

    print("")
    print("=" * 42)
    print("     LexGraph AI v1.0.0")
    print("     Legal Knowledge Graph System")
    print("=" * 42)

    # Show current config
    settings.validate()

    # Initialize PDF extraction in the background
    def bg_pdf_init():
        global _pdf_ready
        _pdf_ready = init_pdf_service()
        if _pdf_ready:
            print("\n[INFO] Background PDF initialization complete.")

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, bg_pdf_init)

    # Initialize AI
    _gemini_ready = init_llm()

    # Verify Neo4j connection
    _use_neo4j = verify_connection()
    if _use_neo4j:
        print("[OK] API: Using Neo4j database")
    else:
        print("[INFO] API: Using in-memory store (Neo4j unavailable)")
        memory_store.load()

    print(f"\n[START] Server running at http://localhost:{settings.PORT}")
    print(f"[API] API available at http://localhost:{settings.PORT}/api")
    print(f"[WEB] Frontend available at http://localhost:{settings.PORT}\n")


# ============================================================
# HELPER — try Neo4j first, fallback to memory
# ============================================================
def try_neo4j(neo4j_fn, memory_fn):
    """Try Neo4j query, fallback to memory store on failure."""
    if _use_neo4j:
        try:
            return neo4j_fn()
        except Exception as e:
            print(f"Neo4j query failed, using memory store: {e}")
    return memory_fn()


# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/api/health")
async def health():
    from datetime import datetime
    return {
        "status": "ok",
        "service": "LexGraph AI",
        "version": "1.0.0",
        "neo4j": "connected" if _use_neo4j else "disconnected",
        "gemini": "ready" if _gemini_ready else "fallback",
        "pdf": "ready" if _pdf_ready else "unavailable",
        "dataSource": "neo4j" if _use_neo4j else "memory+pdf",
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================
# RECONNECT — retry Neo4j and Gemini without restarting
# ============================================================
@app.post("/api/reconnect")
async def reconnect():
    """Re-attempt Neo4j connection and Gemini init (e.g. after updating .env)."""
    global _use_neo4j, _gemini_ready
    from app.db.neo4j_client import reset_driver

    # Reload env vars
    settings.reload()

    # Retry Neo4j
    reset_driver()
    _use_neo4j = verify_connection()
    if not _use_neo4j:
        memory_store.load()

    # Retry Gemini
    _gemini_ready = init_llm()

    return {
        "success": True,
        "neo4j": "connected" if _use_neo4j else "disconnected",
        "gemini": "ready" if _gemini_ready else "fallback",
        "message": (
            "All services connected!" if (_use_neo4j and _gemini_ready)
            else "Some services unavailable — check .env configuration"
        ),
    }


# ============================================================
# SECTION ENDPOINTS
# ============================================================
@app.get("/api/sections")
async def get_sections():
    try:
        data = try_neo4j(
            lambda: run_query(queries.GET_ALL_SECTIONS),
            lambda: memory_store.get_all_sections(),
        )
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/api/section/{number}")
async def get_section(number: int):
    try:
        data = try_neo4j(
            lambda: (run_query(queries.GET_CURRENT_SECTION, {"sectionNumber": number}) or [None])[0],
            lambda: memory_store.get_section(number),
        )
        if not data:
            return JSONResponse(status_code=404, content={"success": False, "error": f"Section {number} not found"})
        return {"success": True, "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/api/section/{number}/amendments")
async def get_section_amendments(number: int):
    try:
        data = try_neo4j(
            lambda: run_query(queries.GET_AMENDMENTS_FOR_SECTION, {"sectionNumber": number}),
            lambda: memory_store.get_amendments_for_section(number),
        )
        return {"success": True, "sectionNumber": number, "count": len(data), "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/api/section/{number}/rules")
async def get_section_rules(number: int):
    try:
        data = try_neo4j(
            lambda: run_query(queries.GET_RULES_FOR_SECTION, {"sectionNumber": number}),
            lambda: memory_store.get_rules_for_section(number),
        )
        return {"success": True, "sectionNumber": number, "count": len(data), "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/api/section/{number}/explain")
async def explain_section(number: int):
    try:
        section_data = try_neo4j(
            lambda: (run_query(queries.GET_SECTION_EXPLANATION, {"sectionNumber": number}) or [None])[0],
            lambda: memory_store.get_section_explanation(number),
        )
        if not section_data:
            return JSONResponse(status_code=404, content={"success": False, "error": f"Section {number} not found"})

        explanation = generate_explanation(section_data)
        return {"success": True, "data": section_data, "explanation": explanation["text"], "source": explanation["source"]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/api/section/{number}/references")
async def get_section_references(number: int):
    try:
        result = try_neo4j(
            lambda: {
                "referencesTo": run_query(queries.GET_CROSS_REFERENCES, {"sectionNumber": number}),
                "referencedBy": run_query(queries.GET_REFERENCED_BY, {"sectionNumber": number}),
            },
            lambda: {
                "referencesTo": memory_store.get_cross_references(number),
                "referencedBy": memory_store.get_referenced_by(number),
            },
        )
        return {"success": True, "sectionNumber": number, **result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/api/section/{number}/history")
async def get_section_history(number: int):
    try:
        data = try_neo4j(
            lambda: (run_query(queries.GET_AMENDMENT_CHAIN, {"sectionNumber": number}) or [None])[0],
            lambda: memory_store.get_amendment_chain(number),
        )
        return {"success": True, "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ============================================================
# AMENDMENTS
# ============================================================
@app.get("/api/amendments")
async def get_amendments():
    try:
        data = try_neo4j(
            lambda: run_query(queries.GET_ALL_AMENDMENTS),
            lambda: memory_store.get_all_amendments(),
        )
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ============================================================
# RULES
# ============================================================
@app.get("/api/rules")
async def get_rules():
    try:
        data = try_neo4j(
            lambda: run_query(queries.GET_ALL_RULES),
            lambda: memory_store.get_all_rules(),
        )
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ============================================================
# SEARCH
# ============================================================
@app.get("/api/search")
async def search(q: str = ""):
    if not q:
        return JSONResponse(status_code=400, content={"success": False, "error": "Search term required (?q=term)"})
    try:
        result = try_neo4j(
            lambda: _neo4j_search(q),
            lambda: memory_store.search(q),
        )
        return {
            "success": True,
            "searchTerm": q,
            "sections": {"count": len(result["sections"]), "data": result["sections"]},
            "rules": {"count": len(result["rules"]), "data": result["rules"]},
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


def _neo4j_search(search_term: str) -> dict:
    """Search using Neo4j fulltext indexes with fallback."""
    try:
        sections = run_query(queries.SEARCH_SECTIONS, {"searchTerm": search_term})
    except Exception:
        sections = run_query(queries.SEARCH_SECTIONS_FALLBACK, {"searchTerm": search_term})
    try:
        rules = run_query(queries.SEARCH_RULES, {"searchTerm": search_term})
    except Exception:
        rules = run_query(queries.SEARCH_RULES_FALLBACK, {"searchTerm": search_term})
    return {"sections": sections, "rules": rules}


# ============================================================
# AI / NATURAL LANGUAGE
# ============================================================
@app.post("/api/query/natural")
async def natural_query(request: Request):
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        if not question:
            return JSONResponse(status_code=400, content={"success": False, "error": "Question is required"})

        if _use_neo4j:
            result = process_natural_language_query(question)
            return {"success": True, **result}

        # Memory store fallback with intelligent query processing
        start_time = time.time()
        result = _process_memory_query(question)

        response_text = result["response"]
        response_source = "fallback"
        try:
            ai_resp = generate_response(question, result["results"], result["cypher"])
            if ai_resp and ai_resp.get("text"):
                response_text = ai_resp["text"]
                response_source = ai_resp["source"]
        except Exception:
            pass

        return {
            "success": True,
            "question": question,
            "cypher": result["cypher"],
            "cypherSource": "memory",
            "results": result["results"],
            "resultCount": len(result["results"]),
            "response": response_text,
            "responseSource": response_source,
            "grounded": len(result["results"]) > 0,
            "processingTimeMs": int((time.time() - start_time) * 1000),
            "error": None,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


def _process_memory_query(question: str) -> dict:
    """Process query against memory store."""
    q = question.lower()

    # Section lookup
    section_match = re.search(r"section\s+(\d+)", q)
    if section_match:
        num = int(section_match.group(1))

        if any(w in q for w in ["amend", "change", "modified"]):
            results = memory_store.get_amendments_for_section(num)
            response = (
                f"## Amendments to Section {num}\n\n"
                + "\n".join(
                    f"### {am['type'][0].upper() + am['type'][1:]} ({am['year']})\n{am['description']}\n"
                    for am in results
                )
                if results
                else f"Section {num} has not been amended."
            )
            return {"results": results, "cypher": f"MATCH (s:Section {{number: {num}}})-[:AMENDED_BY]->(am) RETURN am", "response": response}

        if "rule" in q:
            results = memory_store.get_rules_for_section(num)
            response = (
                f"## Rules for Section {num}\n\n"
                + "\n".join(f"### Rule {r['number']}: {r['title']}\n{r['text']}\n" for r in results)
                if results
                else f"No rules found for Section {num}."
            )
            return {"results": results, "cypher": f"MATCH (s:Section {{number: {num}}})<-[:DERIVED_FROM]-(r:Rule) RETURN r", "response": response}

        if any(w in q for w in ["refer", "cross", "related"]):
            refs_to = memory_store.get_cross_references(num)
            refs_by = memory_store.get_referenced_by(num)
            results = refs_to + refs_by
            response = f"## Cross-References for Section {num}\n\n"
            if refs_to:
                response += "**References to:**\n" + "\n".join(f"- Section {r['number']}: {r['title']} ({r['context']})" for r in refs_to) + "\n\n"
            if refs_by:
                response += "**Referenced by:**\n" + "\n".join(f"- Section {r['number']}: {r['title']} ({r['context']})" for r in refs_by)
            return {"results": results, "cypher": f"MATCH (s:Section {{number: {num}}})-[r:REFERS_TO]-(ref) RETURN ref", "response": response}

        if any(w in q for w in ["explain", "detail", "context"]):
            data = memory_store.get_section_explanation(num)
            if not data:
                return {"results": [], "cypher": "", "response": f"Section {num} not found."}
            response = f"## Section {data['number']}: {data['title']}\n\n**Part {data['partNumber']}** — {data['partTitle']}\n\n### Current Text\n{data['effectiveText']}\n\n"
            if data["isAmended"]:
                response += f"### ⚠️ Amended\n**Original:** {data['originalText']}\n\n"
            if data.get("amendments"):
                response += "### Amendments\n" + "\n".join(f"- **{a['type']}** ({a['year']}): {a['description']}" for a in data["amendments"]) + "\n\n"
            if data.get("rules"):
                response += "### Rules\n" + "\n".join(f"- Rule {r['number']}: {r['title']}" for r in data["rules"]) + "\n\n"
            if data.get("referencesTo"):
                response += "### References\n" + "\n".join(f"- Section {r['number']}: {r['title']}" for r in data["referencesTo"])
            return {"results": [data], "cypher": f"MATCH (s:Section {{number: {num}}}) ...context query", "response": response}

        # Default: just show the section
        data = memory_store.get_section(num)
        if not data:
            return {"results": [], "cypher": f"MATCH (s:Section {{number: {num}}}) RETURN s", "response": f"Section {num} not found in the knowledge graph."}
        response = f"## Section {data['number']}: {data['title']}\n\n{data['effectiveText']}\n"
        if data["isAmended"]:
            response += "\n*⚠️ This section has been amended. Above shows the current effective text.*"
        return {"results": [data], "cypher": f"MATCH (s:Section {{number: {num}}}) RETURN s", "response": response}

    # Definition lookup
    if any(w in q for w in ["definition", "define", "meaning"]):
        section2 = memory_store.get_section(2)
        if section2 and section2.get("subsections"):
            term = re.sub(r".*(?:definition of|define|meaning of|what is (?:a |an )?)", "", q, flags=re.IGNORECASE).replace("?", "").replace('"', "").replace("'", "").strip()
            matching = [ss for ss in section2["subsections"] if ss.get("text") and term.lower() in ss["text"].lower()]
            response = (
                f"## Definition: {term}\n\n" + "\n\n".join(f"**Section 2({ss['number']}):** {ss['text']}" for ss in matching)
                if matching
                else f'No definition found for "{term}" in Section 2.'
            )
            return {"results": matching, "cypher": f"MATCH (s:Section {{number: 2}})-[:HAS_SUBSECTION]->(ss) WHERE ss.text CONTAINS '{term}' RETURN ss", "response": response}
        return {"results": [], "cypher": "", "response": "Section 2 (Definitions) not available."}

    # All amendments
    if "amendment" in q:
        results = memory_store.get_all_amendments()
        response = f"## All Amendments ({len(results)})\n\n" + "\n\n".join(
            f"### Section {am['targetSection']}: {am['sectionTitle']}\n- **{am['type']}** ({am['relationship']})\n- {am['description']}"
            for am in results
        )
        return {"results": results, "cypher": "MATCH (am:Amendment)-[r]->(s:Section) RETURN am, s", "response": response}

    # Rules
    if "rule" in q:
        results = memory_store.get_all_rules()
        if "director" in q:
            results = [r for r in results if r["category"] == "Directors"]
        elif "audit" in q:
            results = [r for r in results if r["category"] == "Audit"]
        elif "csr" in q:
            results = [r for r in results if r["category"] == "CSR"]
        elif "dividend" in q:
            results = [r for r in results if r["category"] == "Dividend"]
        response = f"## Rules ({len(results)})\n\n" + "\n\n".join(
            f"### Rule {r['number']}: {r['title']}\n{r['text']}\n*→ Section {r['sectionNumber']}: {r['sectionTitle']}*"
            for r in results
        )
        return {"results": results, "cypher": "MATCH (r:Rule) RETURN r", "response": response}

    # Stats
    if any(w in q for w in ["statistic", "how many", "count", "overview"]):
        stats = memory_store.get_graph_stats()
        response = f"## Knowledge Graph Statistics\n\n- **Total Nodes:** {stats['totalNodes']}\n- **Total Relationships:** {stats['totalRelationships']}\n\n"
        response += "### Nodes\n" + "\n".join(f"- {n['label']}: **{n['count']}**" for n in stats["nodesByType"])
        response += "\n\n### Relationships\n" + "\n".join(f"- {r['type']}: **{r['count']}**" for r in stats["relationshipsByType"])
        return {"results": stats["nodesByType"], "cypher": "MATCH (n) RETURN labels(n)[0], count(n)", "response": response}

    # Fallback: search
    search_results = memory_store.search(question)
    results = search_results["sections"] + search_results["rules"]
    response = (
        f"## Search Results ({len(results)})\n\n"
        + "\n\n".join(f"### Section {s['number']}: {s['title']}\n{(s.get('text', '') or '')[:200]}..." for s in search_results["sections"])
        if results
        else f'No results found for "{question}". Try asking about a specific section number, amendments, or rules.'
    )
    return {"results": results, "cypher": f"MATCH (s:Section) WHERE s.title CONTAINS '{question}' RETURN s", "response": response}


# ============================================================
# INTERACTIVE CHAT (ChatGPT-like)
# ============================================================
@app.post("/api/chat")
async def chat(request: Request):
    """Interactive conversational AI endpoint with session history."""
    try:
        body = await request.json()
        message = body.get("message", "").strip()
        session_id = body.get("session_id", "").strip()

        if not message:
            return JSONResponse(status_code=400, content={"success": False, "error": "Message is required"})

        # Generate or reuse session ID
        if not session_id:
            session_id = str(uuid.uuid4())

        # Optionally gather knowledge graph context for grounding
        context_data = None
        try:
            context_data = _gather_context_for_chat(message)
        except Exception:
            pass  # Context enrichment is best-effort

        result = chat_with_context(session_id, message, context_data)

        return {
            "success": True,
            "reply": result["reply"],
            "source": result["source"],
            "session_id": result["session_id"] or session_id,
            "turn_count": result["turn_count"],
            "has_context": context_data is not None and len(context_data or []) > 0,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.post("/api/chat/clear")
async def clear_chat(request: Request):
    """Clear a chat session's history."""
    try:
        body = await request.json()
        session_id = body.get("session_id", "")
        if session_id:
            clear_chat_session(session_id)
        return {"success": True, "message": "Chat session cleared"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


def _gather_context_for_chat(message: str) -> list | None:
    """Try to extract relevant knowledge graph data to ground the chat response."""
    q = message.lower()

    # Section mention
    section_match = re.search(r"section\s+(\d+)", q)
    if section_match:
        num = int(section_match.group(1))
        data = try_neo4j(
            lambda: (run_query(
                "MATCH (s:Section {number: $num}) "
                "OPTIONAL MATCH (p:Part)-[:HAS_SECTION]->(s) "
                "OPTIONAL MATCH (s)-[:AMENDED_BY]->(am:Amendment) "
                "OPTIONAL MATCH (s)<-[:DERIVED_FROM]-(r:Rule) "
                "RETURN s.number AS number, s.title AS title, "
                "s.effectiveText AS effectiveText, s.text AS originalText, "
                "s.isAmended AS isAmended, p.title AS partTitle, "
                "collect(DISTINCT {type: am.type, description: am.description, year: am.year}) AS amendments, "
                "collect(DISTINCT {number: r.number, title: r.title}) AS rules",
                {"num": num}
            )),
            lambda: _memory_context_for_section(num),
        )
        if data:
            return data if isinstance(data, list) else [data]

    # Rule mention
    if "rule" in q:
        data = try_neo4j(
            lambda: run_query(
                "MATCH (r:Rule) "
                "OPTIONAL MATCH (r)-[:DERIVED_FROM]->(s:Section) "
                "RETURN r.number AS ruleNumber, r.title AS ruleTitle, r.text AS ruleText, "
                "r.category AS category, s.number AS sectionNumber "
                "ORDER BY r.number LIMIT 10"
            ),
            lambda: memory_store.get_all_rules()[:10],
        )
        if data:
            return data

    # Amendment mention
    if any(w in q for w in ["amend", "change", "modified", "2026"]):
        data = try_neo4j(
            lambda: run_query(
                "MATCH (am:Amendment) "
                "OPTIONAL MATCH (am)-[r]->(s:Section) "
                "WHERE type(r) IN ['SUBSTITUTES','INSERTS','DELETES'] "
                "RETURN am.type AS type, am.description AS description, "
                "am.targetSection AS targetSection, s.title AS sectionTitle, am.year AS year "
                "ORDER BY am.targetSection LIMIT 10"
            ),
            lambda: memory_store.get_all_amendments()[:10],
        )
        if data:
            return data

    return None


def _memory_context_for_section(num: int) -> list | None:
    """Get section context from memory store, with PDF fallback."""
    section = memory_store.get_section(num)
    if section:
        return [section]
    # Fallback to PDF
    try:
        pdf_section = get_section_from_pdf(num)
        if pdf_section:
            return [pdf_section]
    except Exception:
        pass
    return None


# ============================================================
# GRAPH STATS
# ============================================================
@app.get("/api/graph/stats")
async def graph_stats():
    try:
        data = try_neo4j(
            lambda: _neo4j_graph_stats(),
            lambda: memory_store.get_graph_stats(),
        )
        return {"success": True, **data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


def _neo4j_graph_stats() -> dict:
    node_stats = run_query(queries.GET_GRAPH_STATS)
    rel_stats = run_query(queries.GET_RELATIONSHIP_STATS)
    return {
        "totalNodes": sum(n.get("count", 0) for n in node_stats),
        "totalRelationships": sum(r.get("count", 0) for r in rel_stats),
        "nodesByType": node_stats,
        "relationshipsByType": rel_stats,
    }


# ============================================================
# PDF STATS
# ============================================================
@app.get("/api/pdf/stats")
async def pdf_stats():
    """Return stats about the PDF extraction service."""
    return {"success": True, **get_pdf_stats()}


# ============================================================
# SERVE FRONTEND
# ============================================================
_public_dir = Path(__file__).parent.parent / "public"

# Mount static files for CSS, JS, etc.
app.mount("/css", StaticFiles(directory=str(_public_dir / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(_public_dir / "js")), name="js")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = _public_dir / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


# Catch-all for SPA-like routing (serve index.html for non-API routes)
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Don't catch API routes
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"error": "Not found"})
    index_path = _public_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return JSONResponse(status_code=404, content={"error": "Not found"})
