from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable

# ── Colour palette ─────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1a2f5a")
MID_BLUE    = colors.HexColor("#2563eb")
LIGHT_BLUE  = colors.HexColor("#dbeafe")
ACCENT      = colors.HexColor("#0ea5e9")
GREEN       = colors.HexColor("#16a34a")
LIGHT_GREEN = colors.HexColor("#dcfce7")
ORANGE      = colors.HexColor("#ea580c")
LIGHT_ORANGE= colors.HexColor("#ffedd5")
PURPLE      = colors.HexColor("#7c3aed")
LIGHT_PURPLE= colors.HexColor("#ede9fe")
GRAY_BG     = colors.HexColor("#f1f5f9")
GRAY_BORDER = colors.HexColor("#cbd5e1")
WHITE       = colors.white
BLACK       = colors.HexColor("#0f172a")

W, H = A4

# ── Custom flowables ────────────────────────────────────────────────────────────
class ColorBar(Flowable):
    def __init__(self, color, height=4, width=None):
        super().__init__()
        self._color = color
        self._h = height
        self._w = width

    def wrap(self, availW, availH):
        self._w = self._w or availW
        return self._w, self._h

    def draw(self):
        self.canv.setFillColor(self._color)
        self.canv.rect(0, 0, self._w, self._h, stroke=0, fill=1)


class SectionBox(Flowable):
    """Coloured heading banner."""
    def __init__(self, text, bg=DARK_BLUE, fg=WHITE, font_size=13):
        super().__init__()
        self._text = text
        self._bg = bg
        self._fg = fg
        self._fs = font_size
        self._h = font_size + 14

    def wrap(self, availW, availH):
        self._w = availW
        return availW, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(self._bg)
        c.roundRect(0, 0, self._w, self._h, 4, stroke=0, fill=1)
        c.setFillColor(self._fg)
        c.setFont("Helvetica-Bold", self._fs)
        c.drawString(10, 5, self._text)


class ConceptBox(Flowable):
    """Rounded box with title + body text."""
    def __init__(self, title, body_lines, bg=LIGHT_BLUE, title_bg=MID_BLUE,
                 title_fg=WHITE, body_fg=BLACK, width=None):
        super().__init__()
        self.title = title
        self.body_lines = body_lines
        self.bg = bg
        self.title_bg = title_bg
        self.title_fg = title_fg
        self.body_fg = body_fg
        self._w = width
        line_h = 14
        self._h = 26 + len(body_lines) * line_h + 8

    def wrap(self, availW, availH):
        if not self._w:
            self._w = availW
        return self._w, self._h

    def draw(self):
        c = self.canv
        w, h = self._w, self._h
        c.setFillColor(self.bg)
        c.roundRect(0, 0, w, h, 6, stroke=0, fill=1)
        c.setStrokeColor(GRAY_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, w, h, 6, stroke=1, fill=0)
        # title bar
        c.setFillColor(self.title_bg)
        c.roundRect(0, h - 26, w, 26, 6, stroke=0, fill=1)
        c.rect(0, h - 26, w, 13, stroke=0, fill=1)
        c.setFillColor(self.title_fg)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(10, h - 18, self.title)
        # body
        c.setFillColor(self.body_fg)
        c.setFont("Helvetica", 9)
        y = h - 38
        for line in self.body_lines:
            c.drawString(12, y, line)
            y -= 14


class ArrowConnector(Flowable):
    """Simple downward arrow."""
    def __init__(self, label="", color=MID_BLUE):
        super().__init__()
        self._label = label
        self._color = color

    def wrap(self, availW, availH):
        self._w = availW
        return availW, 28

    def draw(self):
        c = self.canv
        mx = self._w / 2
        c.setStrokeColor(self._color)
        c.setFillColor(self._color)
        c.setLineWidth(1.5)
        c.line(mx, 28, mx, 8)
        c.setFillColor(self._color)
        c.beginPath()
        c.moveTo(mx - 5, 8)
        c.lineTo(mx + 5, 8)
        c.lineTo(mx, 0)
        c.closePath()
        c.fill()
        if self._label:
            c.setFont("Helvetica-Oblique", 8)
            c.setFillColor(self._color)
            c.drawCentredString(mx + 30, 12, self._label)


# ── Styles ──────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

