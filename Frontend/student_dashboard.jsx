import { useState, useEffect, useRef } from "react";

/* ─────────────────────────────────────────────────────────────────────────────
   NEXTSTEP · STUDENT DASHBOARD
   Warmer light theme — personal, encouraging, action-oriented
   The flywheel made visible: student behavior → score update → underwriter notified
   ───────────────────────────────────────────────────────────────────────────── */

const SD_CSS = `
/* ── Page ────────────────────────────────────── */
.sd-page { background:#F0F2FA; min-height:calc(100vh - 56px); }
.sd-inner { max-width:840px; margin:0 auto; padding:36px 24px 80px; }

/* ── Hero section ────────────────────────────── */
.sd-hero {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:22px;
  padding:32px 36px; margin-bottom:20px;
  box-shadow:0 2px 12px rgba(0,0,0,0.05);
  display:flex; align-items:center; gap:36px;
  animation:fade-up .5s cubic-bezier(.22,1,.36,1) both; opacity:0;
  position:relative; overflow:hidden;
}
.sd-hero::before {
  content:'';
  position:absolute; top:-80px; right:-80px;
  width:280px; height:280px; border-radius:50%;
  background:radial-gradient(circle, rgba(16,185,129,0.07) 0%, transparent 70%);
  pointer-events:none;
}
.sd-hero-ring { flex-shrink:0; position:relative; }
.sd-hero-text { flex:1; }
.sd-greeting {
  font-family:var(--fd); font-size:11px; font-weight:800;
  letter-spacing:.12em; text-transform:uppercase; color:#94A3B8;
  margin-bottom:6px;
}
.sd-name {
  font-family:var(--fd); font-size:28px; font-weight:800;
  letter-spacing:-.04em; color:#0F172A; margin-bottom:6px;
  line-height:1.1;
}
.sd-headline {
  font-size:15px; color:#475569; line-height:1.6; margin-bottom:16px;
}
.sd-headline strong { color:#0F172A; font-weight:700; }
.sd-next-nudge {
  display:inline-flex; align-items:center; gap:7px;
  padding:9px 16px; border-radius:99px;
  background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
  font-family:var(--fd); font-size:12px; font-weight:700; color:#4338CA;
  cursor:pointer; transition:all .18s;
}
.sd-next-nudge:hover {
  background:rgba(99,102,241,0.12);
  box-shadow:0 2px 10px rgba(99,102,241,0.18);
  transform:translateY(-1px);
}

/* ── Readiness ring ──────────────────────────── */
.readiness-ring-num {
  font-family:var(--fd); font-size:36px; font-weight:800;
  letter-spacing:-.05em; color:#10B981;
  animation:count-in .6s ease both .5s; opacity:0;
}
.readiness-ring-lbl {
  font-family:var(--fd); font-size:9px; font-weight:700;
  letter-spacing:.1em; text-transform:uppercase; color:#94A3B8;
  text-align:center;
}

/* ── Section head ────────────────────────────── */
.sd-sec-head {
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:14px;
}
.sd-sec-title {
  font-family:var(--fd); font-size:9px; font-weight:800;
  letter-spacing:.14em; text-transform:uppercase; color:#94A3B8;
}
.sd-sec-count {
  font-family:var(--fd); font-size:11px; font-weight:700; color:#CBD5E1;
}

/* ── Action card ─────────────────────────────── */
.action-plan-card {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:18px;
  margin-bottom:12px;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
  overflow:hidden;
  animation:fade-up .45s cubic-bezier(.22,1,.36,1) both; opacity:0;
  transition:box-shadow .18s, transform .18s;
}
.action-plan-card:hover { box-shadow:0 4px 20px rgba(0,0,0,0.08); transform:translateY(-1px); }
.action-plan-card.active { border-left:3px solid #6366F1; }
.action-plan-card.done   { border-left:3px solid #10B981; opacity:.75; }
.action-plan-card.pending { border-left:3px solid #E2E8F0; }

.apc-header {
  display:flex; align-items:flex-start; justify-content:space-between;
  padding:18px 20px 14px; gap:12px;
}
.apc-icon-wrap {
  width:38px; height:38px; border-radius:11px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:18px;
}
.apc-title { font-family:var(--fd); font-size:15px; font-weight:800; color:#0F172A; letter-spacing:-.02em; margin-bottom:4px; }
.apc-rationale { font-size:12.5px; color:#64748B; line-height:1.6; }
.apc-body { padding:0 20px 18px; }
.apc-stats {
  display:flex; align-items:center; gap:16px; margin-bottom:12px; flex-wrap:wrap;
}
.apc-stat { display:flex; align-items:center; gap:5px; font-size:11px; color:#64748B; }
.apc-stat-val { font-family:var(--fd); font-weight:700; color:#0F172A; font-size:12px; }
.apc-progress-wrap { margin-bottom:14px; }
.apc-progress-head { display:flex; justify-content:space-between; margin-bottom:6px; }
.apc-progress-lbl { font-family:var(--fd); font-size:10px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:#94A3B8; }
.apc-progress-pct { font-family:var(--fm); font-size:11px; font-weight:600; color:#6366F1; }
.apc-track { height:6px; border-radius:99px; background:rgba(0,0,0,0.07); overflow:hidden; }
.apc-fill  { height:100%; border-radius:99px; animation:fill-bar .9s cubic-bezier(.22,1,.36,1) both; }

/* ── Complete button ──────────────────────────── */
.complete-btn {
  display:flex; align-items:center; justify-content:center; gap:8px;
  width:100%; padding:11px; border-radius:11px; border:none; cursor:pointer;
  font-family:var(--fd); font-size:13px; font-weight:800; letter-spacing:-.01em;
  background:linear-gradient(135deg,#10B981,#059669);
  color:#fff;
  box-shadow:0 3px 12px rgba(16,185,129,0.28);
  position:relative; overflow:hidden;
  transition:transform .15s, box-shadow .15s;
}
.complete-btn:hover:not(:disabled) { transform:translateY(-1px); box-shadow:0 5px 18px rgba(16,185,129,0.36); }
.complete-btn:disabled { opacity:.6; cursor:default; }
.complete-btn.done-state { background:linear-gradient(135deg,#6366F1,#4f46e5); box-shadow:0 3px 12px rgba(99,102,241,0.28); }
.btn-shimmer { position:absolute; inset:0; background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,0.18) 50%,transparent 70%); animation:shimmer 2.8s ease infinite; pointer-events:none; }

/* ── Engagement tracking badge ────────────────── */
.eng-track {
  display:flex; align-items:center; gap:6px; flex-wrap:wrap;
  padding:9px 12px; border-radius:10px;
  background:rgba(99,102,241,0.04); border:1px solid rgba(99,102,241,0.12);
  margin-bottom:12px;
}
.eng-chip {
  display:inline-flex; align-items:center; gap:4px;
  font-family:var(--fm); font-size:10px; color:#475569;
}
.eng-chip-sep { color:#CBD5E1; }

/* ── Live update toast ────────────────────────── */
.live-toast {
  position:fixed; top:70px; right:24px; z-index:300;
  background:#fff; border:1px solid rgba(16,185,129,0.25);
  border-left:4px solid #10B981;
  border-radius:14px; padding:16px 18px;
  box-shadow:0 8px 32px rgba(0,0,0,0.14);
  min-width:300px; max-width:360px;
  animation:toast-in .4s cubic-bezier(.22,1,.36,1);
}
.live-toast-title {
  font-family:var(--fd); font-size:12px; font-weight:800; color:#0F172A;
  letter-spacing:-.01em; margin-bottom:8px;
  display:flex; align-items:center; gap:7px;
}
.live-toast-scores {
  display:flex; align-items:center; gap:12px; margin-bottom:8px;
}
.lts-from { font-family:var(--fd); font-size:28px; font-weight:800; color:#94A3B8; letter-spacing:-.05em; }
.lts-arrow { color:#10B981; font-size:16px; }
.lts-to   { font-family:var(--fd); font-size:28px; font-weight:800; color:#10B981; letter-spacing:-.05em; }
.live-toast-sub { font-size:11px; color:#64748B; line-height:1.5; }
@keyframes toast-in {
  from { opacity:0; transform:translateX(20px); }
  to   { opacity:1; transform:translateX(0); }
}

/* ── Macro panel ──────────────────────────────── */
.macro-panel {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:18px;
  padding:20px 22px; margin-bottom:20px;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
  animation:fade-up .45s ease both; opacity:0;
}
.macro-signals { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:14px; }
.macro-sig {
  padding:12px 14px; border-radius:12px;
  background:rgba(0,0,0,0.025); border:1px solid rgba(0,0,0,0.07);
}
.macro-sig-label { font-family:var(--fd); font-size:9px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#94A3B8; margin-bottom:5px; }
.macro-sig-val { font-family:var(--fd); font-size:15px; font-weight:800; letter-spacing:-.03em; margin-bottom:5px; }
.macro-sig-bar { height:4px; border-radius:99px; background:rgba(0,0,0,0.07); overflow:hidden; }
.macro-sig-fill { height:100%; border-radius:99px; animation:fill-bar .8s cubic-bezier(.22,1,.36,1) both; }
.macro-insight {
  margin-top:14px; padding:12px 14px; border-radius:11px;
  background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.15);
  font-size:13px; color:#1E293B; line-height:1.6; font-style:italic;
}

/* ── Employer table ───────────────────────────── */
.emp-panel {
  background:#fff; border:1px solid rgba(0,0,0,0.07); border-radius:18px;
  overflow:hidden; margin-bottom:20px;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
  animation:fade-up .45s ease both; opacity:0;
}
.emp-panel-head {
  padding:18px 22px 14px;
  border-bottom:1px solid rgba(0,0,0,0.07);
}
.emp-panel-title { font-family:var(--fd); font-size:15px; font-weight:800; color:#0F172A; letter-spacing:-.02em; margin-bottom:3px; }
.emp-panel-sub { font-size:12px; color:#94A3B8; }
.emp-row {
  display:grid; grid-template-columns:32px 1fr 90px 80px;
  padding:12px 22px; border-bottom:1px solid rgba(0,0,0,0.05);
  align-items:center; gap:0;
  transition:background .12s;
  animation:fade-up .35s ease both; opacity:0;
}
.emp-row:last-child { border-bottom:none; }
.emp-row:hover { background:rgba(99,102,241,0.03); }
.emp-rank { font-family:var(--fm); font-size:11px; color:#CBD5E1; font-weight:500; }
.emp-name { font-weight:600; color:#0F172A; font-size:13px; }
.emp-sal  { font-family:var(--fd); font-weight:800; font-size:14px; color:#0F172A; }
.emp-hires { font-size:12px; color:#64748B; text-align:right; }

/* ── Progress checklist ───────────────────────── */
.checklist-item {
  display:flex; align-items:flex-start; gap:12px;
  padding:12px 0; border-bottom:1px solid rgba(0,0,0,0.05);
  animation:fade-up .35s ease both; opacity:0;
}
.checklist-item:last-child { border-bottom:none; }
.check-circle {
  width:22px; height:22px; border-radius:50%; flex-shrink:0; margin-top:1px;
  display:flex; align-items:center; justify-content:center; border:2px solid;
  transition:all .2s;
}
.check-circle.done { border-color:#10B981; background:#10B981; color:#fff; }
.check-circle.active { border-color:#6366F1; background:rgba(99,102,241,0.1); color:#6366F1; }
.check-circle.pending { border-color:#E2E8F0; background:#F8F9FD; color:#CBD5E1; }
.check-label { font-family:var(--fd); font-size:13px; font-weight:700; color:#0F172A; margin-bottom:3px; letter-spacing:-.01em; }
.check-meta { font-size:11px; color:#94A3B8; }

/* ── Tenacity card ────────────────────────────── */
.tenacity-card {
  background:linear-gradient(135deg,rgba(245,158,11,0.06),rgba(245,158,11,0.02));
  border:1px solid rgba(245,158,11,0.2); border-radius:18px; padding:20px 22px;
  margin-bottom:20px;
  animation:fade-up .45s ease both; opacity:0;
}
.tenacity-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.tenacity-score-big {
  font-family:var(--fd); font-size:48px; font-weight:800;
  color:#D97706; letter-spacing:-.06em; line-height:1;
  animation:count-in .5s ease both .4s; opacity:0;
}
.tenacity-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.ten-item { background:rgba(255,255,255,0.7); border:1px solid rgba(245,158,11,0.15); border-radius:11px; padding:11px 13px; }
.ten-item-lbl { font-family:var(--fd); font-size:9px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:#B45309; margin-bottom:5px; }
.ten-item-val { font-family:var(--fd); font-size:16px; font-weight:800; color:#0F172A; letter-spacing:-.03em; }

/* ── Score delta flash ────────────────────────── */
.score-flash {
  animation:score-pop .6s cubic-bezier(.22,1,.36,1) both;
}
@keyframes score-pop {
  0%   { transform:scale(1); }
  40%  { transform:scale(1.12); color:#10B981; }
  100% { transform:scale(1); }
}

/* ── Confetti dot ─────────────────────────────── */
@keyframes confetti-fall {
  0%   { opacity:1; transform:translateY(0) rotate(0deg); }
  100% { opacity:0; transform:translateY(60px) rotate(720deg); }
}
`;

