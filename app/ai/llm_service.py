"""
LLM Service — Google Gemini integration for natural language to Cypher
and structured response generation.
Includes retry logic with exponential backoff and model fallback.
"""
import re
import json
import time
import google.generativeai as genai
from app.ai.prompts import CYPHER_GENERATION_PROMPT, RESPONSE_GENERATION_PROMPT, SECTION_EXPLANATION_PROMPT, CHAT_SYSTEM_PROMPT
from app.db.neo4j_client import run_query
from app.config import settings
from app.data.pdf_service import get_pdf_context_for_query, is_ready as pdf_is_ready

_model = None
_fallback_model = None
_initialized = False

# Models to try in order (primary → fallback)
# gemini-2.5-flash is the current stable model with generous free tier
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-2.5-flash-lite", "gemini-2.0-flash"]

# Retry settings
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2  # seconds


def init_llm() -> bool:
    """Initialize the Gemini model with fallback options."""
    global _model, _fallback_model, _initialized

    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        print("⚠️  Gemini API key not configured. AI features will use fallback mode.")
        print("   → Set GEMINI_API_KEY in your .env file")
        print("   → Get a key at: https://aistudio.google.com/apikey")
        _initialized = False
        return False
    try:
        genai.configure(api_key=api_key)

        # Primary model
        _model = genai.GenerativeModel(PRIMARY_MODEL)

        # Set up fallback models
        for fb_name in FALLBACK_MODELS:
            try:
                _fallback_model = genai.GenerativeModel(fb_name)
                break
            except Exception:
                continue

        _initialized = True
        print(f"✅ Gemini AI initialized (primary: {PRIMARY_MODEL})")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Gemini: {e}")
        _model = None
        _fallback_model = None
        _initialized = False
        return False


def reinit_llm() -> bool:
    """Re-initialize LLM if the API key has changed."""
    global _model, _initialized
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        return False
    if _initialized and _model:
        return True
    return init_llm()


def _get_model():
    """Get the model, attempting re-init if not yet initialized."""
    if not _model:
        reinit_llm()
    return _model


def _call_gemini(prompt: str) -> str:
    """
    Call Gemini with retry logic and model fallback.
    Handles 429 rate limit errors with exponential backoff.
    Falls back to alternate models if primary is quota-exhausted.
    """
    models_to_try = [_model]
    if _fallback_model:
        models_to_try.append(_fallback_model)

    last_error = None

    for model in models_to_try:
        if model is None:
            continue

        for attempt in range(MAX_RETRIES):
            try:
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                last_error = e
                error_str = str(e)

                # Rate limit / quota error — retry with backoff
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    # Extract retry delay if provided
                    delay_match = re.search(r'retry.*?(\d+\.?\d*)\s*s', error_str, re.IGNORECASE)
                    if delay_match:
                        delay = min(float(delay_match.group(1)), 30)
                    else:
                        delay = RETRY_BASE_DELAY * (2 ** attempt)

                    if attempt < MAX_RETRIES - 1:
                        print(f"⏳ Rate limited, retrying in {delay:.0f}s (attempt {attempt + 2}/{MAX_RETRIES})...")
                        time.sleep(delay)
                        continue
                    else:
                        # Exhausted retries for this model, try next
                        print(f"⚠️  Rate limit persists on {model.model_name}, trying fallback...")
                        break
                else:
                    # Non-rate-limit error, don't retry
                    raise

    # All models and retries exhausted
    if last_error:
        raise last_error
    raise RuntimeError("No Gemini model available")


# ============================================================
# CORE AI FUNCTIONS
# ============================================================