styles = {
    "title":    S("title",    fontName="Helvetica-Bold",   fontSize=26, textColor=WHITE,     alignment=TA_CENTER, leading=32),
    "subtitle": S("subtitle", fontName="Helvetica",        fontSize=13, textColor=LIGHT_BLUE, alignment=TA_CENTER, leading=18),
    "h2":       S("h2",       fontName="Helvetica-Bold",   fontSize=14, textColor=DARK_BLUE,  spaceBefore=10, spaceAfter=4),
    "h3":       S("h3",       fontName="Helvetica-Bold",   fontSize=11, textColor=MID_BLUE,   spaceBefore=6,  spaceAfter=3),
    "body":     S("body",     fontName="Helvetica",        fontSize=9.5,textColor=BLACK,      leading=14, spaceAfter=4, alignment=TA_JUSTIFY),
    "bullet":   S("bullet",   fontName="Helvetica",        fontSize=9.5,textColor=BLACK,      leading=14, leftIndent=14, bulletIndent=4, spaceAfter=2),
    "code":     S("code",     fontName="Courier",          fontSize=8.5,textColor=BLACK,      backColor=GRAY_BG, borderPadding=6, leading=12),
    "caption":  S("caption",  fontName="Helvetica-Oblique",fontSize=8.5,textColor=colors.HexColor("#64748b"), alignment=TA_CENTER),
    "tag":      S("tag",      fontName="Helvetica-Bold",   fontSize=9,  textColor=WHITE,      backColor=MID_BLUE, borderPadding=3, alignment=TA_CENTER),
}

def body(txt): return Paragraph(txt, styles["body"])
def h2(txt):   return Paragraph(txt, styles["h2"])
def h3(txt):   return Paragraph(txt, styles["h3"])
def bullet(txt): return Paragraph(f"&#8226;  {txt}", styles["bullet"])
def sp(n=6):   return Spacer(1, n)
def hr():      return HRFlowable(width="100%", thickness=0.5, color=GRAY_BORDER, spaceAfter=6)


def info_table(rows, col_widths=None, header=True):
    col_widths = col_widths or [80*mm, 95*mm]
    t = Table(rows, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("BACKGROUND",  (0,0), (-1,0 if header else -1), DARK_BLUE),
        ("TEXTCOLOR",   (0,0), (-1,0 if header else -1), WHITE),
        ("FONTNAME",    (0,0), (-1,0 if header else -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, GRAY_BG]),
        ("GRID",        (0,0), (-1,-1), 0.4, GRAY_BORDER),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]
    t.setStyle(TableStyle(style))
    return t


def code_block(lines):
    text = "<br/>".join(lines)
    return Paragraph(text, styles["code"])


# ── Cover page ──────────────────────────────────────────────────────────────────
def cover_page():
    story = []
    story.append(Spacer(1, 25*mm))

    # gradient-like header band using nested tables
    cover_data = [[Paragraph(
        "<font color='white' size='28'><b>Gen-AI Architecture</b></font><br/>"
        "<font color='#93c5fd' size='14'>A Complete Visual Guide</font><br/><br/>"
        "<font color='#bfdbfe' size='10'>"
        "LLM &nbsp;|&nbsp; RAG &nbsp;|&nbsp; Vector DB &nbsp;|&nbsp; "
        "MCP &nbsp;|&nbsp; Agentic AI &nbsp;|&nbsp; Agents &nbsp;|&nbsp; n8n"
        "</font>",
        ParagraphStyle("cov", alignment=TA_CENTER, leading=22)
    )]]
    ct = Table(cover_data, colWidths=[165*mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), DARK_BLUE),
        ("TOPPADDING",   (0,0), (-1,-1), 22),
        ("BOTTOMPADDING",(0,0), (-1,-1), 22),
        ("LEFTPADDING",  (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 10),
    ]))
    story.append(ct)
    story.append(sp(10))

    story.append(ColorBar(ACCENT, height=5))
    story.append(sp(18))

    # 3-column tag row
    tags = [["LLM", "RAG", "Vector DB"], ["MCP", "Agentic AI", "n8n"]]
    for row in tags:
        td = [[Paragraph(f"<b>{t}</b>", ParagraphStyle("tg", alignment=TA_CENTER,
               fontSize=10, textColor=WHITE))] for t in row]
        tt = Table([td], colWidths=[52*mm, 52*mm, 52*mm])
        tt.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (0,0), MID_BLUE),
            ("BACKGROUND",   (1,0), (1,0), GREEN),
            ("BACKGROUND",   (2,0), (2,0), PURPLE),
            ("TOPPADDING",   (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",(0,0), (-1,-1), 8),
            ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
            ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ]))
        story.append(tt)
        story.append(sp(6))

    story.append(sp(14))
    story.append(body(
        "This document provides a comprehensive overview of the modern Generative AI "
        "stack — from foundational large language models to fully autonomous agentic "
        "systems. Each concept is explained with diagrams, real-world flow examples, "
        "and practical implementation guidance."
    ))
    story.append(sp(6))
    story.append(Paragraph("2026  ·  Gen-AI Reference Guide  ·  v1.0",
                            ParagraphStyle("footer", alignment=TA_CENTER,
                                           fontSize=9, textColor=colors.HexColor("#94a3b8"))))
    return story


