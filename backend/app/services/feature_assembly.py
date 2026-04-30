from app.models.feature_assembly import (
    EncodedField,
    FeatureAssemblyResult,
    TenacityLookupResult,
)
from app.schemas.common import BehavioralEngagement
from app.schemas.score import OriginationScoringRequest, TenacityBreakdown
from app.services.demo_store import DemoStore
from app.services.reference_data import ReferenceDataService


class FeatureAssemblyService:
    def __init__(self, store: DemoStore, artifacts=None) -> None:
        self.store = store
        self.reference_data = ReferenceDataService(artifacts=artifacts)

    def assemble(self, payload: OriginationScoringRequest) -> FeatureAssemblyResult:
        university = self.reference_data.resolve_university(payload.university_name)
        taxonomy = self.reference_data.map_program(payload.program_name)
        macro = self.reference_data.macro_signal(payload.destination_country)
        tenacity = self._tenacity_lookup(payload.student_id)

        profile, imputation_level = self.reference_data.imputation_profile(
            destination_country=macro.destination_country,
            program_family=taxonomy.program_family,
            institution_tier=university.institution_tier,
            discipline=taxonomy.discipline,
        )

        imputation_flags: list[str] = []
        cgpa = self._resolve_numeric_field(
            raw_value=payload.cgpa,
            present=payload.cgpa_present,
            imputed_value=float(profile["cgpa"]),
            base_flag="cgpa_imputed",
            imputation_level=imputation_level,
            imputation_flags=imputation_flags,
        )
        internship_count = self._resolve_numeric_field(
            raw_value=payload.internship_count,
            present=payload.internship_count_present,
            imputed_value=int(profile["internship_count"]),
            base_flag="internship_count_imputed",
            imputation_level=imputation_level,
            imputation_flags=imputation_flags,
        )
        stem_opt = self._resolve_stem_opt(payload, imputation_flags)

        feature_dict = {
            "destination_country": macro.destination_country,
            "target_sector": payload.target_sector,
            "normalized_university_name": university.normalized_name,
            "university_match_score": university.match_score,
            "institution_tier": university.institution_tier,
            "program_family": taxonomy.program_family,
            "discipline": taxonomy.discipline,
            "loan_amount_inr": payload.loan_amount_inr,
            "interest_rate_annual_pct": payload.interest_rate_annual_pct,
            "repayment_term_months": payload.repayment_term_months,
            "moratorium_months": payload.moratorium_months,
            "cgpa": cgpa.resolved_value,
            "cgpa_encoded_state": cgpa.encoded_state,
            "internship_count": internship_count.resolved_value,
            "internship_count_encoded_state": internship_count.encoded_state,
            "stem_opt_eligible": stem_opt.resolved_value,
            "stem_opt_encoded_state": stem_opt.encoded_state,
            "market_risk_sub": macro.market_risk_sub,
            "tenacity_score": tenacity.tenacity_score,
        }

        return FeatureAssemblyResult(
            university=university,
            taxonomy=taxonomy,
            macro=macro,
            tenacity=tenacity,
            cgpa=cgpa,
            internship_count=internship_count,
            stem_opt_eligible=stem_opt,
            imputation_flags=imputation_flags,
            feature_dict=feature_dict,
        )

    def _resolve_numeric_field(
        self,
        raw_value: float | int | None,
        present: bool,
        imputed_value: float | int,
        base_flag: str,
        imputation_level: str,
        imputation_flags: list[str],
    ) -> EncodedField:
        if present and raw_value is not None:
            return EncodedField(
                raw_value=raw_value,
                resolved_value=raw_value,
                present=True,
                encoded_state=1,
                imputed=False,
                imputation_level=None,
            )

        imputation_flags.append(base_flag)
        return EncodedField(
            raw_value=raw_value,
            resolved_value=imputed_value,
            present=False,
            encoded_state=-1,
            imputed=True,
            imputation_level=imputation_level,
        )

    def _resolve_stem_opt(
        self,
        payload: OriginationScoringRequest,
        imputation_flags: list[str],
    ) -> EncodedField:
        country = payload.destination_country.strip().lower()
        if country not in {"united states", "usa", "us"}:
            return EncodedField(
                raw_value=None,
                resolved_value=None,
                present=False,
                encoded_state=-1,
                imputed=False,
                imputation_level="country_gated",
            )

        if payload.stem_opt_eligible_present and payload.stem_opt_eligible is not None:
            return EncodedField(
                raw_value=payload.stem_opt_eligible,
                resolved_value=payload.stem_opt_eligible,
                present=True,
                encoded_state=1 if payload.stem_opt_eligible else 0,
                imputed=False,
                imputation_level=None,
            )

        imputation_flags.append("stem_opt_eligibility_missing")
        return EncodedField(
            raw_value=payload.stem_opt_eligible,
            resolved_value=None,
            present=False,
            encoded_state=-1,
            imputed=False,
            imputation_level="missing_not_imputed",
        )

    def _tenacity_lookup(self, student_id: str | None) -> TenacityLookupResult:
        if not student_id:
            return TenacityLookupResult(
                tenacity_score=None,
                behavioral_engagement=BehavioralEngagement.NONE,
                data_count=0,
                breakdown=None,
            )

        student = self.store.get_student(student_id)
        if student is None or len(student.preloan_actions) < 3:
            return TenacityLookupResult(
                tenacity_score=None,
                behavioral_engagement=BehavioralEngagement.NONE,
                data_count=0,
                breakdown=None,
            )

        score = self.store.get_tenacity_score(student_id)
        return TenacityLookupResult(
            tenacity_score=score,
            behavioral_engagement=self.store.get_behavioral_engagement(student_id),
            data_count=len(student.preloan_actions),
            breakdown=TenacityBreakdown(
                avg_completion_rate=1.0,
                avg_engagement_depth=0.76,
                avg_consistency=0.82,
                certifications_verified=1,
            ),
        )
