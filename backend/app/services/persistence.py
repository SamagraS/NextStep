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

    async def get_user_by_email(self, email: str) -> dict | None:
        conn = await self.db.connect()
        async with conn.execute(
            "SELECT id, email, password_hash, role, created_at FROM users WHERE email = ?",
            (email.lower(),),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "password_hash": row[2],
                    "role": row[3],
                }
        return None

    async def seed_demo_users(self, auth_service: any) -> None:
        conn = await self.db.connect()
        now = utc_now_iso()
        demo_users = [
            ("user-priya", "priya@example.com", "password123", "student", "Priya Sharma"),
            ("user-aravind", "aravind@example.com", "password123", "student", "Aravind Nair"),
            ("user-sarah", "sarah@example.com", "password123", "student", "Sarah Jenkins"),
            ("user-uw", "underwriter@nextstep.com", "uwpass", "underwriter", "Senior Underwriter"),
            ("user-pm", "manager@nextstep.com", "pmpass", "portfolio_manager", "Portfolio Lead"),
        ]

        for uid, email, password, role, name in demo_users:
            p_hash = auth_service.get_password_hash(password)
            # Insert into users
            await conn.execute(
                """
                INSERT OR REPLACE INTO users (id, email, password_hash, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (uid, email.lower(), p_hash, role, now, now),
            )
            # If student, also insert into students table if not exists
            if role == "student":
                student_id = f"student-{email.split('@')[0]}"
                await conn.execute(
                    """
                    INSERT OR IGNORE INTO students (id, user_id, full_name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (student_id, uid, name, now, now),
                )
        
        await conn.commit()

    async def upsert_student(self, student_id: str, full_name: str, country: str, program_family: str, macro_summary: str, readiness_base_score: int) -> None:
        conn = await self.db.connect()
        now = utc_now_iso()
        await conn.execute(
            """
            INSERT INTO students (id, full_name, destination_country, program_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                full_name = excluded.full_name,
                destination_country = excluded.destination_country,
                program_name = excluded.program_name,
                updated_at = excluded.updated_at
            """,
            (student_id, full_name, country, program_family, now, now),
        )
        # Note: program_family and macro_summary might be in a metadata field or handled in DemoStore
        await conn.commit()

    async def upsert_cohort(self, cohort_id: str, program_name: str, country: str, size: int, baseline: float, current: float) -> None:
        conn = await self.db.connect()
        now = utc_now_iso()
        await conn.execute(
            """
            INSERT INTO cohorts (id, program_name, destination_country, cohort_size, baseline_score, current_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                program_name = excluded.program_name,
                destination_country = excluded.destination_country,
                cohort_size = excluded.cohort_size,
                baseline_score = excluded.baseline_score,
                current_score = excluded.current_score,
                updated_at = excluded.updated_at
            """,
            (cohort_id, program_name, country, size, baseline, current, now, now),
        )
        await conn.commit()

    async def upsert_cohort_alert(self, alert_id: str, cohort_id: str, severity: str, delta: float, driver: str, action: str, ts: str, created_at: str) -> None:
        conn = await self.db.connect()
        await conn.execute(
            """
            INSERT INTO cohort_alerts (id, cohort_id, severity, delta, primary_macro_driver, recommended_action, macro_snapshot_ts, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (alert_id, cohort_id, severity, delta, driver, action, ts, created_at),
        )
        await conn.commit()

    async def get_all_students(self) -> list[dict]:
        conn = await self.db.connect()
        async with conn.execute("SELECT id, full_name, destination_country, program_name FROM students") as cursor:
            return [{"id": r[0], "full_name": r[1], "destination_country": r[2], "program_family": r[3]} for r in await cursor.fetchall()]

    async def get_all_cohorts(self) -> list[dict]:
        conn = await self.db.connect()
        async with conn.execute("SELECT id, program_name, destination_country, cohort_size, baseline_score, current_score FROM cohorts") as cursor:
            return [{"id": r[0], "program_name": r[1], "destination_country": r[2], "cohort_size": r[3], "baseline_score": r[4], "current_score": r[5]} for r in await cursor.fetchall()]

    async def get_all_alerts(self) -> list[dict]:
        conn = await self.db.connect()
        async with conn.execute("SELECT id, cohort_id, severity, delta, primary_macro_driver, recommended_action, macro_snapshot_ts, created_at FROM cohort_alerts") as cursor:
            return [{"id": r[0], "cohort_id": r[1], "severity": r[2], "delta": r[3], "primary_macro_driver": r[4], "recommended_action": r[5], "macro_snapshot_ts": r[6], "created_at": r[7]} for r in await cursor.fetchall()]

    async def get_all_student_actions(self, student_id: str) -> list[dict]:
        conn = await self.db.connect()
        async with conn.execute(
            "SELECT id, action_type, title, status, assigned_at, expected_effort_hours, total_active_seconds, return_visits, certificate_uploaded, completed_at FROM student_actions WHERE student_id = ?",
            (student_id,),
        ) as cursor:
            return [{
                "id": r[0], "action_type": r[1], "title": r[2], "status": r[3],
                "assigned_at": r[4], "expected_effort_hours": r[5], "total_active_seconds": r[6],
                "return_visits": r[7], "certificate_uploaded": bool(r[8]), "completed_at": r[9]
            } for r in await cursor.fetchall()]

    async def seed_all(self, demo_store: any) -> None:
        """
        Idempotently seed students, cohorts, and initial alerts from DemoStore.
        """
        # Seed students and their actions
        for sid, s in demo_store.students.items():
            await self.upsert_student(
                sid, s.full_name, s.destination_country, 
                s.program_family, s.macro_summary, s.readiness_base_score
            )
            for a in s.dashboard_actions:
                await self.upsert_student_action(
                    a.action_id, sid, a.action_type, a.title,
                    a.status, a.assigned_at, a.expected_effort_hours,
                    a.total_active_seconds, a.return_visits, a.certificate_uploaded,
                    a.completed_at
                )

        # Seed cohorts
        for cid, c in demo_store.cohorts.items():
            await self.upsert_cohort(
                cid, c.program_name, c.destination_country,
                c.cohort_size, c.baseline_score, c.current_score
            )

        # Seed alerts
        for aid, a in demo_store.cohort_alerts.items():
            await self.upsert_cohort_alert(
                aid, a.cohort_id, a.severity, a.delta,
                a.primary_macro_driver, a.recommended_action,
                a.macro_snapshot_ts, a.created_at
            )
