import { useState, useEffect } from "react";

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
  white: "#FFFFFF",
  winGreen: "#1DB954",
  lossRed: "#E63946",
  gold: "#D4A843",
};

const CARD_W = 540;
const CARD_H = 540;

function Logo({ size = 16 }) {
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: size * 0.15 }}>
      <span style={{ fontSize: size, fontWeight: 900, color: C.white, letterSpacing: -size * 0.02, lineHeight: 1 }}>PREP</span>
      <span style={{ fontSize: size * 0.9, fontWeight: 300, color: C.crimson, lineHeight: 1 }}>/</span>
      <span style={{ fontSize: size, fontWeight: 900, color: C.crimson, letterSpacing: -size * 0.02, lineHeight: 1 }}>RANK</span>
    </div>
  );
}

function Watermark() {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 24px", background: C.dark, borderTop: `1px solid ${C.steel}44` }}>
      <Logo size={14} />
      <span style={{ fontSize: 11, color: C.crimson, letterSpacing: 3, fontWeight: 700, textTransform: "uppercase" }}>Know What's At Stake</span>
    </div>
  );
}

export default function SocialTemplates() {
  const [active, setActive] = useState(0);

  const templates = [
    { id: "stake", label: "What's At Stake", platform: "All Platforms" },
    { id: "moves", label: "Power Moves", platform: "Twitter / Facebook" },
    { id: "countdown", label: "Countdown", platform: "All Platforms" },
    { id: "pickem", label: "Pick'em Results", platform: "Instagram / Twitter" },
    { id: "awareness", label: "Brand Awareness", platform: "Instagram / Facebook" },
  ];

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif", background: C.dark, minHeight: "100vh", color: C.white }}>
      <style>{`
        @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
        .tmpl-btn { transition: all 0.2s; cursor: pointer; }
        .tmpl-btn:hover { background: ${C.steel} !important; }
      `}</style>

      {/* Header */}
      <div style={{ padding: "32px 40px 20px", borderBottom: `1px solid ${C.steel}33` }}>
        <div style={{ fontSize: 11, letterSpacing: 4, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>Social Media Templates</div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
          <Logo size={28} />
        </div>
        <div style={{ fontSize: 13, color: C.silver, marginTop: 8 }}>5 branded templates · Ready to post or drop into Canva · Real 2025 LHSAA data</div>
      </div>

      {/* Template selector */}
      <div style={{ display: "flex", gap: 0, padding: "0 40px", background: C.charcoal, borderBottom: `1px solid ${C.steel}33`, overflowX: "auto" }}>
        {templates.map((t, i) => (
          <button key={i} className="tmpl-btn" onClick={() => setActive(i)} style={{
            padding: "14px 20px", border: "none", background: "transparent", whiteSpace: "nowrap",
            fontSize: 12, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase",
            color: active === i ? C.white : C.midGray,
            borderBottom: active === i ? `3px solid ${C.crimson}` : "3px solid transparent",
          }}>{t.label}</button>
        ))}
      </div>

      {/* Template display */}
      <div style={{ padding: "40px", display: "flex", gap: 40, alignItems: "flex-start", flexWrap: "wrap" }} key={active}>
        {/* Template card */}
        <div style={{ animation: "fadeUp 0.4s both" }}>
          {active === 0 && <WhatsAtStakeCard />}
          {active === 1 && <PowerMovesCard />}
          {active === 2 && <CountdownCard />}
          {active === 3 && <PickemResultsCard />}
          {active === 4 && <AwarenessCard />}
        </div>

        {/* Info panel */}
        <div style={{ flex: 1, minWidth: 260, animation: "fadeUp 0.4s 0.1s both" }}>
          <div style={{ fontSize: 10, letterSpacing: 2, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>{templates[active].platform}</div>
          <h3 style={{ fontSize: 24, fontWeight: 900, color: C.white, marginBottom: 12 }}>{templates[active].label}</h3>

          {active === 0 && <TemplateInfo
            when="Thursday (preview) & Friday (game day)"
            desc="The signature content piece. Shows exactly what's at stake for a marquee matchup with win/loss playoff probability. This is the card parents screenshot and post to booster group chats."
            notes={[
              "Swap matchup data weekly — pick the game with the biggest probability swing",
              "Works for ALL sports, not just football. Tuesday basketball, Wednesday softball — same format",
              "Sponsor logo placement: bottom-right corner next to the PrepRank watermark",
              "Size: 1080×1080 (Instagram square) or 1200×675 (Twitter/Facebook landscape)",
            ]}
          />}
          {active === 1 && <TemplateInfo
            when="Saturday/Sunday (weekend recap) or Monday"
            desc="Weekly recap showing the biggest power rating movers — who climbed, who fell, and by how much. Creates FOMO for people not using the app yet. The red/green arrows make it instantly scannable."
            notes={[
              "Pull data from actual week's results — biggest climbers and biggest fallers",
              "Tag schools' official accounts when posting for engagement",
              "Rotate between divisions week to week (Non-Select Div I one week, Select Div I the next)",
              "Sponsor placement: 'Presented by [Sponsor]' line below the title",
            ]}
          />}
          {active === 2 && <TemplateInfo
            when="Daily during the 2 weeks before launch"
            desc="Pre-launch countdown building anticipation. Updates the number daily. The sport icons rotating across the bottom reinforce all-8-sports coverage. Drives waitlist signups."
            notes={[
              "Change the number daily. Post at the same time each day for consistency.",
              "Add a different 'feature teaser' line each day (predictions, pick'em, My Athletes, etc.)",
              "CTA always points to the waitlist: 'preprank.com' or 'Link in bio'",
              "On Day 1, swap to a 'WE'RE LIVE' version with App Store / Play Store badges",
            ]}
          />}
          {active === 3 && <TemplateInfo
            when="Saturday morning (after Friday night games)"
            desc="Pick'em contest results showing the school leaderboard. This is the card students screenshot and share to Instagram stories. Every share carries the PrepRank brand to their followers."
            notes={[
              "Update weekly with actual contest results",
              "Tag the winning school's account and top individual predictor",
              "Include sponsor: 'The [Sponsor] Friday Night Pick'em' title treatment",
              "Create an Instagram Story version (1080×1920) in addition to the square format",
            ]}
          />}
          {active === 4 && <TemplateInfo
            when="Pre-launch awareness + ongoing brand building"
            desc="General brand card that communicates the core value prop. Works as a pinned post, profile header, or evergreen content. The seasonal sport rotation at the bottom sells year-round coverage."
            notes={[
              "Use as a pinned post on Twitter and Facebook from Day 1",
              "Works as an Instagram carousel slide 1 (followed by feature breakdowns)",
              "Swap the subheadline seasonally: football focus in fall, basketball in winter, baseball in spring",
              "No sponsor placement on this one — keep it pure brand",
            ]}
          />}
        </div>
      </div>
    </div>
  );
}

function TemplateInfo({ when, desc, notes }) {
  return (
    <div>
      <div style={{ padding: "10px 14px", background: C.darkGray, borderRadius: 8, border: `1px solid ${C.steel}`, marginBottom: 16 }}>
        <div style={{ fontSize: 10, color: C.crimson, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", marginBottom: 4 }}>When to Post</div>
        <div style={{ fontSize: 14, color: C.white, fontWeight: 600 }}>{when}</div>
      </div>
      <p style={{ fontSize: 14, color: C.silver, lineHeight: 1.7, marginBottom: 20 }}>{desc}</p>
      <div style={{ fontSize: 10, color: C.crimson, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 }}>Production Notes</div>
      {notes.map((n, i) => (
        <div key={i} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          <span style={{ color: C.crimson, fontSize: 12, lineHeight: 1.6 }}>•</span>
          <span style={{ fontSize: 13, color: C.lightSilver, lineHeight: 1.6 }}>{n}</span>
        </div>
      ))}
    </div>
  );
}


// ====================================================================
// TEMPLATE 1: WHAT'S AT STAKE
// ====================================================================
function WhatsAtStakeCard() {
  return (
    <div style={{
      width: CARD_W, borderRadius: 12, overflow: "hidden",
      background: C.charcoal, boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
      border: `1px solid ${C.steel}`,
    }}>
      {/* Top accent */}
      <div style={{ height: 4, background: `linear-gradient(90deg, ${C.crimson}, ${C.darkRed}, transparent)` }} />

      {/* Header */}
      <div style={{ padding: "20px 24px 16px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: 3, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 4 }}>What's At Stake · Week 8</div>
          <div style={{ fontSize: 11, color: C.silver }}>Select Division I · Football</div>
        </div>
        <Logo size={14} />
      </div>

      {/* Matchup */}
      <div style={{ padding: "0 24px", textAlign: "center" }}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 28, padding: "12px 0" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 900, color: C.white }}>Edna Karr</div>
            <div style={{ fontSize: 13, color: C.silver }}>10-0 · #1 · PR 15.82</div>
          </div>
          <div style={{
            width: 44, height: 44, borderRadius: 22, border: `2px solid ${C.crimson}`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 14, fontWeight: 900, color: C.crimson, letterSpacing: 1,
          }}>VS</div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 900, color: C.white }}>St. Paul's</div>
            <div style={{ fontSize: 13, color: C.silver }}>8-4 · #9 · PR 13.13</div>
          </div>
        </div>
      </div>

      {/* Win/Loss outcomes */}
      <div style={{ padding: "12px 24px 0", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div style={{ background: `${C.winGreen}10`, border: `1px solid ${C.winGreen}33`, borderRadius: 10, padding: 18, textAlign: "center" }}>
          <div style={{ fontSize: 10, color: C.winGreen, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>If St. Paul's Wins</div>
          <div style={{ fontSize: 52, fontWeight: 900, color: C.winGreen, lineHeight: 1 }}>76%</div>
          <div style={{ fontSize: 12, color: C.silver, marginTop: 4 }}>playoff probability</div>
          <div style={{ marginTop: 10, display: "flex", justifyContent: "center", gap: 16 }}>
            <div>
              <div style={{ fontSize: 9, color: C.midGray, textTransform: "uppercase", letterSpacing: 1 }}>Rank</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: C.winGreen }}>#9 → #5</div>
            </div>
            <div>
              <div style={{ fontSize: 9, color: C.midGray, textTransform: "uppercase", letterSpacing: 1 }}>Rating</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: C.winGreen }}>13.13 → 13.87</div>
            </div>
          </div>
        </div>
        <div style={{ background: `${C.lossRed}10`, border: `1px solid ${C.lossRed}33`, borderRadius: 10, padding: 18, textAlign: "center" }}>
          <div style={{ fontSize: 10, color: C.lossRed, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>If St. Paul's Loses</div>
          <div style={{ fontSize: 52, fontWeight: 900, color: C.lossRed, lineHeight: 1 }}>28%</div>
          <div style={{ fontSize: 12, color: C.silver, marginTop: 4 }}>playoff probability</div>
          <div style={{ marginTop: 10, display: "flex", justifyContent: "center", gap: 16 }}>
            <div>
              <div style={{ fontSize: 9, color: C.midGray, textTransform: "uppercase", letterSpacing: 1 }}>Rank</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: C.lossRed }}>#9 → #14</div>
            </div>
            <div>
              <div style={{ fontSize: 9, color: C.midGray, textTransform: "uppercase", letterSpacing: 1 }}>Rating</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: C.lossRed }}>13.13 → 12.41</div>
            </div>
          </div>
        </div>
      </div>

      {/* Swing callout */}
      <div style={{ padding: "14px 24px 0", textAlign: "center" }}>
        <div style={{
          display: "inline-block", padding: "8px 20px", background: `${C.crimson}15`,
          border: `1px solid ${C.crimson}33`, borderRadius: 20,
          fontSize: 13, fontWeight: 700, color: C.white,
        }}>
          ⚡ <strong style={{ color: C.crimson }}>48-point swing</strong> — biggest in Select Div I this week
        </div>
      </div>

      <div style={{ height: 16 }} />
      <Watermark />
    </div>
  );
}


// ====================================================================
// TEMPLATE 2: POWER MOVES
// ====================================================================
function PowerMovesCard() {
  const movers = [
    { team: "St. Paul's", from: 9, to: 5, dir: "up", delta: "+0.74", pr: "13.87", reason: "Beat Rummel 24-17" },
    { team: "Alexandria", from: 7, to: 4, dir: "up", delta: "+0.61", pr: "14.54", reason: "Beat John Curtis 31-14" },
    { team: "Tioga", from: 6, to: 3, dir: "up", delta: "+0.55", pr: "14.03", reason: "Beat St. Thomas More 28-7" },
    { team: "Evangel", from: 5, to: 8, dir: "down", delta: "-0.52", pr: "12.78", reason: "Lost to Catholic-BR 14-35" },
    { team: "John Curtis", from: 4, to: 7, dir: "down", delta: "-0.48", pr: "12.96", reason: "Lost to Alexandria 14-31" },
    { team: "Rummel", from: 8, to: 11, dir: "down", delta: "-0.44", pr: "12.34", reason: "Lost to St. Paul's 17-24" },
  ];

  return (
    <div style={{
      width: CARD_W, borderRadius: 12, overflow: "hidden",
      background: C.charcoal, boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
      border: `1px solid ${C.steel}`,
    }}>
      <div style={{ height: 4, background: `linear-gradient(90deg, ${C.crimson}, ${C.darkRed}, transparent)` }} />

      <div style={{ padding: "20px 24px 12px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: 3, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 4 }}>Power Moves · Week 8</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: C.white }}>Select Division I</div>
          <div style={{ fontSize: 12, color: C.silver }}>Biggest movers this week</div>
        </div>
        <Logo size={14} />
      </div>

      <div style={{ padding: "0 24px" }}>
        {/* Risers */}
        <div style={{ fontSize: 9, letterSpacing: 2, color: C.winGreen, textTransform: "uppercase", fontWeight: 700, marginBottom: 8, marginTop: 4 }}>▲ Rising</div>
        {movers.filter(m => m.dir === "up").map((m, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", padding: "10px 12px", marginBottom: 6,
            background: `${C.winGreen}08`, borderRadius: 8, border: `1px solid ${C.winGreen}22`,
          }}>
            <div style={{ width: 50, textAlign: "center", marginRight: 12 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
                <span style={{ fontSize: 14, color: C.midGray, fontWeight: 600 }}>#{m.from}</span>
                <span style={{ fontSize: 10, color: C.winGreen }}>→</span>
                <span style={{ fontSize: 16, color: C.winGreen, fontWeight: 900 }}>#{m.to}</span>
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 15, fontWeight: 800, color: C.white }}>{m.team}</div>
              <div style={{ fontSize: 10, color: C.silver }}>{m.reason}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 16, fontWeight: 900, color: C.winGreen }}>{m.delta}</div>
              <div style={{ fontSize: 10, color: C.midGray }}>PR: {m.pr}</div>
            </div>
          </div>
        ))}

        {/* Fallers */}
        <div style={{ fontSize: 9, letterSpacing: 2, color: C.lossRed, textTransform: "uppercase", fontWeight: 700, marginBottom: 8, marginTop: 14 }}>▼ Falling</div>
        {movers.filter(m => m.dir === "down").map((m, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", padding: "10px 12px", marginBottom: 6,
            background: `${C.lossRed}08`, borderRadius: 8, border: `1px solid ${C.lossRed}22`,
          }}>
            <div style={{ width: 50, textAlign: "center", marginRight: 12 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
                <span style={{ fontSize: 14, color: C.midGray, fontWeight: 600 }}>#{m.from}</span>
                <span style={{ fontSize: 10, color: C.lossRed }}>→</span>
                <span style={{ fontSize: 16, color: C.lossRed, fontWeight: 900 }}>#{m.to}</span>
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 15, fontWeight: 800, color: C.white }}>{m.team}</div>
              <div style={{ fontSize: 10, color: C.silver }}>{m.reason}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 16, fontWeight: 900, color: C.lossRed }}>{m.delta}</div>
              <div style={{ fontSize: 10, color: C.midGray }}>PR: {m.pr}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ height: 12 }} />
      <Watermark />
    </div>
  );
}