def generate_cypher(question: str) -> dict:
    """Translate natural language question to Cypher query."""
    model = _get_model()
    if not model:
        return _fallback_cypher_generation(question)

    try:
        prompt = f'{CYPHER_GENERATION_PROMPT}\nQuestion: "{question}"\nCypher:'
        cypher = _call_gemini(prompt)

        # Clean up markdown fences
        cypher = re.sub(r"```cypher\n?", "", cypher, flags=re.IGNORECASE)
        cypher = re.sub(r"```\n?", "", cypher)
        cypher = cypher.strip()

        # Validate basic Cypher structure
        upper = cypher.upper()
        if "MATCH" not in upper and "RETURN" not in upper and "CALL" not in upper:
            print("Generated query may be invalid, using fallback")
            return _fallback_cypher_generation(question)

        return {"cypher": cypher, "source": "gemini"}
    except Exception as e:
        print(f"Cypher generation error: {e}")
        return _fallback_cypher_generation(question)


def generate_response(question: str, query_results: list, cypher: str) -> dict:
    """Generate a structured response from query results."""
    model = _get_model()
    if not model:
        return _fallback_response_generation(question, query_results)

    try:
        prompt = f"""{RESPONSE_GENERATION_PROMPT}

## User Question:
{question}

## Cypher Query Used:
{cypher}

## Query Results (from Neo4j Knowledge Graph):
{json.dumps(query_results, indent=2, default=str)}

Please provide a comprehensive, accurate, and well-structured response based on the query results above."""

        text = _call_gemini(prompt)
        return {
            "text": text,
            "source": "gemini",
            "grounded": True,
        }
    except Exception as e:
        print(f"Response generation error: {e}")
        return _fallback_response_generation(question, query_results)


def generate_explanation(section_data: dict) -> dict:
    """Generate section explanation with full context."""
    model = _get_model()
    if not model:
        return _fallback_explanation(section_data)

    try:
        prompt = f"""{SECTION_EXPLANATION_PROMPT}

## Section Data:
{json.dumps(section_data, indent=2, default=str)}"""

        text = _call_gemini(prompt)
        return {"text": text, "source": "gemini"}
    except Exception as e:
        print(f"Explanation generation error: {e}")
        return _fallback_explanation(section_data)


def process_natural_language_query(question: str) -> dict:
    """Process a complete natural language query end-to-end."""
    start_time = time.time()

    # Step 1: Generate Cypher from question
    result = generate_cypher(question)
    cypher = result["cypher"]
    cypher_source = result["source"]

    # Step 2: Execute the Cypher query
    query_results = []
    query_error = None
    try:
        query_results = run_query(cypher)
    except Exception as e:
        query_error = str(e)
        query_results = []

    # Step 3: Generate structured response
    if query_results:
        response = generate_response(question, query_results, cypher)
    else:
        response = {
            "text": (
                f"I encountered an error executing the query: {query_error}. Please try rephrasing your question."
                if query_error
                else 'No results found for your query. Try asking about specific section numbers (e.g., "What is Section 149?") or topics (e.g., "rules about directors").'
            ),
            "source": cypher_source,
            "grounded": False,
        }

    processing_time = int((time.time() - start_time) * 1000)

    return {
        "question": question,
        "cypher": cypher,
        "cypherSource": cypher_source,
        "results": query_results,
        "resultCount": len(query_results),
        "response": response["text"],
        "responseSource": response["source"],
        "grounded": response.get("grounded", False),
        "processingTimeMs": processing_time,
        "error": query_error,
    }


# ============================================================
# FALLBACK FUNCTIONS (when Gemini is not available)
# ============================================================

