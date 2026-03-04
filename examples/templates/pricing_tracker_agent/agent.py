"""Agent graph construction for Competitor Pricing & Intelligence Tracker."""

from typing import Any, TYPE_CHECKING
from framework.graph import (
    EdgeSpec,
    EdgeCondition,
    Goal,
    SuccessCriterion,
    Constraint,
    NodeSpec,
)
from framework.graph.edge import GraphSpec
from framework.graph.executor import ExecutionResult, GraphExecutor
from framework.runtime.event_bus import EventBus
from framework.runtime.core import Runtime
from framework.llm import LiteLLMProvider
from framework.runner.tool_registry import ToolRegistry

from .config import default_config, metadata, RuntimeConfig
from .nodes import (
    intake_node,
    pricing_scraper_node,
    product_monitor_node,
    news_monitor_node,
    aggregator_node,
    analysis_node,
    report_node,
)

if TYPE_CHECKING:
    from framework.config import RuntimeConfig

# ──────────────────────────────────────────────────────────────────────
# Goal definition
# ──────────────────────────────────────────────────────────────────────
goal: Goal = Goal(
    id="competitor-pricing-intelligence",
    name="Competitor Pricing & Intelligence Tracker",
    description=(
        "Monitor competitor websites for pricing changes, product launches, "
        "and marketing shifts.  Produce a weekly digest with price-change "
        "alerts, per-competitor pricing tables, and 30-day trend analysis."
    ),
    success_criteria=[
        SuccessCriterion(
            id="sc-pricing-coverage",
            description=(
                "Successfully scrape and structure pricing data for each "
                "competitor's public pricing page."
            ),
            metric="pricing_pages_scraped",
            target=">=1_per_competitor",
            weight=0.30,
        ),
        SuccessCriterion(
            id="sc-change-detection",
            description=(
                "Compare current pricing with the stored historical snapshot "
                "and flag any changes."
            ),
            metric="change_detection_run",
            target="true",
            weight=0.25,
        ),
        SuccessCriterion(
            id="sc-multi-source",
            description=(
                "Gather intelligence from at least 2 source types per "
                "competitor (website + news/blog)."
            ),
            metric="sources_per_competitor",
            target=">=2",
            weight=0.20,
        ),
        SuccessCriterion(
            id="sc-report-delivered",
            description=(
                "User receives a formatted HTML report with pricing tables, "
                "alerts, and trend analysis."
            ),
            metric="report_delivered",
            target="true",
            weight=0.25,
        ),
    ],
    constraints=[
        Constraint(
            id="c-no-fabrication",
            description=(
                "Never fabricate pricing data, news, or findings — only "
                "report what was actually found."
            ),
            constraint_type="hard",
            category="quality",
        ),
        Constraint(
            id="c-source-attribution",
            description="Every finding must include a source URL.",
            constraint_type="hard",
            category="quality",
        ),
        Constraint(
            id="c-recency",
            description=(
                "Prioritise findings from the past 7 days; include up to "
                "30 days for trend analysis."
            ),
            constraint_type="soft",
            category="quality",
        ),
        Constraint(
            id="c-price-accuracy",
            description=(
                "Pricing data must be transcribed exactly as shown on the "
                "competitor's page — no rounding or estimation."
            ),
            constraint_type="hard",
            category="quality",
        ),
    ],
)

# ──────────────────────────────────────────────────────────────────────
# Node list
# ──────────────────────────────────────────────────────────────────────
nodes: list[NodeSpec] = [
    intake_node,
    pricing_scraper_node,
    product_monitor_node,
    news_monitor_node,
    aggregator_node,
    analysis_node,
    report_node,
]

