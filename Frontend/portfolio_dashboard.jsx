import { useState, useEffect, useRef } from "react";

/* ─────────────────────────────────────────────────────────────────────────────
   NEXTSTEP · PORTFOLIO DASHBOARD
   Light theme — cohort monitor, alert drawer, live rescore theatrical moment
   ───────────────────────────────────────────────────────────────────────────── */

const PF_CSS = `
/* ── Page shell ─────────────────────────────── */
.pf-page { background:#ECEEF6; min-height:calc(100vh - 56px); }
.pf-inner { max-width:1240px; margin:0 auto; padding:32px 36px 80px; }

/* ── Header row ─────────────────────────────── */
.pf-hdr {
  display:flex; align-items:flex-end; justify-content:space-between;
  margin-bottom:28px;
  animation:slide-r .4s ease both; opacity:0;
}
.pf-hdr-left {}
.pf-eyebrow {
  font-family:var(--fd); font-size:9px; font-weight:800;
  letter-spacing:.16em; text-transform:uppercase; color:#94A3B8;
  margin-bottom:5px;
}
.pf-title {
  font-family:var(--fd); font-size:26px; font-weight:800;
  letter-spacing:-.04em; color:#0F172A;
}
.pf-subtitle {
  font-size:13px; color:#64748B; margin-top:4px; font-family:var(--fb);
}

/* ── Rescore button ─────────────────────────── */
.rescore-btn {
  display:flex; align-items:center; gap:8px;
  padding:11px 20px; border-radius:11px; border:none; cursor:pointer;
  font-family:var(--fd); font-size:13px; font-weight:800; letter-spacing:-.01em;
  color:#6366F1;
  background:rgba(99,102,241,0.08);
  border:1px solid rgba(99,102,241,0.25);
  transition:all .18s cubic-bezier(.22,1,.36,1);
  position:relative; overflow:hidden;
}
.rescore-btn:hover:not(:disabled) {
  background:rgba(99,102,241,0.14);
  border-color:rgba(99,102,241,0.45);
  transform:translateY(-1px);
  box-shadow:0 4px 16px rgba(99,102,241,0.18);
}
.rescore-btn:disabled { opacity:.6; cursor:default; }
.rescore-pulse {
  position:absolute; inset:0; border-radius:11px;
  background:rgba(99,102,241,0.12);
  animation:rescore-ring 1.4s ease-in-out infinite;
}
@keyframes rescore-ring {
  0%,100% { opacity:0; transform:scale(1); }
  50%      { opacity:1; transform:scale(1.03); }
}

/* ── KPI cards ──────────────────────────────── */
.kpi-grid {
  display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
  margin-bottom:24px;
}
.kpi-card {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:16px;
  padding:20px 22px;
  box-shadow:0 1px 4px rgba(0,0,0,0.05);
  animation:fade-up .4s ease both; opacity:0;
  position:relative; overflow:hidden;
}
.kpi-card::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:3px; border-radius:2px 0 0 2px;
  background:var(--kpi-accent,#E2E8F0);
}
.kpi-val {
  font-family:var(--fd); font-size:38px; font-weight:800;
  letter-spacing:-.05em; line-height:1; margin-bottom:5px;
  animation:count-in .5s ease both; opacity:0;
}
.kpi-label {
  font-family:var(--fd); font-size:10px; font-weight:700;
  letter-spacing:.08em; text-transform:uppercase; color:#94A3B8;
}
.kpi-delta {
  margin-top:8px; font-family:var(--fd); font-size:11px; font-weight:600;
  color:#94A3B8;
}

/* ── Filter bar ─────────────────────────────── */
.filter-bar {
  display:flex; align-items:center; gap:8px; margin-bottom:18px;
  animation:fade-up .4s ease both .2s; opacity:0;
  flex-wrap:wrap;
}
.filter-pill {
  padding:6px 14px; border-radius:99px; border:1px solid rgba(0,0,0,0.1);
  font-family:var(--fd); font-size:11px; font-weight:700; cursor:pointer;
  background:#fff; color:#64748B;
  transition:all .15s; user-select:none;
}
.filter-pill:hover { border-color:#6366F1; color:#6366F1; background:rgba(99,102,241,0.04); }
.filter-pill.on { background:#6366F1; color:#fff; border-color:#6366F1; box-shadow:0 2px 8px rgba(99,102,241,0.3); }
.filter-sep { width:1px; height:22px; background:rgba(0,0,0,0.1); margin:0 4px; }
.filter-select {
  padding:6px 12px; border-radius:8px; border:1px solid rgba(0,0,0,0.1);
  font-family:var(--fd); font-size:11px; font-weight:700;
  background:#fff; color:#64748B; cursor:pointer; outline:none;
  transition:border-color .15s;
  appearance:none;
}
.filter-select:focus { border-color:#6366F1; }

/* ── Table card ─────────────────────────────── */
.tbl-card {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:18px;
  box-shadow:0 1px 6px rgba(0,0,0,0.05);
  overflow:hidden;
  animation:fade-up .4s ease both .28s; opacity:0;
}
.tbl-head {
  display:grid;
  grid-template-columns: 28px 200px 1fr 64px 72px 72px 72px 100px 110px;
  padding:11px 18px;
  border-bottom:2px solid rgba(0,0,0,0.06);
  gap:0;
}
.tbl-th {
  font-family:var(--fd); font-size:9px; font-weight:800;
  letter-spacing:.1em; text-transform:uppercase; color:#94A3B8;
  display:flex; align-items:center;
}
.tbl-row {
  display:grid;
  grid-template-columns: 28px 200px 1fr 64px 72px 72px 72px 100px 110px;
  padding:13px 18px;
  border-bottom:1px solid rgba(0,0,0,0.05);
  border-left:3px solid transparent;
  cursor:pointer; gap:0;
  transition:background .12s, border-left-color .12s;
  animation:row-in .38s ease both; opacity:0;
}
.tbl-row:last-child { border-bottom:none; }
.tbl-row:hover { background:rgba(99,102,241,0.025); }
.tbl-row.row-amber { border-left-color:#F59E0B; }
.tbl-row.row-red   { border-left-color:#EF4444; background:rgba(239,68,68,0.015); }
.tbl-row.row-new   { animation:row-flash .9s ease both; }

.tbl-td {
  display:flex; align-items:center;
  font-size:13px; color:#1E293B;
}
.td-mono { font-family:var(--fm); font-size:11px; color:#64748B; font-weight:500; }
.td-name { font-weight:600; color:#0F172A; }
.td-num  { font-family:var(--fd); font-weight:800; font-size:15px; letter-spacing:-.02em; }
.td-delta { font-family:var(--fd); font-weight:800; font-size:14px; letter-spacing:-.02em; }

@keyframes row-flash {
  0%   { background:rgba(245,158,11,0.22); opacity:0; transform:translateY(-6px); }
  15%  { opacity:1; transform:translateY(0); background:rgba(245,158,11,0.18); }
  100% { background:transparent; }
}

@keyframes row-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Severity badge ─────────────────────────── */
.sev-badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:99px;
  font-family:var(--fd); font-size:10px; font-weight:800;
  letter-spacing:.07em; text-transform:uppercase;
}
.sev-badge.g { background:rgba(16,185,129,0.1); color:#059669; border:1px solid rgba(16,185,129,0.25); }
.sev-badge.a { background:rgba(245,158,11,0.1); color:#D97706; border:1px solid rgba(245,158,11,0.25); }
.sev-badge.r { background:rgba(239,68,68,0.1);  color:#DC2626; border:1px solid rgba(239,68,68,0.25); }
.sev-dot { width:6px; height:6px; border-radius:50%; background:currentColor; }

/* ── Alert drawer ───────────────────────────── */
.drawer-overlay {
  position:fixed; inset:0; z-index:200;
  background:rgba(0,0,0,0.18);
  backdrop-filter:blur(4px);
  animation:fade-in .2s ease;
}
.drawer {
  position:fixed; top:0; right:0; bottom:0; z-index:201;
  width:420px;
  background:#fff;
  border-left:1px solid rgba(0,0,0,0.08);
  box-shadow:-8px 0 40px rgba(0,0,0,0.12);
  display:flex; flex-direction:column;
  animation:drawer-in .3s cubic-bezier(.22,1,.36,1);
  overflow:hidden;
}
@keyframes drawer-in {
  from { transform:translateX(100%); opacity:0.6; }
  to   { transform:translateX(0);    opacity:1; }
}
.drawer-close {
  position:absolute; top:16px; right:16px;
  width:30px; height:30px; border-radius:50%;
  background:rgba(0,0,0,0.06); border:none; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  color:#64748B; transition:background .15s, color .15s;
}
.drawer-close:hover { background:rgba(0,0,0,0.1); color:#0F172A; }
.drawer-header {
  padding:28px 24px 20px;
  border-bottom:1px solid rgba(0,0,0,0.07);
  flex-shrink:0;
}
.drawer-body { flex:1; overflow-y:auto; padding:22px 24px; }
.drawer-row {
  display:flex; justify-content:space-between; align-items:flex-start;
  padding:14px 0; border-bottom:1px solid rgba(0,0,0,0.06);
}
.drawer-row:last-child { border-bottom:none; }
.drawer-row-lbl {
  font-family:var(--fd); font-size:10px; font-weight:700;
  letter-spacing:.08em; text-transform:uppercase; color:#94A3B8; margin-bottom:4px;
}
.drawer-row-val { font-family:var(--fd); font-size:15px; font-weight:800; color:#0F172A; letter-spacing:-.02em; }
.drawer-score-change {
  display:flex; align-items:center; gap:10px;
}
.dsc-from { font-family:var(--fd); font-size:32px; font-weight:800; color:#94A3B8; letter-spacing:-.05em; }
.dsc-arrow { color:#EF4444; font-size:18px; }
.dsc-to { font-family:var(--fd); font-size:32px; font-weight:800; letter-spacing:-.05em; }
.driver-box {
  padding:13px 15px; border-radius:12px;
  background:rgba(239,68,68,0.04); border:1px solid rgba(239,68,68,0.15);
  border-left:3px solid #EF4444;
  font-size:13px; color:#7F1D1D; line-height:1.6;
  margin-top:6px;
}
.driver-box.amber {
  background:rgba(245,158,11,0.04); border-color:rgba(245,158,11,0.2);
  border-left-color:#F59E0B; color:#78350F;
}
.macro-strip {
  display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:14px;
}
.macro-item {
  padding:11px 13px; border-radius:11px;
  background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.07);
}
.macro-item-lbl { font-family:var(--fd); font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#94A3B8; margin-bottom:5px; }
.macro-item-val { font-family:var(--fd); font-size:16px; font-weight:800; letter-spacing:-.03em; }
.drawer-action-btn {
  width:100%; padding:13px; border-radius:12px; border:none; cursor:pointer;
  font-family:var(--fd); font-size:14px; font-weight:800; letter-spacing:-.01em;
  background:linear-gradient(135deg,#6366F1,#4f46e5);
  color:#fff;
  box-shadow:0 3px 14px rgba(99,102,241,0.3);
  transition:transform .15s, box-shadow .15s;
  display:flex; align-items:center; justify-content:center; gap:8px;
}
.drawer-action-btn:hover { transform:translateY(-1px); box-shadow:0 5px 20px rgba(99,102,241,0.38); }
.drawer-footer { padding:18px 24px; border-top:1px solid rgba(0,0,0,0.07); flex-shrink:0; }

/* ── Macro bar ──────────────────────────────── */
.macro-bar-track { height:5px; border-radius:99px; background:rgba(0,0,0,0.07); margin-top:6px; overflow:hidden; }
.macro-bar-fill  { height:100%; border-radius:99px; animation:fill-bar .8s cubic-bezier(.22,1,.36,1) both; }

/* ── Empty table state ─────────────────────── */
.tbl-empty {
  padding:48px; text-align:center;
  font-family:var(--fd); font-size:14px; color:#CBD5E1; font-weight:600;
}

/* ── Timestamp ─────────────────────────────── */
.ts-chip {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 9px; border-radius:6px;
  background:rgba(0,0,0,0.04); border:1px solid rgba(0,0,0,0.08);
  font-family:var(--fm); font-size:10px; color:#94A3B8;
}

/* ── Progress ring (mini) ──────────────────── */
.mini-ring-wrap { display:flex; align-items:center; gap:8px; }

/* ── Table chevron ─────────────────────────── */
.row-chevron { color:#CBD5E1; opacity:0; transition:opacity .15s, transform .15s; }
.tbl-row:hover .row-chevron { opacity:1; transform:translateX(2px); }
`;

