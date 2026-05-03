import { useState, useEffect, useRef } from "react";

/* ─────────────────────────────────────────────────────────────────────────────
   NEXTSTEP · CHUNK 2 · Underwriter Console
   Light theme — clean, data-dense, theatrical score reveal
   Drop-in replacement for PlaceholderUnderwriter from Chunk 1
   ───────────────────────────────────────────────────────────────────────────── */

const UW_CSS = `
/* ── Page shell ─────────────────────────────── */
.uw-page { background:transparent; min-height:calc(100vh - 60px); }
.uw-wrap {
  display:grid; grid-template-columns: 100% 0%;
  min-height:calc(100vh - 60px);
  align-items:start;
  transition: grid-template-columns 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}
.uw-wrap.scored {
  grid-template-columns: 42% 58%;
}

/* ── Columns ─────────────────────────────────── */
.uw-left {
  background:rgba(244,245,251,0.85);
  backdrop-filter: blur(12px);
  border-right:1px solid rgba(0,0,0,0.07);
  padding:32px 40px;
  position:sticky; top:60px;
  height:calc(100vh - 60px);
  overflow-y:auto;
  transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}
.uw-left-inner {
  max-width: 580px;
  margin: 0 auto;
  width: 100%;
}
.uw-right {
  padding:28px 32px 60px;
  height: calc(100vh - 60px);
  overflow-y:auto;
  overflow-x:hidden;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.uw-wrap.scored .uw-right {
  opacity: 1;
  transition: opacity 0.8s ease 0.4s;
}
.uw-right-inner {
  min-width: 580px;
}

/* ── Section label ───────────────────────────── */
.sec-lbl {
  font-family:var(--fd); font-size:9px; font-weight:800;
  letter-spacing:.16em; text-transform:uppercase;
  color:#94A3B8; margin-bottom:14px;
}

/* ── White card ───────────────────────────────── */
.wcard {
  background:#fff;
  border:1px solid rgba(0,0,0,0.07);
  border-radius:16px;
  padding:22px;
  box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.wcard + .wcard { margin-top:12px; }

/* ── Form inputs (light) ──────────────────────── */
.fw-in {
  width:100%; background:#F8F9FD;
  border:1px solid rgba(0,0,0,0.1); border-radius:10px;
  padding:10px 13px; color:#0F172A;
  font-family:var(--fb); font-size:13.5px; outline:none;
  transition:border-color .15s, background .15s, box-shadow .15s;
}
.fw-in:focus {
  border-color:#6366F1;
  background:#fff;
  box-shadow:0 0 0 3px rgba(99,102,241,0.12);
}
.fw-in::placeholder { color:#CBD5E1; }
.fw-lbl {
  display:flex; align-items:center; gap:5px;
  font-family:var(--fd); font-size:10px; font-weight:700;
  letter-spacing:.06em; text-transform:uppercase;
  color:#64748B; margin-bottom:6px;
}
.fw-req { width:4px; height:4px; border-radius:50%; background:#EF4444; display:inline-block; }

.fw-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
.fw-col { display:flex; flex-direction:column; }

/* ── Pre-loan panel ───────────────────────────── */
.preloan {
  border:1px solid rgba(245,158,11,0.25);
  border-left:3px solid #F59E0B;
  border-radius:0px; /* SHARP RECTANGLES */
  background:rgba(245,158,11,0.04);
  padding:18px;
  margin-bottom:20px;
  animation:fade-up .4s ease both .1s; opacity:0;
}
.preloan-hdr {
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:14px;
}
.preloan-row {
  padding:10px 0;
  border-bottom:1px solid rgba(245,158,11,0.1);
}
.preloan-row:last-child { border-bottom:none; padding-bottom:0; }
.eng-bar-track { height:4px; border-radius:99px; background:rgba(0,0,0,0.08); margin-top:7px; overflow:hidden; }
.eng-bar-fill  { height:100%; border-radius:99px; animation:fill-bar 1s cubic-bezier(.22,1,.36,1) both; }

/* ── Submit button ────────────────────────────── */
.submit-btn {
  width:100%; height:50px;
  display:flex; align-items:center; justify-content:center; gap:9px;
  border:none; border-radius:0px; cursor:pointer; /* SHARP RECTANGLES */
  font-family:var(--fd); font-size:14px; font-weight:800;
  letter-spacing:-.01em; color:#fff;
  background:linear-gradient(135deg,#6366F1 0%,#5b5beb 50%,#4f46e5 100%);
  box-shadow:0 4px 20px rgba(99,102,241,0.35), inset 0 1px 0 rgba(255,255,255,0.18);
  position:relative; overflow:hidden;
  transition:transform .15s, box-shadow .15s;
  margin-top:22px;
}
.submit-btn:hover:not(:disabled) {
  transform:translateY(-1px);
  box-shadow:0 6px 28px rgba(99,102,241,0.45), inset 0 1px 0 rgba(255,255,255,0.18);
}
.submit-btn:active { transform:scale(0.98); }
.submit-btn:disabled { opacity:.7; cursor:default; }
.btn-shimmer {
  position:absolute; inset:0; pointer-events:none;
  background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,0.18) 50%,transparent 70%);
  animation:shimmer 2.8s ease infinite;
}

/* ── Empty results state ──────────────────────── */
.empty-results {
  display:flex; flex-direction:column; align-items:center;
  justify-content:center; min-height:60vh; gap:12px;
}
.ghost-dial {
  width:180px; height:180px; opacity:0.2;
  border-radius:50%; position:relative;
}

/* ── Result blocks animation ──────────────────── */
.result-block {
  animation:fade-up .45s cubic-bezier(.22,1,.36,1) both;
  opacity:0;
}

/* ── Score hero ───────────────────────────────── */
.score-hero {
  display:flex; align-items:center; gap:28px;
  padding:24px 26px;
}
.score-meta { flex:1; }
.score-main {
  font-family:var(--fd); font-size:72px; font-weight:800;
  letter-spacing:-.05em; line-height:1;
}
.score-slash {
  font-size:24px; font-weight:500; color:#94A3B8;
  font-family:var(--fd); align-self:flex-end; padding-bottom:10px;
}
.score-tier-label {
  font-family:var(--fd); font-size:13px; font-weight:700;
  letter-spacing:.04em; text-transform:uppercase;
  margin-top:6px;
}
.behavioral-note {
  display:flex; align-items:center; gap:6px;
  margin-top:10px;
  padding:8px 12px; border-radius:10px;
  background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2);
  font-size:12px; color:#B45309;
  animation:fade-in .4s ease both 1.8s; opacity:0;
}

/* ── Sub-score bars ───────────────────────────── */
.ss-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.ss-item {}
.ss-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; }
.ss-label { font-family:var(--fd); font-size:11px; font-weight:700; color:#475569; letter-spacing:.03em; }
.ss-val { font-family:var(--fd); font-size:14px; font-weight:800; letter-spacing:-.02em; }
.ss-track { height:6px; border-radius:99px; background:rgba(0,0,0,0.07); overflow:hidden; }
.ss-fill { height:100%; border-radius:99px; animation:fill-bar .9s cubic-bezier(.22,1,.36,1) both; }

/* ── Placement bars ───────────────────────────── */
.pl-row { margin-bottom:12px; }
.pl-row:last-child { margin-bottom:0; }
.pl-header { display:flex; justify-content:space-between; margin-bottom:5px; }
.pl-label { font-family:var(--fd); font-size:12px; font-weight:600; color:#475569; }
.pl-pct { font-family:var(--fd); font-size:13px; font-weight:800; }
.pl-track { height:8px; border-radius:99px; background:rgba(0,0,0,0.07); position:relative; overflow:visible; }
.pl-fill { height:100%; border-radius:99px; animation:fill-bar .9s cubic-bezier(.22,1,.36,1) both; position:relative; }
.pl-mora-line {
  position:absolute; top:-5px; bottom:-5px; width:2px;
  background:#EF4444; border-radius:2px;
  animation:fade-in .3s ease both 1.2s; opacity:0;
}
.mora-label {
  position:absolute; top:-24px; left:50%; transform:translateX(-50%);
  font-family:var(--fm); font-size:9px; color:#EF4444; white-space:nowrap;
  font-weight:600; letter-spacing:.04em;
}
.delayed-flag {
  margin-top:12px; padding:12px 14px; border-radius:12px;
  background:rgba(245,158,11,0.06); border:1px solid rgba(245,158,11,0.2);
  border-left:3px solid #F59E0B;
  font-size:13px; color:#92400E; line-height:1.5;
}

/* ── Salary range ─────────────────────────────── */
.sal-range-wrap { position:relative; padding:14px 0 20px; }
.sal-line { position:absolute; top:27px; left:0; right:0; height:3px; background:rgba(0,0,0,0.08); border-radius:99px; }
.sal-gradient-line { position:absolute; top:27px; height:3px; border-radius:99px;
  background:linear-gradient(90deg,#F59E0B,#10B981,#3B82F6);
  animation:fill-bar .9s cubic-bezier(.22,1,.36,1) both .2s; }
.sal-dots { display:flex; justify-content:space-between; position:relative; }
.sal-dot-wrap { display:flex; flex-direction:column; align-items:center; gap:0; }
.sal-dot { width:14px; height:14px; border-radius:50%; border:2px solid #fff;
  box-shadow:0 2px 6px rgba(0,0,0,0.15); z-index:1; margin-bottom:6px; }
.sal-amt { font-family:var(--fd); font-size:16px; font-weight:800; letter-spacing:-.03em; }
.sal-tag { font-family:var(--fd); font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#94A3B8; margin-top:2px; }
.sal-emi { text-align:center; margin-top:6px; font-size:13px; color:#475569; }
.sal-emi strong { color:#0F172A; font-family:var(--fd); font-weight:700; }

/* ── Explanation ──────────────────────────────── */
.tier1-card {
  background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.15);
  border-radius:14px; padding:16px 18px;
  font-size:14px; color:#1E293B; line-height:1.65;
  margin-bottom:16px; font-style:italic;
}
.factors-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:18px; }
.factors-col {}
.factors-col-lbl {
  font-family:var(--fd); font-size:9px; font-weight:800; letter-spacing:.1em;
  text-transform:uppercase; margin-bottom:8px;
}
.factor-pill {
  display:flex; align-items:flex-start; gap:7px;
  padding:7px 10px; border-radius:9px; margin-bottom:5px;
  font-size:12px; font-weight:500; line-height:1.4;
}
.factor-icon { width:16px; height:16px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }

/* ── Attribution waterfall ────────────────────── */
.waterfall {
  display:flex; align-items:center; gap:0;
  background:rgba(0,0,0,0.03); border-radius:14px;
  padding:16px; overflow-x:auto;
}
.wf-box {
  display:flex; flex-direction:column; align-items:center; gap:4px;
  flex:1; animation:fade-up .4s ease both; opacity:0;
}
.wf-val {
  font-family:var(--fd); font-size:20px; font-weight:800; letter-spacing:-.04em;
  color:#0F172A;
}
.wf-lbl { font-family:var(--fd); font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#94A3B8; text-align:center; }
.wf-op {
  font-family:var(--fd); font-size:22px; font-weight:300; color:#CBD5E1;
  padding:0 6px; align-self:center; flex-shrink:0;
}
.wf-result {
  padding:12px 16px; border-radius:11px;
  background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
  display:flex; flex-direction:column; align-items:center; gap:4px;
}
.wf-result .wf-val { color:#6366F1; }

/* ── Action cards ─────────────────────────────── */
.action-cards { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.action-card {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:14px;
  padding:18px; cursor:pointer;
  transition:transform .18s cubic-bezier(.22,1,.36,1), box-shadow .18s, border-color .18s;
  animation:fade-up .4s cubic-bezier(.22,1,.36,1) both;
  opacity:0; position:relative; overflow:hidden;
}
.action-card:hover {
  transform:translateY(-3px);
  box-shadow:0 8px 24px rgba(0,0,0,0.1);
}
.action-card-top { margin-bottom:10px; }
.action-name { font-family:var(--fd); font-size:14px; font-weight:800; color:#0F172A; letter-spacing:-.02em; margin-bottom:4px; }
.action-rationale { font-size:12px; color:#64748B; line-height:1.55; margin-bottom:12px; }
.action-footer { display:flex; align-items:center; justify-content:space-between; }
.assign-btn {
  padding:5px 12px; border-radius:8px; border:none; cursor:pointer;
  font-family:var(--fd); font-size:11px; font-weight:700; letter-spacing:.03em;
  background:#6366F1; color:#fff;
  transition:background .15s, transform .12s;
}
.assign-btn:hover { background:#5254d4; transform:scale(1.04); }
.action-card.conf-high  { border-top:3px solid #10B981; }
.action-card.conf-med   { border-top:3px solid #F59E0B; }
.action-card.conf-exp   { border-top:3px solid #94A3B8; }
.conf-label { font-family:var(--fd); font-size:9px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }

/* ── Employer table ───────────────────────────── */
.emp-table { width:100%; border-collapse:collapse; }
.emp-table thead tr { border-bottom:2px solid rgba(0,0,0,0.06); }
.emp-table th {
  padding:10px 12px; text-align:left;
  font-family:var(--fd); font-size:9px; font-weight:800;
  letter-spacing:.12em; text-transform:uppercase; color:#94A3B8;
}
.emp-table tbody tr {
  border-bottom:1px solid rgba(0,0,0,0.05);
  transition:background .12s;
  animation:fade-up .35s ease both; opacity:0;
}
.emp-table tbody tr:hover { background:rgba(99,102,241,0.03); }
.emp-table td { padding:11px 12px; font-size:13px; color:#1E293B; }
.emp-rank { font-family:var(--fm); font-size:11px; color:#94A3B8; font-weight:500; }
.visa-dots { display:flex; gap:3px; align-items:center; }
.visa-dot { width:7px; height:7px; border-radius:50%; }

/* ── Section divider ──────────────────────────── */
.sec-divider {
  display:flex; align-items:center; gap:12px; margin:20px 0 16px;
}
.sec-divider-line { flex:1; height:1px; background:rgba(0,0,0,0.07); }
.sec-divider-label {
  font-family:var(--fd); font-size:9px; font-weight:800; letter-spacing:.14em;
  text-transform:uppercase; color:#CBD5E1;
}
.sec-num {
  width:20px; height:20px; border-radius:50%;
  background:#6366F1; color:#fff;
  font-family:var(--fd); font-size:9px; font-weight:800;
  display:flex; align-items:center; justify-content:center;
}

/* ── Reliability badges ───────────────────────── */
.rel-band {
  display:inline-flex; align-items:center; gap:6px;
  padding:4px 10px; border-radius:8px;
  font-family:var(--fd); font-size:10px; font-weight:800;
  letter-spacing:.06em; text-transform:uppercase;
  background:rgba(0,0,0,0.04); border:1px solid rgba(0,0,0,0.08); color:#475569;
}

/* ── Tier badge (large) ───────────────────────── */
.tier-badge-lg {
  display:inline-flex; align-items:center; gap:7px;
  padding:6px 14px; border-radius:99px;
  font-family:var(--fd); font-size:12px; font-weight:800;
  letter-spacing:.06em; text-transform:uppercase;
  animation:drop-spring .5s ease both 1.3s; opacity:0;
}
.tier-badge-lg.g { background:rgba(16,185,129,0.1); color:#059669; border:1.5px solid rgba(16,185,129,0.3); }
.tier-badge-lg.a { background:rgba(245,158,11,0.1); color:#D97706; border:1.5px solid rgba(245,158,11,0.3); }
.tier-badge-lg.r { background:rgba(239,68,68,0.1);  color:#DC2626; border:1.5px solid rgba(239,68,68,0.3); }
.tier-dot { width:8px; height:8px; border-radius:50%; background:currentColor; }

/* ── Score dial SVG glow ──────────────────────── */
.dial-glow { filter:drop-shadow(0 0 10px var(--dial-clr,#10B981)); }

/* ── Not-collected toggle ─────────────────────── */
.nc-toggle {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 8px; border-radius:6px;
  font-family:var(--fd); font-size:9px; font-weight:700; letter-spacing:.06em;
  cursor:pointer; user-select:none;
  border:1px solid rgba(0,0,0,0.12); background:#F8F9FD; color:#94A3B8;
  transition:all .15s;
}
.nc-toggle.on { background:#F1F5F9; color:#6366F1; border-color:rgba(99,102,241,0.3); }
`;

