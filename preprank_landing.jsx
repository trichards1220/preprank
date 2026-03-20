import { useState, useEffect, useRef } from "react";

const C = {
  crimson: "#C22032",
  brightRed: "#E63946",
  darkRed: "#8B1A2B",
  bloodRed: "#6B0F1A",
  charcoal: "#1A1A1E",
  dark: "#111114",
  darkGray: "#2A2A2E",
  steel: "#3D3D42",
  midGray: "#6B6B73",
  silver: "#9B9BA3",
  lightSilver: "#C8C8CF",
  paleGray: "#E8E8EC",
  offWhite: "#F4F4F6",
  white: "#FFFFFF",
  winGreen: "#1DB954",
  lossRed: "#E63946",
};

function useInView(threshold = 0.15) {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVis(true); obs.disconnect(); } }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);
  return [ref, vis];
}

export default function LandingPage() {
  const [email, setEmail] = useState("");
  const [sports, setSports] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => { setTimeout(() => setLoaded(true), 200); }, []);

  const toggleSport = (s) => setSports(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]);

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif", background: C.dark, color: C.white, minHeight: "100vh", overflowX: "hidden" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Source+Sans+3:wght@400;500;600;700&display=swap');
        @keyframes fadeUp { from { opacity:0; transform:translateY(30px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        @keyframes slideRight { from { opacity:0; transform:translateX(-40px); } to { opacity:1; transform:translateX(0); } }
        @keyframes scaleIn { from { opacity:0; transform:scale(0.9); } to { opacity:1; transform:scale(1); } }
        @keyframes pulseGlow { 0%,100% { box-shadow: 0 0 20px rgba(194,32,50,0.3); } 50% { box-shadow: 0 0 40px rgba(194,32,50,0.5); } }
        @keyframes tickerScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        @keyframes barGrow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
        @keyframes countPulse { 0%,100% { transform:scale(1); } 50% { transform:scale(1.05); } }
        .cta-btn { transition: all 0.25s; cursor:pointer; }
        .cta-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(194,32,50,0.5); background: #D42A3C !important; }
        .sport-chip { transition: all 0.2s; cursor:pointer; user-select:none; }
        .sport-chip:hover { transform: scale(1.05); }
        .feature-card { transition: transform 0.3s, box-shadow 0.3s; }
        .feature-card:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.5); }
        .season-card { transition: all 0.3s; }
        .season-card:hover { transform: scale(1.03); border-color: ${C.crimson} !important; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::selection { background: ${C.crimson}; color: white; }
        a { color: ${C.crimson}; text-decoration: none; }
        a:hover { text-decoration: underline; }
      `}</style>

      {/* ===== NAV ===== */}
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        background: `${C.dark}ee`, backdropFilter: "blur(12px)",
        borderBottom: `1px solid ${C.steel}33`,
        padding: "0 40px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 24, fontWeight: 900, color: C.white }}>PREP</span>
          <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 22, fontWeight: 400, color: C.crimson }}>/</span>
          <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 24, fontWeight: 900, color: C.crimson }}>RANK</span>
        </div>
        <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
          {["Features", "Sports", "Pick'em", "Pricing"].map(t => (
            <a key={t} href={`#${t.toLowerCase().replace("'", "")}`} style={{ fontSize: 13, fontWeight: 600, color: C.silver, letterSpacing: 1, textTransform: "uppercase", textDecoration: "none" }}>{t}</a>
          ))}
          <a href="#waitlist" className="cta-btn" style={{
            padding: "8px 20px", background: C.crimson, color: C.white, borderRadius: 6,
            fontSize: 13, fontWeight: 700, letterSpacing: 1, textDecoration: "none",
          }}>Join Waitlist</a>
        </div>
      </nav>

      {/* ===== HERO ===== */}
      <section style={{
        minHeight: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center",
        padding: "120px 40px 80px", textAlign: "center", position: "relative", overflow: "hidden",
        background: `radial-gradient(ellipse at 50% 30%, ${C.darkRed}18 0%, transparent 60%), linear-gradient(180deg, ${C.dark} 0%, ${C.charcoal} 100%)`,
      }}>
        {/* Decorative lines */}
        <div style={{ position: "absolute", top: 0, left: "15%", width: 1, height: "100%", background: `linear-gradient(180deg, transparent, ${C.steel}22, transparent)` }} />
        <div style={{ position: "absolute", top: 0, left: "85%", width: 1, height: "100%", background: `linear-gradient(180deg, transparent, ${C.steel}22, transparent)` }} />
        <div style={{ position: "absolute", top: "50%", left: 0, width: "100%", height: 1, background: `linear-gradient(90deg, transparent, ${C.crimson}15, transparent)` }} />

        <div style={{ opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(20px)", transition: "all 0.7s 0.2s" }}>
          <div style={{ fontSize: 13, letterSpacing: 6, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 24, fontFamily: "'Source Sans 3'" }}>
            Louisiana High School Sports
          </div>
        </div>

        <div style={{ opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(30px)", transition: "all 0.7s 0.4s" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12, marginBottom: 16 }}>
            <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 90, fontWeight: 900, color: C.white, letterSpacing: -3, lineHeight: 1 }}>PREP</span>
            <div style={{ width: 6, height: 68, background: C.crimson, borderRadius: 3, transform: "skewX(-12deg)" }} />
            <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 90, fontWeight: 900, color: C.crimson, letterSpacing: -3, lineHeight: 1 }}>RANK</span>
          </div>
        </div>

        <div style={{ opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(20px)", transition: "all 0.7s 0.6s" }}>
          <h1 style={{ fontFamily: "'Barlow Condensed'", fontSize: 52, fontWeight: 800, color: C.white, lineHeight: 1.1, marginBottom: 20, maxWidth: 700, letterSpacing: -1 }}>
            Know What's At <span style={{ color: C.crimson }}>Stake</span>
          </h1>
        </div>

        <div style={{ opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(20px)", transition: "all 0.7s 0.8s" }}>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 19, color: C.silver, lineHeight: 1.7, maxWidth: 600, marginBottom: 40 }}>
            The only app that predicts how every LHSAA game affects your team's power rating and playoff chances. Football, basketball, baseball, softball, soccer, volleyball — all 8 sports, all year.
          </p>
        </div>

        <div style={{ opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(20px)", transition: "all 0.7s 1s" }}>
          <a href="#waitlist" className="cta-btn" style={{
            display: "inline-block", padding: "16px 44px", background: C.crimson, color: C.white, borderRadius: 8,
            fontFamily: "'Barlow Condensed'", fontSize: 20, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", textDecoration: "none",
            animation: "pulseGlow 3s infinite 2s",
          }}>Join the Waitlist — Get Early Access</a>
          <div style={{ fontSize: 13, color: C.midGray, marginTop: 12, fontFamily: "'Source Sans 3'" }}>Launching August 2026 · Football Jamboree Week</div>
        </div>

        {/* Scroll indicator */}
        <div style={{ position: "absolute", bottom: 30, left: "50%", transform: "translateX(-50%)", opacity: loaded ? 0.4 : 0, transition: "opacity 1s 2s" }}>
          <div style={{ width: 24, height: 40, border: `2px solid ${C.silver}`, borderRadius: 12, display: "flex", justifyContent: "center", paddingTop: 8 }}>
            <div style={{ width: 3, height: 8, background: C.crimson, borderRadius: 2, animation: "fadeUp 1.5s infinite" }} />
          </div>
        </div>
      </section>

      {/* ===== LIVE TICKER BAR ===== */}
      <div style={{ background: C.charcoal, borderTop: `2px solid ${C.crimson}`, borderBottom: `1px solid ${C.steel}`, padding: "10px 0", overflow: "hidden" }}>
        <div style={{ display: "flex", animation: "tickerScroll 30s linear infinite", whiteSpace: "nowrap" }}>
          {[...Array(2)].map((_, rep) => (
            <div key={rep} style={{ display: "flex", gap: 40, paddingRight: 40 }}>
              {[
                { t: "Ruston #1", pr: "14.40", w: "8-2", c: C.winGreen },
                { t: "Neville #2", pr: "14.20", w: "7-3", c: C.white },
                { t: "Destrehan #3", pr: "14.00", w: "8-2", c: C.winGreen },
                { t: "Denham Springs #4", pr: "13.39", w: "8-2", c: C.white },
                { t: "Central #5", pr: "13.32", w: "8-2", c: C.winGreen },
                { t: "Parkway #6", pr: "13.24", w: "9-1", c: C.white },
                { t: "Terrebonne #9", pr: "13.09", w: "7-3", c: C.lossRed },
                { t: "Zachary #13", pr: "12.48", w: "6-3", c: C.white },
              ].map((s, i) => (
                <div key={`${rep}-${i}`} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, fontFamily: "'Source Sans 3'" }}>
                  <span style={{ fontWeight: 700, color: s.c }}>{s.t}</span>
                  <span style={{ color: C.midGray }}>PR: {s.pr}</span>
                  <span style={{ color: C.steel }}>|</span>
                  <span style={{ color: C.silver }}>{s.w}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* ===== FEATURES ===== */}
      <FeaturesSection />

      {/* ===== WHAT'S AT STAKE DEMO ===== */}
      <StakeDemo />

      {/* ===== SPORTS COVERAGE ===== */}
      <SportsSection />

      {/* ===== PICK'EM ===== */}
      <PickemSection />

      {/* ===== PRICING ===== */}
      <PricingSection />

      {/* ===== WAITLIST ===== */}
      <section id="waitlist" style={{
        padding: "100px 40px", textAlign: "center",
        background: `radial-gradient(ellipse at 50% 50%, ${C.darkRed}15 0%, transparent 60%), ${C.dark}`,
        position: "relative",
      }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${C.crimson}, transparent)` }} />
        <div style={{ maxWidth: 540, margin: "0 auto" }}>
          <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "'Source Sans 3'" }}>Be First</div>
          <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 44, fontWeight: 900, color: C.white, marginBottom: 12, letterSpacing: -1 }}>
            Join the Waitlist
          </h2>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 16, color: C.silver, lineHeight: 1.7, marginBottom: 36 }}>
            Get early access before the August launch. We'll notify you when it's time to download — and beta testers get premium free for the first month.
          </p>

          {submitted ? (
            <div style={{ padding: 32, background: `${C.winGreen}12`, border: `1px solid ${C.winGreen}44`, borderRadius: 12 }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: C.winGreen, fontFamily: "'Barlow Condensed'", marginBottom: 8 }}>You're In.</div>
              <p style={{ fontSize: 15, color: C.silver, fontFamily: "'Source Sans 3'" }}>We'll be in touch before launch. Share with your booster club.</p>
            </div>
          ) : (
            <div>
              <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                <input
                  type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="Your email address"
                  style={{
                    flex: 1, padding: "14px 18px", background: C.darkGray, border: `1px solid ${C.steel}`,
                    borderRadius: 8, color: C.white, fontSize: 16, fontFamily: "'Source Sans 3'", outline: "none",
                  }}
                />
                <button
                  className="cta-btn"
                  onClick={() => { if (email.includes("@")) setSubmitted(true); }}
                  style={{
                    padding: "14px 28px", background: C.crimson, color: C.white, border: "none", borderRadius: 8,
                    fontFamily: "'Barlow Condensed'", fontSize: 16, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase",
                  }}
                >Get Early Access</button>
              </div>

              <div style={{ marginBottom: 8, fontSize: 13, color: C.silver, fontFamily: "'Source Sans 3'", textAlign: "left" }}>
                Which sports do you follow? (select all that apply)
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
                {["Football", "Boys Basketball", "Girls Basketball", "Baseball", "Softball", "Boys Soccer", "Girls Soccer", "Volleyball"].map(s => (
                  <div
                    key={s}
                    className="sport-chip"
                    onClick={() => toggleSport(s)}
                    style={{
                      padding: "8px 16px", borderRadius: 20,
                      background: sports.includes(s) ? C.crimson : C.darkGray,
                      border: `1px solid ${sports.includes(s) ? C.crimson : C.steel}`,
                      color: sports.includes(s) ? C.white : C.silver,
                      fontSize: 13, fontWeight: 600, fontFamily: "'Source Sans 3'",
                    }}
                  >{s}</div>
                ))}
              </div>
              <div style={{ fontSize: 12, color: C.midGray, marginTop: 16, fontFamily: "'Source Sans 3'" }}>No spam. Unsubscribe anytime. We respect your inbox.</div>
            </div>
          )}
        </div>
      </section>

      {/* ===== SPONSORS ===== */}
      <section style={{ padding: "80px 40px", background: C.charcoal, borderTop: `1px solid ${C.steel}` }}>
        <div style={{ maxWidth: 700, margin: "0 auto", textAlign: "center" }}>
          <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "'Source Sans 3'" }}>For Local Businesses</div>
          <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 36, fontWeight: 900, color: C.white, marginBottom: 12 }}>
            Reach Every Family in Your Community
          </h2>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 16, color: C.silver, lineHeight: 1.7, marginBottom: 28 }}>
            Sponsor your local school's team page and put your business on the screen that every parent, student, and fan checks on game night. Hyper-local, high-engagement, measurable.
          </p>
          <a href="mailto:sponsors@preprank.com" className="cta-btn" style={{
            display: "inline-block", padding: "14px 32px", background: "transparent",
            border: `2px solid ${C.crimson}`, color: C.crimson, borderRadius: 8,
            fontFamily: "'Barlow Condensed'", fontSize: 16, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", textDecoration: "none",
          }}>Become a Sponsor</a>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer style={{ padding: "48px 40px", background: C.dark, borderTop: `1px solid ${C.steel}33` }}>
        <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 24 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 8 }}>
              <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 20, fontWeight: 900, color: C.white }}>PREP</span>
              <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 18, fontWeight: 400, color: C.crimson }}>/</span>
              <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 20, fontWeight: 900, color: C.crimson }}>RANK</span>
            </div>
            <div style={{ fontSize: 12, color: C.midGray, fontFamily: "'Source Sans 3'" }}>Know What's At Stake</div>
          </div>
          <div style={{ display: "flex", gap: 24 }}>
            {["Twitter/X", "Facebook", "Instagram"].map(p => (
              <span key={p} style={{ fontSize: 13, color: C.silver, fontFamily: "'Source Sans 3'", cursor: "pointer" }}>{p}</span>
            ))}
          </div>
          <div style={{ fontSize: 12, color: C.midGray, fontFamily: "'Source Sans 3'" }}>
            © 2026 PrepRank. All rights reserved. Not affiliated with LHSAA.
          </div>
        </div>
      </footer>
    </div>
  );
}

// ===== FEATURES SECTION =====
function FeaturesSection() {
  const [ref, vis] = useInView();
  const features = [
    { icon: "⚡", title: "Predict, Don't React", desc: "Our engine simulates thousands of scenarios to show how tonight's game changes the playoff picture — before the game starts." },
    { icon: "📊", title: "Live Power Ratings", desc: "Real-time power rating recalculations as scores come in. Watch your team climb or fall with every result across the state." },
    { icon: "🔔", title: "Smart Push Alerts", desc: "Get notified when any game in the state moves your team's playoff odds. Not just scores — what the score means." },
    { icon: "👨‍👩‍👧‍👦", title: "My Athletes", desc: "Follow all your kids' teams across multiple sports in one dashboard. One app for football, basketball, baseball, everything." },
    { icon: "🔮", title: "What-If Scenarios", desc: "Toggle game outcomes and watch power ratings recalculate in real time. See exactly what your team needs to make playoffs." },
    { icon: "🏆", title: "Pick'em Contests", desc: "Free weekly prediction contests with school vs. school leaderboards. Prove your school knows prep sports best." },
  ];

  return (
    <section id="features" ref={ref} style={{ padding: "100px 40px", background: C.charcoal }}>
      <div style={{ maxWidth: 1000, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 56 }}>
          <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 12, fontFamily: "'Source Sans 3'" }}>Why PrepRank</div>
          <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 44, fontWeight: 900, color: C.white, letterSpacing: -1 }}>
            Every Other App Tells You Who Won.<br />
            <span style={{ color: C.crimson }}>We Tell You What It Means.</span>
          </h2>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
          {features.map((f, i) => (
            <div key={i} className="feature-card" style={{
              padding: 28, borderRadius: 12, background: C.darkGray, border: `1px solid ${C.steel}`,
              opacity: vis ? 1 : 0, transform: vis ? "translateY(0)" : "translateY(24px)",
              transition: `all 0.5s ${i * 0.08}s`,
            }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>{f.icon}</div>
              <h3 style={{ fontFamily: "'Barlow Condensed'", fontSize: 20, fontWeight: 800, color: C.white, marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontFamily: "'Source Sans 3'", fontSize: 14, color: C.silver, lineHeight: 1.7 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ===== WHAT'S AT STAKE DEMO =====
function StakeDemo() {
  const [ref, vis] = useInView();
  return (
    <section ref={ref} style={{
      padding: "100px 40px",
      background: `linear-gradient(180deg, ${C.dark} 0%, ${C.charcoal} 50%, ${C.dark} 100%)`,
      position: "relative",
    }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: `linear-gradient(180deg, transparent, ${C.crimson}44, transparent)` }} />

      <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", gap: 60, alignItems: "center", flexWrap: "wrap" }}>
        {/* Text side */}
        <div style={{ flex: 1, minWidth: 300, opacity: vis ? 1 : 0, transform: vis ? "translateX(0)" : "translateX(-30px)", transition: "all 0.6s" }}>
          <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "'Source Sans 3'" }}>The Difference</div>
          <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 40, fontWeight: 900, color: C.white, lineHeight: 1.1, marginBottom: 20, letterSpacing: -1 }}>
            See the Stakes<br />Before <span style={{ color: C.crimson }}>Kickoff</span>
          </h2>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 16, color: C.silver, lineHeight: 1.8, marginBottom: 20 }}>
            Every game preview shows exactly what each outcome means for your team's power rating, division rank, and playoff probability. Not after the game — before.
          </p>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 14, color: C.midGray, lineHeight: 1.7 }}>
            Works for all 8 sports. Friday night football, Tuesday basketball, Wednesday softball doubleheaders — every game has stakes, and PrepRank quantifies them.
          </p>
        </div>

        {/* Mock card */}
        <div style={{
          width: 360, flexShrink: 0, borderRadius: 12, overflow: "hidden",
          background: C.darkGray, border: `1px solid ${C.steel}`,
          opacity: vis ? 1 : 0, transform: vis ? "translateX(0) scale(1)" : "translateX(30px) scale(0.95)",
          transition: "all 0.6s 0.2s",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        }}>
          <div style={{ background: `linear-gradient(135deg, ${C.steel}, ${C.darkGray})`, padding: "14px 20px", borderBottom: `2px solid ${C.crimson}` }}>
            <div style={{ fontSize: 10, color: C.crimson, letterSpacing: 2, textTransform: "uppercase", fontWeight: 700, marginBottom: 3, fontFamily: "'Source Sans 3'" }}>What's At Stake</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: C.white, fontFamily: "'Barlow Condensed'" }}>Destrehan vs Hahnville</div>
            <div style={{ fontSize: 12, color: C.silver, fontFamily: "'Source Sans 3'" }}>Non-Select Division I · Fri 7:00 PM</div>
          </div>
          <div style={{ padding: 20, background: C.charcoal }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
              <div style={{ background: `${C.winGreen}10`, border: `1px solid ${C.winGreen}33`, borderRadius: 8, padding: 14, textAlign: "center" }}>
                <div style={{ fontSize: 10, color: C.winGreen, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", marginBottom: 6, fontFamily: "'Source Sans 3'" }}>If Destrehan Wins</div>
                <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 36, fontWeight: 900, color: C.winGreen }}>89%</div>
                <div style={{ fontSize: 11, color: C.silver, fontFamily: "'Source Sans 3'" }}>playoff probability</div>
                <div style={{ fontSize: 12, color: C.winGreen, fontWeight: 600, marginTop: 6, fontFamily: "'Source Sans 3'" }}>Rank: #3 → #2</div>
              </div>
              <div style={{ background: `${C.lossRed}10`, border: `1px solid ${C.lossRed}33`, borderRadius: 8, padding: 14, textAlign: "center" }}>
                <div style={{ fontSize: 10, color: C.lossRed, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", marginBottom: 6, fontFamily: "'Source Sans 3'" }}>If Destrehan Loses</div>
                <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 36, fontWeight: 900, color: C.lossRed }}>44%</div>
                <div style={{ fontSize: 11, color: C.silver, fontFamily: "'Source Sans 3'" }}>playoff probability</div>
                <div style={{ fontSize: 12, color: C.lossRed, fontWeight: 600, marginTop: 6, fontFamily: "'Source Sans 3'" }}>Rank: #3 → #7</div>
              </div>
            </div>
            <div style={{
              background: `${C.crimson}10`, border: `1px solid ${C.crimson}22`, borderRadius: 6,
              padding: 10, textAlign: "center", fontFamily: "'Source Sans 3'", fontSize: 12, color: C.silver,
            }}>
              <strong style={{ color: C.white }}>45-point swing</strong> — biggest in Division I this week
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ===== SPORTS SECTION =====
function SportsSection() {
  const [ref, vis] = useInView();
  const seasons = [
    { name: "Fall", months: "Aug – Nov", sports: ["Football", "Volleyball"], color: C.crimson },
    { name: "Winter", months: "Nov – Mar", sports: ["Boys Basketball", "Girls Basketball"], color: C.lightSilver },
    { name: "Spring", months: "Feb – May", sports: ["Baseball", "Softball", "Boys Soccer", "Girls Soccer"], color: C.winGreen },
  ];

  return (
    <section id="sports" ref={ref} style={{ padding: "100px 40px", background: C.dark }}>
      <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "center" }}>
        <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 12, fontFamily: "'Source Sans 3'" }}>Year-Round</div>
        <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 44, fontWeight: 900, color: C.white, marginBottom: 12, letterSpacing: -1 }}>
          8 Sports. 400 Schools. <span style={{ color: C.crimson }}>One App.</span>
        </h2>
        <p style={{ fontFamily: "'Source Sans 3'", fontSize: 16, color: C.silver, lineHeight: 1.7, marginBottom: 48, maxWidth: 600, margin: "0 auto 48px" }}>
          There's always a season. There's always something at stake. PrepRank covers every LHSAA sport that uses power ratings — fall through spring.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
          {seasons.map((s, i) => (
            <div key={i} className="season-card" style={{
              padding: 28, borderRadius: 12, background: C.darkGray, border: `1px solid ${C.steel}`,
              textAlign: "left",
              opacity: vis ? 1 : 0, transform: vis ? "translateY(0)" : "translateY(20px)",
              transition: `all 0.5s ${i * 0.12}s`,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <div style={{ width: 4, height: 32, background: s.color, borderRadius: 2 }} />
                <div>
                  <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 24, fontWeight: 800, color: C.white }}>{s.name}</div>
                  <div style={{ fontSize: 12, color: C.midGray, fontFamily: "'Source Sans 3'" }}>{s.months}</div>
                </div>
              </div>
              {s.sports.map(sp => (
                <div key={sp} style={{ padding: "8px 0", borderBottom: `1px solid ${C.steel}33`, fontSize: 15, color: C.lightSilver, fontFamily: "'Source Sans 3'", fontWeight: 500 }}>{sp}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ===== PICK'EM SECTION =====
function PickemSection() {
  const [ref, vis] = useInView();
  const schools = [
    { name: "St. Paul's", pts: 847, correct: "82%" },
    { name: "Mandeville", pts: 812, correct: "79%" },
    { name: "Covington", pts: 798, correct: "77%" },
    { name: "Fontainebleau", pts: 756, correct: "73%" },
    { name: "Slidell", pts: 741, correct: "72%" },
  ];

  return (
    <section id="pickem" ref={ref} style={{ padding: "100px 40px", background: C.charcoal, position: "relative" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${C.crimson}44, transparent)` }} />
      <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", gap: 60, alignItems: "center", flexWrap: "wrap" }}>
        {/* Leaderboard mock */}
        <div style={{
          width: 340, flexShrink: 0, borderRadius: 12, overflow: "hidden",
          background: C.darkGray, border: `1px solid ${C.steel}`,
          opacity: vis ? 1 : 0, transform: vis ? "translateX(0)" : "translateX(-30px)",
          transition: "all 0.6s",
          boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
        }}>
          <div style={{ padding: "14px 20px", borderBottom: `2px solid ${C.crimson}`, background: `linear-gradient(135deg, ${C.steel}, ${C.darkGray})` }}>
            <div style={{ fontSize: 10, letterSpacing: 2, color: C.crimson, textTransform: "uppercase", fontWeight: 700, fontFamily: "'Source Sans 3'", marginBottom: 2 }}>District 6 Leaderboard</div>
            <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 18, fontWeight: 800, color: C.white }}>Friday Night Pick'em</div>
          </div>
          <div style={{ padding: "4px 0", background: C.charcoal }}>
            {schools.map((s, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", padding: "10px 20px", gap: 12,
                background: i === 0 ? `${C.crimson}10` : "transparent",
                borderLeft: i === 0 ? `3px solid ${C.crimson}` : "3px solid transparent",
                opacity: vis ? 1 : 0, transform: vis ? "translateX(0)" : "translateX(-16px)",
                transition: `all 0.4s ${0.3 + i * 0.08}s`,
              }}>
                <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 20, fontWeight: 800, color: i === 0 ? C.crimson : C.midGray, width: 28 }}>#{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: C.white, fontFamily: "'Source Sans 3'" }}>{s.name}</div>
                  <div style={{ fontSize: 11, color: C.midGray, fontFamily: "'Source Sans 3'" }}>{s.correct} accuracy</div>
                </div>
                <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 18, fontWeight: 800, color: i === 0 ? C.crimson : C.silver }}>{s.pts}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Text */}
        <div style={{ flex: 1, minWidth: 300, opacity: vis ? 1 : 0, transform: vis ? "translateX(0)" : "translateX(30px)", transition: "all 0.6s 0.2s" }}>
          <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "'Source Sans 3'" }}>Free to Play</div>
          <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 40, fontWeight: 900, color: C.white, lineHeight: 1.1, marginBottom: 20, letterSpacing: -1 }}>
            Prove Your School<br />Knows <span style={{ color: C.crimson }}>Best</span>
          </h2>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 16, color: C.silver, lineHeight: 1.8, marginBottom: 20 }}>
            Weekly pick'em contests with school vs. school leaderboards. Pick game winners, earn points, climb the rankings. Your individual score feeds your school's total.
          </p>
          <p style={{ fontFamily: "'Source Sans 3'", fontSize: 14, color: C.midGray, lineHeight: 1.7 }}>
            Free to play, every sport, every week. Top predictors earn badges and bragging rights. Screenshot the leaderboard and show the rival school who's smarter.
          </p>
        </div>
      </div>
    </section>
  );
}

