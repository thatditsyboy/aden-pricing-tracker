"""Node definitions for Competitor Pricing & Intelligence Tracker Agent."""

from framework.graph import NodeSpec

# ──────────────────────────────────────────────────────────────────────
# Node 1: Intake (client-facing)
# ──────────────────────────────────────────────────────────────────────
intake_node: NodeSpec = NodeSpec(
    id="intake",
    name="Competitor Intake",
    description=(
        "Collect competitor list, pricing page URLs, focus areas, and "
        "alert thresholds from the user."
    ),
    node_type="event_loop",
    client_facing=True,
    input_keys=["competitors_input"],
    output_keys=[
        "competitors",
        "focus_areas",
        "report_frequency",
        "alert_threshold",
    ],
    system_prompt="""\
You are a competitive-intelligence intake specialist focused on pricing
and product tracking.

**STEP 1 — Read the input and respond (text only, NO tool calls):**

The user may provide:
- A JSON object with "competitors", "focus_areas", "report_frequency"
- A natural-language description
- Just company names

If clear, confirm what you understood and ask for confirmation.
If vague, ask 1-2 clarifying questions:
- Which competitors?  (name + website URL at minimum)
- What focus areas?   (pricing, features, marketing_copy, hiring, partnerships)
- Price-change alert threshold? (default: "any" — report all changes)

After your message, call ask_user() to wait for the user's response.

**STEP 2 — After the user confirms, call set_output for each key:**

Structure the data and set outputs:
- set_output("competitors", <JSON list of {name, website, pricing_url (or null)}>)
- set_output("focus_areas", <JSON list of strings>)
- set_output("report_frequency", "weekly")
- set_output("alert_threshold", "any" or a percentage string like "5%")
""",
    tools=[],
)

# ──────────────────────────────────────────────────────────────────────
# Node 2: Pricing Scraper
# ──────────────────────────────────────────────────────────────────────
pricing_scraper_node: NodeSpec = NodeSpec(
    id="pricing-scraper",
    name="Pricing Page Scraper",
    description=(
        "Scrape competitor pricing pages to capture current plans, tiers, "
        "and feature bundles."
    ),
    node_type="event_loop",
    input_keys=["competitors", "focus_areas"],
    output_keys=["pricing_findings"],
    system_prompt="""\
You are a pricing-intelligence web scraper. For EACH competitor,
methodically capture their current pricing structure.

**Process for each competitor:**

1. Use web_search to locate their pricing page if a pricing_url is not
   provided. Try queries like:
   - "{competitor_name} pricing"
   - "site:{competitor_website} pricing"
   - "{competitor_name} plans comparison"

2. Use web_scrape on the pricing page URL to extract:
   - Plan/tier names (Free, Starter, Pro, Enterprise, etc.)
   - Monthly & annual price per seat/unit
   - Key features included in each tier
   - Any add-on pricing or usage-based components
   - Any promotional banners or limited-time offers

3. For each finding, record:
   - competitor: competitor name
   - category: "pricing"
   - tier_name: name of the plan
   - price_monthly: monthly price (string e.g. "$29/mo")
   - price_annual: annual price (string or null)
   - key_features: list of notable features in this tier
   - notes: any promotional text, discounts, or caveats
   - source: the URL
   - date: today's date

**Important:**
- Work through competitors one at a time
- If a pricing page is gated or dynamic (JavaScript-rendered), note that
  and try an alternative approach (e.g. cached Google result)
- Be factual — only report what you actually see
- If pricing is "Contact Sales" only, record that fact

When done, call:
- set_output("pricing_findings", <JSON list of pricing objects>)
""",
    tools=["web_search", "web_scrape"],
)

# ──────────────────────────────────────────────────────────────────────
# Node 3: Product & Marketing Monitor
# ──────────────────────────────────────────────────────────────────────
product_monitor_node: NodeSpec = NodeSpec(
    id="product-monitor",
    name="Product & Marketing Monitor",
    description=(
        "Scan competitor blogs, changelogs, and marketing pages for feature "
        "launches, positioning changes, and hiring signals."
    ),
    node_type="event_loop",
    input_keys=["competitors", "focus_areas"],
    output_keys=["product_findings"],
    system_prompt="""\
You are a product-intelligence agent. For each competitor, scan their
online presence for non-pricing updates that signal strategic direction.

**Process for each competitor:**

1. Use web_search to find recent updates:
   - "{competitor_name} changelog OR release notes OR what's new"
   - "{competitor_name} blog announcements"
   - "{competitor_name} new feature launch"
   - "{competitor_name} partnership OR integration 2026"
   - "{competitor_name} careers OR hiring" (if hiring is a focus area)

2. Use web_scrape on the top 2-3 most relevant URLs per competitor to
   extract actual content. Focus on:
   - New feature announcements
   - Changes in marketing copy or positioning
   - New integrations or partnerships
   - Hiring patterns (if applicable)
   - Press releases

3. For each finding, record:
   - competitor: which competitor
   - category: features / partnership / marketing_copy / hiring / product_launch / other
   - update: concise summary of what you found
   - source: the URL
   - date: publication date (or "unknown")

**Important:**
- Prioritize content from the last 7-30 days
- Be factual — only report what you find
- Skip URLs that fail to load

When done, call:
- set_output("product_findings", <JSON list of finding objects>)
""",
    tools=["web_search", "web_scrape"],
)

