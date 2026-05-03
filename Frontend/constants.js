// Shared demo data constants

export const DEMO_RESPONSE = {
    placement_6mo: { value: 0.64, confidence: 0.88, source_note: "Based on 700,000+ H1B LCA filings (OFLC 2022–2024)" },
    delayed_placement_risk: { flag: "MODERATE", reason: "Placement by 6 months is likely (64%) but significantly delayed from 3-month probability (38%). Given 9-month moratorium, proactive monitoring is recommended.", p3_p6_gap: 0.26 },
    salary_forecast: { pessimistic: 72000, realistic: 95000, optimistic: 118000, emi_monthly_usd: 1460, emi_as_pct_realistic: 18.4, source_note: "Based on 700,000+ H1B LCA filings (OFLC 2022–2024)" },
    repayment_score: { score: 71, tier: "GREEN", base_score_without_behavioral: 68, behavioral_boost_points: 3, employability_sub: 0.64, affordability_sub: 0.81, market_risk_sub: 0.74, data_confidence_sub: 0.88 },
    reliability: { band: "HIGH", behavioral_engagement: "HIGH", tenacity_score: 0.79, tenacity_data_count: 3, university_match_score: 97 },
    next_best_action: [
        { rank: 1, action_type: "skill_certification", title: "Role-aligned Certification", rationale: "Students at UT Austin MS CS who completed this certification saw 8% better placement within 6 months. High confidence from 312 profiles.", recommendation_confidence: "high" },
        { rank: 2, action_type: "portfolio_project", title: "Build a Portfolio Project", rationale: "Portfolio work improves employer engagement rate 23% for cloud and software engineering roles in the US market.", recommendation_confidence: "medium" },
        { rank: 3, action_type: "mock_interview", title: "Interview Practice", rationale: "Technical interview practice shows positive outcomes for this profile type. Still learning optimal timing.", recommendation_confidence: "exploratory" },
    ],
    employer_match_list: [
        { employer: "Infosys BPM Ltd", median_salary_usd: 89000, annual_h1b_filings: 420, visa_approval_rate: 0.91 },
        { employer: "Cognizant Technology", median_salary_usd: 92000, annual_h1b_filings: 380, visa_approval_rate: 0.89 },
        { employer: "TCS America", median_salary_usd: 87000, annual_h1b_filings: 312, visa_approval_rate: 0.84 },
        { employer: "Wipro Technologies", median_salary_usd: 88000, annual_h1b_filings: 287, visa_approval_rate: 0.78 },
        { employer: "Google LLC", median_salary_usd: 148000, annual_h1b_filings: 241, visa_approval_rate: 0.95 },
    ],
    explanation: {
        tier_1: "Strong placement outlook and manageable EMI burden drive a positive assessment. Priya's active behavioral engagement provides additional confidence. A moderate placement delay is possible — proactive upskilling is recommended.",
        tier_2_positive: ["Top-200 University (UT Austin)", "STEM OPT Extension Eligible", "EMI within 40% of realistic salary", "Cloud/Software — high demand sector", "Behavioral engagement: HIGH"],
        tier_2_risk: ["Moderate GRE score (imputed)", "High competition in target sector", "Certifications not yet collected", "Moderate 3-month placement gap"],
        tier_2_attribution: { base_rate: 0.62, strength_multiplier: 1.08, macro_adjustment: 0.94, tenacity_boost: 0.079 },
    },
};

export const PRE_ACTIONS = [
    { label: "AWS Cloud Fundamentals", hours: 14.2, days: 8, visits: 11, cert: true, pct: 89, level: "HIGH" },
    { label: "Resume Improvement", hours: 2.5, days: 3, visits: 4, cert: false, pct: 71, level: "GOOD" },
    { label: "Mock Interview", hours: 1.8, days: 1, visits: 2, cert: false, pct: 60, level: "FAIR" },
];

export const COHORTS = [
    { id: "US_MSCS_2024_Q1", program: "MS Computer Science", country: "US", size: 43, baseline: 74, current: 70, severity: "AMBER" },
    { id: "UK_MBA_2024_Q2", program: "MBA", country: "UK", size: 28, baseline: 68, current: 68, severity: "GREEN" },
    { id: "CA_ENG_2024_Q1", program: "MS Engineering", country: "CA", size: 31, baseline: 71, current: 63, severity: "RED" },
];

export const BLOBS = [
    { color: "rgba(59, 130, 246, 0.6)",   width: "35vw", height: "30vh", top: "10%",  left: "15%",  anim: "blob1", dur: "22s" },
    { color: "rgba(253, 164, 175, 0.55)", width: "30vw", height: "40vh", top: "45%",  left: "55%",  anim: "blob2", dur: "26s" },
    { color: "rgba(14, 165, 233, 0.5)",   width: "25vw", height: "30vh", top: "15%",  left: "65%",  anim: "blob3", dur: "30s" },
    { color: "rgba(244, 114, 182, 0.45)", width: "35vw", height: "35vh", top: "55%",  left: "15%",  anim: "blob4", dur: "24s" },
];