// ===== PRICING SECTION =====
function PricingSection() {
  const [ref, vis] = useInView();
  const tiers = [
    { name: "Free", price: "$0", period: "forever", features: ["Live scores & schedules", "Current power ratings", "Pick'em contests", "School leaderboards", "Basic standings"], cta: "Join Waitlist", primary: false },
    { name: "Season Pass", price: "$24.99", period: "/season", features: ["Everything in Free", "Projected power ratings", "What's At Stake previews", "My Athletes dashboard", "Push notifications", "Ad-free experience"], cta: "Most Popular", primary: true, badge: "MOST POPULAR" },
    { name: "Annual", price: "$49.99", period: "/year", features: ["Everything in Season Pass", "All 8 sports, all year", "What-if scenario builder", "Historical trends", "Less than $1/week"], cta: "Best Value", primary: false, badge: "BEST VALUE" },
  ];

  return (
    <section id="pricing" ref={ref} style={{ padding: "100px 40px", background: C.dark }}>
      <div style={{ maxWidth: 960, margin: "0 auto", textAlign: "center" }}>
        <div style={{ fontSize: 12, letterSpacing: 5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 12, fontFamily: "'Source Sans 3'" }}>Pricing</div>
        <h2 style={{ fontFamily: "'Barlow Condensed'", fontSize: 44, fontWeight: 900, color: C.white, marginBottom: 12, letterSpacing: -1 }}>
          Free to Start. <span style={{ color: C.crimson }}>Worth Every Penny.</span>
        </h2>
        <p style={{ fontFamily: "'Source Sans 3'", fontSize: 16, color: C.silver, marginBottom: 48, maxWidth: 520, margin: "0 auto 48px" }}>
          Scores and pick'em are always free. Upgrade for predictions, scenarios, and the full playoff picture.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, alignItems: "start" }}>
          {tiers.map((t, i) => (
            <div key={i} style={{
              borderRadius: 12, overflow: "hidden",
              background: t.primary ? `linear-gradient(160deg, ${C.darkRed}44, ${C.darkGray})` : C.darkGray,
              border: t.primary ? `2px solid ${C.crimson}` : `1px solid ${C.steel}`,
              position: "relative",
              opacity: vis ? 1 : 0, transform: vis ? "translateY(0)" : "translateY(24px)",
              transition: `all 0.5s ${i * 0.1}s`,
            }}>
              {t.badge && (
                <div style={{ background: C.crimson, padding: "6px 0", textAlign: "center", fontSize: 11, fontWeight: 700, letterSpacing: 2, color: C.white, fontFamily: "'Source Sans 3'" }}>{t.badge}</div>
              )}
              <div style={{ padding: "28px 24px" }}>
                <div style={{ fontFamily: "'Barlow Condensed'", fontSize: 22, fontWeight: 800, color: C.white, marginBottom: 8 }}>{t.name}</div>
                <div style={{ marginBottom: 24 }}>
                  <span style={{ fontFamily: "'Barlow Condensed'", fontSize: 44, fontWeight: 900, color: t.primary ? C.crimson : C.white }}>{t.price}</span>
                  <span style={{ fontSize: 14, color: C.midGray, fontFamily: "'Source Sans 3'" }}>{t.period}</span>
                </div>
                {t.features.map((f, fi) => (
                  <div key={fi} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: fi < t.features.length - 1 ? `1px solid ${C.steel}33` : "none" }}>
                    <span style={{ color: C.crimson, fontSize: 14 }}>✓</span>
                    <span style={{ fontSize: 14, color: C.silver, fontFamily: "'Source Sans 3'" }}>{f}</span>
                  </div>
                ))}
                <a href="#waitlist" className="cta-btn" style={{
                  display: "block", marginTop: 24, padding: "12px 0", textAlign: "center", borderRadius: 8,
                  background: t.primary ? C.crimson : "transparent",
                  border: t.primary ? "none" : `1px solid ${C.steel}`,
                  color: t.primary ? C.white : C.silver,
                  fontFamily: "'Barlow Condensed'", fontSize: 15, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", textDecoration: "none",
                }}>{t.cta}</a>
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 24, fontSize: 13, color: C.midGray, fontFamily: "'Source Sans 3'" }}>
          Coaches get free premium access for any sport. <a href="mailto:coaches@preprank.com">Contact us.</a>
        </div>
      </div>
    </section>
  );
}
