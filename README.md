# CarbonIQ frontend

A responsive, evidence-aware carbon-credit intelligence interface created for the CarbonIQ academic MVP and designed for Framer. It includes the complete buyer journey and curator entry point described in `PROJECT_DOCUMENTATION.md`:

- project discovery, filtering and two-to-four project comparison;
- transparent CarbonIQ, quality, impact, risk and evidence-confidence views;
- buyer preferences, recommendations with reasons and trade-offs;
- diversified portfolio construction with budget, availability, project-count and concentration constraints;
- saved portfolios, simulated orders and report download;
- project-document assistant states and curator import/status UI;
- explicit provenance, synthetic-data, AI and non-transaction disclosures.

## Run locally

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:3000`. The default is the clearly labelled 30-project synthetic demonstration. See `BACKEND_INTEGRATION.md` to connect FastAPI.

## Verify

```bash
npm run typecheck
npm test
npm run build
```

## Framer

The connected Framer project contains the production-ready `CarbonIQApp.tsx` code component on Desktop, Tablet, and Phone breakpoints. Its property controls expose the data mode, API base URL, full-workspace URL, and signal color. API mode calls `GET /projects` directly and shows an explicit connection error instead of silently substituting demonstration data.

`framer-src/CarbonIQCanvas.tsx` is the local source of that Framer component. `npm run framer:bundle` also generates the complete application as a portable single-file artifact in `framer/CarbonIQ.tsx` for reference or future embedding.

`framer-src/framer.d.ts` and `framer-src/tsconfig.json` provide VS Code-only declarations for Framer's editor module. They prevent false diagnostics for `from "framer"` and property-control callbacks; Framer itself supplies the real module at runtime. If VS Code keeps showing an old diagnostic after pulling the files, run **TypeScript: Restart TS Server** from the Command Palette.
