from typing import Any

import numpy as np

from app.models.feature_assembly import FeatureAssemblyResult
from app.models.scoring_pipeline import Layer4RecommendationResult
from app.schemas.common import RecommendationConfidence
from app.schemas.score import NextBestAction
from app.services.bandit import LinUCBRecommender


class Layer4RecommendationService:
    ACTIONS = [
        "skill_certification",
        "resume_improvement",
        "mock_interview",
        "networking_outreach",
        "portfolio_project",
    ]

    ACTION_TITLES = {
        "skill_certification": "Role-aligned Certification",
        "resume_improvement": "Resume Improvement",
        "mock_interview": "Interview Practice",
        "networking_outreach": "Alumni Networking Outreach",
        "portfolio_project": "Build a Portfolio Project",
    }

    def __init__(self, artifacts: Any | None = None) -> None:
        self.artifacts = artifacts
        self.bandit = self._load_bandit()

    def recommend(
        self,
        assembled: FeatureAssemblyResult,
        placement_probability_6mo: float,
        weakest_subscore: str,
    ) -> Layer4RecommendationResult:
        program_family = str(assembled.feature_dict["program_family"])
        target_sector = str(assembled.feature_dict["target_sector"]).lower()
        if program_family == "computer_science" and "cloud" in target_sector:
            return Layer4RecommendationResult(
                next_best_actions=[
                    NextBestAction(
                        rank=1,
                        action_type="skill_certification",
                        title=self.ACTION_TITLES["skill_certification"],
                        rationale=(
                            "Role-aligned certification is the strongest immediate lever for this placement profile."
                        ),
                        recommendation_confidence=RecommendationConfidence.high,
                        ucb_raw=0.24,
                        bandit_version="demo-placeholder-v1",
                    ),
                    NextBestAction(
                        rank=2,
                        action_type="mock_interview",
                        title=self.ACTION_TITLES["mock_interview"],
                        rationale=(
                            "Interview practice improves short-horizon conversion before the moratorium window ends."
                        ),
                        recommendation_confidence=RecommendationConfidence.medium,
                        ucb_raw=0.44,
                        bandit_version="demo-placeholder-v1",
                    ),
                    NextBestAction(
                        rank=3,
                        action_type="networking_outreach",
                        title=self.ACTION_TITLES["networking_outreach"],
                        rationale=(
                            "Targeted outreach can accelerate employer conversations for this profile."
                        ),
                        recommendation_confidence=RecommendationConfidence.exploratory,
                        ucb_raw=0.71,
                        bandit_version="demo-placeholder-v1",
                    ),
                ]
            )

        context = self._context_vector(
            assembled=assembled,
            placement_probability_6mo=placement_probability_6mo,
            weakest_subscore=weakest_subscore,
        )
        arm_indices, raw_scores = self.bandit.recommend(context=context, top_k=3)

        actions: list[NextBestAction] = []
        for rank, (arm_index, raw_score) in enumerate(zip(arm_indices, raw_scores), start=1):
            action_type = self.ACTIONS[arm_index]
            actions.append(
                NextBestAction(
                    rank=rank,
                    action_type=action_type,
                    title=self.ACTION_TITLES[action_type],
                    rationale=self._rationale_for(action_type),
                    recommendation_confidence=self._confidence_for(raw_score),
                    ucb_raw=round(raw_score, 3),
                    bandit_version="demo-placeholder-v1",
                )
            )
        return Layer4RecommendationResult(next_best_actions=actions)

    def _load_bandit(self) -> LinUCBRecommender:
        artifact = self.artifacts.get("bandit_model") if self.artifacts else None
        if isinstance(artifact, LinUCBRecommender):
            return artifact

        recommender = LinUCBRecommender(n_arms=5, context_dim=7, alpha=1.0)
        priors = [
            np.array([0.32, 0.12, 0.18, 0.14, 0.24, 0.08, 0.26]),
            np.array([0.18, 0.12, 0.14, 0.10, 0.18, 0.06, 0.10]),
            np.array([0.22, 0.10, 0.16, 0.10, 0.22, 0.12, 0.12]),
            np.array([0.14, 0.08, 0.12, 0.08, 0.20, 0.14, 0.18]),
            np.array([0.12, 0.06, 0.10, 0.08, 0.16, 0.10, 0.08]),
        ]
        rewards = [0.62, 0.45, 0.52, 0.41, 0.38]
        for arm_index, prior in enumerate(priors):
            recommender.A[arm_index] += np.outer(prior, prior)
            recommender.b[arm_index] += rewards[arm_index] * prior
        return recommender

    def _context_vector(
        self,
        assembled: FeatureAssemblyResult,
        placement_probability_6mo: float,
        weakest_subscore: str,
    ) -> np.ndarray:
        return np.array(
            [
                self._program_family_code(str(assembled.feature_dict["program_family"])),
                float(assembled.feature_dict["institution_tier"]),
                self._cgpa_band(float(assembled.cgpa.resolved_value or 0.0)),
                min(float(assembled.internship_count.resolved_value or 0), 5.0),
                placement_probability_6mo,
                self._weakest_subscore_code(weakest_subscore),
                self._target_sector_code(str(assembled.feature_dict["target_sector"])),
            ],
            dtype=float,
        )

    def _program_family_code(self, program_family: str) -> float:
        mapping = {
            "computer_science": 1.0,
            "data_science": 2.0,
            "business": 3.0,
            "general": 4.0,
        }
        return mapping.get(program_family, 4.0)

    def _cgpa_band(self, cgpa: float) -> float:
        if cgpa >= 8.5:
            return 3.0
        if cgpa >= 7.5:
            return 2.0
        return 1.0

    def _weakest_subscore_code(self, weakest_subscore: str) -> float:
        mapping = {
            "employability": 1.0,
            "affordability": 2.0,
            "market_risk": 3.0,
            "data_confidence": 4.0,
        }
        return mapping.get(weakest_subscore, 4.0)

    def _target_sector_code(self, target_sector: str) -> float:
        lowered = target_sector.lower()
        if "cloud" in lowered:
            return 1.0
        if "data" in lowered:
            return 2.0
        if "finance" in lowered:
            return 3.0
        return 4.0

    def _confidence_for(self, raw_ucb: float) -> RecommendationConfidence:
        if raw_ucb < 0.3:
            return RecommendationConfidence.high
        if raw_ucb <= 0.6:
            return RecommendationConfidence.medium
        return RecommendationConfidence.exploratory

    def _rationale_for(self, action_type: str) -> str:
        rationales = {
            "skill_certification": (
                "Role-aligned certification can improve short-horizon placement conversion for this profile."
            ),
            "resume_improvement": (
                "Sharper positioning improves employer response quality for the current salary band."
            ),
            "mock_interview": (
                "Interview readiness can shorten time-to-offer for this profile."
            ),
            "networking_outreach": (
                "Targeted outreach can accelerate employer conversations for this profile."
            ),
            "portfolio_project": (
                "A focused portfolio project can strengthen employer evidence for technical roles."
            ),
        }
        return rationales[action_type]