function StyleInjectorSD() {
  useEffect(() => {
    const id = "ns-sd";
    if (!document.getElementById(id)) {
      const el = document.createElement("style");
      el.id = id; el.textContent = SD_CSS;
      document.head.appendChild(el);
    }
    return () => document.getElementById(id)?.remove();
  }, []);
  return null;
}

// ── DATA ──────────────────────────────────────────────────────────────────────
const STUDENT = {
  name: "Priya Sharma",
  readiness: 71,
  program: "MS Computer Science",
  university: "University of Texas Austin",
  tenacity: 0.79,
  tenacity_breakdown: { completion: 1.0, engagement: 0.82, consistency: 0.74 },
  certifications: 1,
};

const ACTIONS = [
  {
    id: 1, status: "active",
    icon: "🎓", iconBg: "rgba(99,102,241,0.1)", iconColor: "#6366F1",
    title: "AWS Cloud Associate Certificate",
    rationale: "Students at UT Austin MS CS who completed this saw 8% better placement within 6 months. High confidence from 312 similar profiles.",
    hours: 14.2, days: 8, visits: 11, cert: true, pct: 89,
    assigned: "Apr 10, 2026", effort: "~72 hours",
    scoreImpact: 3,
  },
  {
    id: 2, status: "pending",
    icon: "💼", iconBg: "rgba(16,185,129,0.1)", iconColor: "#10B981",
    title: "Build a Portfolio Project",
    rationale: "Portfolio work improves employer engagement rate by 23% for cloud and software engineering roles in the US market.",
    hours: 0, days: 0, visits: 0, cert: false, pct: 0,
    assigned: "Apr 14, 2026", effort: "~20 hours",
    scoreImpact: 5,
  },
  {
    id: 3, status: "pending",
    icon: "🎯", iconBg: "rgba(245,158,11,0.1)", iconColor: "#D97706",
    title: "Mock Interview Practice",
    rationale: "Technical interview practice shows positive outcomes for this profile. One focused session is the expected pattern for this action type.",
    hours: 0, days: 0, visits: 0, cert: false, pct: 0,
    assigned: "Apr 14, 2026", effort: "~2 hours",
    scoreImpact: 2,
  },
];