def _fallback_cypher_generation(question: str) -> dict:
    q = question.lower()

    # Section lookup
    section_match = re.search(r"section\s+(\d+)", q)
    if section_match:
        num = int(section_match.group(1))

        if any(w in q for w in ["amend", "change", "modified"]):
            return {
                "cypher": f"MATCH (s:Section {{number: {num}}})-[:AMENDED_BY]->(am:Amendment) OPTIONAL MATCH (aa:AmendmentAct)-[:CONTAINS_AMENDMENT]->(am) RETURN am.amendmentId AS id, am.type AS type, am.description AS description, am.originalText AS originalText, am.newText AS newText, am.year AS year, aa.fullTitle AS amendmentAct ORDER BY am.year",
                "source": "fallback",
            }

        if "rule" in q:
            return {
                "cypher": f"MATCH (s:Section {{number: {num}}})<-[:DERIVED_FROM]-(r:Rule) RETURN r.ruleId AS id, r.number AS number, r.title AS title, r.text AS text, r.category AS category",
                "source": "fallback",
            }

        if any(w in q for w in ["refer", "cross", "related"]):
            return {
                "cypher": f"MATCH (s:Section {{number: {num}}})-[r:REFERS_TO]->(ref:Section) RETURN ref.number AS number, ref.title AS title, r.context AS context UNION MATCH (ref:Section)-[r:REFERS_TO]->(s:Section {{number: {num}}}) RETURN ref.number AS number, ref.title AS title, r.context AS context",
                "source": "fallback",
            }

        if any(w in q for w in ["explain", "detail", "context"]):
            return {
                "cypher": f"MATCH (s:Section {{number: {num}}}) OPTIONAL MATCH (p:Part)-[:HAS_SECTION]->(s) OPTIONAL MATCH (s)-[:HAS_SUBSECTION]->(ss:SubSection) OPTIONAL MATCH (s)-[:AMENDED_BY]->(am:Amendment) OPTIONAL MATCH (s)<-[:DERIVED_FROM]-(r:Rule) OPTIONAL MATCH (s)-[:REFERS_TO]->(ref:Section) RETURN s.number AS number, s.title AS title, s.text AS originalText, s.effectiveText AS effectiveText, s.isAmended AS isAmended, p.title AS partTitle, collect(DISTINCT {{number: ss.number, text: ss.text}}) AS subsections, collect(DISTINCT {{type: am.type, description: am.description}}) AS amendments, collect(DISTINCT {{number: r.number, title: r.title}}) AS rules, collect(DISTINCT {{number: ref.number, title: ref.title}}) AS references",
                "source": "fallback",
            }

        # Default: get section content
        return {
            "cypher": f"MATCH (s:Section {{number: {num}}}) OPTIONAL MATCH (p:Part)-[:HAS_SECTION]->(s) RETURN s.number AS number, s.title AS title, s.effectiveText AS text, s.isAmended AS isAmended, p.title AS partTitle",
            "source": "fallback",
        }

    # Definition lookup
    if any(w in q for w in ["definition", "define", "meaning of", "what is a ", "what is an "]):
        term_match = re.search(r'(?:definition of|define|meaning of|what is (?:a |an )?)\"?([^\"?]+)\"?', q)
        term = term_match.group(1).strip() if term_match else question
        safe_term = term.replace("'", "\\'")
        return {
            "cypher": f"MATCH (s:Section {{number: 2}})-[:HAS_SUBSECTION]->(ss:SubSection) WHERE toLower(ss.text) CONTAINS toLower('{safe_term}') RETURN s.number AS sectionNumber, ss.number AS subsectionNumber, ss.text AS definition",
            "source": "fallback",
        }

    # Amendment queries
    if "amendment" in q:
        return {
            "cypher": "MATCH (am:Amendment) OPTIONAL MATCH (am)-[r]->(s:Section) WHERE type(r) IN ['SUBSTITUTES', 'INSERTS', 'DELETES'] RETURN am.type AS type, am.description AS description, am.targetSection AS targetSection, s.title AS sectionTitle, type(r) AS action, am.year AS year ORDER BY am.targetSection",
            "source": "fallback",
        }

    # Rule queries
    if "rule" in q:
        category = ""
        if "director" in q:
            category = "Directors"
        elif "audit" in q:
            category = "Audit"
        elif "csr" in q:
            category = "CSR"
        elif "dividend" in q:
            category = "Dividend"

        if category:
            return {
                "cypher": f"MATCH (r:Rule) WHERE r.category = '{category}' OPTIONAL MATCH (r)-[:DERIVED_FROM]->(s:Section) RETURN r.number AS ruleNumber, r.title AS ruleTitle, r.text AS ruleText, s.number AS sectionNumber, s.title AS sectionTitle",
                "source": "fallback",
            }
        return {
            "cypher": "MATCH (r:Rule) OPTIONAL MATCH (r)-[:DERIVED_FROM]->(s:Section) RETURN r.number AS number, r.title AS title, r.text AS text, r.category AS category, s.number AS sectionNumber ORDER BY r.number",
            "source": "fallback",
        }

    # Stats
    if any(w in q for w in ["statistic", "how many", "count", "summary", "overview"]):
        return {
            "cypher": "MATCH (n) WITH labels(n)[0] AS label, count(n) AS count RETURN label, count ORDER BY count DESC",
            "source": "fallback",
        }

    # Search (default)
    safe_q = question.replace("'", "\\'")
    return {
        "cypher": f"MATCH (s:Section) WHERE toLower(s.title) CONTAINS toLower('{safe_q}') OR toLower(s.effectiveText) CONTAINS toLower('{safe_q}') RETURN s.number AS number, s.title AS title, s.effectiveText AS text, s.isAmended AS isAmended ORDER BY s.number LIMIT 10",
        "source": "fallback",
    }