function StyleInjector2() {
    useEffect(() => {
        const id = "ns-uw";
        if (!document.getElementById(id)) {
            const el = document.createElement("style");
            el.id = id; el.textContent = UW_CSS;
            document.head.appendChild(el);
        }
        return () => document.getElementById(id)?.remove();
    }, []);
    return null;
}

// ── MOCK DATA ─────────────────────────────────────────────────────────────────
const MOCK = {
    application_id: "APP-2026-001337",
    placement_probability: { p_3mo: 0.38, p_6mo: 0.64, p_12mo: 0.83, moratorium_months: 9 },
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

const PRE_ACTIONS = [
    { label: "AWS Cloud Fundamentals", hours: 14.2, days: 8, visits: 11, cert: true, pct: 89, level: "HIGH" },
    { label: "Resume Improvement", hours: 2.5, days: 3, visits: 4, cert: false, pct: 71, level: "GOOD" },
    { label: "Mock Interview", hours: 1.8, days: 1, visits: 2, cert: false, pct: 60, level: "FAIR" },
];

// ── ICONS ─────────────────────────────────────────────────────────────────────
const Check = () => <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="1.5 6 4.5 9 10.5 3" /></svg>;
const X = () => <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="2" y1="2" x2="10" y2="10" /><line x1="10" y1="2" x2="2" y2="10" /></svg>;
const Bolt = () => <svg width="11" height="11" viewBox="0 0 12 12" fill="currentColor"><polygon points="7 1 2 7 6 7 5 11 10 5 6 5" /></svg>;
const Spin = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ animation: "spin .7s linear infinite" }}><path d="M21 12a9 9 0 11-3.5-7" /></svg>;
const Arr = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>;
const Warn = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><circle cx="12" cy="17" r=".5" fill="currentColor" /></svg>;

