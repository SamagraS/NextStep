from enum import Enum

from pydantic import BaseModel, ConfigDict


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Tier(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class ReliabilityBand(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DelayedPlacementFlag(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class BehavioralEngagement(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    NONE = "NONE"


class RecommendationConfidence(str, Enum):
    high = "high"
    medium = "medium"
    exploratory = "exploratory"


class UniversityMatchStatus(str, Enum):
    resolved = "resolved"
    unresolved = "unresolved"


class DataCoverageLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MoratoriumWindow(str, Enum):
    three_months = "3mo"
    six_months = "6mo"
    twelve_months = "12mo"
