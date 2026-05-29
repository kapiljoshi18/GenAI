# GenAI Architecture — Visual Guide & Live Demo

A complete, beginner-friendly walkthrough of the modern Generative-AI stack:
**LLM · RAG · Vector DB · MCP · Agentic AI · Agents · n8n** — and how they fit
together end-to-end.

## Contents

| File | Description |
|------|-------------|
| [`GenAI_LiveDemo.html`](GenAI_LiveDemo.html) | Interactive, self-contained browser demo. Click through each concept and watch it run — token-by-token LLM generation, semantic vector search, the RAG pipeline, an MCP tool call, the agent Reason→Act→Observe loop, an n8n workflow, and a full end-to-end flow. No install needed. |
| [`GenAI_Architecture.pdf`](GenAI_Architecture.pdf) | Professional PDF reference guide with diagrams, comparison tables, and a worked end-to-end example. |
| [`gen_ai_pdf.py`](gen_ai_pdf.py) | Python (ReportLab) script that generates the PDF. |

## Quick Start

**View the live demo:** open `GenAI_LiveDemo.html` in any browser.

**Regenerate the PDF:**
```bash
pip install reportlab
python gen_ai_pdf.py
```

## Concepts at a Glance

| Concept | What it is | Role in the system |
|---------|-----------|--------------------|
| **LLM** | Neural net trained on text | The brain — understands & reasons |
| **Agentic AI** | LLM + loop + tools | Completes multi-step goals autonomously |
| **RAG** | Retrieve docs → feed to LLM | Gives the LLM private / fresh knowledge |
| **Vector DB** | Stores text as vectors | Enables semantic search for RAG |
| **MCP** | Standard API protocol | Connects agents to any external tool |
| **n8n** | Visual workflow builder | Wires all layers together visually |