// ====================================================================
// TEMPLATE 3: COUNTDOWN
// ====================================================================
function CountdownCard() {
  const [pulse, setPulse] = useState(false);
  useEffect(() => {
    const t = setInterval(() => setPulse(p => !p), 1500);
    return () => clearInterval(t);
  }, []);

  return (
    <div style={{
      width: CARD_W, height: CARD_W, borderRadius: 12, overflow: "hidden",
      background: `radial-gradient(circle at 50% 40%, ${C.darkRed}30 0%, ${C.charcoal} 60%, ${C.dark} 100%)`,
      boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
      border: `1px solid ${C.steel}`,
      display: "flex", flexDirection: "column", justifyContent: "space-between",
      position: "relative",
    }}>
      {/* Decorative elements */}
      <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: 300, height: 300, borderRadius: "50%", border: `1px solid ${C.crimson}15` }} />
      <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: 220, height: 220, borderRadius: "50%", border: `1px solid ${C.crimson}10` }} />

      <div style={{ height: 4, background: `linear-gradient(90deg, ${C.crimson}, ${C.darkRed}, transparent)` }} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", position: "relative", zIndex: 2 }}>
        <Logo size={20} />
        <div style={{ fontSize: 11, letterSpacing: 4, color: C.silver, textTransform: "uppercase", marginTop: 20, fontWeight: 600 }}>Launching In</div>
        <div style={{
          fontSize: 140, fontWeight: 900, color: C.white, lineHeight: 1,
          marginTop: 4,
          textShadow: `0 0 60px ${C.crimson}40`,
          opacity: pulse ? 1 : 0.85, transition: "opacity 0.8s",
        }}>14</div>
        <div style={{ fontSize: 22, fontWeight: 700, color: C.crimson, letterSpacing: 6, textTransform: "uppercase", marginTop: -4 }}>Days</div>

        <div style={{ marginTop: 24, padding: "10px 24px", background: `${C.white}08`, borderRadius: 20, border: `1px solid ${C.steel}44` }}>
          <div style={{ fontSize: 13, color: C.lightSilver, textAlign: "center" }}>
            🏈 🏀 ⚾ 🥎 ⚽ 🏐 — All 8 sports, one app
          </div>
        </div>

        <div style={{ marginTop: 16, fontSize: 14, color: C.silver, fontWeight: 600 }}>
          preprank.com · Join the waitlist
        </div>
      </div>

      <Watermark />
    </div>
  );
}


