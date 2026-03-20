import { useState } from "react";

const C = {
  crimson: "#C22032",
  brightRed: "#E63946",
  darkRed: "#8B1A2B",
  charcoal: "#1A1A1E",
  dark: "#111114",
  darkGray: "#2A2A2E",
  steel: "#3D3D42",
  midGray: "#6B6B73",
  silver: "#9B9BA3",
  lightSilver: "#C8C8CF",
  paleGray: "#E8E8EC",
  white: "#FFFFFF",
  winGreen: "#1DB954",
  lossRed: "#E63946",
};

const PHONE_W = 300;
const PHONE_H = 620;

function PhoneFrame({ children, caption, subcaption }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16, flexShrink: 0 }}>
      {/* Caption above phone */}
      <div style={{ textAlign: "center", maxWidth: PHONE_W }}>
        <div style={{ fontFamily: "'Segoe UI'", fontSize: 18, fontWeight: 800, color: C.white, lineHeight: 1.2, marginBottom: 4 }}>{caption}</div>
        {subcaption && <div style={{ fontFamily: "'Segoe UI'", fontSize: 12, color: C.silver, lineHeight: 1.4 }}>{subcaption}</div>}
      </div>
      {/* Phone */}
      <div style={{
        width: PHONE_W, height: PHONE_H, borderRadius: 36, background: "#000",
        padding: 8, position: "relative",
        boxShadow: "0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.08)",
      }}>
        <div style={{
          width: "100%", height: "100%", borderRadius: 28, overflow: "hidden",
          background: C.charcoal, position: "relative",
        }}>
          {/* Status bar */}
          <div style={{
            height: 44, display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "0 20px", background: C.dark, position: "relative", zIndex: 2,
          }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: C.white }}>9:41</span>
            <div style={{ position: "absolute", left: "50%", transform: "translateX(-50%)", top: 0, width: 100, height: 28, background: "#000", borderRadius: "0 0 16px 16px" }} />
            <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
              <div style={{ width: 16, height: 10, border: `1px solid ${C.white}`, borderRadius: 2, position: "relative" }}>
                <div style={{ position: "absolute", left: 1, top: 1, bottom: 1, width: "70%", background: C.white, borderRadius: 1 }} />
              </div>
            </div>
          </div>
          {/* Content */}
          <div style={{ height: PHONE_H - 16 - 44, overflow: "hidden" }}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

function AppNav({ title, subtitle }) {
  return (
    <div style={{ background: C.dark, padding: "10px 16px 10px", borderBottom: `1px solid ${C.steel}44` }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
          <span style={{ fontSize: 16, fontWeight: 900, color: C.white }}>PREP</span>
          <span style={{ fontSize: 14, fontWeight: 300, color: C.crimson }}>/</span>
          <span style={{ fontSize: 16, fontWeight: 900, color: C.crimson }}>RANK</span>
        </div>
        <div style={{ width: 24, height: 24, borderRadius: 12, background: C.steel, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 10, color: C.silver }}>👤</span>
        </div>
      </div>
      {title && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 8, letterSpacing: 2, color: C.crimson, textTransform: "uppercase", fontWeight: 700 }}>{subtitle || ""}</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: C.white }}>{title}</div>
        </div>
      )}
    </div>
  );
}

function TabBar({ active = 0 }) {
  const tabs = ["Home", "Rankings", "My Athletes", "Pick'em", "More"];
  const icons = ["🏠", "📊", "⭐", "🏆", "⋯"];
  return (
    <div style={{
      position: "absolute", bottom: 0, left: 0, right: 0, height: 50,
      background: C.dark, borderTop: `1px solid ${C.steel}44`,
      display: "flex", alignItems: "center", justifyContent: "space-around", zIndex: 5,
    }}>
      {tabs.map((t, i) => (
        <div key={i} style={{ textAlign: "center" }}>
          <div style={{ fontSize: 16 }}>{icons[i]}</div>
          <div style={{ fontSize: 8, color: i === active ? C.crimson : C.midGray, fontWeight: i === active ? 700 : 400, marginTop: 1 }}>{t}</div>
        </div>
      ))}
    </div>
  );
}

