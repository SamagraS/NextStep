import { useState, useEffect, useRef } from "react";
import backgroundVideo from "./Video Project.mp4";
import UnderwriterConsole from "./underwriter.jsx";
import PortfolioDashboard from "./portfolio_dashboard.jsx";
import StudentDashboard from "./student_dashboard.jsx";
import { DEMO_RESPONSE, PRE_ACTIONS, COHORTS, BLOBS } from "./constants.js";

/* ─────────────────────────────────────────────────────────────────────────────
   NEXTSTEP · CHUNK 1 · v2
   Design: Dark Intelligence — Bloomberg Terminal meets Luxury Fintech
   Fonts:  Outfit (display) · DM Sans (body) · JetBrains Mono (data)
   ───────────────────────────────────────────────────────────────────────────── */

const CSS = `
@import url("https://cdn.jsdelivr.net/npm/@fontsource/outfit@5.0.12/index.css");
@import url("https://cdn.jsdelivr.net/npm/@fontsource/dm-sans@5.0.12/index.css");
@import url("https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.2/index.css");

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:     #F8FAFC;
  --bg-1:   #FFFFFF;
  --bg-2:   #F1F5F9;
  --bg-3:   #E2E8F0;
  --bdr:    rgba(15, 23, 42, 0.08);
  --bdr-hi: rgba(15, 23, 42, 0.14);

  --accent:   #4F46E5;
  --accent-2: #6366F1;
  --acc-glow: rgba(79, 70, 229, 0.1);
  --acc-dim:  rgba(79, 70, 229, 0.05);
  --blue:     #2563EB;
  --green:    #059669;
  --amber:    #D97706;
  --red:      #DC2626;
  --grn-dim:  rgba(5, 150, 105, 0.08);
  --amb-dim:  rgba(217, 119, 6, 0.08);
  --red-dim:  rgba(220, 38, 38, 0.08);

  --t1: #0F172A;
  --t2: #475569;
  --t3: #94A3B8;

  --fd: 'Outfit', system-ui, sans-serif;
  --fb: 'DM Sans', system-ui, sans-serif;
  --fm: 'JetBrains Mono', 'Fira Code', monospace;
}

html, body, #root {
  height: 100%; min-height: 100vh;
  background: var(--bg);
  color: var(--t1);
  font-family: var(--fb);
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg-3); border-radius: 99px; }

/* ── KEYFRAMES ─────────────────────────────── */
@keyframes fa { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(40px,-30px) scale(1.08)} 66%{transform:translate(-25px,20px) scale(0.95)} }
@keyframes fb { 0%,100%{transform:translate(0,0) scale(1)} 40%{transform:translate(-35px,30px) scale(1.05)} 70%{transform:translate(20px,-15px) scale(0.98)} }
@keyframes fc { 0%,100%{transform:translate(0,0) scale(1)} 30%{transform:translate(20px,25px) scale(1.1)} 60%{transform:translate(-30px,-20px) scale(0.92)} }

/* ── FLOATING BLOB ANIMATIONS ─────────────── */
@keyframes blob1 {
  0%   { transform: translate(0, 0) scale(1); }
  20%  { transform: translate(120px, -80px) scale(1.1); }
  40%  { transform: translate(-60px, 100px) scale(0.9); }
  60%  { transform: translate(180px, 40px) scale(1.15); }
  80%  { transform: translate(-30px, -120px) scale(0.95); }
  100% { transform: translate(0, 0) scale(1); }
}
@keyframes blob2 {
  0%   { transform: translate(0, 0) scale(1); }
  25%  { transform: translate(-150px, 60px) scale(1.12); }
  50%  { transform: translate(80px, 140px) scale(0.88); }
  75%  { transform: translate(-100px, -90px) scale(1.08); }
  100% { transform: translate(0, 0) scale(1); }
}
@keyframes blob3 {
  0%   { transform: translate(0, 0) scale(1); }
  30%  { transform: translate(100px, 120px) scale(1.05); }
  60%  { transform: translate(-140px, -40px) scale(0.92); }
  100% { transform: translate(0, 0) scale(1); }
}
@keyframes blob4 {
  0%   { transform: translate(0, 0) scale(1); }
  20%  { transform: translate(-80px, -100px) scale(1.08); }
  45%  { transform: translate(160px, 30px) scale(0.93); }
  70%  { transform: translate(40px, 150px) scale(1.12); }
  100% { transform: translate(0, 0) scale(1); }
}
@keyframes blob5 {
  0%   { transform: translate(0, 0) scale(1); }
  35%  { transform: translate(90px, -60px) scale(0.95); }
  65%  { transform: translate(-120px, 80px) scale(1.1); }
  100% { transform: translate(0, 0) scale(1); }
}
@keyframes blob6 {
  0%   { transform: translate(0, 0) scale(1); }
  25%  { transform: translate(-60px, 130px) scale(1.06); }
  55%  { transform: translate(130px, -70px) scale(0.9); }
  80%  { transform: translate(-40px, -50px) scale(1.14); }
  100% { transform: translate(0, 0) scale(1); }
}

@keyframes bdr-shift {
  0%,100% { background-position: 0% 50%; }
  50%     { background-position: 100% 50%; }
}
@keyframes fade-up {
  from { opacity:0; transform:translateY(12px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes fade-in {
  from { opacity:0; } to { opacity:1; }
}
@keyframes spring-in {
  0%   { opacity:0; transform:scale(0.96) translateY(-4px); }
  100% { opacity:1; transform:scale(1) translateY(0); }
}
@keyframes slide-r {
  from { opacity:0; transform:translateX(-10px); }
  to   { opacity:1; transform:translateX(0); }
}
@keyframes pulse-dot {
  0%,100% { box-shadow:0 0 0 0 rgba(5,150,105,0.4); }
  50%     { box-shadow:0 0 0 5px rgba(5,150,105,0); }
}
@keyframes shimmer {
  from { transform:translateX(-100%); }
  to   { transform:translateX(220%); }
}
@keyframes spin {
  to { transform:rotate(360deg); }
}
@keyframes fill-bar {
  from { width:0; }
}
@keyframes count-in {
  from { opacity:0; transform:translateY(4px); }
  to   { opacity:1; transform:translateY(0); }
}

/* ── PRECISION GEOMETRY ───────────────────── */
.glow-wrap { position:relative; border-radius:2px; }
.glow-wrap::before {
  content:'';
  position:absolute; inset:-1px; border-radius:3px; z-index:0;
  background:linear-gradient(135deg,var(--accent) 0%,var(--blue) 50%,var(--accent) 100%);
  background-size:200% 200%;
  animation: bdr-shift 4s ease infinite;
  opacity:0.4;
}
.glow-inner {
  position:relative; z-index:1; border-radius:1px;
  background: var(--bg-1);
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.06), 0 20px 40px -20px rgba(0,0,0,0.04);
}

/* ── NAV ──────────────────────────────────── */
.ns-nav {
  position:fixed; top:0; left:0; right:0; z-index:100; height:60px;
  display:flex; align-items:center; gap:4px; padding:0 32px;
  background:rgba(255, 255, 255, 0.8);
  backdrop-filter:blur(16px);
  border-bottom:1px solid var(--bdr);
}
.ns-logo {
  font-family:var(--fd); font-size:18px; font-weight:800;
  letter-spacing:-0.03em; color:var(--t1);
  margin-right:32px; display:flex; align-items:center; gap:10px;
  user-select:none;
}
.ns-logo-mark {
  width:28px; height:28px; border-radius:4px;
  background:var(--accent);
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 4px 12px rgba(79,70,229,0.3);
  flex-shrink:0;
}
.ns-logo .hi { color:var(--accent); }

.ns-tab {
  position:relative; display:flex; align-items:center; gap:8px;
  padding:8px 16px; border-radius:2px;
  font-size:13px; font-weight:600; color:var(--t2);
  cursor:pointer; border:none; background:none;
  font-family:var(--fb); letter-spacing:-0.01em;
  transition:all .15s ease;
}
.ns-tab:hover { color:var(--t1); background:var(--bg-2); }
.ns-tab.on { color:var(--accent); background:var(--acc-dim); }
.ns-tab.on::after {
  content:''; position:absolute; bottom:0; left:0; right:0;
  height:2px; background:var(--accent);
}

.ns-sp { flex:1; }

.ns-usr {
  display:flex; align-items:center; gap:12px;
}
.ns-ava {
  width:32px; height:32px; border-radius:4px;
  background:var(--bg-2);
  border:1px solid var(--bdr);
  display:flex; align-items:center; justify-content:center;
  font-size:10px; font-weight:700; color:var(--accent);
  font-family:var(--fd);
}
.ns-log {
  background:none; border:none; cursor:pointer;
  color:var(--t3); padding:8px; border-radius:4px;
  display:flex; align-items:center;
  transition:all .15s ease;
}
.ns-log:hover { color:var(--red); background:var(--red-dim); }

/* ── BADGE ────────────────────────────────── */
.bdg {
  display:inline-flex; align-items:center; gap:6px;
  padding:4px 10px; border-radius:2px;
  font-size:10px; font-weight:700;
  letter-spacing:.06em; text-transform:uppercase;
  font-family:var(--fd);
}
.bdg.g { background:var(--grn-dim); color:var(--green); border:1px solid rgba(5,150,105,0.1); }
.bdg.a { background:var(--amb-dim); color:var(--amber); border:1px solid rgba(217,119,6,0.1); }
.bdg.r { background:var(--red-dim); color:var(--red);   border:1px solid rgba(220,38,38,0.1); }
.bdg.i { background:var(--acc-dim); color:var(--accent); border:1px solid rgba(79,70,229,0.1); }
.bdg.x { background:var(--bg-2); color:var(--t2); border:1px solid var(--bdr); }

/* ── INPUTS ───────────────────────────────── */
.ns-in {
  width:100%; background:var(--bg-1);
  border:1px solid var(--bdr); border-radius:2px;
  padding:12px 16px; color:var(--t1);
  font-family:var(--fb); font-size:14px; outline:none;
  transition:all .15s ease;
}
.ns-in:focus {
  border-color:var(--accent);
  background:var(--bg-1);
  box-shadow:0 0 0 3px var(--acc-dim);
}
.ns-in::placeholder { color:var(--t3); }

/* ── CARDS ────────────────────────────────── */
.cd  { background:var(--bg-1); border:1px solid var(--bdr); border-radius:2px; padding:24px; box-shadow:0 1px 3px rgba(0,0,0,0.02); }
.cde { background:var(--bg-2); border:1px solid var(--bdr); border-radius:2px; padding:24px; }

/* ── SKELETON ─────────────────────────────── */
.sk {
  border-radius:2px;
  background:linear-gradient(90deg, var(--bg-2) 0%, var(--bg-3) 50%, var(--bg-2) 100%);
  background-size:400px 100%;
  position:relative; overflow:hidden;
}
.sk::after {
  content:''; position:absolute; inset:0;
  background:linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.5) 50%, transparent 100%);
  animation: shimmer 1.6s ease-in-out infinite;
}

.ns-page { margin-top: 60px; animation:fade-in .3s ease; }

/* ── LABEL ────────────────────────────────── */
.lbl {
  display:block; font-size:10px; font-weight:700;
  color:var(--t3); margin-bottom:8px;
  letter-spacing:.1em; text-transform:uppercase;
  font-family:var(--fd);
}
.sec-rule {
  font-size:10px; font-weight:700; color:var(--t2);
  letter-spacing:.15em; text-transform:uppercase;
  font-family:var(--fd); padding-bottom:14px;
  border-bottom:1px solid var(--bdr); margin-bottom:20px;
}
`;