def _fallback_response_generation(question: str, results: list) -> dict:
    if not results:
        return {
            "text": 'No matching results found in the knowledge graph. Try asking about a specific section number (e.g., "What is Section 149?"), amendments, or rules.',
            "source": "fallback",
            "grounded": False,
        }

    text = f"## Query Results\n\nFound **{len(results)}** result(s) for your query.\n\n"
    for i, result in enumerate(results):
        text += f"### Result {i + 1}\n"
        for key, value in result.items():
            if value is not None:
                if isinstance(value, list):
                    text += f"- **{key}**: {json.dumps(value, default=str)}\n"
                else:
                    text += f"- **{key}**: {value}\n"
        text += "\n"

    return {"text": text, "source": "fallback", "grounded": True}


def _fallback_explanation(data: dict) -> dict:
    text = ""

    if data.get("number"):
        text += f"## Section {data['number']}: {data.get('title', 'Untitled')}\n\n"

    if data.get("partTitle"):
        text += f"**Part**: {data['partTitle']}\n\n"

    if data.get("effectiveText"):
        text += f"### Current Text\n{data['effectiveText']}\n\n"

    if data.get("isAmended"):
        text += "### ⚠️ This section has been amended\n"
        if data.get("originalText") and data["originalText"] != data.get("effectiveText"):
            text += f"**Original Text**: {data['originalText']}\n\n"

    amendments = data.get("amendments", [])
    if amendments:
        text += "### Amendments\n"
        for am in amendments:
            if am.get("type"):
                text += f"- **{am['type']}** ({am.get('year', 'N/A')}): {am.get('description', 'No description')}\n"
        text += "\n"

    rules = data.get("rules", [])
    if rules:
        text += "### Applicable Rules\n"
        for r in rules:
            if r.get("number"):
                text += f"- **Rule {r['number']}**: {r.get('title', r.get('text', 'No description'))}\n"
        text += "\n"

    refs_to = data.get("referencesTo", [])
    if refs_to:
        text += "### References To\n"
        for ref in refs_to:
            if ref.get("number"):
                text += f"- Section {ref['number']}: {ref.get('title', '')}\n"
        text += "\n"

    refs_by = data.get("referencedBy", [])
    if refs_by:
        text += "### Referenced By\n"
        for ref in refs_by:
            if ref.get("number"):
                text += f"- Section {ref['number']}: {ref.get('title', '')}\n"

    return {"text": text or "No detailed explanation available.", "source": "fallback"}


# ============================================================
# INTERACTIVE CHAT (ChatGPT-like conversational interface)
# ============================================================

# In-memory session store: session_id → list of {"role": "user"|"model", "parts": [text]}
_chat_sessions: dict[str, list] = {}

# Maximum messages to keep in a session for context window management
MAX_HISTORY_MESSAGES = 40