function StyleInjectorPF() {
    useEffect(() => {
        const id = "ns-pf";
        if (!document.getElementById(id)) {
            const el = document.createElement("style");
            el.id = id; el.textContent = PF_CSS;
            document.head.appendChild(el);
        }
        return () => document.getElementById(id)?.remove();
    }, []);
    return null;
}

// ── DATA ──────────────────────────────────────────────────────────────────────
const INITIAL_COHORTS = [
    {
        id: "US_MSCS_2024_Q1", program: "MS Computer Science", country: "US", flag: "🇺🇸",
        size: 43, baseline: 74, current: 70, severity: "AMBER",
        triggered: "Apr 12, 2026",
        driver: "US tech sector hiring index down 18% since origination. H1B approval rates declined sharply in Q1 2026.",
        secondary: "Federal Reserve rate policy has dampened hiring at mid-sized tech firms. Approval rate fell from 87% to 71%.",
        macro: [
            { label: "Hiring Index", val: "–18%", num: 0.32, color: "#EF4444" },
            { label: "H1B Approvals", val: "71%", num: 0.71, color: "#F59E0B" },
            { label: "Job Postings", val: "–9%", num: 0.41, color: "#EF4444" },
            { label: "Sector Demand", val: "MODERATE", num: 0.55, color: "#F59E0B" },
        ],
        recommended: "Review for proactive borrower outreach and consider restructuring timeline.",
    },
    {
        id: "UK_MBA_2024_Q2", program: "MBA Finance", country: "UK", flag: "🇬🇧",
        size: 28, baseline: 68, current: 68, severity: "GREEN",
        triggered: null,
        driver: null,
        secondary: null,
        macro: [
            { label: "Hiring Index", val: "+4%", num: 0.74, color: "#10B981" },
            { label: "Placement Rate", val: "79%", num: 0.79, color: "#10B981" },
            { label: "Job Postings", val: "+2%", num: 0.66, color: "#10B981" },
            { label: "Sector Demand", val: "HIGH", num: 0.80, color: "#10B981" },
        ],
        recommended: "No action required. Monitor quarterly.",
    },
    {
        id: "CA_ENG_2024_Q1", program: "MS Engineering", country: "CA", flag: "🇨🇦",
        size: 31, baseline: 71, current: 63, severity: "RED",
        triggered: "Apr 10, 2026",
        driver: "Canada tech layoffs accelerated across Q1 2026. Work permit processing delays now reaching 8+ months.",
        secondary: "Bank of Canada rate increases reduced startup hiring by 34%. Provincial nominee programs paused until Q3.",
        macro: [
            { label: "Hiring Index", val: "–24%", num: 0.18, color: "#EF4444" },
            { label: "Permit Delays", val: "8mo", num: 0.2, color: "#EF4444" },
            { label: "Layoff Rate", val: "+34%", num: 0.82, color: "#EF4444" },
            { label: "Sector Demand", val: "LOW", num: 0.22, color: "#EF4444" },
        ],
        recommended: "Escalate to senior review. Consider early contact with affected borrowers.",
    },
    {
        id: "SG_DATA_2024_Q3", program: "MS Data Science", country: "SG", flag: "🇸🇬",
        size: 19, baseline: 77, current: 77, severity: "GREEN",
        triggered: null, driver: null, secondary: null,
        macro: [
            { label: "Hiring Index", val: "+11%", num: 0.88, color: "#10B981" },
            { label: "Placement Rate", val: "84%", num: 0.84, color: "#10B981" },
            { label: "Job Postings", val: "+7%", num: 0.77, color: "#10B981" },
            { label: "Sector Demand", val: "HIGH", num: 0.90, color: "#10B981" },
        ],
        recommended: "No action required.",
    },
];