# ──────────────────────────────────────────────────────────────────────
# Edge definitions
# ──────────────────────────────────────────────────────────────────────
edges: list[EdgeSpec] = [
    # intake → pricing-scraper  (always)
    EdgeSpec(
        id="intake-to-pricing-scraper",
        source="intake",
        target="pricing-scraper",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    # pricing-scraper → product-monitor  (always)
    EdgeSpec(
        id="pricing-scraper-to-product-monitor",
        source="pricing-scraper",
        target="product-monitor",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    # product-monitor → news-monitor  (always)
    EdgeSpec(
        id="product-monitor-to-news-monitor",
        source="product-monitor",
        target="news-monitor",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    # news-monitor → aggregator  (always)
    EdgeSpec(
        id="news-monitor-to-aggregator",
        source="news-monitor",
        target="aggregator",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    # aggregator → analysis  (always)
    EdgeSpec(
        id="aggregator-to-analysis",
        source="aggregator",
        target="analysis",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    # analysis → report  (always)
    EdgeSpec(
        id="analysis-to-report",
        source="analysis",
        target="report",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
]

# ──────────────────────────────────────────────────────────────────────
# Graph configuration
# ──────────────────────────────────────────────────────────────────────
entry_node: str = "intake"
entry_points: dict[str, str] = {"start": "intake"}
pause_nodes: list[str] = []
terminal_nodes: list[str] = ["report"]


# ──────────────────────────────────────────────────────────────────────
# Agent class
# ──────────────────────────────────────────────────────────────────────
class PricingTrackerAgent:
    """
    Competitor Pricing & Intelligence Tracker — 7-node pipeline.

    Flow:
        intake → pricing-scraper → product-monitor → news-monitor
          → aggregator → analysis → report
    """

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self.config = config or default_config
        self.goal = goal
        self.nodes = nodes
        self.edges = edges
        self.entry_node = entry_node
        self.entry_points = entry_points
        self.pause_nodes = pause_nodes
        self.terminal_nodes = terminal_nodes
        self._executor: GraphExecutor | None = None
        self._graph: GraphSpec | None = None
        self._event_bus: EventBus | None = None
        self._tool_registry: ToolRegistry | None = None

    # ── graph builder ─────────────────────────────────────────────────

    def _build_graph(self) -> GraphSpec:
        return GraphSpec(
            id="pricing-tracker-agent-graph",
            goal_id=self.goal.id,
            version="1.0.0",
            entry_node=self.entry_node,
            entry_points=self.entry_points,
            terminal_nodes=self.terminal_nodes,
            pause_nodes=self.pause_nodes,
            nodes=self.nodes,
            edges=self.edges,
            default_model=self.config.model,
            max_tokens=self.config.max_tokens,
            loop_config={
                "max_iterations": 100,
                "max_tool_calls_per_turn": 30,
                "max_history_tokens": 32000,
            },
        )

    # ── setup ─────────────────────────────────────────────────────────

    def _setup(self) -> GraphExecutor:
        from pathlib import Path

        storage_path = (
            Path.home() / ".hive" / "agents" / "pricing_tracker_agent"
        )
        storage_path.mkdir(parents=True, exist_ok=True)

        self._event_bus = EventBus()
        self._tool_registry = ToolRegistry()

        mcp_config_path = Path(__file__).parent / "mcp_servers.json"
        if mcp_config_path.exists():
            self._tool_registry.load_mcp_config(mcp_config_path)

        llm = LiteLLMProvider(
            model=self.config.model,
            api_key=self.config.api_key,
            api_base=self.config.api_base,
        )

        tool_executor = self._tool_registry.get_executor()
        tools = list(self._tool_registry.get_tools().values())

        self._graph = self._build_graph()
        runtime = Runtime(storage_path)

        self._executor = GraphExecutor(
            runtime=runtime,
            llm=llm,
            tools=tools,
            tool_executor=tool_executor,
            event_bus=self._event_bus,
            storage_path=storage_path,
            loop_config=self._graph.loop_config,
        )

        return self._executor

    # ── lifecycle ─────────────────────────────────────────────────────

    async def start(self) -> None:
        """Set up the agent (initialize executor and tools)."""
        if self._executor is None:
            self._setup()

    async def stop(self) -> None:
        """Clean up resources."""
        self._executor = None
        self._event_bus = None

    async def trigger_and_wait(
        self,
        entry_point: str,
        input_data: dict[str, Any],
        timeout: float | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> ExecutionResult | None:
        if self._executor is None:
            raise RuntimeError("Agent not started. Call start() first.")
        if self._graph is None:
            raise RuntimeError("Graph not built. Call start() first.")

        return await self._executor.execute(
            graph=self._graph,
            goal=self.goal,
            input_data=input_data,
            session_state=session_state,
        )

    async def run(
        self,
        context: dict[str, Any],
        session_state: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """Run the agent (convenience method for single execution)."""
        await self.start()
        try:
            result = await self.trigger_and_wait(
                "start", context, session_state=session_state
            )
            return result or ExecutionResult(
                success=False, error="Execution timeout"
            )
        finally:
            await self.stop()

    # ── introspection ─────────────────────────────────────────────────

    def info(self) -> dict[str, Any]:
        """Get agent information for introspection."""
        return {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "goal": {
                "name": self.goal.name,
                "description": self.goal.description,
            },
            "nodes": [n.id for n in self.nodes],
            "edges": [e.id for e in self.edges],
            "entry_node": self.entry_node,
            "entry_points": self.entry_points,
            "pause_nodes": self.pause_nodes,
            "terminal_nodes": self.terminal_nodes,
            "client_facing_nodes": [
                n.id for n in self.nodes if n.client_facing
            ],
        }

    def validate(self) -> dict[str, Any]:
        """Validate agent structure."""
        errors: list[str] = []
        warnings: list[str] = []

        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                errors.append(
                    f"Edge {edge.id}: source '{edge.source}' not found"
                )
            if edge.target not in node_ids:
                errors.append(
                    f"Edge {edge.id}: target '{edge.target}' not found"
                )

        if self.entry_node not in node_ids:
            errors.append(f"Entry node '{self.entry_node}' not found")

        for terminal in self.terminal_nodes:
            if terminal not in node_ids:
                errors.append(f"Terminal node '{terminal}' not found")

        for ep_id, node_id in self.entry_points.items():
            if node_id not in node_ids:
                errors.append(
                    f"Entry point '{ep_id}' references unknown node "
                    f"'{node_id}'"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }


# Create default instance
default_agent: PricingTrackerAgent = PricingTrackerAgent()
