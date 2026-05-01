import json
import uuid

from app.db.database import Database
from app.utils.time import utc_now_iso


class PersistenceService:
    """
    Async DB write operations. Every method is best-effort — callers must
    wrap in try/except so DB failures never block the demo flow.
    """

    def __init__(self, database: Database) -> None:
        self.db = database

    async def save_origination(
        self,
        application_id: str,
        student_id: str | None,
        payload_json: str,
        response_json: str,
        score: float,
        tier: str,
        reliability_band: str,
        delayed_placement_risk: str,
        behavioral_engagement: str,
        tenacity_score: float | None,
        macro_snapshot_ts: str,
        scored_at: str,
    ) -> None:
        conn = await self.db.connect()
        now = utc_now_iso()
        if student_id:
            await conn.execute(
                """
                INSERT OR IGNORE INTO students (id, full_name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (student_id, "Demo Student", now, now),
            )
        await conn.execute(
            """
            INSERT OR REPLACE INTO applications
                (id, student_id, student_json, loan_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (application_id, student_id, payload_json, payload_json, scored_at),
        )
        result_id = str(uuid.uuid4())
        await conn.execute(
            """
            INSERT OR REPLACE INTO scoring_results (
                id, application_id, score, tier, reliability_band,
                delayed_placement_risk, behavioral_engagement, tenacity_score,
                model_version, macro_snapshot_ts, full_output_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result_id, application_id, score, tier, reliability_band,
                delayed_placement_risk, behavioral_engagement, tenacity_score,
                "demo-rule-based-v2", macro_snapshot_ts, response_json, now,
            ),
        )
        await conn.commit()

    async def upsert_student_action(
        self,
        action_id: str,
        student_id: str,
        action_type: str,
        title: str,
        status: str,
        assigned_at: str,
        expected_effort_hours: float,
        total_active_seconds: int,
        return_visits: int,
        certificate_uploaded: bool,
        completed_at: str | None = None,
        bandit_arm_index: int | None = None,
        score_before: float | None = None,
        score_after: float | None = None,
        reward_signal: float | None = None,
    ) -> None:
        conn = await self.db.connect()
        now = utc_now_iso()
        if student_id:
            await conn.execute(
                """
                INSERT OR IGNORE INTO students (id, full_name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (student_id, "Demo Student", now, now),
            )
        await conn.execute(
            """
            INSERT OR REPLACE INTO student_actions (
                id, student_id, action_type, title, status, assigned_at,
                started_at, completed_at, expected_effort_hours,
                total_active_seconds, return_visits, certificate_uploaded,
                bandit_arm_index, score_before, score_after,
                counterfactual_score, reward_signal, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action_id, student_id, action_type, title, status, assigned_at,
                None, completed_at, expected_effort_hours,
                total_active_seconds, return_visits, int(certificate_uploaded),
                bandit_arm_index, score_before, score_after,
                None, reward_signal, now, now,
            ),
        )
        await conn.commit()

    async def update_scoring_result_after_action(
        self,
        application_id: str,
        new_score: float,
        new_tier: str,
        new_tenacity_score: float | None,
        new_behavioral_engagement: str,
        response_json: str,
    ) -> None:
        conn = await self.db.connect()
        now = utc_now_iso()
        await conn.execute(
            """
            UPDATE scoring_results
            SET score = ?, tier = ?, tenacity_score = ?,
                behavioral_engagement = ?, full_output_json = ?
            WHERE application_id = ?
            """,
            (
                new_score, new_tier, new_tenacity_score,
                new_behavioral_engagement, response_json, application_id,
            ),
        )
        await conn.commit()