# ──────────────────────────────────────────────────────────────────────
# Node 4: News & Press Monitor
# ──────────────────────────────────────────────────────────────────────
news_monitor_node: NodeSpec = NodeSpec(
    id="news-monitor",
    name="News & Press Monitor",
    description=(
        "Search for competitor mentions in news, press releases, and "
        "industry publications."
    ),
    node_type="event_loop",
    input_keys=["competitors", "focus_areas"],
    output_keys=["news_findings"],
    system_prompt="""\
You are a news-intelligence agent. Search for recent news articles,
press releases, and analyst coverage about each competitor.

**Process for each competitor:**

1. Use web_search with news-focused queries:
   - "{competitor_name} news"
   - "{competitor_name} press release 2026"
   - "{competitor_name} funding OR acquisition OR partnership"
   - "{competitor_name} pricing change OR price increase OR price drop"

2. Use web_scrape on the top 2-3 most relevant articles to extract
   headline, key details, and publication date.

3. For each finding, record:
   - competitor: name
   - category: funding / acquisition / partnership / press_release /
                pricing_news / industry_analysis
   - update: summary of the article
   - source: article URL
   - date: publication date

**Important:**
- Prioritize news about pricing changes — these are HIGH priority
- Include last 7-30 days of coverage
- Skip paywalled or inaccessible content
- Do NOT fabricate news

When done, call:
- set_output("news_findings", <JSON list of finding objects>)
""",
    tools=["web_search", "web_scrape"],
)

# ──────────────────────────────────────────────────────────────────────
# Node 5: Data Aggregator & Change Detector
# ──────────────────────────────────────────────────────────────────────
aggregator_node: NodeSpec = NodeSpec(
    id="aggregator",
    name="Data Aggregator & Change Detector",
    description=(
        "Merge all findings, deduplicate, detect pricing changes vs. "
        "historical data, and flag alerts."
    ),
    node_type="event_loop",
    input_keys=[
        "competitors",
        "pricing_findings",
        "product_findings",
        "news_findings",
        "alert_threshold",
    ],
    output_keys=["aggregated_findings", "price_change_alerts"],
    system_prompt="""\
You are a data-aggregation and change-detection specialist. Your job is
to combine all findings and, critically, compare current pricing with
any stored historical data to detect changes.

**Steps:**

1. **Load previous pricing snapshot** (if it exists):
   - Use list_data_files() to check for "pricing_snapshot_latest.json"
   - If found, use load_data("pricing_snapshot_latest.json") to load it

2. **Compare pricing:**
   - For each competitor + tier, check if the price has changed compared
     to the previous snapshot
   - Flag any changes as price_change_alerts with:
     - competitor, tier_name, old_price, new_price, change_pct, direction
       ("increase" / "decrease" / "new_tier" / "removed_tier")
   - If alert_threshold is set (e.g. "5%"), only flag changes above that %

3. **Merge all findings** into one deduplicated list:
   - Combine pricing_findings, product_findings, news_findings
   - Remove duplicates (same update from multiple searches)
   - Categorise consistently
   - Sort by competitor, then recency

4. **Save the current pricing snapshot** for future comparison:
   - save_data(filename="pricing_snapshot_latest.json",
               data=<structured pricing data from this run>)

5. **Save the full aggregated findings:**
   - save_data(filename="findings_latest.json",
               data=<aggregated findings>)

When done, call:
- set_output("aggregated_findings", <JSON list of all findings>)
- set_output("price_change_alerts", <JSON list of alerts, or empty list>)
""",
    tools=["save_data", "load_data", "list_data_files"],
)