# ── Section 1: LLM ──────────────────────────────────────────────────────────────
def section_llm():
    s = [PageBreak()]
    s.append(SectionBox("  1.  Large Language Model (LLM)", bg=DARK_BLUE))
    s.append(sp(8))
    s.append(body(
        "A <b>Large Language Model (LLM)</b> is a neural network trained on vast amounts "
        "of text data to understand and generate human language. Based on the Transformer "
        "architecture, LLMs learn statistical relationships between tokens and can reason, "
        "summarise, translate, and generate content across virtually any domain."
    ))
    s.append(sp(6))

    s.append(h3("How It Works"))
    steps = [
        ["Stage", "What Happens"],
        ["1. Pre-training", "Model reads billions of documents, learns token probabilities"],
        ["2. Tokenisation", "Text split into tokens (~4 chars each); model thinks in tokens"],
        ["3. Attention", "Transformer weighs relationships between all tokens in context"],
        ["4. Prediction", "Model predicts next token — everything emerges from this"],
        ["5. Fine-tuning / RLHF", "Model tuned on instructions + human feedback to be helpful"],
    ]
    s.append(info_table(steps, col_widths=[55*mm, 110*mm]))
    s.append(sp(8))

    s.append(h3("Key Concepts"))
    concepts = [
        ["Term", "Meaning"],
        ["Parameters",      "Neural network weights — more = more capable (8B to 1T+)"],
        ["Context Window",  "Max tokens model sees at once (e.g. 200 000 tokens)"],
        ["Temperature",     "0 = deterministic output  |  1+ = creative / random"],
        ["Token",           "Chunk of text (~4 chars); models price by token count"],
        ["Hallucination",   "Model generates plausible-sounding but incorrect facts"],
        ["RLHF",            "Reinforcement Learning from Human Feedback — aligns the model"],
    ]
    s.append(info_table(concepts, col_widths=[45*mm, 120*mm]))
    s.append(sp(8))

    s.append(h3("Popular LLMs"))
    llms = [
        ["Model",         "Provider",   "Notes"],
        ["Claude Sonnet / Opus", "Anthropic", "Strong reasoning, long context, safe"],
        ["GPT-4o",        "OpenAI",     "Multimodal, widely integrated"],
        ["Gemini 1.5 Pro","Google",     "Very long context window (1M tokens)"],
        ["Llama 3",       "Meta",       "Open-source, self-hostable"],
    ]
    s.append(info_table(llms, col_widths=[50*mm, 40*mm, 75*mm]))
    return s


# ── Section 2: RAG ──────────────────────────────────────────────────────────────
def section_rag():
    s = [PageBreak()]
    s.append(SectionBox("  2.  Retrieval-Augmented Generation (RAG)", bg=colors.HexColor("#166534")))
    s.append(sp(8))
    s.append(body(
        "<b>RAG</b> enhances LLM responses by first <i>retrieving</i> relevant documents "
        "from a knowledge base, then feeding those documents as context to the LLM before "
        "it generates an answer. This gives the model access to private, up-to-date, or "
        "domain-specific knowledge without retraining."
    ))
    s.append(sp(8))

    s.append(h3("RAG Pipeline — Step by Step"))
    pipeline = [
        ["Step", "Action", "Detail"],
        ["1", "Ingest Documents",   "Load PDFs, web pages, databases into pipeline"],
        ["2", "Chunk Text",         "Split into overlapping chunks (~500 tokens each)"],
        ["3", "Embed Chunks",       "Convert each chunk to a vector using embedding model"],
        ["4", "Store in Vector DB", "Save vector + original text in vector database"],
        ["5", "User Query",         "User asks a question"],
        ["6", "Embed Query",        "Convert query to a vector (same embedding model)"],
        ["7", "Similarity Search",  "Find top-k most similar vectors in Vector DB"],
        ["8", "Retrieve Chunks",    "Fetch the original text of matching chunks"],
        ["9", "Augment Prompt",     "Inject retrieved chunks into LLM system prompt"],
        ["10","Generate Answer",    "LLM answers grounded in the retrieved context"],
    ]
    s.append(info_table(pipeline, col_widths=[12*mm, 50*mm, 103*mm]))
    s.append(sp(8))

    s.append(h3("Why RAG?"))
    for b in [
        "Overcomes LLM knowledge cutoff — always uses fresh data",
        "Enables private knowledge Q&amp;A without exposing data to training",
        "Reduces hallucinations — LLM cites retrieved source text",
        "Cheaper than retraining — update the knowledge base, not the model",
    ]:
        s.append(bullet(b))
    s.append(sp(6))

    s.append(h3("RAG vs Fine-tuning"))
    cmp = [
        ["",            "RAG",                  "Fine-tuning"],
        ["When to use", "Dynamic / private data","Fixed domain knowledge"],
        ["Cost",        "Low (index update)",   "High (GPU training)"],
        ["Freshness",   "Real-time",            "Static until re-trained"],
        ["Transparency","Cites sources",        "Knowledge baked in"],
    ]
    s.append(info_table(cmp, col_widths=[35*mm, 65*mm, 65*mm]))
    return s