export default function AppScreenshots() {
  const [current, setCurrent] = useState(0);

  const screenshots = [
    { caption: "See What Every Game Means", subcaption: "Before kickoff, know the stakes" },
    { caption: "All Your Teams. One Dashboard.", subcaption: "Football, basketball, softball — all in one place" },
    { caption: "Never Miss a Playoff Shift", subcaption: "Real-time alerts when results change your odds" },
    { caption: "Track the Entire Division", subcaption: "Live power ratings and projected playoff seedings" },
    { caption: "Compete With Your School", subcaption: "Free pick'em contests with school leaderboards" },
    { caption: "Build Your Own Scenarios", subcaption: "Toggle outcomes. Watch ratings recalculate." },
  ];

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif", background: C.dark, minHeight: "100vh", color: C.white }}>
      <style>{`
        .dot { transition: all 0.3s; cursor: pointer; }
        .dot:hover { background: ${C.crimson} !important; }
        .scroll-container { scroll-behavior: smooth; }
        .scroll-container::-webkit-scrollbar { display: none; }
      `}</style>

      {/* Header */}
      <div style={{ padding: "32px 40px 20px", textAlign: "center" }}>
        <div style={{ fontSize: 11, letterSpacing: 4, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>App Store Screenshots</div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, marginBottom: 4 }}>
          <span style={{ fontSize: 28, fontWeight: 900, color: C.white }}>PREP</span>
          <span style={{ fontSize: 26, fontWeight: 300, color: C.crimson }}>/</span>
          <span style={{ fontSize: 28, fontWeight: 900, color: C.crimson }}>RANK</span>
        </div>
        <div style={{ fontSize: 12, color: C.silver }}>6 screenshots · iOS & Android · Using real 2025 LHSAA data</div>
      </div>

      {/* Screenshot nav dots */}
      <div style={{ display: "flex", justifyContent: "center", gap: 8, padding: "8px 0 20px" }}>
        {screenshots.map((_, i) => (
          <div key={i} className="dot" onClick={() => setCurrent(i)} style={{
            width: current === i ? 24 : 8, height: 8, borderRadius: 4,
            background: current === i ? C.crimson : C.steel,
          }} />
        ))}
      </div>

      {/* Screenshots carousel */}
      <div className="scroll-container" style={{ display: "flex", gap: 32, overflowX: "auto", padding: "0 40px 40px", justifyContent: "flex-start" }}>

        {/* ===== SCREENSHOT 1: What's At Stake ===== */}
        <PhoneFrame caption={screenshots[0].caption} subcaption={screenshots[0].subcaption}>
          <AppNav />
          <div style={{ padding: "8px 12px", position: "relative" }}>
            <div style={{ fontSize: 9, letterSpacing: 2, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 6 }}>What's At Stake · Week 8</div>

            {/* Main matchup */}
            <div style={{ background: C.darkGray, borderRadius: 10, overflow: "hidden", marginBottom: 8, border: `1px solid ${C.steel}` }}>
              <div style={{ padding: "10px 14px", borderBottom: `2px solid ${C.crimson}`, background: `linear-gradient(135deg, ${C.steel}, ${C.darkGray})` }}>
                <div style={{ fontSize: 7, color: C.crimson, letterSpacing: 1.5, textTransform: "uppercase", fontWeight: 700, marginBottom: 2 }}>Select Division I · District 9</div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ fontSize: 15, fontWeight: 800, color: C.white }}>Edna Karr vs St. Paul's</div>
                  <div style={{ fontSize: 9, color: C.silver }}>Fri 7 PM</div>
                </div>
              </div>
              <div style={{ padding: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                <div style={{ background: `${C.winGreen}10`, border: `1px solid ${C.winGreen}33`, borderRadius: 6, padding: 10, textAlign: "center" }}>
                  <div style={{ fontSize: 7, color: C.winGreen, fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 4 }}>If St. Paul's Wins</div>
                  <div style={{ fontSize: 28, fontWeight: 900, color: C.winGreen }}>76%</div>
                  <div style={{ fontSize: 8, color: C.silver }}>playoff probability</div>
                  <div style={{ fontSize: 9, color: C.winGreen, fontWeight: 700, marginTop: 4 }}>#9 → #5</div>
                </div>
                <div style={{ background: `${C.lossRed}10`, border: `1px solid ${C.lossRed}33`, borderRadius: 6, padding: 10, textAlign: "center" }}>
                  <div style={{ fontSize: 7, color: C.lossRed, fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 4 }}>If St. Paul's Loses</div>
                  <div style={{ fontSize: 28, fontWeight: 900, color: C.lossRed }}>28%</div>
                  <div style={{ fontSize: 8, color: C.silver }}>playoff probability</div>
                  <div style={{ fontSize: 9, color: C.lossRed, fontWeight: 700, marginTop: 4 }}>#9 → #14</div>
                </div>
              </div>
              <div style={{ padding: "6px 12px 10px", textAlign: "center", fontSize: 9, color: C.silver }}>
                <strong style={{ color: C.white }}>48-point swing</strong> — biggest in Select Div I this week
              </div>
            </div>

            {/* Second matchup preview */}
            <div style={{ background: C.darkGray, borderRadius: 10, padding: "10px 14px", border: `1px solid ${C.steel}`, marginBottom: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 7, color: C.crimson, letterSpacing: 1, textTransform: "uppercase", fontWeight: 700 }}>Non-Select Div I</div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.white }}>Destrehan vs Hahnville</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 8, color: C.silver }}>Fri 7 PM</div>
                  <div style={{ fontSize: 9, fontWeight: 700, color: C.crimson }}>45pt swing</div>
                </div>
              </div>
            </div>

            <div style={{ background: C.darkGray, borderRadius: 10, padding: "10px 14px", border: `1px solid ${C.steel}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 7, color: C.crimson, letterSpacing: 1, textTransform: "uppercase", fontWeight: 700 }}>Select Div I</div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.white }}>Catholic-BR vs Evangel</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 8, color: C.silver }}>Fri 7 PM</div>
                  <div style={{ fontSize: 9, fontWeight: 700, color: C.crimson }}>38pt swing</div>
                </div>
              </div>
            </div>
          </div>
          <TabBar active={0} />
        </PhoneFrame>

        {/* ===== SCREENSHOT 2: My Athletes ===== */}
        <PhoneFrame caption={screenshots[1].caption} subcaption={screenshots[1].subcaption}>
          <AppNav title="My Athletes" subtitle="3 Teams Followed" />
          <div style={{ padding: "8px 12px", position: "relative" }}>
            {[
              { sport: "Football", icon: "🏈", team: "St. Paul's Wolves", record: "8-4", rank: "#9 Select Div I", pr: "13.13", playoff: "72%", next: "vs Rummel · Fri 7PM", playoffColor: C.winGreen },
              { sport: "Boys Basketball", icon: "🏀", team: "St. Paul's Wolves", record: "12-6", rank: "#5 Select Div I", pr: "11.82", playoff: "84%", next: "@ Mandeville · Tue 7PM", playoffColor: C.winGreen },
              { sport: "Softball", icon: "🥎", team: "St. Scholastica", record: "14-4", rank: "#3 Div III", pr: "10.45", playoff: "91%", next: "vs Loranger · Wed 4PM", playoffColor: C.winGreen },
            ].map((t, i) => (
              <div key={i} style={{ background: C.darkGray, borderRadius: 10, padding: 12, marginBottom: 8, border: `1px solid ${C.steel}`, borderLeft: `3px solid ${C.crimson}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: 18 }}>{t.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, fontWeight: 800, color: C.white }}>{t.team}</div>
                    <div style={{ fontSize: 8, color: C.silver }}>{t.sport} · {t.record} · {t.rank}</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, marginBottom: 6 }}>
                  <div style={{ flex: 1, background: C.charcoal, borderRadius: 6, padding: "6px 8px", textAlign: "center" }}>
                    <div style={{ fontSize: 7, color: C.midGray, letterSpacing: 1, textTransform: "uppercase" }}>Power Rating</div>
                    <div style={{ fontSize: 16, fontWeight: 900, color: C.white }}>{t.pr}</div>
                  </div>
                  <div style={{ flex: 1, background: C.charcoal, borderRadius: 6, padding: "6px 8px", textAlign: "center" }}>
                    <div style={{ fontSize: 7, color: C.midGray, letterSpacing: 1, textTransform: "uppercase" }}>Playoff Odds</div>
                    <div style={{ fontSize: 16, fontWeight: 900, color: t.playoffColor }}>{t.playoff}</div>
                  </div>
                </div>
                <div style={{ fontSize: 9, color: C.silver, padding: "4px 0 0", borderTop: `1px solid ${C.steel}44` }}>
                  Next: <strong style={{ color: C.white }}>{t.next}</strong>
                </div>
              </div>
            ))}
            <div style={{ textAlign: "center", padding: "8px 0" }}>
              <div style={{ display: "inline-block", padding: "8px 20px", borderRadius: 6, border: `1px dashed ${C.steel}`, fontSize: 10, color: C.midGray }}>+ Add Another Team</div>
            </div>
          </div>
          <TabBar active={2} />
        </PhoneFrame>

        {/* ===== SCREENSHOT 3: Push Notification ===== */}
        <PhoneFrame caption={screenshots[2].caption} subcaption={screenshots[2].subcaption}>
          <div style={{ background: `linear-gradient(180deg, #1c2a4a 0%, #0f1928 100%)`, height: "100%", padding: "0 16px", position: "relative" }}>
            {/* Lock screen clock */}
            <div style={{ textAlign: "center", paddingTop: 30 }}>
              <div style={{ fontSize: 56, fontWeight: 200, color: C.white, lineHeight: 1 }}>10:12</div>
              <div style={{ fontSize: 13, color: C.lightSilver, marginTop: 4 }}>Friday, October 17</div>
            </div>

            {/* Notifications */}
            <div style={{ marginTop: 40, display: "flex", flexDirection: "column", gap: 8 }}>
              {[
                { time: "Now", title: "Playoff odds just shifted!", body: "St. Paul's beat Rummel 24-17. Your team moved from #9 to #6 in Select Div I. Playoff probability: 72% → 88%.", sport: "Football" },
                { time: "2m ago", title: "Score update", body: "Edna Karr 35, Acadiana 14 — FINAL. Karr clinches #1 seed.", sport: "Football" },
                { time: "8m ago", title: "Pick'em results are in!", body: "You got 9/12 correct this week. You're #3 at St. Paul's. School rank: #2 in District 9.", sport: "Pick'em" },
              ].map((n, i) => (
                <div key={i} style={{
                  background: "rgba(255,255,255,0.12)", backdropFilter: "blur(20px)",
                  borderRadius: 16, padding: "12px 14px", border: "1px solid rgba(255,255,255,0.08)",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    <div style={{
                      width: 22, height: 22, borderRadius: 6, background: C.charcoal,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      border: `1px solid ${C.steel}`,
                    }}>
                      <span style={{ fontSize: 7, fontWeight: 900, color: C.white }}>P</span>
                      <span style={{ fontSize: 6, fontWeight: 300, color: C.crimson }}>/</span>
                      <span style={{ fontSize: 7, fontWeight: 900, color: C.crimson }}>R</span>
                    </div>
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: 10, fontWeight: 700, color: C.white }}>PrepRank · {n.sport}</span>
                    </div>
                    <span style={{ fontSize: 9, color: "rgba(255,255,255,0.5)" }}>{n.time}</span>
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.white, marginBottom: 3 }}>{n.title}</div>
                  <div style={{ fontSize: 10, color: "rgba(255,255,255,0.7)", lineHeight: 1.5 }}>{n.body}</div>
                </div>
              ))}
            </div>
          </div>
        </PhoneFrame>

        {/* ===== SCREENSHOT 4: Division Leaderboard ===== */}
        <PhoneFrame caption={screenshots[3].caption} subcaption={screenshots[3].subcaption}>
          <AppNav title="Select Division I" subtitle="Football · Projected Final" />
          <div style={{ padding: "6px 12px", position: "relative" }}>
            {/* Header row */}
            <div style={{ display: "flex", padding: "6px 8px", fontSize: 7, color: C.midGray, letterSpacing: 1, textTransform: "uppercase", fontWeight: 700 }}>
              <div style={{ width: 22 }}>#</div>
              <div style={{ flex: 1 }}>School</div>
              <div style={{ width: 40, textAlign: "center" }}>PR</div>
              <div style={{ width: 36, textAlign: "center" }}>Rec</div>
              <div style={{ width: 48, textAlign: "right" }}>Playoff %</div>
            </div>

            {[
              { r: 1, name: "Edna Karr", pr: "15.82", rec: "10-0", pct: "99%", color: C.winGreen, bar: 99 },
              { r: 2, name: "Teurlings Catholic", pr: "14.83", rec: "10-0", pct: "97%", color: C.winGreen, bar: 97 },
              { r: 3, name: "St. Augustine", pr: "14.58", rec: "9-1", pct: "95%", color: C.winGreen, bar: 95 },
              { r: 4, name: "Catholic - B.R.", pr: "14.47", rec: "8-1", pct: "93%", color: C.winGreen, bar: 93 },
              { r: 5, name: "Alexandria", pr: "13.93", rec: "8-2", pct: "88%", color: C.winGreen, bar: 88 },
              { r: 6, name: "Tioga", pr: "13.48", rec: "8-1", pct: "85%", color: C.winGreen, bar: 85 },
              { r: 7, name: "John Curtis", pr: "13.44", rec: "7-2", pct: "81%", color: C.winGreen, bar: 81 },
              { r: 8, name: "Evangel Christian", pr: "13.30", rec: "8-3", pct: "74%", color: C.winGreen, bar: 74 },
              { r: 9, name: "St. Paul's", pr: "13.13", rec: "8-4", pct: "72%", color: "#D4A843", bar: 72, highlight: true },
              { r: 10, name: "St. Thomas More", pr: "12.80", rec: "7-3", pct: "58%", color: C.lossRed, bar: 58 },
              { r: 11, name: "Abp. Rummel", pr: "12.78", rec: "6-4", pct: "44%", color: C.lossRed, bar: 44 },
              { r: 12, name: "Brother Martin", pr: "12.68", rec: "6-3", pct: "31%", color: C.lossRed, bar: 31 },
            ].map((t, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", padding: "7px 8px",
                background: t.highlight ? `${C.crimson}15` : i % 2 === 1 ? `${C.white}03` : "transparent",
                borderRadius: 4,
                borderLeft: t.highlight ? `2px solid ${C.crimson}` : "2px solid transparent",
              }}>
                <div style={{ width: 22, fontSize: 11, fontWeight: 800, color: t.r <= 8 ? C.white : C.midGray }}>{t.r}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 11, fontWeight: t.highlight ? 800 : 600, color: t.highlight ? C.white : C.lightSilver }}>{t.name}</div>
                  {/* Mini bar */}
                  <div style={{ height: 2, background: C.steel, borderRadius: 1, marginTop: 2, width: "80%" }}>
                    <div style={{ height: 2, background: t.color, borderRadius: 1, width: `${t.bar}%` }} />
                  </div>
                </div>
                <div style={{ width: 40, textAlign: "center", fontSize: 10, fontWeight: 700, color: C.silver }}>{t.pr}</div>
                <div style={{ width: 36, textAlign: "center", fontSize: 10, color: C.midGray }}>{t.rec}</div>
                <div style={{ width: 48, textAlign: "right", fontSize: 11, fontWeight: 800, color: t.color }}>{t.pct}</div>
              </div>
            ))}

            {/* Playoff line indicator */}
            <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 8px", marginTop: -2 }}>
              <div style={{ flex: 1, height: 1, background: `${C.crimson}44` }} />
              <span style={{ fontSize: 7, color: C.crimson, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase" }}>Playoff cutline</span>
              <div style={{ flex: 1, height: 1, background: `${C.crimson}44` }} />
            </div>
          </div>
          <TabBar active={1} />
        </PhoneFrame>

        {/* ===== SCREENSHOT 5: Pick'em ===== */}
        <PhoneFrame caption={screenshots[4].caption} subcaption={screenshots[4].subcaption}>
          <AppNav title="Friday Night Pick'em" subtitle="Week 8 · 4,847 entries" />
          <div style={{ padding: "6px 12px", position: "relative" }}>
            {/* Tabs */}
            <div style={{ display: "flex", gap: 0, marginBottom: 8 }}>
              {["My Picks", "Leaderboard", "School"].map((t, i) => (
                <div key={i} style={{
                  flex: 1, textAlign: "center", padding: "6px 0", fontSize: 9, fontWeight: 700,
                  color: i === 2 ? C.white : C.midGray, letterSpacing: 0.5,
                  borderBottom: i === 2 ? `2px solid ${C.crimson}` : `1px solid ${C.steel}44`,
                }}>{t}</div>
              ))}
            </div>

            {/* School leaderboard */}
            <div style={{ fontSize: 8, letterSpacing: 1.5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 6 }}>District 9 · School Rankings</div>
            {[
              { r: 1, name: "St. Paul's", pts: 2847, pickers: 142, acc: "78%", leader: "@wolf_fan22" },
              { r: 2, name: "Abp. Rummel", pts: 2712, pickers: 128, acc: "75%", leader: "@raider_mike" },
              { r: 3, name: "Edna Karr", pts: 2698, pickers: 156, acc: "74%", leader: "@karr_cougars" },
              { r: 4, name: "Acadiana", pts: 2541, pickers: 98, acc: "71%", leader: "@wreckin_ram" },
              { r: 5, name: "Alexandria", pts: 2480, pickers: 87, acc: "69%", leader: "@trojan_sports" },
            ].map((s, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", padding: "8px 10px", marginBottom: 4,
                background: i === 0 ? `${C.crimson}12` : C.darkGray, borderRadius: 8,
                border: i === 0 ? `1px solid ${C.crimson}33` : `1px solid ${C.steel}`,
                borderLeft: i === 0 ? `3px solid ${C.crimson}` : "none",
              }}>
                <div style={{ fontSize: 16, fontWeight: 900, color: i === 0 ? C.crimson : C.midGray, width: 28 }}>#{s.r}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.white }}>{s.name}</div>
                  <div style={{ fontSize: 8, color: C.midGray }}>{s.pickers} pickers · {s.acc} accuracy</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 14, fontWeight: 900, color: i === 0 ? C.crimson : C.silver }}>{s.pts.toLocaleString()}</div>
                  <div style={{ fontSize: 7, color: C.midGray }}>pts</div>
                </div>
              </div>
            ))}

            {/* Your stats card */}
            <div style={{ background: C.darkGray, borderRadius: 8, padding: 10, marginTop: 8, border: `1px solid ${C.steel}` }}>
              <div style={{ fontSize: 8, letterSpacing: 1.5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 6 }}>Your Season Stats</div>
              <div style={{ display: "flex", gap: 6 }}>
                {[
                  { label: "Rank", val: "#14", sub: "at St. Paul's" },
                  { label: "Accuracy", val: "76%", sub: "season avg" },
                  { label: "Streak", val: "🔥 4", sub: "correct picks" },
                  { label: "Badges", val: "3", sub: "earned" },
                ].map((s, i) => (
                  <div key={i} style={{ flex: 1, background: C.charcoal, borderRadius: 6, padding: "6px 4px", textAlign: "center" }}>
                    <div style={{ fontSize: 7, color: C.midGray, letterSpacing: 0.5, textTransform: "uppercase" }}>{s.label}</div>
                    <div style={{ fontSize: 13, fontWeight: 900, color: C.white, margin: "2px 0" }}>{s.val}</div>
                    <div style={{ fontSize: 7, color: C.midGray }}>{s.sub}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <TabBar active={3} />
        </PhoneFrame>

        {/* ===== SCREENSHOT 6: What-If Scenario Builder ===== */}
        <PhoneFrame caption={screenshots[5].caption} subcaption={screenshots[5].subcaption}>
          <AppNav title="What-If Builder" subtitle="Select Division I · Week 8" />
          <div style={{ padding: "6px 12px", position: "relative" }}>
            <div style={{ fontSize: 8, letterSpacing: 1.5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 6 }}>Toggle game outcomes</div>

            {[
              { away: "Edna Karr", home: "St. Paul's", result: "home", awayR: "#1", homeR: "#9" },
              { away: "Catholic-BR", home: "Evangel", result: "away", awayR: "#4", homeR: "#8" },
              { away: "St. Augustine", home: "Tioga", result: "away", awayR: "#3", homeR: "#6" },
              { away: "Alexandria", home: "Curtis", result: null, awayR: "#5", homeR: "#7" },
              { away: "Teurlings", home: "St. Thomas More", result: "away", awayR: "#2", homeR: "#10" },
            ].map((g, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", padding: "6px 8px", marginBottom: 4,
                background: C.darkGray, borderRadius: 8, border: `1px solid ${C.steel}`,
              }}>
                <div style={{
                  flex: 1, display: "flex", alignItems: "center", gap: 4,
                  padding: "4px 8px", borderRadius: 4, cursor: "pointer",
                  background: g.result === "away" ? `${C.winGreen}15` : "transparent",
                  border: g.result === "away" ? `1px solid ${C.winGreen}44` : "1px solid transparent",
                }}>
                  <span style={{ fontSize: 7, color: C.midGray }}>{g.awayR}</span>
                  <span style={{ fontSize: 10, fontWeight: 700, color: g.result === "away" ? C.winGreen : C.lightSilver }}>{g.away}</span>
                  {g.result === "away" && <span style={{ fontSize: 8, color: C.winGreen }}>W</span>}
                </div>
                <div style={{ fontSize: 8, color: C.midGray, padding: "0 4px" }}>@</div>
                <div style={{
                  flex: 1, display: "flex", alignItems: "center", gap: 4, justifyContent: "flex-end",
                  padding: "4px 8px", borderRadius: 4, cursor: "pointer",
                  background: g.result === "home" ? `${C.winGreen}15` : "transparent",
                  border: g.result === "home" ? `1px solid ${C.winGreen}44` : "1px solid transparent",
                }}>
                  {g.result === "home" && <span style={{ fontSize: 8, color: C.winGreen }}>W</span>}
                  <span style={{ fontSize: 10, fontWeight: 700, color: g.result === "home" ? C.winGreen : C.lightSilver }}>{g.home}</span>
                  <span style={{ fontSize: 7, color: C.midGray }}>{g.homeR}</span>
                </div>
              </div>
            ))}

            {/* Projected result */}
            <div style={{ background: `${C.crimson}10`, border: `1px solid ${C.crimson}33`, borderRadius: 8, padding: 10, marginTop: 8 }}>
              <div style={{ fontSize: 8, letterSpacing: 1.5, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 6 }}>With your selections, St. Paul's projects to:</div>
              <div style={{ display: "flex", gap: 8 }}>
                <div style={{ flex: 1, background: C.charcoal, borderRadius: 6, padding: 8, textAlign: "center" }}>
                  <div style={{ fontSize: 7, color: C.midGray, letterSpacing: 1, textTransform: "uppercase" }}>Final Rank</div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: C.winGreen }}>#5</div>
                  <div style={{ fontSize: 8, color: C.winGreen }}>↑ 4 spots</div>
                </div>
                <div style={{ flex: 1, background: C.charcoal, borderRadius: 6, padding: 8, textAlign: "center" }}>
                  <div style={{ fontSize: 7, color: C.midGray, letterSpacing: 1, textTransform: "uppercase" }}>Power Rating</div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: C.white }}>13.87</div>
                  <div style={{ fontSize: 8, color: C.winGreen }}>↑ 0.74</div>
                </div>
                <div style={{ flex: 1, background: C.charcoal, borderRadius: 6, padding: 8, textAlign: "center" }}>
                  <div style={{ fontSize: 7, color: C.midGray, letterSpacing: 1, textTransform: "uppercase" }}>Playoff %</div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: C.winGreen }}>88%</div>
                  <div style={{ fontSize: 8, color: C.winGreen }}>↑ 16pts</div>
                </div>
              </div>
            </div>

            {/* Share button */}
            <div style={{ marginTop: 8, textAlign: "center" }}>
              <div style={{
                display: "inline-block", padding: "8px 24px", background: C.crimson, borderRadius: 6,
                fontSize: 10, fontWeight: 700, color: C.white, letterSpacing: 1, textTransform: "uppercase",
              }}>Share This Scenario</div>
            </div>
          </div>
          <TabBar active={0} />
        </PhoneFrame>
      </div>

      {/* Screenshot descriptions */}
      <div style={{ padding: "20px 40px 40px", maxWidth: 900, margin: "0 auto" }}>
        <div style={{ fontSize: 11, letterSpacing: 3, color: C.crimson, textTransform: "uppercase", fontWeight: 700, marginBottom: 16 }}>Screenshot Guide</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          {[
            { n: "1", title: "What's At Stake", desc: "The money shot. Shows playoff probability swing for a real matchup. Win/loss outcomes side by side with point swing callout." },
            { n: "2", title: "My Athletes", desc: "Multi-sport dashboard. Three teams from different sports with power ratings, playoff odds, and next game. Sells the all-sport value." },
            { n: "3", title: "Push Notifications", desc: "Lock screen showing 3 notifications: score impact, game result, pick'em results. Demonstrates real-time engagement." },
            { n: "4", title: "Division Leaderboard", desc: "Full division rankings with projected playoff %. St. Paul's highlighted at #9. Playoff cutline clearly marked at #8." },
            { n: "5", title: "Pick'em Contest", desc: "School leaderboard with St. Paul's #1. Shows social competition layer + individual stats. Sells the free engagement hook." },
            { n: "6", title: "What-If Builder", desc: "Premium feature showcase. Toggle game outcomes, watch projections recalculate. 'Share This Scenario' button shows virality." },
          ].map((s, i) => (
            <div key={i} style={{ padding: "10px 14px", borderRadius: 8, background: C.darkGray, border: `1px solid ${C.steel}` }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                <div style={{ width: 20, height: 20, borderRadius: 4, background: C.crimson, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 800 }}>{s.n}</div>
                <span style={{ fontSize: 13, fontWeight: 700, color: C.white }}>{s.title}</span>
              </div>
              <p style={{ fontSize: 11, color: C.silver, lineHeight: 1.6, margin: 0 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