// ====================================================================
// TEMPLATE 4: PICK'EM RESULTS
// ====================================================================
function PickemResultsCard() {
  return (
    <div style={{
      width: CARD_W, borderRadius: 12, overflow: "hidden",
      background: C.charcoal, boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
      border: `1px solid ${C.steel}`,
    }}>
      <div style={{ height: 4, background: `linear-gradient(90deg, ${C.crimson}, ${C.darkRed}, transparent)` }} />

      <div style={{ padding: "20px 24px 12px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: 3, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 4 }}>Pick'em Results · Week 8</div>
          <div style={{ fontSize: 22, fontWeight: 900, color: C.white }}>District 9 School Leaderboard</div>
          <div style={{ fontSize: 12, color: C.silver }}>4,847 total picks this week</div>
        </div>
        <Logo size={14} />
      </div>

      <div style={{ padding: "8px 24px" }}>
        {[
          { r: 1, name: "St. Paul's", pts: 2847, acc: "78%", pickers: 142, trophy: true },
          { r: 2, name: "Abp. Rummel", pts: 2712, acc: "75%", pickers: 128 },
          { r: 3, name: "Edna Karr", pts: 2698, acc: "74%", pickers: 156 },
          { r: 4, name: "Acadiana", pts: 2541, acc: "71%", pickers: 98 },
          { r: 5, name: "Alexandria", pts: 2480, acc: "69%", pickers: 87 },
        ].map((s, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", padding: "12px 14px", marginBottom: 6,
            background: i === 0 ? `${C.crimson}12` : C.darkGray,
            borderRadius: 10,
            border: i === 0 ? `1px solid ${C.crimson}44` : `1px solid ${C.steel}`,
            borderLeft: i === 0 ? `4px solid ${C.crimson}` : `4px solid transparent`,
          }}>
            <div style={{ fontSize: 24, fontWeight: 900, color: i === 0 ? C.crimson : C.midGray, width: 36 }}>
              {s.trophy ? "🏆" : `#${s.r}`}
            </div>
            <div style={{ flex: 1, marginLeft: 4 }}>
              <div style={{ fontSize: 17, fontWeight: 800, color: C.white }}>{s.name}</div>
              <div style={{ fontSize: 11, color: C.silver }}>{s.pickers} students · {s.acc} accuracy</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 22, fontWeight: 900, color: i === 0 ? C.crimson : C.silver }}>{s.pts.toLocaleString()}</div>
              <div style={{ fontSize: 10, color: C.midGray }}>points</div>
            </div>
          </div>
        ))}
      </div>

      {/* Top predictor callout */}
      <div style={{ padding: "4px 24px 0" }}>
        <div style={{
          padding: "10px 16px", background: `${C.gold}10`, border: `1px solid ${C.gold}33`,
          borderRadius: 8, display: "flex", alignItems: "center", gap: 10,
        }}>
          <span style={{ fontSize: 24 }}>🎯</span>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.white }}>Top Predictor: <span style={{ color: C.gold }}>@wolf_fan22</span></div>
            <div style={{ fontSize: 11, color: C.silver }}>12/12 correct · St. Paul's · Perfect week!</div>
          </div>
        </div>
      </div>

      <div style={{ height: 14 }} />
      <Watermark />
    </div>
  );
}