// ── HOOK: count-up number ─────────────────────────────────────────────────────
function useCountUp(target, duration = 1200, start = false) {
    const [val, setVal] = useState(0);
    useEffect(() => {
        if (!start) return;
        const startTime = performance.now();
        const raf = (now) => {
            const p = Math.min((now - startTime) / duration, 1);
            const ease = 1 - Math.pow(1 - p, 3);
            setVal(Math.round(ease * target));
            if (p < 1) requestAnimationFrame(raf);
        };
        requestAnimationFrame(raf);
    }, [start, target]);
    return val;
}

// ── SCORE DIAL ────────────────────────────────────────────────────────────────
const TIER_COLOR = { GREEN: "#10B981", AMBER: "#F59E0B", RED: "#EF4444" };
const TIER_CLASS = { GREEN: "g", AMBER: "a", RED: "r" };
const TIER_LABEL = { GREEN: "Green — Low Risk", AMBER: "Amber — Monitor", RED: "Red — High Risk" };
const ARC_LEN = 377; // 270° arc on r=80

function ScoreDial({ score, tier, animate }) {
    const [offset, setOffset] = useState(ARC_LEN);
    const displayScore = useCountUp(score, 1200, animate);

    useEffect(() => {
        if (!animate) return;
        const target = ARC_LEN * (1 - score / 100);
        const t = setTimeout(() => setOffset(target), 50);
        return () => clearTimeout(t);
    }, [animate, score]);

    const color = TIER_COLOR[tier] || "#10B981";
    const tc = TIER_CLASS[tier] || "g";

    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 0 }}>
            <div style={{ position: "relative", width: 190, height: 160 }}>
                <svg viewBox="0 0 200 175" width="190" height="160">
                    {/* Tick marks */}
                    {Array.from({ length: 11 }, (_, i) => {
                        const angle = 225 - i * 27; // degrees, in SVG convention
                        const rad = (angle * Math.PI) / 180;
                        const inner = 68, outer = 76;
                        const cx = 100 + Math.cos(rad) * inner;
                        const cy = 100 + Math.sin(rad) * inner; // note: using inverted for 225° start
                        return null; // Skip ticks for cleanliness
                    })}
                    {/* Track */}
                    <path
                        d="M 43 157 A 80 80 0 1 1 157 157"
                        fill="none" stroke="#E2E8F0" strokeWidth="11" strokeLinecap="round"
                    />
                    {/* Score arc */}
                    <path
                        d="M 43 157 A 80 80 0 1 1 157 157"
                        fill="none"
                        stroke={color}
                        strokeWidth="11"
                        strokeLinecap="round"
                        strokeDasharray={ARC_LEN}
                        strokeDashoffset={offset}
                        style={{
                            transition: animate ? "stroke-dashoffset 1.2s cubic-bezier(0.22,1,0.36,1)" : "none",
                            filter: `drop-shadow(0 0 8px ${color}80)`,
                        }}
                    />
                    {/* Center score number */}
                    <text x="100" y="108" textAnchor="middle"
                        style={{ fontFamily: "var(--fd)", fontSize: 46, fontWeight: 800, fill: color, letterSpacing: "-2px" }}>
                        {animate ? displayScore : score}
                    </text>
                    <text x="100" y="126" textAnchor="middle"
                        style={{ fontFamily: "var(--fd)", fontSize: 12, fontWeight: 600, fill: "#94A3B8", letterSpacing: "1px" }}>
                        /100
                    </text>
                    {/* Scale labels */}
                    <text x="36" y="172" textAnchor="middle"
                        style={{ fontFamily: "var(--fm)", fontSize: 9, fill: "#CBD5E1", fontWeight: 500 }}>0</text>
                    <text x="100" y="148" textAnchor="middle"
                        style={{ fontFamily: "var(--fm)", fontSize: 9, fill: "#CBD5E1", fontWeight: 500 }}>50</text>
                    <text x="164" y="172" textAnchor="middle"
                        style={{ fontFamily: "var(--fm)", fontSize: 9, fill: "#CBD5E1", fontWeight: 500 }}>100</text>
                </svg>
            </div>

            {/* Tier badge */}
            <div className={`tier-badge-lg ${tc}`} style={{ animationDelay: animate ? "1.3s" : "0s" }}>
                <div className="tier-dot" />
                {TIER_LABEL[tier]}
            </div>
        </div>
    );
}

