const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ── Icon helpers ──────────────────────────────────────────────────────────────
const { FaGlobe, FaChartLine, FaDatabase, FaBrain, FaShieldAlt,
        FaArrowUp, FaArrowDown, FaExchangeAlt, FaGithub, FaEnvelope,
        FaUniversity, FaCheckCircle, FaRobot, FaUsers, FaSearch } = require("react-icons/fa");
const { MdTrendingUp, MdTrendingDown, MdEqualizer } = require("react-icons/md");

async function iconPng(IconComp, color = "#FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComp, { color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// ── Color Palette — "Midnight Intelligence" ───────────────────────────────────
const C = {
  navy:       "0D1B2A",   // dominant dark
  teal:       "00B4D8",   // primary accent
  tealDark:   "0077A8",   // deeper teal
  tealLight:  "90E0EF",   // light teal
  gold:       "F4A261",   // warm accent for wins
  rose:       "E63946",   // alert/falls
  mint:       "06D6A0",   // adapters / positive
  white:      "FFFFFF",
  offWhite:   "F0F4F8",
  slate:      "4A5568",
  slateLight: "A0AEC0",
  cardBg:     "132337",   // card background on dark slides
  lightBg:    "F0F6FA",   // content slide background
  lightCard:  "FFFFFF",
};

const makeShadow = () => ({ type: "outer", color: "000000", blur: 8, offset: 3, angle: 45, opacity: 0.18 });
const makeCardShadow = () => ({ type: "outer", color: "000000", blur: 5, offset: 2, angle: 45, opacity: 0.10 });

// ─────────────────────────────────────────────────────────────────────────────
async function buildPresentation() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.3" × 7.5"
  pres.author  = "Daipayan Chatterjee";
  pres.title   = "The Economics of Abundant Intelligence";
  pres.subject = "Global Evidence on Income Stability and Career Sustainability in the AI Era";

  const W = 13.3, H = 7.5;

  // Pre-render icons
  const iGlobe   = await iconPng(FaGlobe,       "#" + C.teal);
  const iChart    = await iconPng(FaChartLine,   "#" + C.teal);
  const iDb       = await iconPng(FaDatabase,    "#" + C.teal);
  const iBrain    = await iconPng(FaBrain,       "#" + C.teal);
  const iShield   = await iconPng(FaShieldAlt,   "#" + C.teal);
  const iWin      = await iconPng(FaArrowUp,     "#" + C.gold);
  const iFall     = await iconPng(FaArrowDown,   "#" + C.rose);
  const iAdapt    = await iconPng(FaExchangeAlt, "#" + C.mint);
  const iGithub   = await iconPng(FaGithub,      "#" + C.tealLight);
  const iEmail    = await iconPng(FaEnvelope,    "#" + C.tealLight);
  const iUni      = await iconPng(FaUniversity,  "#" + C.tealLight);
  const iCheck    = await iconPng(FaCheckCircle, "#" + C.mint);
  const iRobot    = await iconPng(FaRobot,       "#" + C.teal);
  const iUsers    = await iconPng(FaUsers,       "#" + C.gold);
  const iSearch   = await iconPng(FaSearch,      "#" + C.teal);
  const iWinW     = await iconPng(FaArrowUp,     "#FFFFFF");
  const iFallW    = await iconPng(FaArrowDown,   "#FFFFFF");
  const iAdaptW   = await iconPng(FaExchangeAlt, "#FFFFFF");
  const iTrendUp  = await iconPng(MdTrendingUp,  "#" + C.mint);
  const iTrendDn  = await iconPng(MdTrendingDown,"#" + C.rose);
  const iEqual    = await iconPng(MdEqualizer,   "#" + C.teal);

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 1 — TITLE
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    // Left dark panel
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: 7.2, h: H,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    // Right teal panel
    s.addShape(pres.shapes.RECTANGLE, {
      x: 7.2, y: 0, w: 6.1, h: H,
      fill: { color: C.tealDark }, line: { color: C.tealDark }
    });
    // Diagonal separator overlay
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.8, y: 0, w: 0.8, h: H,
      fill: { color: C.teal, transparency: 40 },
      line: { color: C.teal, transparency: 40 }
    });

    // Title text
    s.addText("THE ECONOMICS OF", {
      x: 0.55, y: 0.55, w: 6.5, h: 0.65,
      fontSize: 22, bold: true, color: C.tealLight,
      fontFace: "Calibri", charSpacing: 4, margin: 0
    });
    s.addText("ABUNDANT\nINTELLIGENCE", {
      x: 0.55, y: 1.1, w: 6.5, h: 1.85,
      fontSize: 54, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("Who Wins, Who Falls, and Who Adapts?", {
      x: 0.55, y: 2.95, w: 6.5, h: 0.55,
      fontSize: 18, italic: true, color: C.tealLight,
      fontFace: "Calibri", margin: 0
    });
    s.addText("Global Evidence on Income Stability and Career Sustainability in the AI Era", {
      x: 0.55, y: 3.52, w: 6.5, h: 0.65,
      fontSize: 13, color: C.slateLight,
      fontFace: "Calibri", margin: 0
    });

    // Divider
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.55, y: 4.3, w: 2.5, h: 0.04,
      fill: { color: C.teal }, line: { color: C.teal }
    });

    // Author block
    s.addText("DAIPAYAN CHATTERJEE", {
      x: 0.55, y: 4.48, w: 6.4, h: 0.4,
      fontSize: 16, bold: true, color: C.white,
      fontFace: "Calibri", charSpacing: 2, margin: 0
    });
    s.addText("M.Sc. Economics · Quantitative Economics & Econometrics", {
      x: 0.55, y: 4.88, w: 6.4, h: 0.3,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    // Contact row
    s.addImage({ data: iEmail, x: 0.55, y: 5.32, w: 0.22, h: 0.22 });
    s.addText("daipayanchatterjee01@gmail.com", {
      x: 0.83, y: 5.28, w: 3.2, h: 0.3,
      fontSize: 11, color: C.slateLight, fontFace: "Calibri", margin: 0
    });
    s.addImage({ data: iGithub, x: 0.55, y: 5.65, w: 0.22, h: 0.22 });
    s.addText("github.com/dchatterjee01-prog", {
      x: 0.83, y: 5.61, w: 3.2, h: 0.3,
      fontSize: 11, color: C.slateLight, fontFace: "Calibri", margin: 0
    });

    // Right panel stats
    const stats = [
      { val: "264", lbl: "Countries Analyzed" },
      { val: "25", lbl: "Years (2000–2025)" },
      { val: "6,774", lbl: "Panel Observations" },
      { val: "82", lbl: "Engineered Features" },
    ];
    stats.forEach((st, i) => {
      const yy = 0.7 + i * 1.55;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 7.55, y: yy, w: 5.3, h: 1.2,
        fill: { color: C.navy, transparency: 30 },
        line: { color: C.tealLight, transparency: 60 },
        rectRadius: 0.08,
        shadow: makeShadow()
      });
      s.addText(st.val, {
        x: 7.65, y: yy + 0.08, w: 5.1, h: 0.65,
        fontSize: 40, bold: true, color: C.white,
        fontFace: "Cambria", align: "center", margin: 0
      });
      s.addText(st.lbl, {
        x: 7.65, y: yy + 0.72, w: 5.1, h: 0.35,
        fontSize: 13, color: C.tealLight,
        fontFace: "Calibri", align: "center", margin: 0
      });
    });

    s.addNotes("Title slide. Present the research scope: 264 countries, 25 years, production-grade pipeline.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 2 — RESEARCH AGENDA
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.lightBg };

    // Header band
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    s.addText("RESEARCH AGENDA", {
      x: 0.5, y: 0.18, w: 10, h: 0.6,
      fontSize: 28, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("Three core questions driving this investigation", {
      x: 0.5, y: 0.65, w: 10, h: 0.3,
      fontSize: 13, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    const cards = [
      {
        icon: iRobot, col: C.teal,
        q: "Q1 — The Displacement Question",
        body: "Does AI exposure systematically erode labor income share and elevate labor market stress across heterogeneous economies?",
        finding: "ai_exposure_proxy → +0.143* on Labor Market Stress"
      },
      {
        icon: iShield, col: C.gold,
        q: "Q2 — The Buffer Question",
        body: "Do institutional buffers — social protection, R&D investment, human capital — mediate the negative labor market effects of AI adoption?",
        finding: "tech_vulnerability_index → −0.214** (R&D buffers AI shock)"
      },
      {
        icon: iGlobe, col: C.mint,
        q: "Q3 — The Convergence Question",
        body: "Is the global distribution of AI-era outcomes converging or diverging across income groups and regions? Who wins, who falls, who adapts?",
        finding: "HISI Range: 19.5 (QAT) → 88.5 (ISL) — Divergence confirmed"
      }
    ];

    cards.forEach((c, i) => {
      const x = 0.45 + i * 4.25;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.2, w: 4.05, h: 5.85,
        fill: { color: C.white }, line: { color: "E2EAF0" },
        rectRadius: 0.12, shadow: makeCardShadow()
      });
      // Top color band on card
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.2, w: 4.05, h: 0.55,
        fill: { color: c.col }, line: { color: c.col },
        rectRadius: 0.12
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x, y: 1.55, w: 4.05, h: 0.2,
        fill: { color: c.col }, line: { color: c.col }
      });
      s.addImage({ data: c.icon, x: x + 0.15, y: 1.27, w: 0.36, h: 0.36 });
      s.addText(c.q, {
        x: x + 0.15, y: 1.85, w: 3.75, h: 0.55,
        fontSize: 13, bold: true, color: C.navy,
        fontFace: "Calibri", margin: 0
      });
      s.addText(c.body, {
        x: x + 0.15, y: 2.52, w: 3.75, h: 2.1,
        fontSize: 12, color: C.slate,
        fontFace: "Calibri", margin: 0
      });
      // Finding box
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: x + 0.15, y: 4.78, w: 3.75, h: 1.9,
        fill: { color: C.lightBg }, line: { color: "D0DDE8" },
        rectRadius: 0.08
      });
      s.addText("KEY FINDING", {
        x: x + 0.25, y: 4.88, w: 3.55, h: 0.28,
        fontSize: 9, bold: true, color: c.col, charSpacing: 2,
        fontFace: "Calibri", margin: 0
      });
      s.addText(c.finding, {
        x: x + 0.25, y: 5.18, w: 3.55, h: 1.35,
        fontSize: 11, color: C.navy, fontFace: "Calibri",
        italic: true, margin: 0
      });
    });

    s.addNotes("Three research questions. Each maps to a specific econometric model and HISI cluster.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 3 — DATA ARCHITECTURE
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.cardBg }, line: { color: C.cardBg }
    });
    s.addText("ENTERPRISE DATA ARCHITECTURE", {
      x: 0.5, y: 0.18, w: 10, h: 0.55,
      fontSize: 28, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("5-table SQLite relational schema · 3-stage imputation · 74% missingness threshold", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    const tables = [
      { name: "country_metadata",      src: "266 countries", icon: iGlobe,  col: C.teal },
      { name: "macro_economic_core",   src: "World Bank · 14 indicators",  icon: iChart,   col: C.gold },
      { name: "labor_dynamics",        src: "ILOSTAT · 4 indicators",      icon: iUsers,   col: C.mint },
      { name: "ai_vibrancy_readiness", src: "Stanford AI Index · 5 vars",  icon: iRobot,   col: C.tealLight },
      { name: "institutional_buffers", src: "IMF/WB · 5 indicators",       icon: iShield,  col: C.rose },
    ];

    tables.forEach((t, i) => {
      const x = 0.35 + i * 2.52;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.25, w: 2.3, h: 2.1,
        fill: { color: C.cardBg }, line: { color: t.col, transparency: 30 },
        rectRadius: 0.1, shadow: makeShadow()
      });
      s.addImage({ data: t.icon, x: x + 0.85, y: 1.35, w: 0.5, h: 0.5 });
      s.addText(t.name, {
        x: x + 0.1, y: 1.92, w: 2.1, h: 0.6,
        fontSize: 11, bold: true, color: C.white,
        fontFace: "Calibri", align: "center", margin: 0
      });
      s.addText(t.src, {
        x: x + 0.1, y: 2.55, w: 2.1, h: 0.65,
        fontSize: 10, color: C.slateLight,
        fontFace: "Calibri", align: "center", margin: 0
      });
    });

    // Arrow flow
    for (let i = 0; i < 4; i++) {
      s.addShape(pres.shapes.LINE, {
        x: 2.55 + i * 2.52, y: 2.3, w: 0.22, h: 0,
        line: { color: C.teal, width: 2 }
      });
    }

    // Imputation pipeline box
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.35, y: 3.6, w: 12.6, h: 1.65,
      fill: { color: C.cardBg }, line: { color: C.teal, transparency: 50 },
      rectRadius: 0.1, shadow: makeShadow()
    });
    s.addText("3-STAGE IMPUTATION PIPELINE", {
      x: 0.6, y: 3.72, w: 12, h: 0.3,
      fontSize: 12, bold: true, color: C.teal, charSpacing: 2,
      fontFace: "Calibri", margin: 0
    });
    const steps = [
      "① Outer Merge\n(iso_alpha3 + year)",
      "② Drop >74%\nmissing columns",
      "③ Rolling ffill/bfill\nwithin country (w=3)",
      "④ KNNImputer\n(k=5, structural gaps)",
      "⑤ master_panel_imputed\n6,774 rows · 31 cols · 0% null"
    ];
    steps.forEach((st, i) => {
      const x = 0.55 + i * 2.52;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 4.1, w: 2.3, h: 0.95,
        fill: { color: C.navy }, line: { color: C.teal, transparency: 60 },
        rectRadius: 0.08
      });
      s.addText(st, {
        x: x + 0.05, y: 4.13, w: 2.2, h: 0.88,
        fontSize: 10, color: C.white,
        fontFace: "Calibri", align: "center", margin: 0
      });
    });

    // Final panel callout
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.35, y: 5.45, w: 12.6, h: 1.65,
      fill: { color: C.tealDark, transparency: 70 },
      line: { color: C.teal, transparency: 40 }, rectRadius: 0.1
    });
    const finalStats = [
      ["6,774", "Panel Observations"],
      ["264", "Countries"],
      ["2000–2025", "Time Span"],
      ["82", "Engineered Features"],
      ["74%", "Missingness Threshold"],
      ["0.00%", "Residual Missing"],
    ];
    finalStats.forEach((fs, i) => {
      const x = 0.6 + i * 2.1;
      s.addText(fs[0], {
        x, y: 5.55, w: 2.0, h: 0.6,
        fontSize: 26, bold: true, color: C.teal,
        fontFace: "Cambria", align: "center", margin: 0
      });
      s.addText(fs[1], {
        x, y: 6.18, w: 2.0, h: 0.28,
        fontSize: 10, color: C.slateLight,
        fontFace: "Calibri", align: "center", margin: 0
      });
    });

    s.addNotes("5 source tables, 3-stage imputation. All paths derived dynamically. KNN fills structural missingness after rolling fill.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 4 — ECONOMETRIC FRAMEWORK
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.lightBg };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    s.addText("ECONOMETRIC ARCHITECTURE", {
      x: 0.5, y: 0.18, w: 10, h: 0.55,
      fontSize: 28, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("Two-Way Fixed Effects · Hausman Test · IV/2SLS Robustness · Clustered Standard Errors", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    // Formula card
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.4, y: 1.18, w: 8.1, h: 2.2,
      fill: { color: C.white }, line: { color: "D0DDE8" },
      rectRadius: 0.1, shadow: makeCardShadow()
    });
    s.addText("TWFE Model Specification", {
      x: 0.65, y: 1.28, w: 7.6, h: 0.35,
      fontSize: 13, bold: true, color: C.navy,
      fontFace: "Calibri", charSpacing: 1, margin: 0
    });
    s.addText("Y\u1d62\u209c = \u03b2\u2080 + \u03b2\u2081(AI_Exposure\u1d62\u209c) + \u03b2\u2082(Tech_Invest\u1d62\u209c) + \u03b3X\u1d62\u209c + \u03b1\u1d62 + \u03b4\u209c + \u03b5\u1d62\u209c", {
      x: 0.65, y: 1.72, w: 7.7, h: 0.6,
      fontSize: 17, bold: true, color: C.tealDark,
      fontFace: "Cambria", margin: 0
    });
    s.addText([
      { text: "\u03b1\u1d62", options: { bold: true, color: C.gold } },
      { text: " = Country Fixed Effects  |  ", options: { color: C.slate } },
      { text: "\u03b4\u209c", options: { bold: true, color: C.mint } },
      { text: " = Year Fixed Effects  |  ", options: { color: C.slate } },
      { text: "Clustered SE", options: { bold: true, color: C.teal } },
      { text: " at country level", options: { color: C.slate } },
    ], { x: 0.65, y: 2.38, w: 7.7, h: 0.35, fontSize: 12, fontFace: "Calibri", margin: 0 });
    s.addText("Hausman Test: H-stat ≥ 69.3, p = 0.000 for all models → Fixed Effects formally confirmed", {
      x: 0.65, y: 2.82, w: 7.7, h: 0.38,
      fontSize: 11, italic: true, color: C.slate,
      fontFace: "Calibri", margin: 0
    });

    // Hausman card
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 8.75, y: 1.18, w: 4.1, h: 2.2,
      fill: { color: C.navy }, line: { color: C.teal, transparency: 40 },
      rectRadius: 0.1, shadow: makeShadow()
    });
    s.addText("HAUSMAN TEST", {
      x: 8.95, y: 1.28, w: 3.7, h: 0.3,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 2,
      fontFace: "Calibri", margin: 0
    });
    const hRows = [
      ["Labor Income Share", "69.3", "0.000"],
      ["Unemployment Rate",  "69.2", "0.000"],
      ["Labor Market Stress","82.6", "0.000"],
    ];
    s.addText([
      { text: "Outcome", options: { bold: true, color: C.tealLight, breakLine: true } },
    ], { x: 8.95, y: 1.65, w: 1.8, h: 0.28, fontSize: 10, fontFace: "Calibri", margin: 0 });
    hRows.forEach((r, i) => {
      const yy = 1.98 + i * 0.42;
      s.addText(r[0], {
        x: 8.95, y: yy, w: 2.2, h: 0.35,
        fontSize: 10, color: C.white, fontFace: "Calibri", margin: 0
      });
      s.addText(r[1], {
        x: 11.18, y: yy, w: 0.7, h: 0.35,
        fontSize: 10, bold: true, color: C.gold,
        fontFace: "Calibri", align: "center", margin: 0
      });
      s.addText("✓ FE", {
        x: 11.92, y: yy, w: 0.8, h: 0.35,
        fontSize: 10, bold: true, color: C.mint,
        fontFace: "Calibri", margin: 0
      });
    });

    // Results table
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.4, y: 3.55, w: 12.45, h: 3.6,
      fill: { color: C.white }, line: { color: "D0DDE8" },
      rectRadius: 0.1, shadow: makeCardShadow()
    });
    s.addText("TWFE REGRESSION RESULTS — KEY COEFFICIENTS", {
      x: 0.65, y: 3.68, w: 12, h: 0.3,
      fontSize: 12, bold: true, color: C.navy, charSpacing: 1,
      fontFace: "Calibri", margin: 0
    });

    // Table header
    const colX = [0.65, 3.7, 5.6, 7.3, 9.0, 10.6, 11.8];
    const hdrs = ["Regressor", "Dep. Variable", "Coef.", "Std Err", "t-stat", "p-value", "Sig."];
    hdrs.forEach((h, i) => {
      s.addText(h, {
        x: colX[i], y: 4.05, w: colX[i+1] ? colX[i+1]-colX[i]-0.05 : 1.5, h: 0.3,
        fontSize: 10, bold: true, color: C.navy,
        fontFace: "Calibri", margin: 0
      });
    });
    s.addShape(pres.shapes.LINE, {
      x: 0.55, y: 4.38, w: 12.3, h: 0,
      line: { color: "D0DDE8", width: 1 }
    });

    const rows = [
      ["social_buffer_index",        "Labor Income Share", "+0.264", "0.077", "3.42",  "0.001", "***", C.mint],
      ["gdp_growth_pct",             "Labor Income Share", "−0.054", "0.019", "−2.86", "0.004", "***", C.rose],
      ["economic_resilience",        "Unemployment Rate",  "−2.950", "0.785", "−3.76", "0.000", "***", C.mint],
      ["govt_expenditure_pct_gdp",   "Unemployment Rate",  "+0.033", "0.008", "+4.25", "0.000", "***", C.rose],
      ["ai_exposure_proxy",          "Labor Mkt Stress",  "+0.143", "0.083", "+1.73", "0.084", "*",   C.rose],
      ["tech_vulnerability_index",   "Labor Mkt Stress",  "−0.214", "0.106", "−2.02", "0.043", "**",  C.mint],
      ["economic_resilience",        "Labor Mkt Stress",  "−6.448", "1.266", "−5.09", "0.000", "***", C.mint],
      ["gini_index",                 "Labor Mkt Stress",  "+0.100", "0.026", "+3.90", "0.000", "***", C.rose],
    ];

    rows.forEach((r, i) => {
      const yy = 4.45 + i * 0.35;
      const bg = i % 2 === 0 ? "F8FAFB" : C.white;
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.55, y: yy - 0.02, w: 12.3, h: 0.34,
        fill: { color: bg }, line: { color: bg }
      });
      const vals = [r[0], r[1], r[2], r[3], r[4], r[5]];
      vals.forEach((v, j) => {
        s.addText(v, {
          x: colX[j], y: yy, w: colX[j+1] ? colX[j+1]-colX[j]-0.05 : 1.5, h: 0.3,
          fontSize: 10, color: j === 2 ? r[7] : C.slate,
          bold: j === 2, fontFace: "Calibri", margin: 0
        });
      });
      s.addText(r[6], {
        x: colX[6], y: yy, w: 0.6, h: 0.3,
        fontSize: 11, bold: true, color: r[7],
        fontFace: "Calibri", margin: 0
      });
    });

    s.addNotes("TWFE model with entity + time FE. Hausman confirms FE over RE. All SE clustered at country level.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 5 — HISI INDEX
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.cardBg }, line: { color: C.cardBg }
    });
    s.addText("HISI — HUMAN INCOME STABILITY INDEX", {
      x: 0.5, y: 0.18, w: 11, h: 0.55,
      fontSize: 26, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("A novel composite metric · PCA-derived weights · Normalized 0–100", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    // Formula card
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.4, y: 1.18, w: 12.5, h: 1.45,
      fill: { color: C.cardBg }, line: { color: C.teal, transparency: 50 },
      rectRadius: 0.1, shadow: makeShadow()
    });
    s.addText("HISI\u1d62\u209c = w\u2081 \u00b7 (Labor_Share / Gini)\u207f\u1d52\u02b3\u1d50 + w\u2082 \u00b7 (Social_Protection)\u207f\u1d52\u02b3\u1d50 \u2212 w\u2083 \u00b7 (AI_Displacement_Risk)\u207f\u1d52\u02b3\u1d50", {
      x: 0.65, y: 1.3, w: 12.0, h: 0.65,
      fontSize: 18, bold: true, color: C.teal,
      fontFace: "Cambria", margin: 0
    });
    s.addText("Weights w\u2081, w\u2082, w\u2083 derived via Principal Component Analysis — mathematically unbiased, variance-maximizing", {
      x: 0.65, y: 2.0, w: 12.0, h: 0.35,
      fontSize: 12, italic: true, color: C.slateLight,
      fontFace: "Calibri", margin: 0
    });

    // Component cards
    const comps = [
      { label: "Component A", sub: "Income Equity", formula: "labor_income_share / gini_index", color: C.gold },
      { label: "Component B", sub: "Social Buffer", formula: "social_protection + health + education spend", color: C.mint },
      { label: "Component C", sub: "AI Displacement Risk", formula: "ai_exposure × (1 − tech_vulnerability/100)", color: C.rose },
    ];
    comps.forEach((c, i) => {
      const x = 0.4 + i * 4.3;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 2.78, w: 4.1, h: 1.55,
        fill: { color: C.cardBg }, line: { color: c.color, transparency: 30 },
        rectRadius: 0.1, shadow: makeShadow()
      });
      s.addText(c.label, {
        x: x + 0.15, y: 2.88, w: 3.8, h: 0.3,
        fontSize: 12, bold: true, color: c.color,
        fontFace: "Calibri", margin: 0
      });
      s.addText(c.sub, {
        x: x + 0.15, y: 3.2, w: 3.8, h: 0.25,
        fontSize: 11, color: C.white,
        fontFace: "Calibri", margin: 0
      });
      s.addText(c.formula, {
        x: x + 0.15, y: 3.5, w: 3.8, h: 0.65,
        fontSize: 10, italic: true, color: C.slateLight,
        fontFace: "Calibri", margin: 0
      });
    });

    // Range bar
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.4, y: 4.52, w: 12.5, h: 0.7,
      fill: { color: C.cardBg }, line: { color: "2A3F5A" },
      rectRadius: 0.08
    });
    s.addText("HISI Range:  19.5 (Qatar, lowest)  ──────────────────────────────────────────  88.5 (Iceland, highest)  |  Global Mean: ~50", {
      x: 0.6, y: 4.63, w: 12.2, h: 0.48,
      fontSize: 12, color: C.white, fontFace: "Calibri", margin: 0
    });

    // Top/Bottom countries
    const wins   = ["ISL 88.5","SVN 88.1","BEL 85.3","DNK 82.8","NLD 78.9","FIN 75.6","SWE 75.4","AUT 75.0"];
    const falls  = ["QAT 19.5","VEN 21.5","GAB 22.0","MEX 23.2","TJK 23.3","PAN 24.9","CIV 25.0","BRN 25.4"];

    const groupCards = [
      { title: "TOP HISI COUNTRIES", data: wins,  col: C.mint,  icon: iWin,  x: 0.4 },
      { title: "LOWEST HISI COUNTRIES", data: falls, col: C.rose,  icon: iFall, x: 6.75 },
    ];
    groupCards.forEach(gc => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: gc.x, y: 5.38, w: 6.15, h: 1.75,
        fill: { color: C.cardBg }, line: { color: gc.col, transparency: 50 },
        rectRadius: 0.1, shadow: makeShadow()
      });
      s.addImage({ data: gc.icon, x: gc.x + 0.15, y: 5.45, w: 0.3, h: 0.3 });
      s.addText(gc.title, {
        x: gc.x + 0.52, y: 5.45, w: 5.5, h: 0.3,
        fontSize: 11, bold: true, color: gc.col,
        fontFace: "Calibri", charSpacing: 1, margin: 0
      });
      gc.data.forEach((d, i) => {
        const col2 = i < 4 ? gc.x + 0.2 : gc.x + 3.15;
        const row  = i < 4 ? i : i - 4;
        s.addText(d, {
          x: col2, y: 5.88 + row * 0.3, w: 2.7, h: 0.28,
          fontSize: 10, color: C.white, fontFace: "Calibri", margin: 0
        });
      });
    });

    s.addNotes("HISI construction: PCA weights, normalized 0-100, clustered via GMM into 3 segments.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 6 — THREE CLUSTERS
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.lightBg };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    s.addText("GLOBAL SEGMENTATION — THREE DESTINIES", {
      x: 0.5, y: 0.18, w: 12, h: 0.55,
      fontSize: 26, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("Gaussian Mixture Model clustering · 264 countries · 6,774 country-year observations", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    const clusters = [
      {
        icon: iWinW, bg: C.gold, label: "THE WINS",
        count: "90 Countries", share: "34%",
        desc: "High Digital Capital · Stable HISI trajectory · Strong institutional buffers · Advanced R&D ecosystems",
        examples: "Iceland · Slovenia · Belgium · Denmark · Netherlands · Finland · Sweden · Austria",
        stats: [["Avg HISI", "75–88"], ["AI Exposure", "High"], ["Social Buffer", "Very High"], ["R²", "0.421"]],
        iconImg: iWin
      },
      {
        icon: iFallW, bg: C.rose, label: "THE FALLS",
        count: "196 Countries", share: "74%",
        desc: "High Task Displacement · Low institutional buffers · Inadequate social protection · Structural vulnerability",
        examples: "Tajikistan · Côte d'Ivoire · Belarus · Sub-Saharan cluster · Low-income economies",
        stats: [["Avg HISI", "20–45"], ["AI Exposure", "Low–Med"], ["Social Buffer", "Low"], ["Gini Effect", "+0.100***"]],
        iconImg: iFall
      },
      {
        icon: iAdaptW, bg: C.mint, label: "THE ADAPTERS",
        count: "169 Countries", share: "64%",
        desc: "High AI Exposure + High Institutional Lifelines · Medium HISI · Transition economies with reform capacity",
        examples: "Moldova · Czech Republic · India · Puerto Rico · Latin America · Eastern Europe",
        stats: [["Avg HISI", "45–75"], ["AI Exposure", "Med–High"], ["Social Buffer", "Medium"], ["Tech Vuln", "−0.214**"]],
        iconImg: iAdapt
      },
    ];

    clusters.forEach((cl, i) => {
      const x = 0.4 + i * 4.3;
      // Main card
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.22, w: 4.1, h: 5.95,
        fill: { color: C.white }, line: { color: "E2EAF0" },
        rectRadius: 0.12, shadow: makeCardShadow()
      });
      // Header color
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.22, w: 4.1, h: 1.15,
        fill: { color: cl.bg }, line: { color: cl.bg },
        rectRadius: 0.12
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x, y: 1.9, w: 4.1, h: 0.47,
        fill: { color: cl.bg }, line: { color: cl.bg }
      });
      s.addImage({ data: cl.iconImg, x: x + 0.18, y: 1.3, w: 0.45, h: 0.45 });
      s.addText(cl.label, {
        x: x + 0.7, y: 1.3, w: 3.25, h: 0.48,
        fontSize: 20, bold: true, color: C.white,
        fontFace: "Cambria", margin: 0
      });
      s.addText(cl.count + " · " + cl.share + " of panel", {
        x: x + 0.15, y: 1.82, w: 3.8, h: 0.3,
        fontSize: 11, color: C.white,
        fontFace: "Calibri", margin: 0
      });
      // Description
      s.addText(cl.desc, {
        x: x + 0.15, y: 2.5, w: 3.8, h: 1.0,
        fontSize: 11, color: C.slate,
        fontFace: "Calibri", margin: 0
      });
      // Examples
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: x + 0.1, y: 3.62, w: 3.9, h: 0.88,
        fill: { color: C.lightBg }, line: { color: "D8E6F0" },
        rectRadius: 0.07
      });
      s.addText("EXAMPLES", {
        x: x + 0.2, y: 3.7, w: 3.7, h: 0.25,
        fontSize: 9, bold: true, color: cl.bg, charSpacing: 2,
        fontFace: "Calibri", margin: 0
      });
      s.addText(cl.examples, {
        x: x + 0.2, y: 3.97, w: 3.7, h: 0.48,
        fontSize: 10, color: C.navy,
        fontFace: "Calibri", margin: 0
      });
      // Stat grid
      cl.stats.forEach((st, j) => {
        const sx = x + 0.15 + (j % 2) * 1.95;
        const sy = 4.65 + Math.floor(j / 2) * 0.72;
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
          x: sx, y: sy, w: 1.85, h: 0.62,
          fill: { color: C.white }, line: { color: "E2EAF0" },
          rectRadius: 0.06, shadow: makeCardShadow()
        });
        s.addText(st[1], {
          x: sx + 0.05, y: sy + 0.04, w: 1.75, h: 0.3,
          fontSize: 13, bold: true, color: cl.bg,
          fontFace: "Cambria", align: "center", margin: 0
        });
        s.addText(st[0], {
          x: sx + 0.05, y: sy + 0.35, w: 1.75, h: 0.22,
          fontSize: 9, color: C.slate,
          fontFace: "Calibri", align: "center", margin: 0
        });
      });
    });

    s.addNotes("GMM clustering segments 264 countries. Note: countries appear in multiple clusters across years as conditions change.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 7 — FORECAST 2050
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.cardBg }, line: { color: C.cardBg }
    });
    s.addText("FORECASTING 2026–2050", {
      x: 0.5, y: 0.18, w: 11, h: 0.55,
      fontSize: 26, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("XGBoost Panel Forecaster · Rolling Expanding-Window CV · Two Divergent Scenarios", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    // Chart — HISI forecast bar chart
    s.addChart(pres.charts.BAR, [
      {
        name: "Aggressive Automation",
        labels: ["2026","2028","2030","2032","2034","2036","2038","2040","2042","2044","2046","2048","2050"],
        values: [45.2, 44.8, 44.4, 44.1, 43.8, 43.5, 43.2, 43.0, 42.9, 42.8, 42.7, 42.6, 42.6]
      },
      {
        name: "Equitable Adaptation",
        labels: ["2026","2028","2030","2032","2034","2036","2038","2040","2042","2044","2046","2048","2050"],
        values: [45.5, 45.9, 46.2, 46.6, 47.0, 47.3, 47.6, 47.9, 48.1, 48.3, 48.4, 48.5, 48.5]
      }
    ], {
      x: 0.4, y: 1.18, w: 7.8, h: 4.3,
      barDir: "col",
      chartColors: [C.rose, C.mint],
      chartArea: { fill: { color: C.cardBg }, roundedCorners: true },
      catAxisLabelColor: C.slateLight,
      valAxisLabelColor: C.slateLight,
      valGridLine: { color: "1E3A5A", size: 0.5 },
      catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendColor: C.white,
      showTitle: true, title: "Global Avg HISI Forecast by Scenario",
      titleColor: C.white, titleFontSize: 13,
      valAxisMinVal: 40, valAxisMaxVal: 52,
    });

    // Scenario cards
    const scenarios = [
      {
        icon: iTrendDn, label: "SCENARIO A",
        sub: "Aggressive Automation",
        col: C.rose,
        bullets: [
          "AI exposure +5%/yr",
          "Social buffer −2%/yr",
          "R&D investment flat",
          "Global HISI 2050: 42.6",
          "Net HISI decline: −5.9pts"
        ]
      },
      {
        icon: iTrendUp, label: "SCENARIO B",
        sub: "Equitable Adaptation",
        col: C.mint,
        bullets: [
          "AI exposure +3%/yr",
          "Social buffer +3%/yr",
          "R&D investment +1%/yr",
          "Global HISI 2050: 48.5",
          "Net HISI gain: +2.0pts"
        ]
      }
    ];

    scenarios.forEach((sc, i) => {
      const x = 8.45 + i * 2.35;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.18, w: 2.25, h: 4.3,
        fill: { color: C.cardBg }, line: { color: sc.col, transparency: 40 },
        rectRadius: 0.1, shadow: makeShadow()
      });
      s.addImage({ data: sc.icon, x: x + 0.85, y: 1.28, w: 0.45, h: 0.45 });
      s.addText(sc.label, {
        x: x + 0.1, y: 1.8, w: 2.05, h: 0.3,
        fontSize: 11, bold: true, color: sc.col, charSpacing: 1,
        fontFace: "Calibri", align: "center", margin: 0
      });
      s.addText(sc.sub, {
        x: x + 0.1, y: 2.12, w: 2.05, h: 0.3,
        fontSize: 10, color: C.slateLight,
        fontFace: "Calibri", align: "center", margin: 0
      });
      sc.bullets.forEach((b, j) => {
        s.addText(b, {
          x: x + 0.15, y: 2.55 + j * 0.45, w: 2.0, h: 0.4,
          fontSize: 10, color: j >= 3 ? sc.col : C.white,
          bold: j >= 3, fontFace: "Calibri", margin: 0
        });
      });
    });

    // XGBoost feature importance bar
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.4, y: 5.62, w: 12.5, h: 1.65,
      fill: { color: C.cardBg }, line: { color: C.teal, transparency: 60 },
      rectRadius: 0.1
    });
    s.addText("TOP XGBOOST FEATURES", {
      x: 0.6, y: 5.72, w: 12, h: 0.28,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 2,
      fontFace: "Calibri", margin: 0
    });
    const feats = [
      ["labor_income_share_pct", 30.6],
      ["labor_income_share_pct_ma3", 18.1],
      ["gini_index", 11.9],
      ["gini_index_lag1", 7.3],
      ["ai_exp_region_ECS", 5.8],
      ["social_buffer_index", 2.8],
      ["ai_exposure_proxy", 0.7],
    ];
    feats.forEach((f, i) => {
      const x = 0.6 + i * 1.78;
      const barH = f[1] / 30.6 * 0.55;
      s.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.3, y: 6.85 - barH, w: 1.0, h: barH,
        fill: { color: i === 0 ? C.teal : C.tealDark },
        line: { color: i === 0 ? C.teal : C.tealDark }
      });
      s.addText(f[0].replace(/_/g," "), {
        x, y: 6.93, w: 1.7, h: 0.28,
        fontSize: 8, color: C.slateLight,
        fontFace: "Calibri", align: "center", margin: 0
      });
    });

    s.addNotes("XGBoost trained with rolling CV. Scenario gap at 2050: 5.9 HISI points. Labor income share dominates feature importance.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 8 — KEY FINDINGS
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.lightBg };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    s.addText("KEY FINDINGS & POLICY IMPLICATIONS", {
      x: 0.5, y: 0.18, w: 12, h: 0.55,
      fontSize: 26, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("Evidence-based conclusions from 6,774 country-year observations", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    const findings = [
      {
        icon: iCheck, num: "01",
        title: "AI Raises Labor Market Stress",
        body: "ai_exposure_proxy coefficient: +0.143* (p=0.084) on labor market stress. Effect is heterogeneous — displacement in North America (+0.432*) vs. skill-upgrading in South Asia (−0.452**).",
        col: C.rose
      },
      {
        icon: iCheck, num: "02",
        title: "R&D Buffers the AI Shock",
        body: "tech_vulnerability_index: −0.214** (p=0.043). Countries with higher R&D investment systematically absorb AI disruption. Policy lever: invest in technological adaptation capacity.",
        col: C.teal
      },
      {
        icon: iCheck, num: "03",
        title: "Social Protection Stabilizes Income",
        body: "social_buffer_index: +0.264*** (p=0.001) on labor income share. Institutional safety nets are the strongest modifiable determinant of income stability in the AI transition.",
        col: C.mint
      },
      {
        icon: iCheck, num: "04",
        title: "Economic Resilience Dominates",
        body: "economic_resilience: −6.448*** (p<0.001) on labor market stress. Wealthier, more trade-open economies with productive labor forces absorb AI shocks with far lower stress outcomes.",
        col: C.gold
      },
      {
        icon: iCheck, num: "05",
        title: "Inequality Amplifies Vulnerability",
        body: "gini_index: +0.100*** (p<0.001). High inequality countries face compounding stress — unequal distribution of AI gains creates feedback loops that worsen labor market outcomes.",
        col: C.rose
      },
      {
        icon: iCheck, num: "06",
        title: "Scenario Gap Widens to 2050",
        body: "Under Equitable Adaptation vs. Aggressive Automation: global HISI diverges by 5.9 points by 2050. Policy choice today determines whether the world converges or diverges on income stability.",
        col: C.teal
      }
    ];

    findings.forEach((f, i) => {
      const col = i % 2 === 0 ? 0.4 : 6.85;
      const row = Math.floor(i / 2);
      const y = 1.22 + row * 2.0;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: col, y, w: 6.25, h: 1.82,
        fill: { color: C.white }, line: { color: "E2EAF0" },
        rectRadius: 0.1, shadow: makeCardShadow()
      });
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: col + 0.15, y: y + 0.18, w: 0.5, h: 0.5,
        fill: { color: f.col }, line: { color: f.col },
        rectRadius: 0.08
      });
      s.addText(f.num, {
        x: col + 0.15, y: y + 0.18, w: 0.5, h: 0.5,
        fontSize: 14, bold: true, color: C.white,
        fontFace: "Cambria", align: "center", valign: "middle", margin: 0
      });
      s.addText(f.title, {
        x: col + 0.78, y: y + 0.2, w: 5.35, h: 0.38,
        fontSize: 13, bold: true, color: C.navy,
        fontFace: "Calibri", margin: 0
      });
      s.addText(f.body, {
        x: col + 0.78, y: y + 0.62, w: 5.35, h: 1.05,
        fontSize: 11, color: C.slate,
        fontFace: "Calibri", margin: 0
      });
    });

    s.addNotes("Six findings. Findings 1-3 are the core AI labor market results. Findings 4-6 are structural amplifiers.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 9 — REGIONAL EVIDENCE
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.cardBg }, line: { color: C.cardBg }
    });
    s.addText("REGIONAL HETEROGENEITY", {
      x: 0.5, y: 0.18, w: 11, h: 0.55,
      fontSize: 26, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("AI exposure effects differ sharply by region — one-size-fits-all policy is insufficient", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    // Regional chart
    const regionData = [
      { region: "SAS", coef: -0.452, sig: "**",  n: 6,  r2: 0.183, col: C.mint },
      { region: "ECS", coef: -0.031, sig: "",    n: 57, r2: 0.124, col: C.slateLight },
      { region: "MEA", coef:  0.009, sig: "",    n: 23, r2: 0.135, col: C.slateLight },
      { region: "SSF", coef: -0.120, sig: "",    n: 48, r2: 0.019, col: C.slateLight },
      { region: "EAS", coef:  0.073, sig: "",    n: 37, r2: 0.097, col: C.slateLight },
      { region: "LCN", coef:  0.279, sig: "",    n: 42, r2: 0.175, col: C.gold },
      { region: "NAC", coef:  0.432, sig: "*",   n: 3,  r2: 0.366, col: C.rose },
    ];

    s.addChart(pres.charts.BAR, [{
      name: "AI Exposure Coefficient on Labor Income Share",
      labels: regionData.map(r => r.region),
      values: regionData.map(r => r.coef)
    }], {
      x: 0.4, y: 1.18, w: 7.5, h: 4.5,
      barDir: "bar",
      chartColors: regionData.map(r => r.col),
      chartArea: { fill: { color: C.cardBg }, roundedCorners: true },
      catAxisLabelColor: C.white,
      valAxisLabelColor: C.slateLight,
      valGridLine: { color: "1E3A5A", size: 0.5 },
      catGridLine: { style: "none" },
      showValue: true, dataLabelColor: C.white,
      showLegend: false,
      showTitle: true, title: "AI Exposure Coef by Region (TWFE on Labor Income Share)",
      titleColor: C.tealLight, titleFontSize: 11,
    });

    // Interpretation cards
    const interps = [
      {
        region: "NAC", label: "North America",
        col: C.rose, icon: iTrendDn,
        text: "Coef: +0.432* — AI exposure increases labor market stress. High-wage service displacement effect dominates.",
        countries: "USA, CAN (3 countries, R²=0.37)"
      },
      {
        region: "SAS", label: "South Asia",
        col: C.mint, icon: iTrendUp,
        text: "Coef: −0.452** — AI exposure reduces stress. Skill-upgrading in tech services outpaces displacement.",
        countries: "IND, BGD, PAK + 3 (R²=0.18)"
      },
      {
        region: "ECS", label: "Europe & C. Asia",
        col: C.slateLight, icon: iEqual,
        text: "Coef: −0.031 (ns) — Neutral effect. Strong institutional buffers absorb AI impact across 57 countries.",
        countries: "57 countries, R²=0.12"
      },
      {
        region: "LCN", label: "Latin America",
        col: C.gold, icon: iChart,
        text: "Coef: +0.279 (ns) — Positive but noisy. Informal labor markets amplify exposure risk.",
        countries: "42 countries, R²=0.18"
      },
    ];
    interps.forEach((it, i) => {
      const y = 1.22 + i * 1.55;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 8.1, y, w: 4.82, h: 1.42,
        fill: { color: C.cardBg }, line: { color: it.col, transparency: 50 },
        rectRadius: 0.08, shadow: makeShadow()
      });
      s.addImage({ data: it.icon, x: 8.22, y: y + 0.12, w: 0.3, h: 0.3 });
      s.addText(it.region + " — " + it.label, {
        x: 8.58, y: y + 0.12, w: 4.2, h: 0.3,
        fontSize: 11, bold: true, color: it.col,
        fontFace: "Calibri", margin: 0
      });
      s.addText(it.text, {
        x: 8.22, y: y + 0.5, w: 4.6, h: 0.65,
        fontSize: 10, color: C.white,
        fontFace: "Calibri", margin: 0
      });
      s.addText(it.countries, {
        x: 8.22, y: y + 1.17, w: 4.6, h: 0.2,
        fontSize: 9, italic: true, color: C.slateLight,
        fontFace: "Calibri", margin: 0
      });
    });

    s.addNotes("Regional heterogeneity is the most policy-relevant finding. Same AI exposure, opposite effects by region.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 10 — PIPELINE & TECH STACK
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.lightBg };

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: W, h: 1.05,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    s.addText("PRODUCTION PIPELINE & TECHNOLOGY STACK", {
      x: 0.5, y: 0.18, w: 12, h: 0.55,
      fontSize: 26, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });
    s.addText("End-to-end reproducible research infrastructure · Python 3.10 · SQLite · Streamlit", {
      x: 0.5, y: 0.68, w: 12, h: 0.28,
      fontSize: 12, color: C.tealLight, fontFace: "Calibri", margin: 0
    });

    // Pipeline flow
    const phases = [
      { ph: "Phase 1", label: "Data\nArchitecture", tools: "wbgapi · ILOSTAT\nSQLite · KNNImputer", col: C.teal },
      { ph: "Phase 2", label: "Feature\nEngineering", tools: "pandas · numpy\n82 features built", col: C.gold },
      { ph: "Phase 3", label: "Econometric\nModeling", tools: "linearmodels · scipy\nTWFE · Hausman · IV", col: C.mint },
      { ph: "Phase 4", label: "HISI Index\nConstruction", tools: "sklearn PCA\nGMM Clustering", col: C.tealLight },
      { ph: "Phase 5", label: "Forecasting\n2050", tools: "XGBoost · rolling CV\nScenario simulation", col: C.gold },
      { ph: "Phase 6", label: "Dashboard\n& Portfolio", tools: "Streamlit · Plotly\nREADME · LinkedIn", col: C.rose },
    ];

    phases.forEach((p, i) => {
      const x = 0.4 + i * 2.08;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.22, w: 1.92, h: 2.55,
        fill: { color: C.white }, line: { color: "E2EAF0" },
        rectRadius: 0.1, shadow: makeCardShadow()
      });
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.22, w: 1.92, h: 0.48,
        fill: { color: p.col }, line: { color: p.col }, rectRadius: 0.1
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x, y: 1.52, w: 1.92, h: 0.18,
        fill: { color: p.col }, line: { color: p.col }
      });
      s.addText(p.ph, {
        x: x + 0.05, y: 1.27, w: 1.82, h: 0.3,
        fontSize: 11, bold: true, color: C.white,
        fontFace: "Calibri", align: "center", margin: 0
      });
      s.addText(p.label, {
        x: x + 0.08, y: 1.8, w: 1.76, h: 0.65,
        fontSize: 12, bold: true, color: C.navy,
        fontFace: "Calibri", align: "center", margin: 0
      });
      s.addText(p.tools, {
        x: x + 0.08, y: 2.52, w: 1.76, h: 0.9,
        fontSize: 10, color: C.slate,
        fontFace: "Calibri", align: "center", margin: 0
      });
      // Arrow between phases
      if (i < 5) {
        s.addShape(pres.shapes.LINE, {
          x: x + 1.92, y: 2.5, w: 0.16, h: 0,
          line: { color: C.teal, width: 2 }
        });
      }
    });

    // Tech stack grid
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.4, y: 3.98, w: 12.5, h: 3.22,
      fill: { color: C.white }, line: { color: "E2EAF0" },
      rectRadius: 0.1, shadow: makeCardShadow()
    });
    s.addText("FULL TECHNOLOGY STACK", {
      x: 0.65, y: 4.1, w: 12, h: 0.3,
      fontSize: 13, bold: true, color: C.navy, charSpacing: 1,
      fontFace: "Calibri", margin: 0
    });

    const techCols = [
      { cat: "Data Ingestion", items: ["wbgapi (World Bank)", "ILOSTAT REST API", "SQLAlchemy ORM", "SQLite relational DB"] },
      { cat: "Processing", items: ["pandas / numpy", "scikit-learn KNN", "Rolling imputation", "Feature engineering"] },
      { cat: "Econometrics", items: ["linearmodels TWFE", "statsmodels IV/2SLS", "scipy Hausman test", "Clustered SE"] },
      { cat: "ML & Forecast", items: ["XGBoost regressor", "Expanding-window CV", "GMM clustering", "PCA weights"] },
      { cat: "Deployment", items: ["Streamlit dashboard", "Plotly choropleth", "GitHub repository", "Live web app"] },
    ];
    techCols.forEach((tc, i) => {
      const x = 0.6 + i * 2.42;
      s.addText(tc.cat, {
        x, y: 4.5, w: 2.2, h: 0.28,
        fontSize: 11, bold: true, color: C.tealDark,
        fontFace: "Calibri", margin: 0
      });
      tc.items.forEach((item, j) => {
        s.addText(item, {
          x, y: 4.85 + j * 0.52, w: 2.2, h: 0.45,
          fontSize: 10, color: C.slate,
          fontFace: "Calibri", margin: 0,
          bullet: true
        });
      });
    });

    s.addNotes("Full pipeline: 6 phases, end-to-end reproducible. SQLite + Python for portability. Streamlit for live deployment.");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SLIDE 11 — CLOSING / CONTACT
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    // Left content panel
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: 7.5, h: H,
      fill: { color: C.navy }, line: { color: C.navy }
    });
    // Right accent panel
    s.addShape(pres.shapes.RECTANGLE, {
      x: 7.5, y: 0, w: 5.8, h: H,
      fill: { color: C.tealDark }, line: { color: C.tealDark }
    });

    s.addText("CONCLUSION", {
      x: 0.55, y: 0.5, w: 6.5, h: 0.4,
      fontSize: 15, bold: true, color: C.teal, charSpacing: 4,
      fontFace: "Calibri", margin: 0
    });
    s.addText("The future of work\nis a policy choice.", {
      x: 0.55, y: 0.95, w: 6.8, h: 1.6,
      fontSize: 42, bold: true, color: C.white,
      fontFace: "Cambria", margin: 0
    });

    s.addText("This research demonstrates that AI's labor market impact is neither uniform nor inevitable. The 5.9-point HISI gap between our 2050 scenarios is determined entirely by institutional choices made today: social protection investment, R&D commitment, and equitable distribution of AI-era productivity gains.", {
      x: 0.55, y: 2.65, w: 6.8, h: 1.6,
      fontSize: 13, color: C.slateLight,
      fontFace: "Calibri", margin: 0
    });

    // Three takeaways
    const takes = [
      { t: "Protect", b: "Expand social buffers now — every 1pt increase in social_buffer_index yields +0.264pts on labor income share" },
      { t: "Invest", b: "R&D is the shock absorber — tech_vulnerability_index coefficient: −0.214** confirms this" },
      { t: "Measure", b: "HISI provides a unified, reproducible metric to track AI-era income stability across 264 countries" },
    ];
    takes.forEach((tk, i) => {
      const y = 4.38 + i * 0.9;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.55, y, w: 6.8, h: 0.78,
        fill: { color: C.cardBg }, line: { color: C.teal, transparency: 60 },
        rectRadius: 0.08
      });
      s.addText(tk.t + ":", {
        x: 0.75, y: y + 0.08, w: 1.0, h: 0.58,
        fontSize: 13, bold: true, color: C.teal,
        fontFace: "Calibri", margin: 0
      });
      s.addText(tk.b, {
        x: 1.75, y: y + 0.08, w: 5.4, h: 0.6,
        fontSize: 11, color: C.white,
        fontFace: "Calibri", margin: 0
      });
    });

    // Right panel — author & links
    s.addText("DAIPAYAN\nCHATTERJEE", {
      x: 7.75, y: 0.55, w: 5.3, h: 1.3,
      fontSize: 30, bold: true, color: C.white,
      fontFace: "Cambria", align: "center", margin: 0
    });
    s.addText("M.Sc. Economics\nQuantitative Economics & Econometrics", {
      x: 7.75, y: 1.9, w: 5.3, h: 0.65,
      fontSize: 13, color: C.tealLight,
      fontFace: "Calibri", align: "center", margin: 0
    });
    s.addShape(pres.shapes.LINE, {
      x: 8.5, y: 2.7, w: 3.8, h: 0,
      line: { color: C.teal, width: 1.5 }
    });

    const links = [
      { icon: iEmail,  label: "daipayanchatterjee01@gmail.com" },
      { icon: iGithub, label: "github.com/dchatterjee01-prog" },
      { icon: iGlobe,  label: "economics-of-abundant-intelligence\n.streamlit.app" },
      { icon: iUni,    label: "GitHub: dchatterjee01-prog/economics-\nof-abundant-intelligence" },
    ];
    links.forEach((lk, i) => {
      const y = 2.95 + i * 1.05;
      s.addImage({ data: lk.icon, x: 7.85, y: y + 0.12, w: 0.3, h: 0.3 });
      s.addText(lk.label, {
        x: 8.22, y: y + 0.08, w: 5.0, h: 0.6,
        fontSize: 11, color: C.white,
        fontFace: "Calibri", margin: 0
      });
    });

    // Final stat row
    const finalNums = [["264", "Countries"], ["6,774", "Observations"], ["82", "Features"], ["2050", "Horizon"]];
    finalNums.forEach((fn, i) => {
      const x = 7.65 + i * 1.4;
      s.addText(fn[0], {
        x, y: 7.0, w: 1.35, h: 0.28,
        fontSize: 18, bold: true, color: C.teal,
        fontFace: "Cambria", align: "center", margin: 0
      });
      s.addText(fn[1], {
        x, y: 7.28, w: 1.35, h: 0.18,
        fontSize: 9, color: C.slateLight,
        fontFace: "Calibri", align: "center", margin: 0
      });
    });

    s.addNotes("Closing slide. Three policy imperatives: Protect, Invest, Measure. All grounded in empirical coefficients.");
  }

  // ── Write file ─────────────────────────────────────────────────────────────
  const outPath = "/mnt/user-data/outputs/Economics_of_Abundant_Intelligence_Daipayan_Chatterjee.pptx";
  await pres.writeFile({ fileName: outPath });
  console.log("✅ Presentation saved:", outPath);
}

buildPresentation().catch(err => {
  console.error("Build failed:", err);
  process.exit(1);
});