# ── Section 3: Vector DB ────────────────────────────────────────────────────────
def section_vectordb():
    s = [PageBreak()]
    s.append(SectionBox("  3.  Vector Database", bg=PURPLE))
    s.append(sp(8))
    s.append(body(
        "A <b>Vector Database</b> stores data as high-dimensional numerical vectors "
        "(embeddings) and enables ultra-fast <i>semantic similarity search</i>. Unlike "
        "traditional SQL databases that match exact values, vector DBs find content that "
        "is <i>semantically similar</i> in meaning — even if the words are different."
    ))
    s.append(sp(8))

    s.append(h3("Embedding — Text to Numbers"))
    s.append(code_block([
        'Text:  "dog"   →  [0.21, -0.54,  0.87, 0.33, ...] (1536 dims)',
        'Text:  "cat"   →  [0.19, -0.51,  0.83, 0.31, ...] (similar → nearby)',
        'Text:  "car"   →  [0.92,  0.13, -0.44, 0.71, ...] (different → far away)',
        "",
        "Similarity = cosine distance between vectors",
    ]))
    s.append(sp(8))

    s.append(h3("SQL vs Vector DB"))
    cmp = [
        ["Feature",        "SQL Database",              "Vector Database"],
        ["Search type",    "Exact / keyword match",     "Semantic / meaning match"],
        ["Query example",  "WHERE name = 'dog'",        "find things like dog"],
        ["Data type",      "Structured rows",           "Unstructured text / images"],
        ["Speed on vectors","Slow (full scan)",         "Fast (ANN index)"],
        ["Use case",       "Transactions, reports",     "RAG, recommendations, search"],
    ]
    s.append(info_table(cmp, col_widths=[40*mm, 62*mm, 63*mm]))
    s.append(sp(8))

    s.append(h3("Popular Vector Databases"))
    dbs = [
        ["Name",      "Type",              "Best For"],
        ["Pinecone",  "Managed cloud",     "Production, zero-ops"],
        ["Qdrant",    "Open source",       "High performance, Rust-based"],
        ["ChromaDB",  "Open source",       "Local dev, Python-native"],
        ["Weaviate",  "Open source",       "Multi-modal + GraphQL API"],
        ["pgvector",  "Postgres extension","Teams already using Postgres"],
        ["FAISS",     "Library (Meta)",    "In-memory research / prototyping"],
        ["Milvus",    "Open source",       "Enterprise scale"],
    ]
    s.append(info_table(dbs, col_widths=[35*mm, 50*mm, 80*mm]))
    return s