const EMPLOYERS = [
  { rank: 1, name: "Infosys BPM Ltd",      salary: 89000,  hires: 420 },
  { rank: 2, name: "Cognizant Technology",  salary: 92000,  hires: 380 },
  { rank: 3, name: "TCS America",           salary: 87000,  hires: 312 },
  { rank: 4, name: "Wipro Technologies",    salary: 88000,  hires: 287 },
  { rank: 5, name: "Google LLC",            salary: 148000, hires: 241 },
];

const MACRO = [
  { label: "Hiring Demand",  val: "HIGH",     num: 0.84, color: "#10B981" },
  { label: "Competition",    val: "MODERATE", num: 0.55, color: "#F59E0B" },
  { label: "Visa Climate",   val: "CAUTIOUS", num: 0.42, color: "#F59E0B" },
];

// ── ICONS ─────────────────────────────────────────────────────────────────────
const CheckI   = () => <svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="1.5 6 4.5 9 10.5 3"/></svg>;
const SpinI    = () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{animation:"spin .7s linear infinite"}}><path d="M21 12a9 9 0 11-3.5-7"/></svg>;
const BoltI    = () => <svg width="11" height="11" viewBox="0 0 12 12" fill="currentColor"><polygon points="7 1 2 7 6 7 5 11 10 5 6 5"/></svg>;
const ArrI     = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>;
const ClockI   = () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
const CalI     = () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>;
const EyeI     = () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>;
const CertI    = () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>;

