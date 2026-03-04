# 🏷️ Competitor Pricing & Intelligence Tracker Agent

> **Built on the [Aden Hive](https://github.com/aden-hive/hive) framework** — an outcome-driven, self-healing AI agent development platform.

An autonomous AI agent that monitors competitor websites for **pricing changes**, product launches, and marketing shifts. It produces structured weekly digests with **price-change alerts**, per-competitor pricing tables, and **30-day trend analysis**.

---

## 📋 Table of Contents

- [Why This Agent?](#-why-this-agent)
- [Architecture](#-architecture)
- [How It Works](#-how-it-works)
- [Prerequisites](#-prerequisites)
- [Setup & Installation](#-setup--installation)
- [Running the Agent](#-running-the-agent)
- [Input Format](#-input-format)
- [Sample Output](#-sample-output)
- [Project Structure](#-project-structure)
- [What Hive Brings to the Table](#-what-hive-brings-to-the-table)
- [Feedback & Contributing](#-feedback--contributing)

---

## 🎯 Why This Agent?

Every product and GTM team manually tracks competitor pricing — checking websites weekly, eyeballing changelogs, Googling press releases. This agent **automates that entire workflow**:

| Pain Point | How This Agent Solves It |
|---|---|
| Manually checking 5+ competitor pricing pages | **Pricing Scraper** node extracts all tiers, prices, and features automatically |
| Missing a competitor's price increase | **Change Detection** compares against stored historical snapshots and flags changes |
| Scattered competitive intel across bookmarks | **Unified Report** — one HTML digest with all findings, organized by competitor |
| No trend visibility | **30-Day Trend Analysis** surfaces strategic patterns across the competitive landscape |
| Competitor websites redesign and break your scraping scripts | **Hive's self-healing framework** detects failures and evolves the agent's graph |

---

## 🏗️ Architecture

The agent is built as a **7-node directed graph** that executes sequentially:

```
┌──────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
│  intake   │───▶│ pricing-scraper │───▶│ product-monitor │───▶│ news-monitor │
│ (client)  │    │                 │    │                 │    │              │
└──────────┘    └─────────────────┘    └─────────────────┘    └──────┬───────┘
                                                                     │
┌──────────┐    ┌──────────────┐    ┌──────────────────────────┐     │
│  report   │◀──│   analysis   │◀──│ aggregator + change det. │◀────┘
│ (client)  │    │              │    │                          │
└──────────┘    └──────────────┘    └──────────────────────────┘
```

| Node | Type | Purpose | Tools Used |
|------|------|---------|------------|
| **intake** | `event_loop` (client-facing) | Collect competitor list, pricing URLs, focus areas & alert thresholds | — |
| **pricing-scraper** | `event_loop` | Scrape competitor pricing pages for plans, tiers, monthly/annual prices & features | `web_search`, `web_scrape` |
| **product-monitor** | `event_loop` | Scan blogs, changelogs for feature launches, marketing changes, hiring signals | `web_search`, `web_scrape` |
| **news-monitor** | `event_loop` | Search news, press releases, funding announcements | `web_search`, `web_scrape` |
| **aggregator** | `event_loop` | Merge + deduplicate all findings; compare pricing vs historical snapshot; flag alerts | `save_data`, `load_data`, `list_data_files` |
| **analysis** | `event_loop` | Extract key highlights, pricing trends, strategic recommendations | `save_data`, `load_data`, `list_data_files` |
| **report** | `event_loop` (client-facing) | Generate a polished HTML report with price alerts, comparison tables & trends | `save_data`, `serve_file_to_user` |

---

## ⚙️ How It Works

1. **You provide competitors** — names, website URLs, and optionally direct pricing page URLs
2. **The agent autonomously**:
   - Scrapes each competitor's pricing page for plan names, prices, and features
   - Scans blogs, changelogs, and marketing pages for product/positioning updates
   - Searches news sites for press releases, funding rounds, and acquisitions
   - Loads the previous pricing snapshot (if any) and flags changes
   - Analyses all findings for key highlights and 30-day trends
   - Generates a complete HTML report and serves it to you
3. **On subsequent runs**, the aggregator automatically compares new prices against historical data and alerts you to changes

---

## 📦 Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **An OpenAI API key** (or any LiteLLM-compatible provider)

---

## 🚀 Setup & Installation

### 1. Clone and set up the Hive framework

```bash
git clone https://github.com/thatditsyboy/aden.git
cd aden

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Set up core framework
cd core && uv sync && cd ..

# Set up tools
cd tools && uv sync && cd ..
```

### 2. Configure your API key

```bash
# Create the Hive config directory
mkdir -p ~/.hive

# Set up the LLM configuration
cat > ~/.hive/configuration.json << 'EOF'
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key_env_var": "OPENAI_API_KEY",
    "max_tokens": 16384
  }
}
EOF

# Set your API key as an environment variable
export OPENAI_API_KEY="sk-your-key-here"
```

> ⚠️ **Never commit your API key!** The `.env` file is already in `.gitignore`. Use the `.env.example` as a reference.

---

## ▶️ Running the Agent

### Interactive Shell (recommended for first use)

```bash
cd examples/templates
uv run --directory ../../core python -m pricing_tracker_agent shell
```

### CLI One-Shot Run

```bash
cd examples/templates

# Track Notion vs Coda vs ClickUp
OPENAI_API_KEY="sk-..." PYTHONPATH=.:$PYTHONPATH \
uv run --directory ../../core python -m pricing_tracker_agent run \
  --competitors '[
    {"name":"Notion","website":"https://notion.so","pricing_url":"https://notion.so/pricing"},
    {"name":"Coda","website":"https://coda.io","pricing_url":"https://coda.io/pricing"},
    {"name":"ClickUp","website":"https://clickup.com","pricing_url":"https://clickup.com/pricing"}
  ]' \
  --focus-areas "pricing,features,marketing_copy,partnerships" \
  --frequency weekly \
  --alert-threshold "any" \
  --verbose
```

### Validate & Info

```bash
uv run --directory ../../core python -m pricing_tracker_agent validate
# ✅ Agent is valid

uv run --directory ../../core python -m pricing_tracker_agent info
# Agent: Competitor Pricing & Intelligence Tracker
# Nodes: intake, pricing-scraper, product-monitor, news-monitor, aggregator, analysis, report
```

### TUI Dashboard

```bash
uv run --directory ../../core python -m pricing_tracker_agent tui
```

---

## 📥 Input Format

```json
{
  "competitors": [
    {
      "name": "Notion",
      "website": "https://notion.so",
      "pricing_url": "https://notion.so/pricing"
    },
    {
      "name": "Coda",
      "website": "https://coda.io",
      "pricing_url": null
    }
  ],
  "focus_areas": ["pricing", "features", "marketing_copy", "partnerships"],
  "report_frequency": "weekly",
  "alert_threshold": "any"
}
```

- **`pricing_url`** — optional; if omitted, the agent will use `web_search` to find it
- **`alert_threshold`** — `"any"` flags all changes; `"5%"` only flags changes above 5%

---

## 📊 Sample Output

The agent produces an HTML report saved to `~/.hive/agents/pricing_tracker_agent/data/` containing:

### 🚨 Price Change Alerts
Flagged pricing increases/decreases with old vs new prices and % change (compared against historical snapshots)

### 🔥 Key Highlights
The 3-5 most important competitive moves requiring attention

### 💰 Current Pricing Landscape
Per-competitor tables with plan names, monthly/annual prices, and key features:

| Plan | Monthly | Annual | Key Features |
|------|---------|--------|-------------|
| Free | $0/mo | N/A | Basic features, Limited blocks |
| Pro | $10/mo | $96/year | Unlimited blocks, Advanced collaboration, Admin tools |

### 📊 Detailed Findings
Per-competitor tables with Category, Update, Source URL, and Date

### 📈 30-Day Trends
Strategic pattern analysis across the competitive landscape

---

## 📁 Project Structure

```
examples/templates/pricing_tracker_agent/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point (run, tui, shell, validate, info)
├── agent.py             # Goal definition, node/edge wiring, agent class
├── agent.json           # Serialized graph for Hive UI
├── config.py            # RuntimeConfig & AgentMetadata
├── mcp_servers.json     # MCP tools server configuration
├── .env.example         # Environment variable template
├── README.md            # This file
└── nodes/
    └── __init__.py      # All 7 node definitions with system prompts
```

### Key Files Explained

| File | What It Does |
|------|-------------|
| `agent.py` | Defines the **Goal** (with success criteria like "scrape pricing for each competitor"), wires the 7 nodes together with **EdgeSpec** connections, and provides the `PricingTrackerAgent` class with lifecycle methods |
| `nodes/__init__.py` | Contains all **7 NodeSpec definitions**, each with a detailed system prompt that instructs the LLM on exactly what to do, what tools to call, and how to structure its output |
| `agent.json` | The serialized JSON representation of the entire graph — used by the Hive web UI and server for visualization and execution |
| `config.py` | Loads LLM configuration from `~/.hive/configuration.json` (provider, model, API key env var) |
| `mcp_servers.json` | Points to the Hive MCP tools server which provides `web_search`, `web_scrape`, `save_data`, `load_data`, etc. |

---

## 🐝 What Hive Brings to the Table

This agent is built on the **[Aden Hive](https://github.com/aden-hive/hive)** framework. Here's what the framework provides vs what this agent adds:

### Hive Framework Capabilities (what we get for free)

| Capability | Description |
|---|---|
| **Goal-Driven Graph Execution** | Define objectives + success criteria; the framework evaluates whether the agent achieved its goal |
| **Event Loop Nodes** | Each node is an autonomous LLM loop that can call tools, set outputs, and ask the user questions |
| **Dynamic Edge Routing** | Conditional edges allow the graph to dynamically skip nodes or take alternative paths |
| **Shared Memory** | All nodes share a memory store — outputs from earlier nodes are automatically available to later ones |
| **MCP Tool Integration** | Connects to any MCP-compatible tool server (web search, web scrape, GitHub, file utilities) |
| **Self-Healing / Adaptiveness** | When a node fails (e.g. a website changes its DOM), the framework captures failure data and can evolve the agent |
| **Human-in-the-Loop** | Pause execution for human input with configurable timeouts |
| **Observability** | WebSocket streaming for live monitoring of agent execution |
| **TUI Dashboard** | Built-in terminal UI for interactive agent sessions |
| **Historical Data Persistence** | `save_data` / `load_data` tools for storing snapshots across runs |

### What This Agent Specifically Adds

| Feature | How It's Implemented |
|---|---|
| **Dedicated Pricing Scraper** | A specialized node with prompts tuned for extracting plan names, prices, features per tier |
| **Price Change Detection** | The aggregator loads `pricing_snapshot_latest.json` and compares tier-by-tier |
| **Alert Thresholds** | User-configurable sensitivity (e.g. only flag changes > 5%) |
| **Price Accuracy Constraint** | A hard constraint ensuring prices are transcribed exactly as shown — no rounding |
| **Multi-Source Intelligence** | 3 parallel scraping nodes (pricing + product + news) for comprehensive coverage |
| **Pricing-Focused HTML Report** | Custom report template with price alert badges, pricing comparison tables, and trend analysis |

---

## 💡 Feedback & Contributing

This agent was built as a demonstration of the Hive framework's capabilities. Feedback is welcome!

- **Hive Framework Issues**: [github.com/aden-hive/hive/issues](https://github.com/aden-hive/hive/issues)
- **Hive Discord**: [discord.com/invite/hQdU7QDkgR](https://discord.com/invite/hQdU7QDkgR)

---

## 📄 License

This project inherits the [Apache-2.0 License](../../LICENSE) from the Hive framework.