def chat_with_context(
    session_id: str,
    user_message: str,
    context_data: list | None = None,
) -> dict:
    """
    Handle an interactive chat turn with conversation history.
    
    Args:
        session_id: Unique session identifier for conversation continuity.
        user_message: The user's message text.
        context_data: Optional list of knowledge graph results to ground the response.
    
    Returns:
        dict with keys: reply, source, session_id, turn_count
    """
    model = _get_model()
    if not model:
        return _fallback_chat(user_message, context_data)

    # Ensure session exists
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = []

    history = _chat_sessions[session_id]

    # Build the user prompt — optionally enriched with graph context
    prompt_parts = []
    if context_data:
        prompt_parts.append(
            f"[Knowledge Graph Context — use this data to ground your answer]\n"
            f"{json.dumps(context_data, indent=2, default=str)}\n\n"
            f"[User Question]\n{user_message}"
        )
    else:
        prompt_parts.append(user_message)

    full_user_text = "".join(prompt_parts)

    # If no context_data was provided, try enriching with PDF content
    if not context_data and pdf_is_ready():
        try:
            pdf_context = get_pdf_context_for_query(user_message)
            if pdf_context:
                full_user_text = (
                    f"[PDF-Extracted Legal Reference — use this to ground your answer]\n"
                    f"{pdf_context}\n\n"
                    f"[User Question]\n{user_message}"
                )
        except Exception:
            pass  # PDF enrichment is best-effort

    try:
        # Create a Gemini chat session with system instruction and history
        chat = model.start_chat(history=history)

        # If this is the first message in the session, prepend system prompt
        if len(history) == 0:
            # Use system instruction via the first exchange
            system_setup = CHAT_SYSTEM_PROMPT
            first_prompt = f"{system_setup}\n\n---\n\nUser message:\n{full_user_text}"
            response = _call_gemini_chat(chat, first_prompt)
        else:
            response = _call_gemini_chat(chat, full_user_text)

        # Update history with the new exchange
        history.append({"role": "user", "parts": [full_user_text]})
        history.append({"role": "model", "parts": [response]})

        # Trim if history is too long
        if len(history) > MAX_HISTORY_MESSAGES:
            # Keep the first 2 messages (system prompt exchange) and last N
            keep_start = 2
            keep_end = MAX_HISTORY_MESSAGES - keep_start
            history[:] = history[:keep_start] + history[-keep_end:]

        return {
            "reply": response,
            "source": "gemini",
            "session_id": session_id,
            "turn_count": len(history) // 2,
        }

    except Exception as e:
        print(f"Chat error: {e}")
        return _fallback_chat(user_message, context_data)


def _call_gemini_chat(chat, message: str) -> str:
    """Call Gemini chat with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = chat.send_message(message)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                if attempt < MAX_RETRIES - 1:
                    print(f"⏳ Chat rate limited, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
            raise
    raise RuntimeError("Chat retries exhausted")


def clear_chat_session(session_id: str) -> bool:
    """Clear a chat session's history."""
    if session_id in _chat_sessions:
        del _chat_sessions[session_id]
        return True
    return False


def get_chat_sessions() -> list[str]:
    """List all active session IDs."""
    return list(_chat_sessions.keys())


def _fallback_chat(user_message: str, context_data: list | None) -> dict:
    """Provide a reasonable response when Gemini is unavailable."""
    if context_data and len(context_data) > 0:
        text = f"## Query Results\n\nI found **{len(context_data)}** result(s) from the knowledge graph.\n\n"
        for i, item in enumerate(context_data[:5]):
            text += f"### Result {i + 1}\n"
            for key, value in item.items():
                if value is not None:
                    text += f"- **{key}**: {value}\n"
            text += "\n"
        text += "\n*Note: AI assistant is currently unavailable. Showing raw graph data.*"
    else:
        text = (
            "I'm currently unable to process your request through the AI assistant. "
            "However, you can try:\n\n"
            "- Asking about a specific **section number** (e.g., 'What is Section 149?')\n"
            "- Querying **amendments** or **rules**\n"
            "- Using the **Browse** tab to explore sections directly\n\n"
            "*The AI service will be restored once the Gemini API connection is re-established.*"
        )

    return {
        "reply": text,
        "source": "fallback",
        "session_id": "",
        "turn_count": 0,
    }

