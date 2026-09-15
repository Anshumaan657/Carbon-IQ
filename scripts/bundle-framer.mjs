import { build } from "esbuild";
import { mkdir, writeFile } from "node:fs/promises";

const result = await build({
  entryPoints: ["framer-src/CarbonIQFramer.tsx"],
  bundle: true,
  write: false,
  format: "esm",
  platform: "browser",
  target: "es2020",
  jsx: "transform",
  external: ["react", "react-dom", "framer", "framer-motion"],
  legalComments: "none",
  minify: true,
  keepNames: false,
});

const banner = `// @ts-nocheck\n// Generated from the typed CarbonIQ frontend. The source is strictly type-checked before bundling.\n`;
const output = result.outputFiles[0].text;
const defaultExport = output.match(/export\{([A-Za-z_$][\w$]*) as default\};?\s*$/);
const reactImport = output.match(/import\*as ([A-Za-z_$][\w$]*) from["']react["']/);
const addControlsImport = output.match(/addPropertyControls as ([A-Za-z_$][\w$]*)/);
const controlTypeImport = output.match(/ControlType as ([A-Za-z_$][\w$]*)/);
if (!defaultExport || !reactImport || !addControlsImport || !controlTypeImport) {
  throw new Error("Could not locate the generated Framer wrapper symbols.");
}
const [, innerComponent] = defaultExport;
const [, reactName] = reactImport;
const [, addControlsName] = addControlsImport;
const [, controlTypeName] = controlTypeImport;
const footer = `/**
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight auto
 */
export default function CarbonIQApp(props) {
  return ${reactName}.createElement(${innerComponent}, props)
}
${addControlsName}(CarbonIQApp, {
  mode: { type: ${controlTypeName}.Enum, title: "Data mode", options: ["demo", "api"], optionTitles: ["Synthetic demo", "Live FastAPI"], defaultValue: "demo" },
  apiBaseUrl: { type: ${controlTypeName}.String, title: "API base URL", defaultValue: "http://localhost:8000/api/v1", hidden: props => props.mode !== "api" },
  initialView: { type: ${controlTypeName}.Enum, title: "Starting view", options: ["home", "catalogue", "preferences", "methodology"], optionTitles: ["Landing", "Catalogue", "Preferences", "Methodology"], defaultValue: "home" },
  accent: { type: ${controlTypeName}.Color, title: "Signal color", defaultValue: "#C9F58A" },
})
`;
const bundled = output.replace(/export\{[A-Za-z_$][\w$]* as default\};?\s*$/, footer);
const code = banner + bundled;
const existingId = process.env.FRAMER_CODE_FILE_ID;
const fileExpression = existingId
  ? `await framer.getCodeFile(${JSON.stringify(existingId)})`
  : `await framer.createCodeFile("CarbonIQ.tsx", code)`;
await mkdir("framer", { recursive: true });
await writeFile("framer/CarbonIQ.tsx", code);
await writeFile("framer/upload-to-framer.js", `const code = ${JSON.stringify(code)}\nlet file = ${fileExpression}\n${existingId ? "file = await file.setFileContent(code)" : ""}\nconst errors = await file.typecheck({ strict: true })\nconsole.log(JSON.stringify({ id: file.id, path: await file.path, exports: await file.exports, errors }, null, 2))\n`);
console.log(`Generated framer/CarbonIQ.tsx (${result.outputFiles[0].text.length.toLocaleString()} bytes)`);
