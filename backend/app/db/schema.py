TABLE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('underwriter', 'portfolio_manager', 'student')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        full_name TEXT NOT NULL,
        university_name TEXT,
        program_name TEXT,
        destination_country TEXT,
        target_sector TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        student_id TEXT,
        student_json TEXT NOT NULL,
        loan_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS scoring_results (
        id TEXT PRIMARY KEY,
        application_id TEXT NOT NULL,
        score REAL NOT NULL,
        tier TEXT NOT NULL CHECK (tier IN ('GREEN', 'AMBER', 'RED')),
        reliability_band TEXT NOT NULL CHECK (reliability_band IN ('HIGH', 'MEDIUM', 'LOW')),
        delayed_placement_risk TEXT NOT NULL CHECK (delayed_placement_risk IN ('HIGH', 'MODERATE', 'LOW')),
        behavioral_engagement TEXT NOT NULL CHECK (behavioral_engagement IN ('HIGH', 'MODERATE', 'LOW', 'NONE')),
        tenacity_score REAL,
        model_version TEXT NOT NULL,
        macro_snapshot_ts TEXT NOT NULL,
        full_output_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (application_id) REFERENCES applications(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS student_actions (
        id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        action_type TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('assigned', 'started', 'completed')),
        assigned_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        expected_effort_hours REAL,
        total_active_seconds INTEGER NOT NULL DEFAULT 0,
        return_visits INTEGER NOT NULL DEFAULT 0,
        certificate_uploaded INTEGER NOT NULL DEFAULT 0,
        bandit_arm_index INTEGER,
        score_before REAL,
        score_after REAL,
        counterfactual_score REAL,
        reward_signal REAL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS student_interaction_events (
        id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        action_id TEXT,
        event_type TEXT NOT NULL CHECK (
            event_type IN (
                'page_view',
                'session_active',
                'session_idle',
                'resource_clicked',
                'action_started',
                'action_completed',
                'certification_uploaded',
                'return_visit'
            )
        ),
        occurred_at TEXT NOT NULL,
        metadata_json TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (action_id) REFERENCES student_actions(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS cohorts (
        id TEXT PRIMARY KEY,
        program_name TEXT NOT NULL,
        destination_country TEXT NOT NULL,
        cohort_size INTEGER NOT NULL,
        baseline_score REAL NOT NULL,
        current_score REAL NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS cohort_alerts (
        id TEXT PRIMARY KEY,
        cohort_id TEXT NOT NULL,
        severity TEXT NOT NULL CHECK (severity IN ('AMBER', 'RED')),
        delta REAL NOT NULL,
        primary_macro_driver TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        macro_snapshot_ts TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (cohort_id) REFERENCES cohorts(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS macro_signal_cache (
        destination_country TEXT PRIMARY KEY,
        signal_payload_json TEXT NOT NULL,
        snapshot_ts TEXT NOT NULL,
        stale_warning TEXT,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS bandit_checkpoints (
        id TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        state_json TEXT NOT NULL,
        saved_at TEXT NOT NULL
    );
    """,
]

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_student_id ON applications(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_scoring_results_application_id ON scoring_results(application_id);",
    "CREATE INDEX IF NOT EXISTS idx_student_actions_student_id ON student_actions(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_student_actions_status ON student_actions(status);",
    "CREATE INDEX IF NOT EXISTS idx_student_interaction_events_student_id ON student_interaction_events(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_student_interaction_events_action_id ON student_interaction_events(action_id);",
    "CREATE INDEX IF NOT EXISTS idx_cohort_alerts_cohort_id ON cohort_alerts(cohort_id);",
    "CREATE INDEX IF NOT EXISTS idx_cohort_alerts_severity ON cohort_alerts(severity);",
]