const NEW_ALERT_COHORT = {
    id: "DE_SWE_2024_Q2", program: "MS Software Engineering", country: "DE", flag: "🇩🇪",
    size: 24, baseline: 72, current: 68, severity: "AMBER",
    triggered: "Just now",
    driver: "German tech sector contraction following Q1 GDP miss. BMW, SAP and Deutsche Telekom hiring freezes announced.",
    secondary: "EUR/USD exchange rate movement adds repayment pressure for borrowers with INR-denominated loans.",
    macro: [
        { label: "Hiring Index", val: "–11%", num: 0.39, color: "#EF4444" },
        { label: "GDP Growth", val: "–0.2%", num: 0.3, color: "#F59E0B" },
        { label: "Job Postings", val: "–6%", num: 0.44, color: "#F59E0B" },
        { label: "Sector Demand", val: "MODERATE", num: 0.51, color: "#F59E0B" },
    ],
    recommended: "Monitor closely. Send proactive status email to affected cohort.",
};

// ── ICONS ─────────────────────────────────────────────────────────────────────
const XIcon = () => <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="2" y1="2" x2="10" y2="10" /><line x1="10" y1="2" x2="2" y2="10" /></svg>;
const ChevR = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="9 18 15 12 9 6" /></svg>;
const SpinI = () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ animation: "spin .7s linear infinite" }}><path d="M21 12a9 9 0 11-3.5-7" /></svg>;
const RefreshI = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" /></svg>;
const AlertI = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><circle cx="12" cy="17" r=".5" fill="currentColor" /></svg>;
const EyeI = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>;