// ── INJECT ───────────────────────────────────────────────────────────────────
function StyleInjector() {
    useEffect(() => {
        const id = "ns2";
        if (!document.getElementById(id)) {
            const el = document.createElement("style");
            el.id = id; el.textContent = CSS;
            document.head.appendChild(el);
        }
        return () => document.getElementById(id)?.remove();
    }, []);
    return null;
}

// ── ICONS ────────────────────────────────────────────────────────────────────
const Ic = {
    Logo: () => <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3 13V7L8 3L13 7V13" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /><path d="M6 13V10H10V13" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
    Monitor: () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" /></svg>,
    Signal: () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>,
    Cap: () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z" /><path d="M6 12v5c3 3 9 3 12 0v-5" /></svg>,
    Arrow: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>,
    Logout: () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>,
    Spin: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ animation: "spin .7s linear infinite" }}><path d="M21 12a9 9 0 11-3.5-7" /></svg>,
};


// ── MOCK DATA (now imported from constants.js) ─────────────────────────────────

// ── FLOATING BLOBS ──────────────────────────────────────────────────────────
// BLOBS is now imported from constants.js

function FloatingBlobs({ isActive }) {
    return (
        <div style={{
            position: "fixed", inset: 0, overflow: "hidden",
            pointerEvents: "none", zIndex: 0,
            opacity: isActive ? 1 : 0.8,
            transition: "opacity 1.5s ease"
        }}>
            <style>{`
                @keyframes sprawl {
                    0%, 100% { border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%; }
                    33%      { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
                    66%      { border-radius: 50% 50% 60% 40% / 40% 60% 50% 60%; }
                }
            `}</style>
            {BLOBS.map((b, i) => (
                <div key={i} style={{
                    position: "absolute",
                    top: b.top,
                    left: b.left,
                    width: b.width,
                    height: b.height,
                    background: `radial-gradient(ellipse at center, ${b.color} 0%, transparent 65%)`,
                    filter: `blur(${isActive ? "20px" : "40px"})`,
                    mixBlendMode: "multiply",
                    animation: `${b.anim} ${b.dur} ease-in-out infinite, sprawl ${b.dur} ease-in-out infinite alternate`,
                    willChange: "transform, border-radius",
                    transition: "filter 1.5s ease"
                }} />
            ))}
        </div>
    );
}

