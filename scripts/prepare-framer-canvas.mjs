import { readFile, writeFile } from "node:fs/promises";

const content = await readFile("framer-src/CarbonIQCanvas.tsx", "utf8");
await writeFile("framer/upload-canvas.js", `let file = await framer.getCodeFile("cFHM6Da")\nfile = await file.setFileContent(${JSON.stringify(content)})\nconsole.log(JSON.stringify({ id:file.id, path:await file.path, errors:await file.typecheck({ strict:true }), lint:await file.lint(), exports:await file.exports }, null, 2))\n`);
console.log("Generated framer/upload-canvas.js");