// ── HOOK: count-up ────────────────────────────────────────────────────────────
function useCountUp(target, duration = 800, startOn = true) {
    const [v, setV] = useState(0);
    useEffect(() => {
        if (!startOn) return;
        const t0 = performance.now();
        const tick = (now) => {
            const p = Math.min((now - t0) / duration, 1);
            const e = 1 - Math.pow(1 - p, 3);
            setV(Math.round(e * target));
            if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }, [startOn, target]);
    return v;
}

// ── KPI CARD ──────────────────────────────────────────────────────────────────
function KpiCard({ val, label, color, accent, delta, delay, animStart }) {
    const n = useCountUp(val, 700, animStart);
    return (
        <div className="kpi-card" style={{ "--kpi-accent": accent, animationDelay: `${delay}ms` }}>
            <div className="kpi-val" style={{ color, animationDelay: `${delay + 120}ms` }}>{n}</div>
            <div className="kpi-label">{label}</div>
            {delta && <div className="kpi-delta">{delta}</div>}
        </div>
    );
}

// ── SEVERITY helpers ──────────────────────────────────────────────────────────
const SEV_CLS = { GREEN: "g", AMBER: "a", RED: "r" };
const SEV_ROW = { GREEN: "", AMBER: "row-amber", RED: "row-red" };
const DELTA_CLR = (d) => d < -3 ? "#EF4444" : d < 0 ? "#F59E0B" : d > 0 ? "#10B981" : "#94A3B8";

// ── ALERT DRAWER ──────────────────────────────────────────────────────────────
function AlertDrawer({ cohort, onClose }) {
    const delta = cohort.current - cohort.baseline;
    const isRed = cohort.severity === "RED";
    const accentColor = isRed ? "#EF4444" : "#F59E0B";

    // Prevent body scroll when drawer open
    useEffect(() => {
        document.body.style.overflow = "hidden";
        return () => { document.body.style.overflow = ""; };
    }, []);

    return (
        <>
            <div className="drawer-overlay" onClick={onClose} />
            <div className="drawer">
                {/* Header */}
                <div className="drawer-header" style={{ borderTop: `3px solid ${accentColor}` }}>
                    <button className="drawer-close" onClick={onClose}><XIcon /></button>

                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                        <span style={{ fontSize: 20 }}>{cohort.flag}</span>
                        <div>
                            <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".12em", textTransform: "uppercase", color: "#94A3B8", marginBottom: 2 }}>
                                Cohort Alert
                            </div>
                            <div style={{ fontFamily: "var(--fd)", fontSize: 17, fontWeight: 800, letterSpacing: "-.03em", color: "#0F172A" }}>
                                {cohort.id}
                            </div>
                        </div>
                        <div style={{ marginLeft: "auto" }}>
                            <span className={`sev-badge ${SEV_CLS[cohort.severity]}`}>
                                <span className="sev-dot" />
                                {cohort.severity}
                            </span>
                        </div>
                    </div>

                    {/* Score change */}
                    <div style={{ background: "rgba(0,0,0,0.03)", border: "1px solid rgba(0,0,0,0.07)", borderRadius: 13, padding: "14px 16px" }}>
                        <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".1em", textTransform: "uppercase", color: "#94A3B8", marginBottom: 8 }}>Score change since origination</div>
                        <div className="drawer-score-change">
                            <div className="dsc-from">{cohort.baseline}</div>
                            <div className="dsc-arrow">→</div>
                            <div className="dsc-to" style={{ color: accentColor }}>{cohort.current}</div>
                            <div style={{ marginLeft: "auto", fontFamily: "var(--fd)", fontSize: 22, fontWeight: 800, color: accentColor }}>
                                {delta > 0 ? "+" : ""}{delta}
                            </div>
                        </div>
                        <div style={{ marginTop: 6, fontSize: 11, color: "#94A3B8" }}>
                            Max observable delta from macro re-score: ±6 pts (20% weight × 30% cap)
                        </div>
                    </div>
                </div>

                {/* Body */}
                <div className="drawer-body">

                    {/* Program + Size */}
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 16 }}>
                        {[
                            { label: "Program", val: cohort.program },
                            { label: "Country", val: cohort.country },
                            { label: "Borrowers", val: `${cohort.size}` },
                        ].map((r, i) => (
                            <div key={i} style={{ padding: "11px 13px", background: "rgba(0,0,0,0.03)", borderRadius: 11, border: "1px solid rgba(0,0,0,0.07)" }}>
                                <div className="drawer-row-lbl">{r.label}</div>
                                <div className="drawer-row-val" style={{ fontSize: 13 }}>{r.val}</div>
                            </div>
                        ))}
                    </div>

                    {/* Primary driver */}
                    {cohort.driver && (
                        <>
                            <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".1em", textTransform: "uppercase", color: "#94A3B8", marginBottom: 8 }}>
                                Primary macro driver
                            </div>
                            <div className={`driver-box ${cohort.severity === "AMBER" ? "amber" : ""}`}>
                                {cohort.driver}
                            </div>
                        </>
                    )}

                    {/* Secondary */}
                    {cohort.secondary && (
                        <div style={{ marginTop: 10, padding: "11px 14px", borderRadius: 11, background: "rgba(0,0,0,0.025)", border: "1px solid rgba(0,0,0,0.07)", fontSize: 12, color: "#475569", lineHeight: 1.6 }}>
                            {cohort.secondary}
                        </div>
                    )}

                    {/* Macro signals */}
                    <div style={{ marginTop: 18 }}>
                        <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".1em", textTransform: "uppercase", color: "#94A3B8", marginBottom: 10 }}>
                            Macro signal snapshot · Apr 30 2026
                        </div>
                        <div className="macro-strip">
                            {cohort.macro.map((m, i) => (
                                <div key={i} className="macro-item">
                                    <div className="macro-item-lbl">{m.label}</div>
                                    <div className="macro-item-val" style={{ color: m.color }}>{m.val}</div>
                                    <div className="macro-bar-track">
                                        <div className="macro-bar-fill" style={{ width: `${m.num * 100}%`, background: m.color, animationDelay: `${i * 80}ms` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Recommended action */}
                    <div style={{ marginTop: 18, padding: "13px 15px", borderRadius: 12, background: "rgba(99,102,241,0.05)", border: "1px solid rgba(99,102,241,0.15)" }}>
                        <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".1em", textTransform: "uppercase", color: "#6366F1", marginBottom: 6 }}>
                            Recommended action · rule-based
                        </div>
                        <div style={{ fontSize: 13, color: "#1E293B", lineHeight: 1.6 }}>{cohort.recommended}</div>
                    </div>

                    {/* Timestamp */}
                    <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 8 }}>
                        <div className="ts-chip">Macro snapshot: Apr 30, 2026 · 02:00 UTC</div>
                        {cohort.triggered && <div className="ts-chip">Triggered: {cohort.triggered}</div>}
                    </div>
                </div>

                {/* Footer actions */}
                <div className="drawer-footer">
                    <button className="drawer-action-btn">
                        <EyeI /> View Affected Applications
                    </button>
                    <button onClick={onClose} style={{
                        display: "block", width: "100%", marginTop: 8, padding: "11px",
                        borderRadius: 11, border: "1px solid rgba(0,0,0,0.1)",
                        background: "transparent", fontFamily: "var(--fd)", fontSize: 13, fontWeight: 700,
                        color: "#64748B", cursor: "pointer", transition: "background .15s",
                    }}
                        onMouseEnter={e => e.currentTarget.style.background = "rgba(0,0,0,0.04)"}
                        onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                        Mark Resolved
                    </button>
                </div>
            </div>
        </>
    );
}