// ── LOGIN ─────────────────────────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
    const [role, setRole] = useState("underwriter");
    const [email, setEmail] = useState("");
    const [pass, setPass] = useState("");
    const [loading, setLoad] = useState(false);
    const [error, setError] = useState("");
    const [ready, setReady] = useState(false);
    const videoRef = useRef(null);

    useEffect(() => { const t = setTimeout(() => setReady(true), 60); return () => clearTimeout(t); }, []);

    const handleVideoEnded = () => {
        if (videoRef.current) {
            videoRef.current.currentTime = 2.0; // Loop strictly from 2nd second to keep flow
            videoRef.current.play();
        }
    };

    const ROLES = [
        { id: "underwriter", label: "Underwriter", Icon: Ic.Monitor },
        { id: "portfolio_manager", label: "Portfolio Manager", Icon: Ic.Signal },
        { id: "student", label: "Student", Icon: Ic.Cap },
    ];
    const DEMO = {
        underwriter: { email: "underwriter@nextstep.com", pass: "uwpass" },
        portfolio_manager: { email: "manager@nextstep.com", pass: "pmpass" },
        student: { email: "priya@example.com", pass: "password123" },
    };

    const submit = async (e) => {
        e.preventDefault();
        setError("");
        setLoad(true);
        try {
            const res = await fetch("http://localhost:8000/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password: pass })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Authentication failed");
            
            // Artificial delay for premium feel as per original design
            setTimeout(() => {
                setLoad(false);
                onLogin(data);
            }, 800);
        } catch (err) {
            setLoad(false);
            setError(err.message === "Failed to fetch" ? "Backend unavailable. Ensure server is running on port 8000." : err.message);
        }
    };

    return (
        <div style={{ position: "relative", minHeight: "100vh", display: "flex", overflow: "hidden" }}>
            
            {/* Left Pane: Branding */}
            <div style={{
                flex: "0 0 45%",
                background: "linear-gradient(145deg, #0F172A 0%, #1E293B 100%)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                padding: "0 80px",
                position: "relative",
                zIndex: 1,
                borderRight: "1px solid rgba(255,255,255,0.05)"
            }}>
                
                <video 
                    ref={videoRef}
                    autoPlay 
                    muted 
                    playsInline 
                    onEnded={handleVideoEnded}
                    style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        zIndex: 0,
                        opacity: 0.5,
                        mixBlendMode: "screen",
                    }}
                >
                    <source src={backgroundVideo} type="video/mp4" />
                </video>

                <div style={{
                    opacity: ready ? 1 : 0,
                    transform: ready ? "translateX(0)" : "translateX(-20px)",
                    transition: "all .8s cubic-bezier(.22,1,.36,1) .2s",
                    position: "relative",
                    zIndex: 2,
                    textAlign: "center", // Center text within the block
                    width: "max-content" // Keep block tight so it anchors to the left padding
                }}>
                    {/* Logo Removed as requested */}
                    <h1 style={{
                        fontFamily: "var(--fd)",
                        fontSize: "72px",
                        fontWeight: 800,
                        color: "#fff",
                        letterSpacing: "-0.04em",
                        lineHeight: 1,
                        marginBottom: 12
                    }}>
                        NextStep
                    </h1>
                    <div style={{
                        fontFamily: "var(--fb)",
                        fontSize: "20px",
                        color: "#94A3B8",
                        fontWeight: 500,
                        letterSpacing: "0.01em"
                    }}>
                        by team <span style={{ color: "#fff", fontWeight: 700 }}>Hello World</span>
                    </div>
                </div>

                {/* Decorative Grid Overlay to blend with Video */}
                <div style={{
                    position: "absolute", inset: 0, opacity: 0.15,
                    backgroundImage: `
                        linear-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255, 255, 255, 0.15) 1px, transparent 1px)
                    `,
                    backgroundSize: "80px 80px", 
                    pointerEvents: "none",
                    zIndex: 1
                }} />
            </div>

            {/* Right Pane: Login Card */}
            <div style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative"
            }}>
                
                {/* Vignette */}
                <div style={{
                    position: "absolute", inset: 0, pointerEvents: "none",
                    background: "radial-gradient(ellipse 80% 80% at 50% 50%, transparent 20%, rgba(248,250,252,0.4) 100%)"
                }} />

                {/* Card */}
                <div style={{
                    position: "relative", zIndex: 10, width: 430,
                    opacity: ready ? 1 : 0,
                    transform: ready ? "translateY(0)" : "translateY(28px)",
                    transition: "opacity .65s cubic-bezier(.22,1,.36,1), transform .65s cubic-bezier(.22,1,.36,1)",
                }}>
                    <div className="glow-wrap">
                        <div className="glow-inner" style={{ padding: "36px 34px 28px" }}>

                            {/* System status */}
                            <div style={{
                                display: "flex", alignItems: "center", justifyContent: "space-between",
                                marginBottom: 28, paddingBottom: 16, borderBottom: "1px solid var(--bdr)",
                                animation: "fade-in .4s ease both .35s", opacity: 0
                            }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                    <div style={{
                                        width: 7, height: 7, borderRadius: "50%", background: "var(--green)",
                                        animation: "pulse-dot 2.2s ease infinite"
                                    }} />
                                    <span style={{
                                        fontFamily: "var(--fm)", fontSize: 10, color: "var(--green)",
                                        letterSpacing: ".1em", textTransform: "uppercase", fontWeight: 500
                                    }}>
                                        System Operational
                                    </span>
                                </div>
                                <span style={{ fontFamily: "var(--fm)", fontSize: 10, color: "var(--t3)", letterSpacing: ".06em" }}>
                                    v1.0.0
                                </span>
                            </div>

                            {/* Mobile Logo (Only visible on small screens - mock) */}
                            <div style={{ textAlign: "center", marginBottom: 30, display: "none" }}>
                                <div style={{ display: "inline-flex", alignItems: "center", gap: 12 }}>
                                    <div className="ns-logo-mark"><Ic.Logo /></div>
                                    <span style={{ fontFamily: "var(--fd)", fontSize: 24, fontWeight: 800, color: "var(--t1)" }}>NextStep</span>
                                </div>
                            </div>

                            {/* Role selector */}
                            <div style={{ marginBottom: 22, animation: "fade-up .4s ease both .22s", opacity: 0 }}>
                                <div style={{
                                    fontSize: 10, color: "var(--t3)", letterSpacing: ".12em",
                                    textTransform: "uppercase", fontFamily: "var(--fd)", fontWeight: 700,
                                    textAlign: "center", marginBottom: 10
                                }}>Sign in as</div>
                                <div style={{
                                    display: "flex", gap: 6, background: "var(--bg-2)",
                                    borderRadius: 2, padding: 4, border: "1px solid var(--bdr)"
                                }}>
                                    {ROLES.map(r => {
                                        const on = role === r.id;
                                        return (
                                            <button key={r.id} onClick={() => setRole(r.id)} style={{
                                                flex: 1, padding: "10px 6px", borderRadius: 1,
                                                border: "none", cursor: "pointer",
                                                display: "flex", flexDirection: "column", alignItems: "center", gap: 5,
                                                fontFamily: "var(--fd)",
                                                background: on ? "var(--accent)" : "transparent",
                                                color: on ? "#fff" : "var(--t3)",
                                                boxShadow: on ? "0 4px 12px rgba(79,70,229,0.25)" : "none",
                                                transition: "all .15s cubic-bezier(.22,1,.36,1)",
                                            }}>
                                                <r.Icon />
                                                <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".02em" }}>{r.label}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Form */}
                            <form onSubmit={submit} style={{ animation: "fade-up .4s ease both .32s", opacity: 0 }}>
                                <div style={{ marginBottom: 13 }}>
                                    <label className="lbl">Email address</label>
                                    <input className="ns-in" type="email" placeholder="you@institution.edu"
                                        value={email} onChange={e => setEmail(e.target.value)} />
                                </div>
                                <div style={{ marginBottom: 20 }}>
                                    <label className="lbl">Password</label>
                                    <input className="ns-in" type="password" placeholder="••••••••"
                                        value={pass} onChange={e => setPass(e.target.value)} />
                                </div>

                                {error && (
                                    <div style={{
                                        marginBottom: 16, padding: "10px 12px", borderRadius: 2,
                                        background: "var(--red-dim)", border: "1px solid rgba(220,38,38,0.2)",
                                        color: "var(--red)", fontSize: 12, fontFamily: "var(--fb)",
                                        animation: "fade-in .3s ease"
                                    }}>
                                        {error}
                                    </div>
                                )}

                                {/* Submit */}
                                <button type="submit" disabled={loading} style={{
                                    width: "100%", height: 50, border: "none", borderRadius: 2, cursor: "pointer",
                                    display: "flex", alignItems: "center", justifyContent: "center", gap: 9,
                                    fontFamily: "var(--fd)", fontSize: 14, fontWeight: 800,
                                    letterSpacing: "-0.01em", color: "#fff", position: "relative", overflow: "hidden",
                                    background: "var(--accent)",
                                    boxShadow: loading ? "none" : "0 8px 24px -6px rgba(79,70,229,0.4), inset 0 1px 0 rgba(255,255,255,0.1)",
                                    transition: "transform .15s, box-shadow .15s",
                                }}
                                    onMouseEnter={e => { if (!loading) { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 12px 28px -6px rgba(79,70,229,0.5), inset 0 1px 0 rgba(255,255,255,0.1)"; } }}
                                    onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 8px 24px -6px rgba(79,70,229,0.4), inset 0 1px 0 rgba(255,255,255,0.1)"; }}>
                                    {!loading && <div style={{
                                        position: "absolute", inset: 0, pointerEvents: "none",
                                        background: "linear-gradient(100deg, transparent 35%, rgba(255,255,255,0.14) 50%, transparent 65%)",
                                        animation: "shimmer 2.8s ease infinite",
                                    }} />}
                                    <span style={{ position: "relative", display: "flex", alignItems: "center", gap: 8 }}>
                                        {loading ? <><Ic.Spin /> Authenticating…</> : <>Access Platform <Ic.Arrow /></>}
                                    </span>
                                </button>

                                <button type="button" onClick={() => { const c = DEMO[role]; setEmail(c.email); setPass(c.pass); }} style={{
                                    display: "block", width: "100%", marginTop: 10, padding: "8px",
                                    background: "none", border: "none", cursor: "pointer",
                                    fontFamily: "var(--fb)", fontSize: 12, color: "var(--t3)", transition: "color .15s",
                                }}
                                    onMouseEnter={e => e.currentTarget.style.color = "var(--t2)"}
                                    onMouseLeave={e => e.currentTarget.style.color = "var(--t3)"}>
                                    Use demo credentials
                                </button>
                            </form>

                            {/* Footer data strip */}
                            <div style={{
                                marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--bdr)",
                                display: "flex", justifyContent: "space-between",
                                animation: "fade-in .4s ease both .5s", opacity: 0
                            }}>
                                {["4 sessions active", "Scoring engine ready", "TenzorX 2026"].map((s, i) => (
                                    <span key={i} style={{
                                        fontFamily: "var(--fm)", fontSize: 9, color: "var(--t3)",
                                        letterSpacing: ".08em", textTransform: "uppercase"
                                    }}>{s}</span>
                                ))}
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ── NAV ───────────────────────────────────────────────────────────────────────
const TABS = {
    underwriter: { label: "Underwriter Console", Icon: Ic.Monitor, roles: ["underwriter"] },
    portfolio: { label: "Portfolio Dashboard", Icon: Ic.Signal, roles: ["portfolio_manager", "underwriter"] },
    student: { label: "Student Dashboard", Icon: Ic.Cap, roles: ["student", "underwriter"] },
};

function NavBar({ user, view, setView, onLogout }) {
    const role = user.role;
    const tabs = Object.entries(TABS).filter(([, t]) => t.roles.includes(role));
    const inits = { underwriter: "UW", portfolio_manager: "PM", student: "PS" }[role] ?? "??";
    const name = user.full_name || role;
    return (
        <nav className="ns-nav">
            <div className="ns-logo">
                <div className="ns-logo-mark"><Ic.Logo /></div>
                Next<span className="hi">Step</span>
            </div>
            {tabs.map(([key, t]) => (
                <button key={key} className={`ns-tab ${view === key ? "on" : ""}`} onClick={() => setView(key)}>
                    <t.Icon />{t.label}
                </button>
            ))}
            <div className="ns-sp" />
            <div className="ns-usr">
                <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "var(--t3)", letterSpacing: ".08em", textTransform: "uppercase", paddingRight: 12, borderRight: "1px solid var(--bdr)" }}>
                    Live · Apr 30 2026
                </span>
                <div className="ns-ava">{inits}</div>
                <span style={{ fontSize: 12, color: "var(--t2)", fontFamily: "var(--fb)" }}>{name}</span>
                <button className="ns-log" onClick={onLogout}><Ic.Logout /></button>
            </div>
        </nav>
    );
}

// ── PLACEHOLDER VIEWS ─────────────────────────────────────────────────────────
// These are intentionally polished stubs — replaced in Chunk 2 & 3

function PlaceholderUnderwriter() {
    const stats = [
        { val: "71", unit: "/100", label: "Repayment Score", color: "var(--green)" },
        { val: "64%", unit: "", label: "6-Month Placement", color: "var(--accent-2)" },
        { val: "$95K", unit: "/yr", label: "Realistic Salary", color: "var(--amber)" },
    ];
    return (
        <div style={{ padding: "32px 40px", maxWidth: 1180, margin: "0 auto" }}>
            <div style={{ marginBottom: 28, animation: "slide-r .4s ease both" }}>
                <div style={{ fontFamily: "var(--fd)", fontSize: 10, color: "var(--t3)", letterSpacing: ".14em", textTransform: "uppercase", marginBottom: 6 }}>Underwriter Console</div>
                <div style={{ fontFamily: "var(--fd)", fontSize: 28, fontWeight: 800, letterSpacing: "-0.04em", color: "var(--t1)" }}>Score a new application</div>
            </div>

            {/* Stat cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 24 }}>
                {stats.map((s, i) => (
                    <div key={i} className="cd" style={{ animation: `fade-up .4s ease both ${i * .07}s`, opacity: 0 }}>
                        <div style={{ display: "flex", alignItems: "baseline", gap: 5, marginBottom: 5 }}>
                            <span style={{ fontFamily: "var(--fd)", fontSize: 34, fontWeight: 800, letterSpacing: "-0.05em", color: s.color, animation: `count-in .5s ease both ${.2 + i * .07}s`, opacity: 0 }}>{s.val}</span>
                            {s.unit && <span style={{ fontSize: 13, color: "var(--t3)", fontFamily: "var(--fd)" }}>{s.unit}</span>}
                        </div>
                        <div style={{ fontSize: 11, color: "var(--t3)", fontFamily: "var(--fd)", letterSpacing: ".06em", textTransform: "uppercase", fontWeight: 700 }}>{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Skeleton form */}
            <div className="cd" style={{ animation: "fade-up .4s ease both .2s", opacity: 0 }}>
                <div className="sec-rule">Application Form · Priya Sharma</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginBottom: 24 }}>
                    {[["Student name", "University", "Program", "GRE Score", "Target Country", "Loan Amount"]].flat().map((f, i) => (
                        <div key={i} style={{ animation: `fade-up .35s ease both ${.28 + i * .05}s`, opacity: 0 }}>
                            <div style={{ height: 10, width: 70, borderRadius: 5, background: "var(--bg-3)", marginBottom: 8 }} />
                            <div className="sk" style={{ height: 44, borderRadius: 10 }} />
                        </div>
                    ))}
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end", animation: "fade-up .4s ease both .58s", opacity: 0 }}>
                    <div style={{
                        height: 48, width: 220, borderRadius: 2, cursor: "default",
                        background: "var(--bg-2)",
                        border: "1px solid var(--bdr)",
                        display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                        fontFamily: "var(--fd)", fontWeight: 800, fontSize: 14, color: "var(--t3)",
                    }}>Score Application <Ic.Arrow /></div>
                </div>
                <p style={{ marginTop: 14, textAlign: "center", fontFamily: "var(--fm)", fontSize: 10, color: "var(--t3)", letterSpacing: ".08em", animation: "fade-in .4s ease both .65s", opacity: 0 }}>
                    ↑ Full scoring engine with animated dial ships in Chunk 2
                </p>
            </div>
        </div>
    );
}

