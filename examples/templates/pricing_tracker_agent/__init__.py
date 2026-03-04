"""
Competitor Pricing & Intelligence Tracker Agent.

Monitors competitor websites for pricing changes, product launches, and
marketing shifts. Produces weekly digests with price-change alerts,
per-competitor pricing tables, and 30-day trend analysis.
"""

from .agent import PricingTrackerAgent, default_agent, goal, nodes, edges
from .config import RuntimeConfig, AgentMetadata, default_config, metadata

__version__ = "1.0.0"

__all__ = [
    "PricingTrackerAgent",
    "default_agent",
    "goal",
    "nodes",
    "edges",
    "RuntimeConfig",
    "AgentMetadata",
    "default_config",
    "metadata",
]