// ── TABLE ROW ─────────────────────────────────────────────────────────────────
function TableRow({ cohort, onClick, delay, isNew }) {
    const delta = cohort.current - cohort.baseline;
    return (
        <div className={`tbl-row ${SEV_ROW[cohort.severity]} ${isNew ? "row-new" : ""}`}
            style={{ animationDelay: `${delay}ms` }}
            onClick={() => onClick(cohort)}>

            <div className="tbl-td">
                <span style={{ fontSize: 14 }}>{cohort.flag}</span>
            </div>
            <div className="tbl-td td-mono">{cohort.id}</div>
            <div className="tbl-td td-name" style={{ paddingRight: 12, fontSize: 13 }}>{cohort.program}</div>
            <div className="tbl-td" style={{ fontSize: 13, color: "#475569" }}>{cohort.size}</div>
            <div className="tbl-td td-num" style={{ color: "#0F172A" }}>{cohort.baseline}</div>
            <div className="tbl-td td-num" style={{ color: "#0F172A" }}>{cohort.current}</div>
            <div className="tbl-td td-delta" style={{ color: DELTA_CLR(delta) }}>
                {delta > 0 ? "+" : ""}{delta}
            </div>
            <div className="tbl-td">
                <span className={`sev-badge ${SEV_CLS[cohort.severity]}`}>
                    <span className="sev-dot" />
                    {cohort.severity}
                </span>
            </div>
            <div className="tbl-td" style={{ justifyContent: "flex-end" }}>
                <span className="row-chevron"><ChevR /></span>
            </div>
        </div>
    );
}

