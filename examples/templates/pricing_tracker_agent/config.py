"""Runtime configuration for Pricing Tracker Agent."""

from dataclasses import dataclass
from framework.config import RuntimeConfig

default_config: RuntimeConfig = RuntimeConfig()


@dataclass
class AgentMetadata:
    """Metadata for the Pricing Tracker Agent."""

    name: str = "Competitor Pricing & Intelligence Tracker"
    version: str = "1.0.0"
    description: str = (
        "Monitors competitor websites for pricing changes, new product launches, "
        "and shifts in marketing copy. Produces weekly digests with price-change "
        "alerts, trend analysis, and actionable intelligence for product & GTM teams."
    )
    intro_message: str = (
        "Hi! I'm your competitor pricing & intelligence tracker. Tell me which "
        "competitors to monitor (name + website URL), what areas to focus on "
        "(pricing tiers, feature packaging, marketing messaging, hiring signals), "
        "and I'll scan their web presence to produce a detailed competitive digest "
        "with price-change alerts and trend analysis."
    )


metadata: AgentMetadata = AgentMetadata()
