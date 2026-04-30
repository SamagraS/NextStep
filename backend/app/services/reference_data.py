from dataclasses import dataclass
from typing import Any

from rapidfuzz import fuzz, process

from app.models.feature_assembly import MacroSignalSnapshot, TaxonomyResolution, UniversityResolution
from app.schemas.common import UniversityMatchStatus
from app.services.demo_store import MOCK_SNAPSHOT_TS


@dataclass(frozen=True)
class UniversityEntry:
    canonical_name: str
    aliases: tuple[str, ...]
    institution_tier: int


class ReferenceDataService:
    def __init__(self, artifacts: Any | None = None) -> None:
        self.artifacts = artifacts

    def resolve_university(self, university_name: str) -> UniversityResolution:
        entries = self._university_entries()
        alias_map: dict[str, UniversityEntry] = {}
        for entry in entries:
            alias_map[entry.canonical_name] = entry
            for alias in entry.aliases:
                alias_map[alias] = entry

        match = process.extractOne(
            university_name,
            alias_map.keys(),
            scorer=fuzz.ratio,
        )

        if match is None or match[1] < 90:
            return UniversityResolution(
                original_name=university_name,
                normalized_name=university_name.strip(),
                match_status=UniversityMatchStatus.unresolved,
                match_score=int(match[1]) if match is not None else 0,
                institution_tier=3,
                source="placeholder_lookup",
            )

        alias, score, _ = match
        entry = alias_map[alias]
        return UniversityResolution(
            original_name=university_name,
            normalized_name=entry.canonical_name,
            match_status=UniversityMatchStatus.resolved,
            match_score=int(score),
            institution_tier=entry.institution_tier,
            source="placeholder_lookup",
        )

    def map_program(self, program_name: str) -> TaxonomyResolution:
        taxonomy_artifact = self.artifacts.get("taxonomy_map") if self.artifacts else None
        lowered = program_name.strip().lower()

        if isinstance(taxonomy_artifact, dict):
            for key, value in taxonomy_artifact.items():
                if key.lower() in lowered and isinstance(value, dict):
                    return TaxonomyResolution(
                        original_program_name=program_name,
                        program_family=str(value.get("program_family", "general")),
                        discipline=str(value.get("discipline", "general")),
                        source="artifact_taxonomy_map",
                    )

        if "computer science" in lowered or "software" in lowered:
            family, discipline = "computer_science", "engineering"
        elif "data science" in lowered or "analytics" in lowered:
            family, discipline = "data_science", "engineering"
        elif lowered.startswith("mba") or "business" in lowered:
            family, discipline = "business", "business"
        else:
            family, discipline = "general", "general"

        return TaxonomyResolution(
            original_program_name=program_name,
            program_family=family,
            discipline=discipline,
            source="placeholder_taxonomy",
        )

    def imputation_profile(
        self,
        destination_country: str,
        program_family: str,
        institution_tier: int,
        discipline: str,
    ) -> tuple[dict[str, float | int], str]:
        country = destination_country.strip().lower()
        profiles = {
            ("united states", "computer_science", 1): {"cgpa": 8.4, "internship_count": 2},
            ("united states", "data_science", 1): {"cgpa": 8.3, "internship_count": 2},
            ("canada", "data_science", 2): {"cgpa": 8.1, "internship_count": 1},
        }
        if (country, program_family, institution_tier) in profiles:
            return profiles[(country, program_family, institution_tier)], "country_program_tier"

        profiles_level_2 = {
            ("united states", "computer_science"): {"cgpa": 8.2, "internship_count": 2},
            ("united states", "data_science"): {"cgpa": 8.1, "internship_count": 1},
            ("canada", "data_science"): {"cgpa": 8.0, "internship_count": 1},
        }
        if (country, program_family) in profiles_level_2:
            return profiles_level_2[(country, program_family)], "country_program"

        profiles_level_3 = {
            ("united states", "engineering"): {"cgpa": 8.0, "internship_count": 1},
            ("united states", "business"): {"cgpa": 7.8, "internship_count": 1},
            ("canada", "engineering"): {"cgpa": 7.9, "internship_count": 1},
        }
        if (country, discipline) in profiles_level_3:
            return profiles_level_3[(country, discipline)], "country_discipline"

        return {"cgpa": 7.8, "internship_count": 1}, "global"

    def macro_signal(self, destination_country: str) -> MacroSignalSnapshot:
        country = destination_country.strip().lower()
        if country in {"united states", "usa", "us"}:
            return MacroSignalSnapshot(
                destination_country="United States",
                market_risk_sub=0.66,
                summary="Cloud engineering demand in the US is currently HIGH. Your action plan reflects this.",
                macro_snapshot_ts=MOCK_SNAPSHOT_TS,
                stale_signal_warning=None,
                source="placeholder_macro_cache",
            )
        if country == "canada":
            return MacroSignalSnapshot(
                destination_country="Canada",
                market_risk_sub=0.7,
                summary="Data hiring conditions in Canada are stable but softening slightly.",
                macro_snapshot_ts=MOCK_SNAPSHOT_TS,
                stale_signal_warning=None,
                source="placeholder_macro_cache",
            )
        if country in {"united kingdom", "uk"}:
            return MacroSignalSnapshot(
                destination_country="United Kingdom",
                market_risk_sub=0.62,
                summary="UK hiring conditions are mixed across graduate business pathways.",
                macro_snapshot_ts=MOCK_SNAPSHOT_TS,
                stale_signal_warning=None,
                source="placeholder_macro_cache",
            )
        return MacroSignalSnapshot(
            destination_country=destination_country.strip(),
            market_risk_sub=0.64,
            summary=f"Macro signals for {destination_country.strip()} are running on placeholder cache data.",
            macro_snapshot_ts=MOCK_SNAPSHOT_TS,
            stale_signal_warning=None,
            source="placeholder_macro_cache",
        )

    def _university_entries(self) -> list[UniversityEntry]:
        artifact = self.artifacts.get("university_lookup") if self.artifacts else None
        if isinstance(artifact, dict):
            entries: list[UniversityEntry] = []
            for canonical_name, metadata in artifact.items():
                if not isinstance(metadata, dict):
                    continue
                aliases = metadata.get("aliases", ())
                institution_tier = int(metadata.get("institution_tier", 3))
                entries.append(
                    UniversityEntry(
                        canonical_name=str(canonical_name),
                        aliases=tuple(str(alias) for alias in aliases),
                        institution_tier=institution_tier,
                    )
                )
            if entries:
                return entries

        return [
            UniversityEntry(
                canonical_name="University of Texas Austin",
                aliases=("University of Texas at Austin", "UT Austin"),
                institution_tier=1,
            ),
            UniversityEntry(
                canonical_name="University of Toronto",
                aliases=("U of T",),
                institution_tier=1,
            ),
            UniversityEntry(
                canonical_name="University of Melbourne",
                aliases=("Melbourne University",),
                institution_tier=1,
            ),
        ]