// ── MAIN COMPONENT ────────────────────────────────────────────────────────────
export default function PortfolioDashboard() {
    const [cohorts, setCohorts] = useState(INITIAL_COHORTS);
    const [filter, setFilter] = useState("ALL");
    const [selected, setSelected] = useState(null);
    const [rescoring, setRescoring] = useState(false);
    const [newRowId, setNewRowId] = useState(null);
    const [kpiAnim, setKpiAnim] = useState(false);
    const [toast, setToast] = useState(null);

    useEffect(() => { setTimeout(() => setKpiAnim(true), 100); }, []);

    // Derived KPIs
    const amber = cohorts.filter(c => c.severity === "AMBER").length;
    const red = cohorts.filter(c => c.severity === "RED").length;

    // Filter
    const visible = cohorts.filter(c =>
        filter === "ALL" ? true :
            filter === "AMBER" ? c.severity === "AMBER" :
                filter === "RED" ? c.severity === "RED" :
                    filter === "GREEN" ? c.severity === "GREEN" : true
    );

    const triggerRescore = () => {
        if (rescoring) return;
        setRescoring(true);
        setTimeout(() => {
            const exists = cohorts.find(c => c.id === NEW_ALERT_COHORT.id);
            if (!exists) {
                setCohorts(prev => [NEW_ALERT_COHORT, ...prev]);
                setNewRowId(NEW_ALERT_COHORT.id);
                setTimeout(() => setNewRowId(null), 1200);
            } else {
                // cycle an existing green cohort to amber for demo
                setCohorts(prev => prev.map(c =>
                    c.id === "SG_DATA_2024_Q3" ? { ...c, current: 73, severity: "AMBER", triggered: "Just now" } : c
                ));
            }
            setRescoring(false);
            setToast({ msg: "Re-score complete · 1 new alert detected", type: "amber" });
            setTimeout(() => setToast(null), 4000);
        }, 1800);
    };

    return (
        <>
            <StyleInjectorPF />
            <div className="pf-page">
                <div className="pf-inner">

                    {/* ── HEADER ──────────────────────────────── */}
                    <div className="pf-hdr">
                        <div>
                            <div className="pf-eyebrow">Portfolio Dashboard</div>
                            <div className="pf-title">Cohort Risk Monitor</div>
                            <div className="pf-subtitle">
                                {cohorts.length} active cohorts · Macro snapshot: Apr 30, 2026 · 02:00 UTC
                            </div>
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                            <button className="rescore-btn" onClick={triggerRescore} disabled={rescoring}>
                                {rescoring && <div className="rescore-pulse" />}
                                {rescoring ? <SpinI /> : <RefreshI />}
                                {rescoring ? "Re-scoring cohorts…" : "Trigger Re-score"}
                            </button>
                            <div style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#94A3B8", letterSpacing: ".06em" }}>
                                Using FRED + World Bank signals · Weekly cadence
                            </div>
                        </div>
                    </div>

                    {/* ── KPI CARDS ────────────────────────────── */}
                    <div className="kpi-grid">
                        <KpiCard val={cohorts.length} label="Active Cohorts" color="#0F172A" accent="#E2E8F0" delta={`↑ 3 added this month`} delay={0} animStart={kpiAnim} />
                        <KpiCard val={amber} label="At Risk — AMBER" color="#D97706" accent="#F59E0B" delta={`↑ ${amber > 1 ? "2" : "1"} this week`} delay={70} animStart={kpiAnim} />
                        <KpiCard val={red} label="Critical — RED" color="#DC2626" accent="#EF4444" delta="— unchanged" delay={140} animStart={kpiAnim} />
                        <KpiCard val={Math.round(cohorts.reduce((s, c) => s + c.size, 0))} label="Total Borrowers" color="#6366F1" accent="#6366F1" delta="Across all cohorts" delay={210} animStart={kpiAnim} />
                    </div>

                    {/* ── FILTER BAR ───────────────────────────── */}
                    <div className="filter-bar">
                        {["ALL", "RED", "AMBER", "GREEN"].map(f => (
                            <div key={f} className={`filter-pill ${filter === f ? "on" : ""}`} onClick={() => setFilter(f)}>
                                {f === "ALL" ? "All Cohorts" :
                                    f === "RED" ? `🔴 RED (${red})` :
                                        f === "AMBER" ? `⚠ AMBER (${amber})` :
                                            `✓ GREEN (${cohorts.filter(c => c.severity === "GREEN").length})`}
                            </div>
                        ))}
                        <div className="filter-sep" />
                        <select className="filter-select">
                            <option>All Countries</option>
                            <option>US</option>
                            <option>UK</option>
                            <option>Canada</option>
                            <option>Singapore</option>
                            <option>Germany</option>
                        </select>
                        <select className="filter-select">
                            <option>All Programs</option>
                            <option>MS Computer Science</option>
                            <option>MBA</option>
                            <option>MS Engineering</option>
                            <option>MS Data Science</option>
                        </select>
                        <div style={{ marginLeft: "auto", fontFamily: "var(--fm)", fontSize: 10, color: "#94A3B8" }}>
                            {visible.length} cohort{visible.length !== 1 ? "s" : ""} shown
                        </div>
                    </div>

                    {/* ── TABLE ────────────────────────────────── */}
                    <div className="tbl-card">
                        {/* Head */}
                        <div className="tbl-head">
                            <div className="tbl-th"></div>
                            <div className="tbl-th">Cohort ID</div>
                            <div className="tbl-th">Program</div>
                            <div className="tbl-th">Size</div>
                            <div className="tbl-th">Baseline</div>
                            <div className="tbl-th">Current</div>
                            <div className="tbl-th">Δ Delta</div>
                            <div className="tbl-th">Severity</div>
                            <div className="tbl-th"></div>
                        </div>

                        {/* Rows */}
                        {visible.length === 0 && (
                            <div className="tbl-empty">No cohorts match this filter</div>
                        )}
                        {visible.map((c, i) => (
                            <TableRow
                                key={c.id}
                                cohort={c}
                                onClick={setSelected}
                                delay={i * 60}
                                isNew={c.id === newRowId}
                            />
                        ))}
                    </div>

                    {/* ── TABLE FOOTER ──────────────────────────── */}
                    <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 16, padding: "0 4px" }}>
                        <div style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#94A3B8" }}>
                            Alert thresholds: AMBER ≥ –4 pts · RED ≥ –8 pts · Based on 20% market_risk weight × 30% macro cap
                        </div>
                        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
                            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10B981", animation: "pulse-dot 2.2s ease infinite" }} />
                            <span style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#10B981", letterSpacing: ".07em", textTransform: "uppercase", fontWeight: 500 }}>
                                Live · Last sync Apr 30 2026 · 02:14 UTC
                            </span>
                        </div>
                    </div>

                </div>
            </div>

            {/* ── DRAWER ───────────────────────────────────── */}
            {selected && (
                <AlertDrawer cohort={selected} onClose={() => setSelected(null)} />
            )}

            {/* ── TOAST ────────────────────────────────────── */}
            {toast && (
                <div style={{
                    position: "fixed", bottom: 24, left: "50%", transform: "translateX(-50%)",
                    zIndex: 300,
                    background: "#fff", borderRadius: 12, padding: "12px 20px",
                    border: "1px solid rgba(245,158,11,0.3)",
                    borderLeft: "4px solid #F59E0B",
                    boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
                    display: "flex", alignItems: "center", gap: 10,
                    animation: "toast-in .35s cubic-bezier(.22,1,.36,1)",
                    fontFamily: "var(--fd)", fontSize: 13, fontWeight: 700, color: "#0F172A",
                    whiteSpace: "nowrap",
                }}>
                    <AlertI />
                    {toast.msg}
                </div>
            )}
        </>
    );
}