// ── COUNT-UP HOOK ─────────────────────────────────────────────────────────────
function useCountUp(target, duration = 900, go = true) {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!go) return;
    const t0 = performance.now();
    const tick = (now) => {
      const p = Math.min((now - t0) / duration, 1);
      setV(Math.round((1 - Math.pow(1 - p, 3)) * target));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [go, target]);
  return v;
}

// ── READINESS RING ────────────────────────────────────────────────────────────
function ReadinessRing({ score, animate }) {
  const R = 62, CIRC = 2 * Math.PI * R;
  const [offset, setOffset] = useState(CIRC);
  const display = useCountUp(score, 1100, animate);

  useEffect(() => {
    if (!animate) return;
    const t = setTimeout(() => setOffset(CIRC * (1 - score / 100)), 80);
    return () => clearTimeout(t);
  }, [animate, score]);

  return (
    <div className="sd-hero-ring">
      <svg width="158" height="158" viewBox="0 0 158 158">
        {/* Outer glow ring */}
        <circle cx="79" cy="79" r="70" fill="none" stroke="rgba(16,185,129,0.08)" strokeWidth="14"/>
        {/* Track */}
        <circle cx="79" cy="79" r={R} fill="none" stroke="#F0F2FA" strokeWidth="12"/>
        {/* Progress */}
        <circle cx="79" cy="79" r={R} fill="none"
          stroke="#10B981" strokeWidth="12" strokeLinecap="round"
          strokeDasharray={CIRC} strokeDashoffset={offset}
          transform="rotate(-90 79 79)"
          style={{
            transition: animate ? "stroke-dashoffset 1.2s cubic-bezier(0.22,1,0.36,1)" : "none",
            filter: "drop-shadow(0 0 10px rgba(16,185,129,0.5))",
          }}
        />
        {/* Center */}
        <text x="79" y="73" textAnchor="middle"
          style={{ fontFamily:"var(--fd)", fontSize:32, fontWeight:800, fill:"#10B981", letterSpacing:"-1.5px" }}>
          {animate ? display : score}
        </text>
        <text x="79" y="88" textAnchor="middle"
          style={{ fontFamily:"var(--fd)", fontSize:9, fontWeight:700, fill:"#94A3B8", letterSpacing:"1.5px", textTransform:"uppercase" }}>
          READINESS
        </text>
      </svg>
    </div>
  );
}