# ── Section 4: MCP ──────────────────────────────────────────────────────────────
def section_mcp():
    s = [PageBreak()]
    s.append(SectionBox("  4.  Model Context Protocol (MCP)", bg=ORANGE))
    s.append(sp(8))
    s.append(body(
        "<b>MCP</b> is an open standard by Anthropic that provides a unified protocol "
        "for AI agents to connect to external tools, APIs, and data sources. Instead of "
        "writing custom integration code for every API, developers wrap the API once as "
        "an MCP Server — and any MCP-compatible agent can use it immediately."
    ))
    s.append(sp(8))

    s.append(h3("MCP Architecture"))
    arch = [
        ["Layer",       "Component",     "Responsibility"],
        ["Agent",       "LLM + Logic",   "Decides which tool to call and when"],
        ["MCP Client",  "Built into app","Sends tool requests using MCP protocol"],
        ["MCP Server",  "API wrapper",   "Receives MCP calls, executes real API"],
        ["External API","GitHub / Jira…","The actual service being controlled"],
    ]
    s.append(info_table(arch, col_widths=[35*mm, 45*mm, 85*mm]))
    s.append(sp(8))

    s.append(h3("MCP Core Concepts"))
    concepts = [
        ["Concept",   "Description"],
        ["Tools",     "Functions the agent can call, e.g. create_issue(), send_message()"],
        ["Resources", "Data sources the agent can read, e.g. files, DB rows"],
        ["Prompts",   "Reusable prompt templates exposed by the MCP server"],
        ["Server",    "Process that wraps an API and speaks the MCP protocol"],
        ["Client",    "Component inside the agent app that connects to servers"],
    ]
    s.append(info_table(concepts, col_widths=[35*mm, 130*mm]))
    s.append(sp(8))

    s.append(h3("Official MCP Servers (ready to use)"))
    servers = [
        ["Package",                                  "Connects To"],
        ["@modelcontextprotocol/server-github",      "GitHub — issues, PRs, repos"],
        ["@modelcontextprotocol/server-slack",       "Slack — messages, channels"],
        ["@modelcontextprotocol/server-postgres",    "PostgreSQL — queries, schema"],
        ["@modelcontextprotocol/server-filesystem",  "Local file system"],
        ["@modelcontextprotocol/server-brave-search","Brave web search"],
        ["@modelcontextprotocol/server-google-maps", "Google Maps — directions, places"],
    ]
    s.append(info_table(servers, col_widths=[90*mm, 75*mm]))
    s.append(sp(8))

    s.append(h3("MCP vs Direct API Integration"))
    cmp = [
        ["",              "Direct API",               "MCP"],
        ["Setup per API", "Custom code every time",   "Standardised once"],
        ["Reusability",   "Agent-specific",           "Any agent can use"],
        ["Tool discovery","Manual",                   "Automatic"],
        ["Maintenance",   "High",                     "Low"],
        ["Security",      "Per integration",          "Centralised"],
    ]
    s.append(info_table(cmp, col_widths=[40*mm, 62*mm, 63*mm]))
    return s


# ── Section 5: Agentic AI ───────────────────────────────────────────────────────
def section_agentic():
    s = [PageBreak()]
    s.append(SectionBox("  5.  Agentic AI", bg=colors.HexColor("#7c3aed")))
    s.append(sp(8))
    s.append(body(
        "<b>Agentic AI</b> refers to AI systems that autonomously plan, decide, and "
        "take sequences of actions to achieve a goal — rather than answering a single "
        "prompt. The LLM acts as the reasoning engine inside a loop that continues until "
        "the goal is complete."
    ))
    s.append(sp(8))

    s.append(h3("Traditional LLM vs Agentic AI"))
    cmp = [
        ["Dimension",       "Traditional LLM",       "Agentic AI"],
        ["Input",           "One prompt",            "A high-level goal"],
        ["Output",          "One response",          "Series of actions"],
        ["Memory",          "None (stateless)",      "Maintains state across steps"],
        ["Tools",           "No",                    "Yes — search, code, APIs"],
        ["Decision-making", "Single step",           "Multi-step planning & replanning"],
        ["Loops",           "No",                    "Runs until goal is achieved"],
    ]
    s.append(info_table(cmp, col_widths=[40*mm, 60*mm, 65*mm]))
    s.append(sp(8))

    s.append(h3("The Agent Loop — ReAct Pattern"))
    s.append(code_block([
        "Thought : I need to find the current stock price of AAPL.",
        "Action  : search('AAPL stock price today')",
        "Observe : AAPL is trading at $189.43",
        "Thought : I now have the answer.",
        "Answer  : Apple (AAPL) is currently trading at $189.43.",
    ]))
    s.append(sp(8))

    s.append(h3("Agent Components"))
    comp = [
        ["Component",      "Role"],
        ["LLM",            "Reasoning engine — understands goal, plans, decides next action"],
        ["Memory",         "Short-term (chat history) + long-term (Vector DB)"],
        ["Tools",          "Functions the agent can invoke (search, code, APIs via MCP)"],
        ["System Prompt",  "Defines agent persona, constraints, available tools"],
        ["Orchestrator",   "Manages the loop, routes to specialist agents, collects results"],
    ]
    s.append(info_table(comp, col_widths=[40*mm, 125*mm]))
    s.append(sp(8))

    s.append(h3("Multi-Agent Pattern"))
    s.append(body(
        "Complex tasks can be split across <b>specialist agents</b> coordinated by an "
        "<b>Orchestrator Agent</b>:"
    ))
    s.append(sp(4))
    for b in [
        "<b>Orchestrator</b> — receives goal, plans, delegates to specialists",
        "<b>Research Agent</b> — web search, RAG lookups",
        "<b>Coder Agent</b> — writes and executes code",
        "<b>Writer Agent</b> — formats and polishes final output",
        "<b>API Agent</b> — calls external services via MCP",
    ]:
        s.append(bullet(b))

    s.append(sp(8))
    s.append(h3("Popular Agent Frameworks"))
    fw = [
        ["Framework",        "Language", "Notes"],
        ["Claude Agent SDK", "Python",   "Anthropic-native, MCP-first"],
        ["LangGraph",        "Python",   "Graph-based stateful agents"],
        ["AutoGen",          "Python",   "Microsoft, multi-agent conversations"],
        ["CrewAI",           "Python",   "Role-based crew of agents"],
        ["n8n",              "Visual",   "No-code / low-code agent builder"],
    ]
    s.append(info_table(fw, col_widths=[50*mm, 30*mm, 85*mm]))
    return s