// ====================================================================
// TEMPLATE 5: BRAND AWARENESS
// ====================================================================
function AwarenessCard() {
  return (
    <div style={{
      width: CARD_W, height: CARD_W, borderRadius: 12, overflow: "hidden",
      background: `radial-gradient(ellipse at 50% 30%, ${C.darkRed}20 0%, ${C.charcoal} 50%, ${C.dark} 100%)`,
      boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
      border: `1px solid ${C.steel}`,
      display: "flex", flexDirection: "column",
      position: "relative",
    }}>
      {/* Decorative lines */}
      <div style={{ position: "absolute", top: 0, left: "20%", width: 1, height: "100%", background: `linear-gradient(180deg, transparent, ${C.steel}15, transparent)` }} />
      <div style={{ position: "absolute", top: 0, left: "80%", width: 1, height: "100%", background: `linear-gradient(180deg, transparent, ${C.steel}15, transparent)` }} />
      <div style={{ position: "absolute", left: 0, top: "45%", width: "100%", height: 1, background: `linear-gradient(90deg, transparent, ${C.crimson}10, transparent)` }} />

      <div style={{ height: 4, background: `linear-gradient(90deg, ${C.crimson}, ${C.darkRed}, transparent)` }} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 40px", textAlign: "center", position: "relative", zIndex: 2 }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 28 }}>
          <span style={{ fontSize: 52, fontWeight: 900, color: C.white, letterSpacing: -2 }}>PREP</span>
          <div style={{ width: 5, height: 40, background: C.crimson, borderRadius: 2, transform: "skewX(-12deg)" }} />
          <span style={{ fontSize: 52, fontWeight: 900, color: C.crimson, letterSpacing: -2 }}>RANK</span>
        </div>

        {/* Headline */}
        <div style={{ fontSize: 32, fontWeight: 900, color: C.white, lineHeight: 1.15, marginBottom: 12, letterSpacing: -0.5 }}>
          Know What's At <span style={{ color: C.crimson }}>Stake</span>
        </div>

        <div style={{ fontSize: 15, color: C.silver, lineHeight: 1.7, marginBottom: 28, maxWidth: 380 }}>
          The only app that predicts how every LHSAA game affects your team's playoff chances. Before the game starts.
        </div>

        {/* Sport pills */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center", maxWidth: 400 }}>
          {[
            { s: "Football", e: "🏈" }, { s: "Basketball", e: "🏀" }, { s: "Baseball", e: "⚾" },
            { s: "Softball", e: "🥎" }, { s: "Soccer", e: "⚽" }, { s: "Volleyball", e: "🏐" },
          ].map(sp => (
            <div key={sp.s} style={{
              padding: "6px 14px", borderRadius: 16, background: `${C.white}08`,
              border: `1px solid ${C.steel}`, fontSize: 12, color: C.lightSilver, fontWeight: 500,
              display: "flex", alignItems: "center", gap: 5,
            }}>
              <span>{sp.e}</span> {sp.s}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 24, fontSize: 14, color: C.midGray, fontWeight: 600 }}>
          All 8 sports · 400 schools · Year-round
        </div>
      </div>

      <Watermark />
    </div>
  );
}