// ── SUB SCORES ────────────────────────────────────────────────────────────────
function SubScores({ data, delay = 0 }) {
    const items = [
        { label: "Employability", val: data.employability_sub, delay: delay },
        { label: "Affordability", val: data.affordability_sub, delay: delay + 60 },
        { label: "Market Risk", val: data.market_risk_sub, delay: delay + 120 },
        { label: "Data Confidence", val: data.data_confidence_sub, delay: delay + 180 },
    ];
    const col = (v) => v >= 0.7 ? "#10B981" : v >= 0.45 ? "#F59E0B" : "#EF4444";
    return (
        <div className="ss-grid">
            {items.map((it, i) => (
                <div key={i} className="ss-item">
                    <div className="ss-header">
                        <span className="ss-label">{it.label}</span>
                        <span className="ss-val" style={{ color: col(it.val) }}>{Math.round(it.val * 100)}%</span>
                    </div>
                    <div className="ss-track">
                        <div className="ss-fill" style={{
                            width: `${it.val * 100}%`,
                            background: col(it.val),
                            animationDelay: `${it.delay}ms`,
                        }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

// ── PLACEMENT TIMELINE ────────────────────────────────────────────────────────
function PlacementTimeline({ data, delay = 0 }) {
    const { p_3mo, p_6mo, p_12mo, moratorium_months } = data;
    const rows = [
        { label: "Within 3 months", val: p_3mo, delay: delay },
        { label: "Within 6 months", val: p_6mo, delay: delay + 150 },
        { label: "Within 12 months", val: p_12mo, delay: delay + 300 },
    ];
    // Moratorium marker position (9mo out of 12 = 75% along the 12-month bar)
    const moraPos = (moratorium_months / 12) * 100;
    const col = (v) => v >= 0.7 ? "#10B981" : v >= 0.45 ? "#F59E0B" : "#EF4444";

    return (
        <div>
            {rows.map((r, i) => (
                <div key={i} className="pl-row">
                    <div className="pl-header">
                        <span className="pl-label">{r.label}</span>
                        <span className="pl-pct" style={{ color: col(r.val) }}>{Math.round(r.val * 100)}%</span>
                    </div>
                    <div className="pl-track">
                        <div className="pl-fill" style={{ width: `${r.val * 100}%`, background: `linear-gradient(90deg, ${col(r.val)}99, ${col(r.val)})`, animationDelay: `${r.delay}ms` }} />
                        {i === 2 && (
                            <div className="pl-mora-line" style={{ left: `${moraPos}%` }}>
                                <div className="mora-label">Moratorium end (mo. {moratorium_months})</div>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

// ── SALARY RANGE ──────────────────────────────────────────────────────────────
function SalaryRange({ data }) {
    const { pessimistic: p, realistic: r, optimistic: o, emi_as_pct_realistic: emi } = data;
    const fmt = (n) => `$${(n / 1000).toFixed(0)}K`;
    return (
        <div className="sal-range-wrap">
            <div className="sal-line" />
            <div className="sal-gradient-line" style={{ left: 0, right: 0 }} />
            <div className="sal-dots">
                <div className="sal-dot-wrap">
                    <div className="sal-dot" style={{ background: "#F59E0B" }} />
                    <div className="sal-amt" style={{ color: "#B45309" }}>{fmt(p)}</div>
                    <div className="sal-tag">Pessimistic</div>
                </div>
                <div className="sal-dot-wrap">
                    <div className="sal-dot" style={{ background: "#10B981" }} />
                    <div className="sal-amt" style={{ color: "#047857" }}>{fmt(r)}</div>
                    <div className="sal-tag">Realistic</div>
                    <div style={{ fontSize: 10, fontFamily: "var(--fd)", fontWeight: 700, color: "#6366F1", marginTop: 4, background: "rgba(99,102,241,0.1)", padding: "2px 7px", borderRadius: 6 }}>
                        EMI: {emi}%
                    </div>
                </div>
                <div className="sal-dot-wrap">
                    <div className="sal-dot" style={{ background: "#3B82F6" }} />
                    <div className="sal-amt" style={{ color: "#1D4ED8" }}>{fmt(o)}</div>
                    <div className="sal-tag">Optimistic</div>
                </div>
            </div>
            <div className="sal-emi" style={{ marginTop: 18, fontSize: 12, color: "#64748B" }}>
                <strong>EMI is {emi}% of expected realistic salary</strong> · {data.source_note}
            </div>
        </div>
    );
}

// ── EXPLANATION ───────────────────────────────────────────────────────────────
function ExplanationBlock({ data, show }) {
    const attr = data.tier_2_attribution;
    const wfBoxes = [
        { val: attr.base_rate.toFixed(2), label: "Base Rate", delay: show ? 0 : 999 },
        { op: "×" },
        { val: attr.strength_multiplier.toFixed(2), label: "Strength ×", delay: show ? 120 : 999 },
        { op: "×" },
        { val: attr.macro_adjustment.toFixed(2), label: "Macro ×", delay: show ? 240 : 999 },
        { op: "=" },
    ];

    return (
        <div>
            <div className="tier1-card">"{data.tier_1}"</div>

            <div className="factors-grid">
                <div className="factors-col">
                    <div className="factors-col-lbl" style={{ color: "#059669" }}>✓ Positive factors</div>
                    {data.tier_2_positive.map((f, i) => (
                        <div key={i} className="factor-pill" style={{ background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.15)" }}>
                            <div className="factor-icon" style={{ background: "#D1FAE5", color: "#059669" }}><Check /></div>
                            <span style={{ fontSize: 12, color: "#065F46" }}>{f}</span>
                        </div>
                    ))}
                </div>
                <div className="factors-col">
                    <div className="factors-col-lbl" style={{ color: "#DC2626" }}>✗ Risk factors</div>
                    {data.tier_2_risk.map((f, i) => (
                        <div key={i} className="factor-pill" style={{ background: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.12)" }}>
                            <div className="factor-icon" style={{ background: "#FEE2E2", color: "#DC2626" }}><X /></div>
                            <span style={{ fontSize: 12, color: "#7F1D1D" }}>{f}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ marginBottom: 10 }}>
                <div className="sec-lbl">Score breakdown</div>
                <div className="waterfall">
                    {wfBoxes.map((b, i) =>
                        b.op
                            ? <div key={i} className="wf-op">{b.op}</div>
                            : (
                                <div key={i} className="wf-box" style={{ animationDelay: `${b.delay}ms` }}>
                                    <div style={{
                                        padding: "12px 14px", borderRadius: 12, background: "#fff",
                                        border: "1px solid rgba(0,0,0,0.08)", textAlign: "center", minWidth: 72,
                                    }}>
                                        <div className="wf-val">{b.val}</div>
                                        <div className="wf-lbl" style={{ marginTop: 4 }}>{b.label}</div>
                                    </div>
                                </div>
                            )
                    )}
                    <div className="wf-result" style={{ animationDelay: show ? "360ms" : "999ms", animation: `fade-up .4s ease both ${show ? "360ms" : "999ms"}`, opacity: 0 }}>
                        <div className="wf-val">{(attr.base_rate * attr.strength_multiplier * attr.macro_adjustment).toFixed(2)}</div>
                        <div className="wf-lbl" style={{ marginTop: 4 }}>Final Prob.</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ── ACTION CARDS ──────────────────────────────────────────────────────────────
const ACTION_ICON = {
    skill_certification: "🎓",
    portfolio_project: "💼",
    mock_interview: "🎯",
    networking_outreach: "🤝",
};
const CONF_INFO = {
    high: { label: "High confidence", color: "#059669", cls: "conf-high" },
    medium: { label: "Med. confidence", color: "#D97706", cls: "conf-med" },
    exploratory: { label: "Exploratory", color: "#64748B", cls: "conf-exp" },
};

function ActionCards({ actions, onAssign, delay = 0 }) {
    const [assigned, setAssigned] = useState({});
    const assign = (rank) => {
        setAssigned(p => ({ ...p, [rank]: true }));
        onAssign?.(rank);
    };

    return (
        <div className="action-cards">
            {actions.map((a, i) => {
                const ci = CONF_INFO[a.recommendation_confidence] || CONF_INFO.exploratory;
                const done = assigned[a.rank];
                return (
                    <div key={i} className={`action-card ${ci.cls}`}
                        style={{ animationDelay: `${delay + i * 80}ms` }}>
                        <div style={{ fontSize: 22, marginBottom: 8 }}>{ACTION_ICON[a.action_type] || "📋"}</div>
                        <div className="action-name">{a.title || a.label}</div>
                        <div className="action-rationale">{a.rationale}</div>
                        <div className="action-footer">
                            <div className="conf-label" style={{ color: ci.color }}>{ci.label}</div>
                            <button className="assign-btn" onClick={() => assign(a.rank)}
                                style={{ background: done ? "#10B981" : "#6366F1" }}>
                                {done ? "✓ Assigned" : "Assign →"}
                            </button>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

// ── EMPLOYER TABLE ────────────────────────────────────────────────────────────
function EmployerTable({ employers, delay = 0 }) {
    const visaDots = (rate) => {
        const filled = Math.round(rate * 4);
        return Array.from({ length: 4 }, (_, i) => (
            <div key={i} className="visa-dot" style={{ background: i < filled ? (rate >= 0.85 ? "#10B981" : rate >= 0.7 ? "#F59E0B" : "#EF4444") : "#E2E8F0" }} />
        ));
    };
    return (
        <table className="emp-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Company</th>
                    <th>Median Salary</th>
                    <th>Annual Hires</th>
                    <th>Visa Approval</th>
                </tr>
            </thead>
            <tbody>
                {employers.map((e, i) => (
                    <tr key={i} style={{ animationDelay: `${delay + i * 60}ms` }}>
                        <td><span className="emp-rank">{i + 1}</span></td>
                        <td style={{ fontWeight: 600, color: "#0F172A" }}>{e.employer}</td>
                        <td style={{ fontFamily: "var(--fd)", fontWeight: 700 }}>${(e.median_salary_usd / 1000).toFixed(0)}K</td>
                        <td style={{ color: "#475569" }}>{e.annual_h1b_filings}/yr</td>
                        <td>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <div className="visa-dots">{visaDots(e.visa_approval_rate)}</div>
                                <span style={{ fontFamily: "var(--fm)", fontSize: 11, color: "#475569" }}>{Math.round(e.visa_approval_rate * 100)}%</span>
                            </div>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

// ── PRE-LOAN PANEL ────────────────────────────────────────────────────────────
function PreLoanPanel({ data }) {
    if (!data) return (
        <div className="preloan sk" style={{ height: 160, marginBottom: 20, opacity: 0.5 }} />
    );

    const actions = data.completed_actions || [];
    const tenacity = data.tenacity_summary?.tenacity_score || 0;
    const engagement = data.tenacity_summary?.behavioral_engagement || "NONE";

    return (
        <div className="preloan">
            <div className="preloan-hdr">
                <div>
                    <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".12em", textTransform: "uppercase", color: "#B45309", marginBottom: 3 }}>
                        Pre-Loan Behavioral Engagement
                    </div>
                    <div style={{ fontFamily: "var(--fd)", fontSize: 13, fontWeight: 700, color: "#0F172A" }}>Priya Sharma · {actions.length} actions completed</div>
                </div>
                <div style={{ textAlign: "right" }}>
                    <div style={{ fontFamily: "var(--fd)", fontSize: 22, fontWeight: 800, color: "#D97706", letterSpacing: "-.04em" }}>{tenacity.toFixed(2)}</div>
                    <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".08em", textTransform: "uppercase", color: "#B45309" }}>Tenacity</div>
                </div>
            </div>
            {actions.map((a, i) => (
                <div key={i} className="preloan-row" style={{ animationDelay: `${.3 + i * .12}s` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 5 }}>
                        <div>
                            <span style={{ fontFamily: "var(--fd)", fontSize: 12, fontWeight: 700, color: "#0F172A" }}>{a.title}</span>
                            {a.certificate_uploaded && <span style={{ marginLeft: 6, fontSize: 10 }}>📄</span>}
                            <div style={{ fontSize: 11, color: "#94A3B8", marginTop: 2 }}>
                                {a.expected_effort_hours}h active · {a.return_visits} visits
                            </div>
                        </div>
                        <div style={{ fontFamily: "var(--fd)", fontSize: 11, fontWeight: 800, letterSpacing: ".06em", textTransform: "uppercase", color: "#059669" }}>
                            {engagement}
                        </div>
                    </div>
                    <div className="eng-bar-track">
                        <div className="eng-bar-fill" style={{ width: `${Math.min(100, (a.total_active_seconds / (Math.max(1, a.expected_effort_hours) * 3600) * 100))}%`, background: `linear-gradient(90deg,#F59E0B, #D97706)`, animationDelay: `${.4 + i * .12}s` }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

// ── SECTION DIVIDER ───────────────────────────────────────────────────────────
function Divider({ num, label }) {
    return (
        <div className="sec-divider">
            <div className="sec-num">{num}</div>
            <div className="sec-divider-label">{label}</div>
            <div className="sec-divider-line" />
        </div>
    );
}

// ── RESULTS PANEL ─────────────────────────────────────────────────────────────
function ResultsPanel({ result, scored }) {
    const [step, setStep] = useState(0);

    useEffect(() => {
        if (!scored) return;
        const delays = [0, 200, 400, 600, 800, 1000, 1200, 1400];
        delays.forEach((d, i) => setTimeout(() => setStep(s => Math.max(s, i + 1)), d));
    }, [scored]);

    if (!scored || !result) {
        return (
            <div className="empty-results">
                <svg width="160" height="140" viewBox="0 0 200 175" opacity="0.15">
                    <path d="M 43 157 A 80 80 0 1 1 157 157" fill="none" stroke="#6366F1" strokeWidth="11" strokeLinecap="round" strokeDasharray="10 6" />
                    <text x="100" y="108" textAnchor="middle" style={{ fontFamily: "var(--fd)", fontSize: 36, fontWeight: 800, fill: "#6366F1", letterSpacing: "-2px" }}>—</text>
                </svg>
                <div style={{ fontFamily: "var(--fd)", fontSize: 14, fontWeight: 700, color: "#CBD5E1" }}>Score an application to see results</div>
                <div style={{ fontSize: 12, color: "#E2E8F0" }}>Fill in Priya's profile on the left and click Score Application</div>
            </div>
        );
    }

    const r = result;
    const score = r.repayment_score;
    const tierCls = { GREEN: "g", AMBER: "a", RED: "r" }[score.tier] || "g";

    return (
        <div>
            {/* ① SCORE HERO */}
            <div className="result-block wcard" style={{ animationDelay: "0ms", marginBottom: 12 }}>
                <div className="score-hero">
                    <ScoreDial score={score.score} tier={score.tier} animate={step >= 1} />
                    <div className="score-meta">
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                            <div className="rel-band">
                                <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10B981" }} />
                                {r.reliability.band} Reliability
                            </div>
                        </div>
                        <div style={{ fontSize: 12, color: "#94A3B8", lineHeight: 1.6, marginBottom: 10, fontStyle: "italic" }}>
                            "{r.explanation.tier_1.substring(0, 100)}…"
                        </div>
                        <div className="behavioral-note" style={{ animationDelay: scored ? "1.9s" : "999s" }}>
                            <Bolt />
                            <span>
                                <strong style={{ color: "#92400E" }}>+{score.behavioral_boost_points} behavioral boost</strong>
                                &nbsp;· base score was {score.base_score_without_behavioral} · tenacity: {Math.round(r.reliability.tenacity_score * 100)}%
                            </span>
                        </div>
                    </div>
                </div>

                {/* Sub-scores */}
                <div style={{ borderTop: "1px solid rgba(0,0,0,0.06)", paddingTop: 18, marginTop: 4 }}>
                    <div className="sec-lbl">Component breakdown</div>
                    {step >= 2 && <SubScores data={score} delay={0} />}
                </div>
            </div>

            {/* ② PLACEMENT TIMING */}
            {step >= 3 && (
                <div className="result-block wcard" style={{ animationDelay: "0ms", marginBottom: 12 }}>
                    <Divider num="2" label="Placement Probability" />
                    <PlacementTimeline data={r.placement_probability} delay={0} />
                    {r.delayed_placement_risk.flag !== "LOW" && (
                        <div className="delayed-flag" style={{ marginTop: 14 }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 4, fontWeight: 700, fontSize: 12 }}>
                                <Warn /> DELAYED PLACEMENT RISK: {r.delayed_placement_risk.flag}
                            </div>
                            {r.delayed_placement_risk.reason}
                        </div>
                    )}
                </div>
            )}

            {/* ③ SALARY */}
            {step >= 4 && (
                <div className="result-block wcard" style={{ animationDelay: "0ms", marginBottom: 12 }}>
                    <Divider num="3" label="Expected Salary Range" />
                    <SalaryRange data={r.salary_forecast} />
                </div>
            )}

            {/* ④ EXPLANATION */}
            {step >= 5 && (
                <div className="result-block wcard" style={{ animationDelay: "0ms", marginBottom: 12 }}>
                    <Divider num="4" label="Risk Assessment" />
                    <ExplanationBlock data={r.explanation} show={step >= 5} />
                </div>
            )}

            {/* ⑤ ACTIONS */}
            {step >= 6 && (
                <div className="result-block wcard" style={{ animationDelay: "0ms", marginBottom: 12 }}>
                    <Divider num="5" label="Recommended Actions" />
                    <ActionCards actions={r.next_best_action} delay={0} />
                </div>
            )}

            {/* ⑥ EMPLOYERS */}
            {step >= 7 && (
                <div className="result-block wcard" style={{ animationDelay: "0ms", marginBottom: 12 }}>
                    <Divider num="6" label="Employer Match List — H1B Filings" />
                    <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 14, fontFamily: "var(--fm)" }}>
                        Companies that historically hired this profile · filtered by program + target sector
                    </div>
                    <EmployerTable employers={r.employer_match_list} delay={0} />
                </div>
            )}
        </div>
    );
}

// ── FORM ──────────────────────────────────────────────────────────────────────
const SECTORS = ["Cloud & Software Engineering", "Data Science & AI", "Finance & FinTech", "Consulting", "Healthcare Tech", "Cybersecurity"];
const COUNTRIES = ["United States", "United Kingdom", "Canada", "Australia", "Germany", "Singapore"];

function ApplicationForm({ onScore, loading }) {
    const [form, setForm] = useState({
        studentName: "Priya Sharma",
        university: "University of Texas Austin",
        program: "MS Computer Science",
        country: "United States",
        loanAmount: "4500000",
        moratorium: "9",
        sector: "Cloud & Software Engineering",
        gpa: "8.4",
        interns: "1",
    });
    const [nc, setNc] = useState({ gre: false, gmat: false }); // not-collected
    const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }));

    const fields1 = [
        { key: "studentName", label: "Student Name", req: true },
        { key: "university", label: "University", req: true },
        { key: "program", label: "Program", req: true },
        { key: "gpa", label: "CGPA / GPA", req: true, type: "number" },
    ];
    const fields2 = [
        { key: "country", label: "Target Country", req: true, type: "select", opts: COUNTRIES },
        { key: "sector", label: "Target Sector", req: true, type: "select", opts: SECTORS },
        { key: "loanAmount", label: "Loan Amount (₹)", req: true, type: "number" },
        { key: "moratorium", label: "Moratorium (months)", req: true, type: "number" },
    ];

    return (
        <form onSubmit={(e) => { e.preventDefault(); onScore(form); }}>
            {/* Section 1 */}
            <div className="sec-lbl" style={{ animation: "slide-r .4s ease both .05s", opacity: 0 }}>Student profile</div>
            <div className="fw-row" style={{ animation: "fade-up .4s ease both .1s", opacity: 0 }}>
                {fields1.map(f => (
                    <div key={f.key} className="fw-col">
                        <label className="fw-lbl">{f.label} {f.req && <span className="fw-req" />}</label>
                        <input className="fw-in" value={form[f.key]} onChange={set(f.key)} type={f.type || "text"} />
                    </div>
                ))}
            </div>

            {/* Section 2 */}
            <div className="sec-lbl" style={{ animation: "slide-r .4s ease both .2s", opacity: 0 }}>Loan parameters</div>
            <div className="fw-row" style={{ animation: "fade-up .4s ease both .25s", opacity: 0 }}>
                {fields2.map(f => (
                    <div key={f.key} className="fw-col">
                        <label className="fw-lbl">{f.label} {f.req && <span className="fw-req" />}</label>
                        {f.type === "select"
                            ? <select className="fw-in" value={form[f.key]} onChange={set(f.key)} style={{ cursor: "pointer" }}>
                                {f.opts.map(o => <option key={o}>{o}</option>)}
                            </select>
                            : <input className="fw-in" value={form[f.key]} onChange={set(f.key)} type="number" />
                        }
                    </div>
                ))}
            </div>

            {/* Optional fields */}
            <div className="sec-lbl" style={{ animation: "slide-r .4s ease both .35s", opacity: 0 }}>Optional signals</div>
            <div className="fw-row" style={{ animation: "fade-up .4s ease both .4s", opacity: 0 }}>
                <div className="fw-col">
                    <label className="fw-lbl">
                        GRE Score
                        <span className="nc-toggle on" style={{ marginLeft: "auto" }} onClick={() => setNc(p => ({ ...p, gre: !p.gre }))}>
                            {nc.gre ? "Not collected" : "Enter value"}
                        </span>
                    </label>
                    <input className="fw-in" placeholder={nc.gre ? "—" : "e.g. 318"} disabled={nc.gre} style={{ opacity: nc.gre ? 0.45 : 1 }} />
                </div>
                <div className="fw-col">
                    <label className="fw-lbl">Internships completed</label>
                    <input className="fw-in" type="number" value={form.interns} onChange={set("interns")} />
                </div>
            </div>

            {/* Submit */}
            <div style={{ animation: "fade-up .4s ease both .5s", opacity: 0 }}>
                <button type="submit" className="submit-btn" disabled={loading}>
                    {!loading && <div className="btn-shimmer" />}
                    {loading
                        ? <><Spin /> Analyzing profile…</>
                        : <>Score Application <Arr /></>
                    }
                </button>
                <div style={{ marginTop: 10, textAlign: "center" }}>
                    <span style={{ fontSize: 11, color: "#CBD5E1", fontFamily: "var(--fm)", letterSpacing: ".04em" }}>
                        Form pre-filled with Priya Sharma · demo profile
                    </span>
                </div>
            </div>
        </form>
    );
}

// ── UNDERWRITER CONSOLE ───────────────────────────────────────────────────────
export default function UnderwriterConsole() {
    const [loading, setLoading] = useState(false);
    const [studentDashboard, setStudentDashboard] = useState(null);
    const [scored, setScored] = useState(false);
    const [result, setResult] = useState(null);
    const rightRef = useRef(null);

    useEffect(() => {
        fetch("http://localhost:8000/api/v1/student/dashboard/student-priya")
            .then(res => res.json())
            .then(data => setStudentDashboard(data))
            .catch(err => console.error("Failed to fetch student dashboard:", err));
    }, []);

    const handleScore = async (form) => {
        setLoading(true);
        setScored(false);
        setResult(null);

        try {
            const payload = {
                student_id: form.studentName === "Priya Sharma" ? "student-priya" : null,
                full_name: form.studentName,
                university_name: form.university,
                program_name: form.program,
                destination_country: form.country,
                target_sector: form.sector,
                cgpa: parseFloat(form.gpa) || 8.0,
                cgpa_present: true,
                internship_count: parseInt(form.interns) || 0,
                internship_count_present: true,
                loan_amount_inr: parseFloat(form.loanAmount) || 4500000,
                interest_rate_annual_pct: 10.5,
                repayment_term_months: 120,
                moratorium_months: parseInt(form.moratorium) || 9
            };

            const res = await fetch("http://localhost:8000/api/v1/score/origination", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Scoring failed");
            }
            
            const data = await res.json();
            
            // Artificial delay for premium "calculating" feel
            setTimeout(() => {
                setLoading(false);
                setScored(true);
                setResult(data);
                if (rightRef.current) rightRef.current.scrollTop = 0;
            }, 1200);

        } catch (err) {
            setLoading(false);
            alert("Scoring Error: " + err.message);
        }
    };

    return (
        <>
            <StyleInjector2 />
            <div className="uw-page">
                <div className={`uw-wrap ${scored ? "scored" : ""}`}>

                    {/* LEFT: Form */}
                    <div className="uw-left">
                        <div className="uw-left-inner">
                            {/* Page header */}
                            <div style={{ marginBottom: 22, animation: "slide-r .4s ease both", opacity: 0 }}>
                                <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".16em", textTransform: "uppercase", color: "#94A3B8", marginBottom: 5 }}>
                                    Underwriter Console
                                </div>
                                <div style={{ fontFamily: "var(--fd)", fontSize: 22, fontWeight: 800, letterSpacing: "-.04em", color: "#0F172A" }}>
                                    New Application
                                </div>
                            </div>

                            {/* Pre-loan panel */}
                             <PreLoanPanel data={studentDashboard} />

                            {/* Form */}
                            <ApplicationForm onScore={handleScore} loading={loading} />
                        </div>
                    </div>

                    {/* RIGHT: Results */}
                    <div className="uw-right" ref={rightRef}>
                        <div className="uw-right-inner">
                            <ResultsPanel result={result} scored={scored} />
                        </div>
                    </div>

                </div>
            </div>
        </>
    );
}