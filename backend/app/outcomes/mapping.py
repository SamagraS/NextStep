from __future__ import annotations

from dataclasses import dataclass


PROGRAM_FAMILIES = (
    "computer_science",
    "data_science",
    "engineering",
    "business",
    "finance",
    "economics",
    "law",
    "medicine",
    "healthcare",
    "biological_sciences",
    "physical_sciences",
    "mathematics",
    "education",
    "social_sciences",
    "psychology",
    "architecture",
    "creative_arts",
    "agriculture",
    "environmental_sciences",
    "humanities",
    "communications",
    "hospitality",
    "public_policy",
    "general_studies",
)


COUNTRY_ALIASES = {
    "us": "United States",
    "usa": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "england": "United Kingdom",
    "australia": "Australia",
    "canada": "Canada",
    "india": "India",
    "germany": "Germany",
}


KEYWORD_TO_PROGRAM = {
    "computing": "computer_science",
    "computer": "computer_science",
    "software": "computer_science",
    "information technology": "computer_science",
    "artificial intelligence": "data_science",
    "analytics": "data_science",
    "data": "data_science",
    "engineering": "engineering",
    "technology": "engineering",
    "business": "business",
    "management": "business",
    "commerce": "business",
    "finance": "finance",
    "economics": "economics",
    "law": "law",
    "medicine": "medicine",
    "dentistry": "medicine",
    "nursing": "healthcare",
    "health": "healthcare",
    "psychology": "psychology",
    "education": "education",
    "social": "social_sciences",
    "biology": "biological_sciences",
    "sport": "biological_sciences",
    "physical sciences": "physical_sciences",
    "physics": "physical_sciences",
    "chemistry": "physical_sciences",
    "mathematical": "mathematics",
    "math": "mathematics",
    "architecture": "architecture",
    "building": "architecture",
    "creative arts": "creative_arts",
    "design": "creative_arts",
    "agriculture": "agriculture",
    "environment": "environmental_sciences",
    "humanities": "humanities",
    "history": "humanities",
    "language": "humanities",
    "communication": "communications",
    "journalism": "communications",
    "hospitality": "hospitality",
    "public policy": "public_policy",
}


SOC_PREFIX_TO_PROGRAM = {
    "11": "business",
    "13": "finance",
    "15": "computer_science",
    "17": "engineering",
    "19": "physical_sciences",
    "21": "community_and_social",
    "23": "education",
    "27": "communications",
    "29": "healthcare",
}


ISCED_TO_PROGRAM = {
    "01": "education",
    "02": "creative_arts",
    "03": "humanities",
    "04": "business",
    "05": "physical_sciences",
    "06": "information_and_communication_technologies",
    "07": "engineering",
    "08": "agriculture",
    "09": "healthcare",
}


NORMALIZED_PROGRAM_OVERRIDES = {
    "community_and_social": "social_sciences",
    "information_and_communication_technologies": "computer_science",
}


@dataclass(frozen=True)
class TaxonomyMapper:
    def normalize_country(self, country: str) -> str:
        key = country.strip().lower()
        return COUNTRY_ALIASES.get(key, country.strip().title())

    def normalize_program_family(self, value: str) -> str:
        lowered = value.strip().lower().replace("&", "and")
        lowered = " ".join(lowered.split())
        if lowered in PROGRAM_FAMILIES:
            return lowered

        for keyword, family in KEYWORD_TO_PROGRAM.items():
            if keyword in lowered:
                return NORMALIZED_PROGRAM_OVERRIDES.get(family, family)
        return "general_studies"

    def map_hesa_subject(self, subject: str) -> str:
        return self.normalize_program_family(subject)

    def map_qilt_field(self, field: str) -> str:
        return self.normalize_program_family(field)

    def map_eurostat_isced(self, isced_code: str) -> str:
        family = ISCED_TO_PROGRAM.get(isced_code[:2], "general_studies")
        return NORMALIZED_PROGRAM_OVERRIDES.get(family, family)

    def map_soc_code(self, soc_code: str | int | float | None, soc_title: str = "") -> str:
        code = str(soc_code or "").strip()
        prefix = code[:2]
        if prefix in SOC_PREFIX_TO_PROGRAM:
            family = SOC_PREFIX_TO_PROGRAM[prefix]
            return NORMALIZED_PROGRAM_OVERRIDES.get(family, family)
        if soc_title:
            return self.normalize_program_family(soc_title)
        return "general_studies"


def soc_to_program_family(soc_code: str | int | float | None, soc_title: str = "") -> str:
    return TaxonomyMapper().map_soc_code(soc_code=soc_code, soc_title=soc_title)


def isced_to_program_family(isced_code: str) -> str:
    return TaxonomyMapper().map_eurostat_isced(isced_code)