# ── Section 6: n8n ──────────────────────────────────────────────────────────────
def section_n8n():
    s = [PageBreak()]
    s.append(SectionBox("  6.  n8n — Visual Agentic Workflow Builder", bg=colors.HexColor("#b45309")))
    s.append(sp(8))
    s.append(body(
        "<b>n8n</b> is an open-source workflow automation platform with first-class "
        "support for building AI agents visually. It lets you wire together triggers, "
        "LLMs, memory, tools, and APIs on a canvas — no boilerplate code needed."
    ))
    s.append(sp(8))

    s.append(h3("Core Nodes"))
    nodes = [
        ["Node",            "Purpose"],
        ["Trigger",         "Starts the flow — Chat, Webhook, Schedule, Email"],
        ["AI Agent",        "The brain: LLM + tools + memory orchestrator"],
        ["Chat Model",      "Connect Claude, GPT-4o, Gemini to the agent"],
        ["Memory",          "Window Buffer or Vector Store for conversation history"],
        ["Tool Nodes",      "SerpAPI, HTTP Request, Gmail, Slack, Jira, DB, etc."],
        ["MCP Client Tool", "Connect to any MCP server as an agent tool"],
        ["Execute Workflow","Call a sub-workflow (specialist agent pattern)"],
        ["Switch / Merge",  "Route and combine results for multi-agent patterns"],
    ]
    s.append(info_table(nodes, col_widths=[45*mm, 120*mm]))
    s.append(sp(8))

    s.append(h3("AI Agent Node Settings"))
    settings = [
        ["Setting",             "Recommended Value"],
        ["System Prompt",       "Define persona, goal, and available tools"],
        ["Max Iterations",      "10–15 (prevents infinite loops)"],
        ["Agent Type",          "Tools Agent (most flexible)"],
        ["Return Intermediate", "On during development for debugging"],
    ]
    s.append(info_table(settings, col_widths=[55*mm, 110*mm]))
    s.append(sp(8))

    s.append(h3("Example Flows in n8n"))
    flows = [
        ["Flow",                 "Trigger",     "Agent Tools",                 "Output"],
        ["Customer Support",     "Webhook",     "DB lookup, Shipping API",     "Email reply"],
        ["Daily Research Digest","Schedule",    "Web search, Summarise",       "Gmail to team"],
        ["GitHub to Jira Sync",  "GitHub event","Jira MCP, Slack MCP",         "Jira ticket + Slack"],
        ["RAG Q&A Bot",          "Chat",        "Vector DB, HTTP Request",     "Chat response"],
    ]
    s.append(info_table(flows, col_widths=[38*mm, 28*mm, 55*mm, 44*mm]))
    return s


