import pytest
from app.services.scoring import DemoScoringService
from app.schemas.score import OriginationScoringRequest
from app.services.demo_store import DemoStore
from app.services.artifact_loader import ArtifactRegistry
from app.core.config import get_settings

@pytest.fixture
def scoring_service():
    store = DemoStore()
    settings = get_settings()
    artifacts = ArtifactRegistry(settings.artifacts_dir)
    # Don't strictly need to load artifacts if we are just testing basic structure,
    # but let's load them or use a mocked one if needed.
    return DemoScoringService(store=store, artifacts=artifacts)

@pytest.mark.unit
def test_scoring_service_origination(scoring_service):
    request = OriginationScoringRequest(
        student_id="student_123",
        full_name="John Doe",
        university_name="Stanford University",
        program_name="Computer Science",
        destination_country="USA",
        target_sector="Technology",
        cgpa=9.0,
        cgpa_present=True,
        internship_count=2,
        internship_count_present=True,
        stem_opt_eligible=True,
        stem_opt_eligible_present=True,
        loan_amount_inr=4000000,
        interest_rate_annual_pct=10.5,
        repayment_term_months=120,
        moratorium_months=24
    )
    
    # We can test origination scoring
    response, scored_at = scoring_service.score_origination(request)
    
    assert response.application_id is not None
    assert response.repayment_score.score > 0
    assert response.reliability.band is not None
    assert len(response.next_best_action) > 0