function PlaceholderPortfolio() {
    const rows = [
        { id: "US_MSCS_2024_Q1", program: "MS Computer Science", country: "US", size: 43, base: 74, cur: 70, sev: "AMBER" },
        { id: "UK_MBA_2024_Q2", program: "MBA", country: "UK", size: 28, base: 68, cur: 68, sev: "GREEN" },
        { id: "CA_ENG_2024_Q1", program: "MS Engineering", country: "CA", size: 31, base: 71, cur: 63, sev: "RED" },
    ];
    const sevClr = { GREEN: "transparent", AMBER: "var(--amber)", RED: "var(--red)" };

    return (
        <div style={{ padding: "32px 40px", maxWidth: 1180, margin: "0 auto" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28, animation: "slide-r .4s ease both" }}>
                <div>
                    <div style={{ fontFamily: "var(--fd)", fontSize: 10, color: "var(--t3)", letterSpacing: ".14em", textTransform: "uppercase", marginBottom: 6 }}>Portfolio Dashboard</div>
                    <div style={{ fontFamily: "var(--fd)", fontSize: 28, fontWeight: 800, letterSpacing: "-0.04em", color: "var(--t1)" }}>Cohort Risk Monitor</div>
                </div>
                <div style={{
                    padding: "11px 20px", borderRadius: 2, border: "1px solid var(--accent)",
                    fontFamily: "var(--fd)", fontSize: 13, fontWeight: 700, color: "var(--accent)",
                    cursor: "pointer", background: "var(--acc-dim)", transition: "all .15s",
                }} onMouseEnter={e => e.currentTarget.style.background = "rgba(79,70,229,0.1)"}
                    onMouseLeave={e => e.currentTarget.style.background = "var(--acc-dim)"}>
                    Trigger Re-score →
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 24 }}>
                {[
                    { val: "47", label: "Active Cohorts", clr: "var(--t1)", bd: "var(--bg-3)" },
                    { val: "8", label: "At Risk — AMBER", clr: "var(--amber)", bd: "var(--amber)" },
                    { val: "2", label: "Critical — RED", clr: "var(--red)", bd: "var(--red)" },
                ].map((s, i) => (
                    <div key={i} className="cd" style={{
                        borderLeft: `3px solid ${s.bd}`,
                        animation: `fade-up .4s ease both ${i * .07}s`, opacity: 0,
                    }}>
                        <div style={{ fontFamily: "var(--fd)", fontSize: 36, fontWeight: 800, letterSpacing: "-0.05em", color: s.clr, marginBottom: 5, animation: `count-in .5s ease both ${.2 + i * .07}s`, opacity: 0 }}>{s.val}</div>
                        <div style={{ fontSize: 11, color: "var(--t3)", fontFamily: "var(--fd)", letterSpacing: ".06em", textTransform: "uppercase", fontWeight: 700 }}>{s.label}</div>
                    </div>
                ))}
            </div>

            <div className="cd" style={{ padding: 0, overflow: "hidden", animation: "fade-up .4s ease both .22s", opacity: 0 }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                        <tr style={{ borderBottom: "1px solid var(--bdr)" }}>
                            {["Cohort ID", "Program", "Co.", "Size", "Baseline", "Current", "Δ Delta", "Severity"].map(h => (
                                <th key={h} style={{ padding: "13px 16px", textAlign: "left", fontFamily: "var(--fd)", fontSize: 9, fontWeight: 700, color: "var(--t3)", letterSpacing: ".1em", textTransform: "uppercase" }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((r, i) => {
                            const d = r.cur - r.base;
                            return (
                                <tr key={r.id} style={{
                                    borderBottom: "1px solid var(--bdr)",
                                    borderLeft: `3px solid ${sevClr[r.sev]}`,
                                    cursor: "pointer", transition: "background .15s",
                                    animation: `row-in .35s ease both ${.32 + i * .08}s`, opacity: 0,
                                }}
                                    onMouseEnter={e => e.currentTarget.style.background = "var(--bg-2)"}
                                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                                    <td style={{ padding: "13px 16px", fontFamily: "var(--fm)", fontSize: 11, color: "var(--t2)" }}>{r.id}</td>
                                    <td style={{ padding: "13px 16px", fontSize: 13, color: "var(--t1)", fontWeight: 500 }}>{r.program}</td>
                                    <td style={{ padding: "13px 16px", fontSize: 13, color: "var(--t2)" }}>{r.country}</td>
                                    <td style={{ padding: "13px 16px", fontSize: 13, color: "var(--t2)" }}>{r.size}</td>
                                    <td style={{ padding: "13px 16px", fontFamily: "var(--fd)", fontSize: 15, fontWeight: 700 }}>{r.base}</td>
                                    <td style={{ padding: "13px 16px", fontFamily: "var(--fd)", fontSize: 15, fontWeight: 700 }}>{r.cur}</td>
                                    <td style={{ padding: "13px 16px", fontFamily: "var(--fd)", fontSize: 15, fontWeight: 800, color: d < 0 ? "var(--red)" : "var(--green)" }}>{d > 0 ? "+" : ""}{d}</td>
                                    <td style={{ padding: "13px 16px" }}>
                                        <span className={`bdg ${r.sev === "GREEN" ? "g" : r.sev === "AMBER" ? "a" : "r"}`}>{r.sev}</span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function PlaceholderStudent() {
    return (
        <div style={{ padding: "40px 24px", maxWidth: 740, margin: "0 auto" }}>
            <div style={{ textAlign: "center", marginBottom: 36, animation: "spring-in .6s ease both" }}>
                <div style={{ fontFamily: "var(--fd)", fontSize: 14, color: "var(--t3)", letterSpacing: ".1em", textTransform: "uppercase", marginBottom: 12 }}>Hi, Priya 👋</div>

                {/* Ring */}
                <div style={{ position: "relative", width: 150, height: 150, margin: "0 auto 18px" }}>
                    <svg width="150" height="150" viewBox="0 0 150 150">
                        <circle cx="75" cy="75" r="60" fill="none" stroke="var(--bg-3)" strokeWidth="10" />
                        <circle cx="75" cy="75" r="60" fill="none" stroke="var(--green)" strokeWidth="10"
                            strokeLinecap="round"
                            strokeDasharray={`${2 * Math.PI * 60}`}
                            strokeDashoffset={`${2 * Math.PI * 60 * (1 - 0.71)}`}
                            transform="rotate(-90 75 75)"
                            style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(.22,1,.36,1)" }}
                        />
                    </svg>
                    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                        <span style={{ fontFamily: "var(--fd)", fontSize: 30, fontWeight: 800, color: "var(--green)", letterSpacing: "-0.05em" }}>71%</span>
                        <span style={{ fontSize: 9, color: "var(--t3)", textTransform: "uppercase", letterSpacing: ".1em" }}>Readiness</span>
                    </div>
                </div>

                <div style={{ fontFamily: "var(--fd)", fontSize: 22, fontWeight: 800, letterSpacing: "-0.04em", color: "var(--t1)", marginBottom: 6 }}>On track for 6-month placement</div>
                <div style={{ fontSize: 13, color: "var(--t2)" }}>Complete your next action to reach 75%</div>
            </div>

            {[
                { label: "AWS Cloud Associate Certificate", status: "IN PROGRESS", active: true, pct: 89 },
                { label: "Build a Portfolio Project", status: "ASSIGNED", active: false, pct: 0 },
                { label: "Mock Interview Practice", status: "ASSIGNED", active: false, pct: 0 },
            ].map((a, i) => (
                <div key={i} className="cd" style={{
                    marginBottom: 10,
                    borderLeft: `3px solid ${a.active ? "var(--accent)" : "var(--bg-3)"}`,
                    animation: `fade-up .4s ease both ${.15 + i * .1}s`, opacity: 0,
                }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: a.active ? 10 : 0 }}>
                        <span style={{ fontFamily: "var(--fd)", fontSize: 15, fontWeight: 700, color: "var(--t1)", letterSpacing: "-0.02em" }}>{a.label}</span>
                        <span className={`bdg ${a.active ? "i" : "x"}`}>{a.status}</span>
                    </div>
                    {a.active && (
                        <>
                            <div style={{ fontSize: 11, color: "var(--t3)", marginBottom: 8 }}>14.2h active · 8 days · 11 visits · 📄 Certificate uploaded</div>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 6 }}>
                                <span style={{ color: "var(--t3)" }}>Progress</span>
                                <span style={{ fontFamily: "var(--fm)", color: "var(--green)" }}>{a.pct}%</span>
                            </div>
                            <div style={{ height: 5, borderRadius: 99, background: "var(--bg-3)", overflow: "hidden" }}>
                                <div style={{
                                    height: "100%", width: `${a.pct}%`, borderRadius: 99,
                                    background: "linear-gradient(90deg,var(--accent),var(--green))",
                                    animation: "fill-bar 1.3s cubic-bezier(.22,1,.36,1) both .4s"
                                }} />
                            </div>
                        </>
                    )}
                </div>
            ))}
        </div>
    );
}

// ── APP ───────────────────────────────────────────────────────────────────────
export default function NextStepApp() {
    const [auth, setAuth] = useState(null);
    const [view, setView] = useState("underwriter");

    useEffect(() => {
        const stored = localStorage.getItem("ns_auth");
        if (stored) {
            try {
                const data = JSON.parse(stored);
                setAuth(data);
                setView(data.role === "portfolio_manager" ? "portfolio" : data.role === "student" ? "student" : "underwriter");
            } catch (e) {
                localStorage.removeItem("ns_auth");
            }
        }
    }, []);

    const login = (data) => {
        setAuth(data);
        localStorage.setItem("ns_auth", JSON.stringify(data));
        setView(data.role === "portfolio_manager" ? "portfolio" : data.role === "student" ? "student" : "underwriter");
    };

    const logout = () => {
        setAuth(null);
        localStorage.removeItem("ns_auth");
    };

    return (
        <>
            <StyleInjector />
            <FloatingBlobs isActive={!!auth} />
            {!auth
                ? <LoginScreen onLogin={login} />
                : <>
                    <NavBar user={auth} view={view} setView={setView} onLogout={logout} />
                    <div className="ns-page">
                        {view === "underwriter" && <UnderwriterConsole />}
                        {view === "portfolio" && <PortfolioDashboard />}
                        {view === "student" && <StudentDashboard auth={auth} />}
                    </div>
                </>
            }
        </>
    );
}