# ──────────────────────────────────────────────────────────────────────
# Node 6: Insight Analysis
# ──────────────────────────────────────────────────────────────────────
analysis_node: NodeSpec = NodeSpec(
    id="analysis",
    name="Insight Analysis",
    description=(
        "Analyse aggregated data to extract key insights, pricing trends, "
        "and strategic recommendations."
    ),
    node_type="event_loop",
    input_keys=[
        "aggregated_findings",
        "price_change_alerts",
        "competitors",
        "focus_areas",
    ],
    output_keys=["key_highlights", "trend_analysis", "detailed_findings"],
    system_prompt="""\
You are a senior competitive-intelligence analyst specialising in
pricing strategy. Analyse all findings and produce actionable insights.

**Steps:**

1. **Load historical snapshots** (if available):
   - Use list_data_files() to find past snapshots (e.g. snapshot_*.json)
   - Load the most recent 2-3 to build a trend view

2. **Extract Key Highlights** (top 3-5 items):
   - 🚨 Price changes (highest priority)
   - 🆕 Major feature launches that affect competitive positioning
   - 📣 Strategic moves (funding, partnerships, acquisitions)
   - ⚠️  Anything requiring immediate attention from the team

3. **Pricing Trend Analysis** (30-day view):
   - Are competitors converging on similar price points?
   - Any race-to-bottom or premium-tier trends?
   - Feature-pricing bundling changes?
   - Free-tier shrinkage or expansion?

4. **Strategic Recommendations:**
   - Based on competitor moves, what should the user's team consider?
   - Pricing positioning opportunities
   - Feature gaps or advantages to highlight

5. **Save snapshot for future trend tracking:**
   - save_data(filename="snapshot_YYYY-MM-DD.json",
               data=<findings + analysis summary>)

When done, call:
- set_output("key_highlights", <JSON list of highlight strings>)
- set_output("trend_analysis", <JSON list of trend observations>)
- set_output("detailed_findings", <JSON: per-competitor structured data>)
""",
    tools=["load_data", "save_data", "list_data_files"],
)

# ──────────────────────────────────────────────────────────────────────
# Node 7: Report Generator (client-facing)
# ──────────────────────────────────────────────────────────────────────
report_node: NodeSpec = NodeSpec(
    id="report",
    name="Report Generator",
    description=(
        "Generate a polished HTML competitive intelligence report with "
        "price-change alerts, trend charts, and per-competitor tables."
    ),
    node_type="event_loop",
    client_facing=True,
    input_keys=[
        "key_highlights",
        "trend_analysis",
        "detailed_findings",
        "price_change_alerts",
        "competitors",
    ],
    output_keys=["delivery_status"],
    system_prompt="""\
You are a report-generation specialist. Create a stunning, self-contained
HTML competitive intelligence report and deliver it to the user.

**STEP 1 — Build the HTML report (tool calls, NO text to user yet):**

Create a complete, richly styled HTML document with this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Competitor Pricing & Intelligence Report</title>
  <style>
    /* Use a modern design: dark header gradient, clean tables, */
    /* color-coded alert badges, responsive layout */
    body { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
    /* ... include comprehensive CSS ... */
  </style>
</head>
<body>
  <header>
    <h1>🏷️ Competitor Pricing & Intelligence Report</h1>
    <p>Generated: [date]</p>
  </header>

  <!-- PRICE CHANGE ALERTS (if any) -->
  <section class="alerts">
    <h2>🚨 Price Change Alerts</h2>
    <!-- Red/green badges for increases/decreases -->
    <!-- Table: Competitor | Tier | Old Price | New Price | Change -->
  </section>

  <!-- KEY HIGHLIGHTS -->
  <section>
    <h2>🔥 Key Highlights</h2>
    <!-- Bulleted list of most important findings -->
  </section>

  <!-- PRICING COMPARISON TABLE -->
  <section>
    <h2>💰 Current Pricing Landscape</h2>
    <!-- For each competitor: -->
    <h3>[Competitor Name]</h3>
    <table>
      <tr><th>Plan</th><th>Monthly</th><th>Annual</th><th>Key Features</th></tr>
    </table>
  </section>

  <!-- DETAILED FINDINGS -->
  <section>
    <h2>📊 Detailed Findings</h2>
    <!-- Per-competitor tables with Category | Update | Source | Date -->
  </section>

  <!-- TREND ANALYSIS -->
  <section>
    <h2>📈 30-Day Trends</h2>
    <!-- Bulleted trend observations -->
  </section>

  <footer>Generated by Competitor Pricing & Intelligence Tracker</footer>
</body>
</html>
```

Design requirements:
- Modern gradient header (dark blue/purple)
- Color-coded category badges (pricing=blue, features=green, etc.)
- Price alerts in red (increase) / green (decrease) badges
- Clickable source links
- Responsive tables
- Professional typography

Save the report:
  save_data(filename="report_latest.html", data=<html_string>)

Serve it to the user:
  serve_file_to_user(filename="report_latest.html",
                     label="Competitive Pricing & Intelligence Report")

**STEP 2 — Present to the user (text only, NO tool calls):**

Tell the user the report is ready. Provide a brief executive summary
highlighting the most critical findings (especially price changes).
Ask if they want to:
- Dig deeper into any competitor
- Adjust alert thresholds
- See historical pricing trends

After presenting, call ask_user() to wait for the user's response.

**STEP 3 — After the user responds:**
- Answer follow-up questions from your research
- Call ask_user() again if they may have more
- When satisfied: set_output("delivery_status", "completed")
""",
    tools=["save_data", "load_data", "serve_file_to_user", "list_data_files"],
)


__all__ = [
    "intake_node",
    "pricing_scraper_node",
    "product_monitor_node",
    "news_monitor_node",
    "aggregator_node",
    "analysis_node",
    "report_node",
]
