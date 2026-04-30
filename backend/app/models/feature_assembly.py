from dataclasses import dataclass

from app.schemas.common import BehavioralEngagement, UniversityMatchStatus
from app.schemas.score import TenacityBreakdown


@dataclass(frozen=True)
class EncodedField:
    raw_value: float | int | bool | None
    resolved_value: float | int | bool | None
    present: bool
    encoded_state: int
    imputed: bool
    imputation_level: str | None = None


@dataclass(frozen=True)
class UniversityResolution:
    original_name: str
    normalized_name: str
    match_status: UniversityMatchStatus
    match_score: int
    institution_tier: int
    source: str


@dataclass(frozen=True)
class TaxonomyResolution:
    original_program_name: str
    program_family: str
    discipline: str
    source: str


@dataclass(frozen=True)
class MacroSignalSnapshot:
    destination_country: str
    market_risk_sub: float
    summary: str
    macro_snapshot_ts: str
    stale_signal_warning: str | None
    source: str


@dataclass(frozen=True)
class TenacityLookupResult:
    tenacity_score: float | None
    behavioral_engagement: BehavioralEngagement
    data_count: int
    breakdown: TenacityBreakdown | None


@dataclass(frozen=True)
class FeatureAssemblyResult:
    university: UniversityResolution
    taxonomy: TaxonomyResolution
    macro: MacroSignalSnapshot
    tenacity: TenacityLookupResult
    cgpa: EncodedField
    internship_count: EncodedField
    stem_opt_eligible: EncodedField
    imputation_flags: list[str]
    feature_dict: dict[str, object]