# ── Section 7: End-to-End Architecture ─────────────────────────────────────────
def section_e2e():
    s = [PageBreak()]
    s.append(SectionBox("  7.  End-to-End Architecture — All Concepts Together", bg=MID_BLUE))
    s.append(sp(10))

    s.append(h3("Full System Flow Diagram"))
    s.append(sp(4))

    def flow_box(label, bg, fg=WHITE, w=165*mm):
        d = [[Paragraph(f"<b>{label}</b>",
                        ParagraphStyle("fb", alignment=TA_CENTER,
                                       fontSize=10, textColor=fg))]]
        t = Table(d, colWidths=[w])
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), bg),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("ROUNDEDCORNERS",(0,0),(-1,-1),6),
        ]))
        return t

    def arrow_row():
        d = [[Paragraph("&#9660;", ParagraphStyle("arr", alignment=TA_CENTER,
                                                   fontSize=16, textColor=MID_BLUE))]]
        t = Table(d, colWidths=[165*mm])
        t.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),
                                ("BOTTOMPADDING",(0,0),(-1,-1),2)]))
        return t

    s.append(flow_box("USER  —  'Summarise AI news, create Jira ticket, notify Slack'", DARK_BLUE))
    s.append(arrow_row())
    s.append(flow_box("TRIGGER LAYER  (n8n Chat Trigger / Webhook / Schedule)", colors.HexColor("#b45309")))
    s.append(arrow_row())
    s.append(flow_box("ORCHESTRATOR AGENT  (LLM: Claude Sonnet + System Prompt + Memory)", MID_BLUE))
    s.append(sp(4))

    # 3-column tools row
    tool_data = [[
        Paragraph("<b>RAG Tool</b><br/><font size='8'>1. Embed query<br/>2. Search Vector DB<br/>3. Retrieve chunks<br/>4. Inject into prompt</font>",
                  ParagraphStyle("tc", alignment=TA_CENTER, fontSize=9, leading=13, textColor=WHITE)),
        Paragraph("<b>Specialist Agents</b><br/><font size='8'>Research Agent<br/>Coder Agent<br/>Writer Agent<br/>(via Execute Workflow)</font>",
                  ParagraphStyle("tc", alignment=TA_CENTER, fontSize=9, leading=13, textColor=WHITE)),
        Paragraph("<b>MCP Tools</b><br/><font size='8'>GitHub Server<br/>Jira Server<br/>Slack Server<br/>Web Search</font>",
                  ParagraphStyle("tc", alignment=TA_CENTER, fontSize=9, leading=13, textColor=WHITE)),
    ]]
    tt = Table(tool_data, colWidths=[52*mm, 55*mm, 52*mm])
    tt.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), GREEN),
        ("BACKGROUND",   (1,0),(1,0), PURPLE),
        ("BACKGROUND",   (2,0),(2,0), ORANGE),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
        ("INNERGRID",    (0,0),(-1,-1), 2, WHITE),
    ]))
    s.append(tt)
    s.append(sp(4))

    # underlying stores row
    store_data = [[
        Paragraph("<b>Vector DB</b><br/><font size='8'>Pinecone / Qdrant<br/>Stores embeddings<br/>Semantic search</font>",
                  ParagraphStyle("sc", alignment=TA_CENTER, fontSize=9, leading=13, textColor=BLACK)),
        Paragraph("<b>LLM</b><br/><font size='8'>Claude / GPT-4o<br/>Reasons over results<br/>Generates response</font>",
                  ParagraphStyle("sc", alignment=TA_CENTER, fontSize=9, leading=13, textColor=BLACK)),
        Paragraph("<b>External APIs</b><br/><font size='8'>GitHub API<br/>Jira REST API<br/>Slack API</font>",
                  ParagraphStyle("sc", alignment=TA_CENTER, fontSize=9, leading=13, textColor=BLACK)),
    ]]
    st = Table(store_data, colWidths=[52*mm, 55*mm, 52*mm])
    st.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), GRAY_BG),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
        ("GRID",         (0,0),(-1,-1), 0.5, GRAY_BORDER),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
    ]))
    s.append(st)
    s.append(arrow_row())
    s.append(flow_box("FINAL RESPONSE TO USER  (Chat / Email / Slack notification)", GREEN))

    s.append(sp(12))
    s.append(h3("Worked Example — Step by Step"))
    steps = [
        ["#", "Who Acts",          "What Happens"],
        ["1",  "User",             "Asks: 'Summarise today AI news, create Jira ticket, notify Slack'"],
        ["2",  "n8n Trigger",      "Webhook fires, passes message to Orchestrator Agent"],
        ["3",  "Orchestrator LLM", "Plans 5 steps; chooses web-search tool first"],
        ["4",  "MCP: Web Search",  "Calls Tavily/Brave API, returns 5 articles"],
        ["5",  "RAG",              "Embeds articles, stores in Vector DB for future use"],
        ["6",  "Orchestrator LLM", "Retrieves chunks, writes 200-word summary"],
        ["7",  "MCP: Jira Server", "Calls create_issue() → returns ticket DEV-201"],
        ["8",  "MCP: Slack Server","Calls send_message(#ai-updates) → team notified"],
        ["9",  "Orchestrator LLM", "Confirms all steps done, composes final reply"],
        ["10", "User",             "Receives: summary + 'DEV-201 created + Slack notified'"],
    ]
    s.append(info_table(steps, col_widths=[10*mm, 38*mm, 117*mm]))
    return s