// ── CONFETTI BURST ────────────────────────────────────────────────────────────
function Confetti({ x, y }) {
  const dots = Array.from({ length: 12 }, (_, i) => ({
    angle: (i / 12) * 360,
    color: ["#10B981","#6366F1","#F59E0B","#3B82F6","#EF4444"][i % 5],
    size: 5 + Math.random() * 4,
    dist: 30 + Math.random() * 40,
  }));
  return (
    <div style={{ position: "fixed", left: x, top: y, pointerEvents: "none", zIndex: 500 }}>
      {dots.map((d, i) => (
        <div key={i} style={{
          position: "absolute",
          width: d.size, height: d.size, borderRadius: "50%",
          background: d.color,
          left: Math.cos((d.angle * Math.PI) / 180) * d.dist - d.size / 2,
          top:  Math.sin((d.angle * Math.PI) / 180) * d.dist - d.size / 2,
          animation: `confetti-fall .8s ease both`,
          animationDelay: `${i * 30}ms`,
        }} />
      ))}
    </div>
  );
}

// ── ACTION CARD ────────────────────────────────────────────────────────────────
function ActionCard({ action, onComplete, delay }) {
  const [completing, setCompleting] = useState(false);
  const [done, setDone]             = useState(action.status === "done");
  const btnRef = useRef(null);
  const [confetti, setConfetti]     = useState(null);

  const handleComplete = () => {
    if (completing || done) return;
    setCompleting(true);
    const rect = btnRef.current?.getBoundingClientRect();
    setTimeout(() => {
      setCompleting(false);
      setDone(true);
      if (rect) setConfetti({ x: rect.left + rect.width / 2, y: rect.top });
      setTimeout(() => setConfetti(null), 1200);
      onComplete?.(action);
    }, 1000);
  };

  const isActive  = action.status === "active" && !done;
  const isPending = action.status === "pending" && !done;
  const cardCls   = done ? "done" : isActive ? "active" : "pending";

  return (
    <>
      <div className={`action-plan-card ${cardCls}`} style={{ animationDelay: `${delay}ms` }}>
        <div className="apc-header">
          <div style={{ display: "flex", gap: 12, flex: 1 }}>
            <div className="apc-icon-wrap" style={{ background: action.iconBg }}>
              <span>{action.icon}</span>
            </div>
            <div style={{ flex: 1 }}>
              <div className="apc-title">{action.title}</div>
              <div className="apc-rationale">{action.rationale}</div>
            </div>
          </div>
          <div style={{ flexShrink: 0 }}>
            {done
              ? <span style={{ display:"inline-flex", alignItems:"center", gap:5, padding:"4px 10px", borderRadius:99, background:"rgba(16,185,129,0.1)", color:"#059669", border:"1px solid rgba(16,185,129,0.25)", fontFamily:"var(--fd)", fontSize:10, fontWeight:800, letterSpacing:".06em", textTransform:"uppercase" }}><CheckI /> Done</span>
              : isActive
                ? <span style={{ display:"inline-flex", alignItems:"center", gap:5, padding:"4px 10px", borderRadius:99, background:"rgba(99,102,241,0.1)", color:"#6366F1", border:"1px solid rgba(99,102,241,0.25)", fontFamily:"var(--fd)", fontSize:10, fontWeight:800, letterSpacing:".06em", textTransform:"uppercase" }}>● In Progress</span>
                : <span style={{ display:"inline-flex", alignItems:"center", gap:5, padding:"4px 10px", borderRadius:99, background:"rgba(0,0,0,0.04)", color:"#94A3B8", border:"1px solid rgba(0,0,0,0.08)", fontFamily:"var(--fd)", fontSize:10, fontWeight:800, letterSpacing:".06em", textTransform:"uppercase" }}>Assigned</span>
            }
          </div>
        </div>

        {(isActive || done) && (
          <div className="apc-body">
            {/* Passive tracking row */}
            {(action.hours > 0 || done) && (
              <div className="eng-track">
                {[
                  { icon: <ClockI />, label: `${done ? action.hours : action.hours}h active` },
                  { icon: <CalI />,   label: `${done ? action.days : action.days} days` },
                  { icon: <EyeI />,   label: `${done ? action.visits : action.visits} visits` },
                  ...(action.cert || done ? [{ icon: <CertI />, label: "Certificate ✓", color: "#D97706" }] : []),
                ].map((s, i) => (
                  <span key={i} className="eng-chip" style={s.color ? { color: s.color, fontWeight: 700 } : {}}>
                    {i > 0 && <span className="eng-chip-sep">·</span>}
                    {s.icon} {s.label}
                  </span>
                ))}
              </div>
            )}

            {/* Progress */}
            {!done && (
              <div className="apc-progress-wrap">
                <div className="apc-progress-head">
                  <span className="apc-progress-lbl">Progress</span>
                  <span className="apc-progress-pct">{action.pct}%</span>
                </div>
                <div className="apc-track">
                  <div className="apc-fill" style={{
                    width: `${action.pct}%`,
                    background: "linear-gradient(90deg,#6366F1,#818CF8)",
                  }} />
                </div>
              </div>
            )}

            {/* Footer meta */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
              <div style={{ display: "flex", gap: 14 }}>
                <span style={{ fontSize: 11, color: "#94A3B8", display: "flex", alignItems: "center", gap: 4 }}>
                  <CalI /> Assigned {action.assigned}
                </span>
                <span style={{ fontSize: 11, color: "#94A3B8", display: "flex", alignItems: "center", gap: 4 }}>
                  <ClockI /> Expected {action.effort}
                </span>
              </div>
              {!done && (
                <button
                  ref={btnRef}
                  className={`complete-btn${done ? " done-state" : ""}`}
                  style={{ width: "auto", padding: "9px 18px", fontSize: 12 }}
                  onClick={handleComplete}
                  disabled={completing}>
                  <div className="btn-shimmer" />
                  {completing ? <><SpinI /> Saving…</> : <><CheckI /> Mark Complete</>}
                </button>
              )}
              {done && (
                <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#059669", fontFamily: "var(--fd)", fontWeight: 700 }}>
                  <BoltI /> Great work!
                </div>
              )}
            </div>
          </div>
        )}

        {/* Pending card footer */}
        {isPending && (
          <div className="apc-body" style={{ paddingTop: 0 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: 11, color: "#94A3B8", display: "flex", alignItems: "center", gap: 4 }}>
                <CalI /> Assigned {action.assigned} · {action.effort}
              </span>
              <span style={{ fontSize: 11, color: "#6366F1", fontFamily: "var(--fd)", fontWeight: 700 }}>
                High impact action
              </span>
            </div>
          </div>
        )}
      </div>
      {confetti && <Confetti x={confetti.x} y={confetti.y} />}
    </>
  );
}

// ── LIVE UPDATE TOAST ─────────────────────────────────────────────────────────
function LiveToast({ from, to, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 6000);
    return () => clearTimeout(t);
  }, []);
  return (
    <div className="live-toast">
      <div className="live-toast-title">
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10B981", animation: "pulse-dot 1.5s ease infinite" }} />
        Profile strength updated
      </div>
      <div className="live-toast-scores">
        <div className="lts-from">{from}</div>
        <div className="lts-arrow">→</div>
        <div className="lts-to">{to}</div>
        <div style={{ marginLeft: 6, fontFamily: "var(--fd)", fontSize: 13, fontWeight: 800, color: "#10B981" }}>
          ↑ Improved
        </div>
      </div>
      <div className="live-toast-sub">
        Your readiness score has improved!<br />
        Great job staying on track.
      </div>
      <button onClick={onDismiss} style={{
        marginTop: 10, padding: "7px 14px", borderRadius: 8, border: "1px solid rgba(0,0,0,0.1)",
        background: "transparent", fontFamily: "var(--fd)", fontSize: 11, fontWeight: 700,
        color: "#64748B", cursor: "pointer", width: "100%", transition: "background .15s",
      }}
        onMouseEnter={e => e.currentTarget.style.background = "rgba(0,0,0,0.04)"}
        onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
        Dismiss
      </button>
    </div>
  );
}

