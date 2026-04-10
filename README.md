# 🏛️ LexGraph AI — Legal Knowledge Graph System

> **AI-powered Legal Knowledge Graph for Accurate, Traceable Querying of Indian Corporate Law**

Built with **Neo4j** (Graph Database), **Python / FastAPI** (Backend), **Google Gemini** (AI), and **pdfplumber** (PDF Extraction).

LexGraph AI models the **Companies Act, 2013** (470+ sections), the **Corporate Laws (Amendment) Act, 2026**, and the **Companies Rules, 2014** as an interconnected knowledge graph. It supports natural language querying, amendment traceability, cross-reference traversal, and AI-powered legal explanations — all grounded in structured graph data.

---

## 📑 Table of Contents

- [Graph Schema Design](#-graph-schema-design)
- [Key Modeling Decisions](#-key-modeling-decisions)
- [How to Run the System](#-how-to-run-the-system)
- [How to Run Queries](#-how-to-run-queries)
- [API Reference](#-api-reference)
- [AI Integration](#-ai-integration)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)

---

## 📐 Graph Schema Design

### Visual Schema

```
                              ┌─────────────────┐
                              │      Act         │
                              │ (Companies Act)  │
                              └────────┬─────────┘
                                       │ HAS_PART
                              ┌────────▼─────────┐
                              │      Part         │
                              │ (Part I, II...)   │
                              └────────┬─────────┘
                                       │ HAS_SECTION
                    ┌──────────────────▼──────────────────┐
                    │            Section                   │
                    │  (S.2, S.149, S.185, ... 421 total)  │
                    └──┬──────┬──────┬──────┬──────┬──────┘
                       │      │      │      │      │
            HAS_SUBSECTION   │   AMENDED_BY │   HAS_RULE
                       │      │      │      │      │
                  ┌────▼──┐   │  ┌───▼────┐ │  ┌───▼────┐
                  │SubSec │   │  │Amendmt │ │  │  Rule  │
                  └───────┘   │  └───┬────┘ │  └────────┘
                              │      │      │
                       REFERS_TO  CONTAINS_AMENDMENT
                              │      │
                         ┌────▼──┐ ┌─▼──────────────┐
                         │Section│ │  AmendmentAct   │
                         └───────┘ │ (Corp Laws 2026)│
                                   └─────────────────┘
```

### Node Types (6 Labels)

| Node Label      | Key Properties                                                  | Description                              |
|------------------|-----------------------------------------------------------------|------------------------------------------|
| **Act**          | `name`, `year`, `fullTitle`, `dateEnacted`, `shortDescription`  | The legislation itself                   |
| **Part**         | `partId`, `number`, `title`                                     | Structural divisions of the Act          |
| **Section**      | `sectionId`, `number`, `title`, `text`, `effectiveText`, `isAmended`, `actName`, `source` | Individual legal provisions   |
| **SubSection**   | `subSectionId`, `number`, `text`, `sectionNumber`               | Clauses within a section                 |
| **Amendment**    | `amendmentId`, `type`, `description`, `targetSection`, `year`, `originalText`, `newText` | Individual amendment entries |
| **AmendmentAct** | `name`, `year`, `fullTitle`, `dateEnacted` *(also labeled Act)* | The amending legislation                 |
| **Rule**         | `ruleId`, `number`, `title`, `text`, `category`, `year`         | Delegated rules under the Act            |

### Relationship Types (9 Types)

| Relationship           | Direction                  | Description                                         |
|------------------------|----------------------------|-----------------------------------------------------|
| `HAS_PART`             | Act → Part                 | Act is divided into structural parts                |
| `HAS_SECTION`          | Part → Section             | Part contains sections                              |
| `HAS_SUBSECTION`       | Section → SubSection       | Section has sub-clauses                             |
| `AMENDED_BY`           | Section → Amendment        | Tracks which amendments affect a section            |
| `SUBSTITUTES`          | Amendment → Section        | Amendment replaces section text                     |
| `INSERTS`              | Amendment → Section        | Amendment adds new text to a section                |
| `DELETES`              | Amendment → Section        | Amendment removes text from a section               |
| `CONTAINS_AMENDMENT`   | AmendmentAct → Amendment   | Groups amendments under their parent act            |
| `DERIVED_FROM`         | Rule → Section             | Rule implements/derives from a section              |
| `HAS_RULE`             | Section → Rule             | Bidirectional link for rule lookup                  |
| `REFERS_TO`            | Section → Section          | Cross-reference between sections (with `context`)   |

### Constraints & Indexes

```cypher
-- Uniqueness Constraints
CREATE CONSTRAINT FOR (a:Act) REQUIRE a.name IS UNIQUE
CREATE CONSTRAINT FOR (s:Section) REQUIRE s.sectionId IS UNIQUE
CREATE CONSTRAINT FOR (am:Amendment) REQUIRE am.amendmentId IS UNIQUE
CREATE CONSTRAINT FOR (r:Rule) REQUIRE r.ruleId IS UNIQUE
CREATE CONSTRAINT FOR (p:Part) REQUIRE p.partId IS UNIQUE

-- Performance Indexes
CREATE INDEX FOR (s:Section) ON (s.number)
CREATE INDEX FOR (s:Section) ON (s.title)
CREATE INDEX FOR (r:Rule) ON (r.number)
CREATE INDEX FOR (am:Amendment) ON (am.type)

-- Full-Text Search Indexes
CREATE FULLTEXT INDEX section_fulltext FOR (s:Section) ON EACH [s.title, s.text, s.effectiveText]
CREATE FULLTEXT INDEX rule_fulltext FOR (r:Rule) ON EACH [r.title, r.text]
```

---

## 🏗️ Key Modeling Decisions

### 1. Dual Text Fields for Amendment Traceability

Each `Section` stores both `text` (the original enacted text) and `effectiveText` (after amendments are applied). This enables before/after comparison without losing the legislative history.

```cypher
-- Compare original vs. amended text for Section 149
MATCH (s:Section {number: 149})
RETURN s.text AS original, s.effectiveText AS current, s.isAmended
```

### 2. Typed Amendment Relationships (Not Generic "AMENDS")

Instead of a single generic `AMENDS` relationship, three specific types are used: `SUBSTITUTES`, `INSERTS`, `DELETES`. This mirrors real legislative drafting conventions and allows precise Cypher queries by amendment operation.

```cypher
-- Find all sections where text was substituted by the 2026 Amendment
MATCH (am:Amendment)-[:SUBSTITUTES]->(s:Section)
WHERE am.year = 2026
RETURN s.number, s.title, am.description
```

### 3. Bidirectional Amendment Links

Both `Section → AMENDED_BY → Amendment` and `Amendment → SUBSTITUTES → Section` exist. This optimizes queries from either direction — "what amendments affect Section X?" and "which sections does this amendment target?"

### 4. Two-Phase Data Ingestion Pipeline

- **Phase 1 — PDF Extraction**: `pdfplumber` parses all three PDFs (Companies Act: 370 pages, Rules: 195 pages, Amendment: 98 pages) using regex-based section recognition. This yields full coverage: **421 sections**, **43 rules**, **45 amendment clauses**.
- **Phase 2 — Curated Enrichment**: A hand-curated `sample_data.py` enriches the graph with subsections, precise amendment descriptions, cross-references, and rule categories. MERGE operations update PDF-created nodes rather than duplicating them.

### 5. Cross-Reference Context

`REFERS_TO` relationships carry a `context` property explaining *why* sections are linked — not just *that* they are linked.

```cypher
MATCH (s1:Section)-[r:REFERS_TO]->(s2:Section)
RETURN s1.number, s2.number, r.context
-- e.g. Section 149 → Section 152: "Independent directors under S.149(6) must meet conditions in S.152"
```

### 6. Graceful Degradation Architecture

The system operates in three tiers:
1. **Neo4j + Gemini AI** → Full graph queries with AI-generated responses
2. **Neo4j + Fallback Rules** → Graph queries with pattern-matched responses (no API key needed)
3. **In-Memory Store + PDF** → No database required; identical API responses from Python dictionaries

This ensures the system always works, even without Neo4j running or a Gemini API key.

### 7. AmendmentAct as Multi-Label Node

`AmendmentAct` carries both `:Act` and `:AmendmentAct` labels, allowing it to participate in queries for "all acts" while remaining distinguishable as an amending statute.

---

## 🚀 How to Run the System

### Prerequisites

| Requirement         | Version  | Notes                                                |
|---------------------|----------|------------------------------------------------------|
| **Python**          | 3.9+     | Required                                             |
| **Neo4j**           | 5.x      | Desktop or Server ([download](https://neo4j.com/download/)) |
| **Gemini API Key**  | —        | Optional ([get free key](https://aistudio.google.com/apikey)) |

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/LexGraph-AI.git
cd LexGraph-AI

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your Neo4j password and (optionally) Gemini API key

# 4. Start Neo4j
#    Option A: Neo4j Desktop → Start your database
#    Option B: Command line → neo4j console

# 5. (Optional) Pre-ingest data into Neo4j
python scripts/ingest_data.py

# 6. Start the server
python run.py
```

Open **http://localhost:3000** in your browser.

> **Note**: If Neo4j is not running, the server automatically starts in **fallback mode** using an in-memory store. All features remain functional — just without persistent graph storage.

### What Happens at Startup

1. **PDF Parsing** — All three legal PDFs are parsed with `pdfplumber` (~30s for 10 MB of PDFs)
2. **AI Init** — Google Gemini model is loaded (or fallback rules activated)
3. **Neo4j Check** — Connection verified; if unavailable, in-memory store loaded
4. **Schema Setup** — Constraints and indexes created in Neo4j
5. **Data Ingestion** — Two-phase pipeline populates the graph (Phase 1: PDF → 421 sections; Phase 2: curated enrichment)

---

## 🔍 How to Run Queries

### Option 1: Web Interface (Recommended)

Navigate to `http://localhost:3000` and use the **AI Query** tab. Type natural language questions:

| Example Query                                          | What It Does                                    |
|--------------------------------------------------------|-------------------------------------------------|
| "What does Section 149 say about independent directors?" | Retrieves Section 149 with full context         |
| "What amendments affected Section 185?"                | Lists all amendments targeting Section 185       |
| "What are the rules for CSR?"                          | Retrieves all CSR-related rules                  |
| "Define 'related party'"                               | Searches Section 2 definitions                   |
| "Compare original and amended text of Section 135"     | Shows before/after for CSR provision             |
| "Show me the knowledge graph statistics"               | Returns node/relationship counts                 |

### Option 2: REST API (curl / Postman)

```bash
# Natural language query
curl -X POST http://localhost:3000/api/query/natural \
  -H "Content-Type: application/json" \
  -d '{"question": "What amendments affected Section 185?"}'

# Interactive chat (with session memory)
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Section 149", "session_id": "my-session"}'

# Get a specific section
curl http://localhost:3000/api/section/149

# Get amendments for a section
curl http://localhost:3000/api/section/185/amendments

# Full-text search
curl "http://localhost:3000/api/search?q=independent+director"

# Health check
curl http://localhost:3000/api/health
```

### Option 3: Direct Cypher Queries (Neo4j Browser)

Open Neo4j Browser at `http://localhost:7474` and run Cypher directly:

```cypher
-- 1. Get all sections of the Companies Act (with part info)
MATCH (a:Act {name: 'Companies Act'})-[:HAS_PART]->(p:Part)-[:HAS_SECTION]->(s:Section)
RETURN p.number AS part, p.title AS partTitle, s.number AS section, s.title
ORDER BY s.number

-- 2. Find all amendments and their target sections
MATCH (aa:AmendmentAct)-[:CONTAINS_AMENDMENT]->(am:Amendment)-[r]->(s:Section)
WHERE type(r) IN ['SUBSTITUTES', 'INSERTS', 'DELETES']
RETURN am.type AS amendmentType, type(r) AS operation,
       s.number AS targetSection, s.title AS sectionTitle,
       am.description AS description
ORDER BY s.number

-- 3. Trace the amendment history of a specific section
MATCH (s:Section {number: 185})
OPTIONAL MATCH (am:Amendment)-[r]->(s)
WHERE type(r) IN ['SUBSTITUTES', 'INSERTS', 'DELETES']
RETURN s.title, s.text AS originalText, s.effectiveText AS currentText,
       collect({type: am.type, description: am.description, year: am.year}) AS amendments

-- 4. Cross-reference traversal (2-hop)
MATCH path = (s:Section {number: 149})-[:REFERS_TO*1..2]->(related:Section)
RETURN s.number AS from, related.number AS to, related.title
ORDER BY related.number

-- 5. Find rules derived from a section
MATCH (s:Section {number: 135})<-[:DERIVED_FROM]-(r:Rule)
RETURN r.number, r.title, r.text, r.category

-- 6. Full-text search across all sections
CALL db.index.fulltext.queryNodes("section_fulltext", "independent director")
YIELD node, score
RETURN node.number AS section, node.title, score
ORDER BY score DESC LIMIT 10

-- 7. Graph statistics
MATCH (n)
RETURN labels(n)[0] AS label, count(n) AS count
ORDER BY count DESC

-- 8. Find all sections amended by the 2026 Act
MATCH (aa:AmendmentAct {year: 2026})-[:CONTAINS_AMENDMENT]->(am)-[:SUBSTITUTES|INSERTS|DELETES]->(s:Section)
RETURN DISTINCT s.number AS section, s.title, am.type AS amendmentType
ORDER BY s.number

-- 9. Section with all connected entities (neighborhood query)
MATCH (s:Section {number: 149})
OPTIONAL MATCH (s)-[r]-(connected)
RETURN s, r, connected

-- 10. Sections with the most amendments
MATCH (s:Section)-[:AMENDED_BY]->(am:Amendment)
RETURN s.number, s.title, count(am) AS amendmentCount
ORDER BY amendmentCount DESC
LIMIT 10
```

---

## 📡 API Reference

### Core Endpoints

| Method | Endpoint                            | Description                                      |
|--------|-------------------------------------|--------------------------------------------------|
| GET    | `/api/health`                       | Health check (Neo4j, Gemini, PDF status)         |
| POST   | `/api/reconnect`                    | Re-attempt Neo4j/Gemini connections              |

### Section Endpoints

| Method | Endpoint                            | Description                                      |
|--------|-------------------------------------|--------------------------------------------------|
| GET    | `/api/sections`                     | List all sections                                |
| GET    | `/api/section/{number}`             | Get section with subsections                     |
| GET    | `/api/section/{number}/amendments`  | Amendments targeting this section                |
| GET    | `/api/section/{number}/rules`       | Rules derived from this section                  |
| GET    | `/api/section/{number}/explain`     | AI-powered explanation with full context          |
| GET    | `/api/section/{number}/references`  | Cross-references (to and from)                   |
| GET    | `/api/section/{number}/history`     | Complete amendment chain                         |

### Browse Endpoints

| Method | Endpoint                            | Description                                      |
|--------|-------------------------------------|--------------------------------------------------|
| GET    | `/api/amendments`                   | List all amendments                              |
| GET    | `/api/rules`                        | List all rules                                   |
| GET    | `/api/search?q=term`                | Full-text search (sections + rules)              |
| GET    | `/api/graph/stats`                  | Graph node/relationship statistics               |
| GET    | `/api/pdf/stats`                    | PDF extraction statistics                        |

### AI Endpoints

| Method | Endpoint                            | Description                                      |
|--------|-------------------------------------|--------------------------------------------------|
| POST   | `/api/query/natural`                | Natural language → Cypher → structured response  |
| POST   | `/api/chat`                         | Interactive chat with session memory             |
| POST   | `/api/chat/clear`                   | Clear a chat session                             |

### Example Response: Natural Language Query

```json
{
  "success": true,
  "question": "What amendments affected Section 185?",
  "cypher": "MATCH (s:Section {number: 185})-[:AMENDED_BY]->(am:Amendment) RETURN am",
  "cypherSource": "gemini",
  "results": [...],
  "resultCount": 2,
  "response": "## Amendments to Section 185\n\nSection 185 (Loan to Directors) has been amended by...",
  "responseSource": "gemini",
  "grounded": true,
  "processingTimeMs": 1243
}
```

---

## 🧠 AI Integration

The intelligence layer uses **Google Gemini (gemini-2.0-flash)** for:

1. **Natural Language → Cypher Translation** — Schema-aware few-shot prompting converts questions to graph queries
2. **Grounded Response Generation** — AI generates structured, formatted answers from query results
3. **Section Explanations** — Full legal context with amendments, rules, and cross-references
4. **Conversational Chat** — Session-based memory for follow-up questions

**Traceability**: Every AI response includes the generated Cypher query, result count, processing time, and `grounded` flag indicating whether the answer is backed by graph data.

**Fallback**: When Gemini is unavailable, pattern-matching rules generate appropriate Cypher queries and structured responses — the system remains fully functional.

---

## 📁 Project Structure

```
LexGraph AI/
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── run.py                            # Server entry point (uvicorn)
├── README.md                         # This file
│
├── app/                              # Backend application
│   ├── __init__.py
│   ├── config.py                     # Settings (env vars, validation)
│   ├── main.py                       # FastAPI routes, middleware, startup
│   │
│   ├── db/                           # Database layer
│   │   ├── neo4j_client.py           # Neo4j driver singleton + query execution
│   │   ├── schema.py                 # Constraints, indexes, schema init
│   │   ├── ingest.py                 # Two-phase data ingestion pipeline
│   │   └── memory_store.py           # In-memory fallback (no DB required)
│   │
│   ├── data/                         # Data sources
│   │   ├── sample_data.py            # Curated legal dataset (48 KB)
│   │   └── pdf_service.py            # PDF extraction + search (pdfplumber)
│   │
│   ├── queries/                      # Query library
│   │   └── cypher_queries.py         # 15+ pre-built Cypher queries
│   │
│   └── ai/                           # AI layer
│       ├── prompts.py                # System prompts + few-shot examples
│       └── llm_service.py            # Gemini integration + fallback logic
│
├── scripts/                          # CLI tools
│   └── ingest_data.py                # Standalone data ingestion script
│
├── public/                           # Frontend (served by FastAPI)
│   ├── index.html                    # Main HTML (premium dark UI)
│   ├── css/styles.css                # Styling (glassmorphism, animations)
│   └── js/app.js                     # Client-side logic (chat, browse, graph)
│
└── *.pdf                             # Source legal documents (3 PDFs, ~10 MB)
    ├── Companies Act, 2013.pdf
    ├── Companies Rules, 2014.pdf
    └── Corporate Laws (Amendment) Act, 2026 - converted.pdf
```

---

## 📊 Technology Stack

| Component          | Technology                          | Purpose                              |
|--------------------|-------------------------------------|--------------------------------------|
| **Graph Database** | Neo4j 5.x                          | Knowledge graph storage & Cypher     |
| **Backend**        | Python 3.9+ / FastAPI              | REST API, middleware, routing        |
| **AI Engine**      | Google Gemini (gemini-2.0-flash)   | NL→Cypher, explanations, chat       |
| **PDF Extraction** | pdfplumber                         | Parse legal PDFs to structured data  |
| **Frontend**       | Vanilla HTML / CSS / JavaScript    | Premium dark-mode chat interface     |
| **Query Language** | Cypher                             | Graph traversal and pattern matching |
| **Server**         | Uvicorn (ASGI)                     | High-performance async server        |

---

## 📊 Data Coverage

| Source Document                           | Pages | Extracted             |
|-------------------------------------------|-------|-----------------------|
| Companies Act, 2013                       | 370   | 421 sections indexed  |
| Companies Rules, 2014                     | 195   | 43 rule entries       |
| Corporate Laws (Amendment) Act, 2026      | 98    | 45 amendment clauses  |

**Total Graph Size**: ~550 nodes, ~290 relationships (when fully ingested)

---

## 📝 License

MIT