# ── Section 8: Concept Summary ──────────────────────────────────────────────────
def section_summary():
    s = [PageBreak()]
    s.append(SectionBox("  8.  Concept Summary — One-Page Reference", bg=DARK_BLUE))
    s.append(sp(10))

    s.append(h3("What Each Concept Does"))
    summary = [
        ["Concept",      "What It Is",                  "Role in the System"],
        ["LLM",          "Neural net trained on text",  "The brain — understands, reasons, decides"],
        ["Agentic AI",   "LLM + loop + tools",          "Autonomously completes multi-step goals"],
        ["Agent",        "LLM + memory + tools",        "Worker that executes a specific task"],
        ["RAG",          "Retrieve docs → feed to LLM", "Gives LLM access to private/fresh data"],
        ["Vector DB",    "Stores text as vectors",      "Enables semantic search for RAG"],
        ["MCP",          "Standard API protocol",       "Connects agents to any external API/tool"],
        ["n8n",          "Visual workflow builder",     "Wires all of the above together visually"],
    ]
    s.append(info_table(summary, col_widths=[28*mm, 58*mm, 79*mm]))
    s.append(sp(10))

    s.append(h3("How They Connect"))
    s.append(body(
        "Every layer depends on the one below. The <b>LLM</b> is the foundational engine. "
        "<b>Agentic AI</b> wraps the LLM in a loop with tools and memory. Individual "
        "<b>Agents</b> are specialised instances of Agentic AI. <b>RAG</b> feeds relevant "
        "knowledge to agents using a <b>Vector DB</b> as the semantic memory store. "
        "<b>MCP</b> standardises how agents call external APIs. <b>n8n</b> is the canvas "
        "that visually connects all layers into production-ready workflows."
    ))
    s.append(sp(10))

    s.append(h3("Technology Stack at a Glance"))
    stack = [
        ["Layer",             "Open-source Options",         "Managed / Cloud Options"],
        ["LLM",               "Llama 3, Mistral, Falcon",    "Claude, GPT-4o, Gemini"],
        ["Agent Framework",   "LangGraph, CrewAI, AutoGen",  "Claude Agent SDK"],
        ["RAG Orchestration", "LlamaIndex, LangChain",       "Built into Claude API"],
        ["Vector DB",         "Qdrant, Chroma, FAISS",       "Pinecone, Weaviate Cloud"],
        ["MCP Servers",       "Community GitHub servers",    "Anthropic official servers"],
        ["Workflow Builder",  "n8n (self-hosted)",           "n8n.cloud, Zapier AI"],
        ["Embedding Model",   "sentence-transformers",       "OpenAI ada-002, Cohere"],
    ]
    s.append(info_table(stack, col_widths=[38*mm, 62*mm, 65*mm]))
    s.append(sp(10))

    s.append(h3("Quick-Start Checklist — Build Your First Agent"))
    checklist = [
        "Get an LLM API key (Anthropic / OpenAI)",
        "Choose a Vector DB (ChromaDB for local, Pinecone for cloud)",
        "Ingest your documents → chunk → embed → store",
        "Set up an MCP server for each external API you need",
        "Open n8n, add Chat Trigger + AI Agent + Chat Model + Memory",
        "Connect tool nodes (web search, your MCP servers)",
        "Write a clear system prompt for your agent",
        "Set Max Iterations to 10–15",
        "Test with a real end-to-end query",
        "Activate workflow and monitor logs",
    ]
    for i, item in enumerate(checklist, 1):
        s.append(bullet(f"<b>Step {i}:</b>  {item}"))

    s.append(sp(14))
    s.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE))
    s.append(sp(6))
    s.append(Paragraph(
        "Gen-AI Architecture Reference Guide  ·  2026  ·  Powered by Claude",
        ParagraphStyle("foot", alignment=TA_CENTER, fontSize=8,
                       textColor=colors.HexColor("#94a3b8"))
    ))
    return s


# ── Build PDF ───────────────────────────────────────────────────────────────────
def build():
    path = r"D:\2025_Workspace\GenAI_Architecture.pdf"
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm,  bottomMargin=16*mm,
        title="Gen-AI Architecture Guide",
        author="Gen-AI Reference",
    )

    story = []
    story += cover_page()
    story += section_llm()
    story += section_rag()
    story += section_vectordb()
    story += section_mcp()
    story += section_agentic()
    story += section_n8n()
    story += section_e2e()
    story += section_summary()

    doc.build(story)
    print(f"PDF saved to: {path}")

build()