// ── TENACITY CARD ─────────────────────────────────────────────────────────────
function TenacityCard({ data, animate }) {
  const display = useCountUp(Math.round(data.tenacity * 100), 900, animate);
  return (
    <div className="tenacity-card" style={{ animationDelay: "300ms" }}>
      <div className="tenacity-header">
        <div>
          <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".12em", textTransform: "uppercase", color: "#B45309", marginBottom: 4 }}>
            Behavioral Tenacity Score
          </div>
          <div style={{ fontSize: 13, color: "#78350F", lineHeight: 1.6, maxWidth: 380 }}>
            Based on your active engagement across {data.actions} completed actions over {data.days} days.
            This signal contributes to your repayment confidence score.
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="tenacity-score-big">{animate ? `0.${display < 100 ? display.toString().padStart(2,"0") : "100"}` : `0.${Math.round(data.tenacity * 100)}`}</div>
          <div style={{ fontFamily: "var(--fd)", fontSize: 9, fontWeight: 800, letterSpacing: ".1em", textTransform: "uppercase", color: "#B45309" }}>HIGH</div>
        </div>
      </div>
      <div className="tenacity-grid">
        {[
          { label: "Completion Rate", val: `${Math.round(data.breakdown.completion * 100)}%` },
          { label: "Engagement Depth", val: `${Math.round(data.breakdown.engagement * 100)}%` },
          { label: "Consistency", val: `${Math.round(data.breakdown.consistency * 100)}%` },
        ].map((t, i) => (
          <div key={i} className="ten-item" style={{ animationDelay: `${400 + i * 80}ms` }}>
            <div className="ten-item-lbl">{t.label}</div>
            <div className="ten-item-val">{t.val}</div>
            <div style={{ height: 3, borderRadius: 99, background: "rgba(245,158,11,0.15)", marginTop: 6, overflow: "hidden" }}>
              <div style={{ height: "100%", width: t.val, background: "#F59E0B", borderRadius: 99, animation: "fill-bar .8s cubic-bezier(.22,1,.36,1) both", animationDelay: `${500 + i * 80}ms` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── MAIN COMPONENT ────────────────────────────────────────────────────────────
export default function StudentDashboard() {
  const [readiness, setReadiness]     = useState(STUDENT.readiness);
  const [actions, setActions]         = useState(ACTIONS);
  const [toast, setToast]             = useState(null);
  const [animated, setAnimated]       = useState(false);
  const [ringFlash, setRingFlash]     = useState(false);
  const [completedCount, setCompleted] = useState(0);

  useEffect(() => { setTimeout(() => setAnimated(true), 100); }, []);

  const handleComplete = (action) => {
    // Update score
    const newScore = Math.min(readiness + action.scoreImpact, 100);
    setReadiness(newScore);
    setCompleted(c => c + 1);
    setRingFlash(true);
    setTimeout(() => setRingFlash(false), 700);

    // SSE simulation → show underwriter toast
    setTimeout(() => {
      setToast({ from: readiness, to: newScore });
    }, 400);

    // Mark action as done in state
    setActions(prev => prev.map(a => a.id === action.id ? { ...a, status: "done" } : a));
  };

  const doneCount    = actions.filter(a => a.status === "done").length;
  const activeCount  = actions.filter(a => a.status === "active").length;
  const pendingCount = actions.filter(a => a.status === "pending").length;

  return (
    <>
      <StyleInjectorSD />
      <div className="sd-page">
        <div className="sd-inner">

          {/* ── HERO ─────────────────────────────────── */}
          <div className="sd-hero">
            <div style={{ position: "relative" }}>
              <ReadinessRing score={readiness} animate={animated} />
              {ringFlash && (
                <div style={{
                  position: "absolute", inset: -8, borderRadius: "50%",
                  border: "2px solid #10B981",
                  animation: "score-pop .5s ease both",
                  pointerEvents: "none",
                }} />
              )}
            </div>
            <div className="sd-hero-text">
              <div className="sd-greeting">Your dashboard · Apr 30, 2026</div>
              <div className="sd-name">Hi, Priya 👋</div>
              <div className="sd-headline">
                You're <strong>on track for placement within 6 months</strong> based on
                your profile and current market conditions.
                Complete your next action to reach {Math.min(readiness + 3, 100)}%.
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                <div className="sd-next-nudge">
                  Complete next action <ArrI />
                </div>
                <div style={{ fontSize: 11, color: "#94A3B8", fontFamily: "var(--fd)", fontWeight: 600 }}>
                  {doneCount} done · {activeCount} in progress · {pendingCount} assigned
                </div>
              </div>
            </div>
          </div>



          {/* ── ACTION PLAN ───────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <div className="sd-sec-head">
              <div className="sd-sec-title">Your action plan</div>
              <div className="sd-sec-count">{actions.length} total · {doneCount} completed</div>
            </div>
            {actions.map((a, i) => (
              <ActionCard
                key={a.id}
                action={a}
                onComplete={handleComplete}
                delay={i * 80}
              />
            ))}
          </div>

          {/* ── PROGRESS CHECKLIST ────────────────────── */}
          <div className="wcard" style={{ marginBottom: 20, animation: "fade-up .45s ease both .3s", opacity: 0 }}>
            <div className="sd-sec-head" style={{ marginBottom: 16 }}>
              <div className="sd-sec-title">Progress tracker</div>
            </div>
            {[
              { label: "Profile submitted",       meta: "Apr 8, 2026",  status: "done" },
              { label: "Pre-loan plan assigned",  meta: "Apr 10, 2026", status: "done" },
              { label: "AWS certification",       meta: "In progress",  status: "active" },
              { label: "Portfolio project",       meta: "Not started",  status: "pending" },
              { label: "Mock interview",          meta: "Not started",  status: "pending" },
              { label: "Final score review",      meta: "Pending",      status: "pending" },
            ].map((item, i) => (
              <div key={i} className="checklist-item" style={{ animationDelay: `${350 + i * 55}ms` }}>
                <div className={`check-circle ${item.status}`}>
                  {item.status === "done"   && <CheckI />}
                  {item.status === "active" && <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#6366F1" }} />}
                  {item.status === "pending" && <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#E2E8F0" }} />}
                </div>
                <div>
                  <div className="check-label" style={{ color: item.status === "pending" ? "#94A3B8" : "#0F172A" }}>
                    {item.label}
                  </div>
                  <div className="check-meta">{item.meta}</div>
                </div>
              </div>
            ))}
          </div>

          {/* ── MACRO PANEL ───────────────────────────── */}
          <div className="macro-panel" style={{ animationDelay: "350ms" }}>
            <div className="sd-sec-head" style={{ marginBottom: 0 }}>
              <div>
                <div className="sd-sec-title" style={{ marginBottom: 2 }}>Market conditions in your target sector</div>
                <div style={{ fontSize: 12, color: "#64748B" }}>🇺🇸 United States · Cloud & Software Engineering</div>
              </div>
              <div style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#94A3B8" }}>Updated Apr 30, 2026</div>
            </div>
            <div className="macro-signals">
              {MACRO.map((m, i) => (
                <div key={i} className="macro-sig" style={{ animation: `fade-up .35s ease both ${400 + i * 70}ms`, opacity: 0 }}>
                  <div className="macro-sig-label">{m.label}</div>
                  <div className="macro-sig-val" style={{ color: m.color }}>{m.val}</div>
                  <div className="macro-sig-bar">
                    <div className="macro-sig-fill" style={{ width: `${m.num * 100}%`, background: m.color, animationDelay: `${450 + i * 70}ms` }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="macro-insight">
              "Your action plan was updated this week to reflect rising cloud engineering demand
              in the US market. AWS certification completion now has a stronger placement signal
              than it did at origination."
            </div>
          </div>

          {/* ── EMPLOYERS ─────────────────────────────── */}
          <div className="emp-panel" style={{ animationDelay: "400ms" }}>
            <div className="emp-panel-head">
              <div className="emp-panel-title">Companies looking for profiles like yours</div>
              <div className="emp-panel-sub">Based on 700,000+ real H1B hiring records · filtered to your program + target sector</div>
            </div>
            {EMPLOYERS.map((e, i) => (
              <div key={i} className="emp-row" style={{ animationDelay: `${450 + i * 60}ms` }}>
                <div className="emp-rank">{e.rank}</div>
                <div className="emp-name">{e.name}</div>
                <div className="emp-sal">${(e.salary / 1000).toFixed(0)}K<span style={{ fontSize: 10, fontWeight: 500, color: "#94A3B8", marginLeft: 2 }}>/yr</span></div>
                <div className="emp-hires">{e.hires} hires/yr</div>
              </div>
            ))}
          </div>



        </div>
      </div>

      {/* ── LIVE TOAST ────────────────────────────────── */}
      {toast && (
        <LiveToast
          from={toast.from}
          to={toast.to}
          onDismiss={() => setToast(null)}
        />
      )}
    </>
  );
}
