import { readFile, writeFile } from "node:fs/promises";

const sourceRoot = "apps/web/src/carboniq";
const withExtensions = (content) => content
  .replaceAll('"./domain"', '"./domain.ts"')
  .replaceAll('"./api"', '"./api.ts"')
  .replaceAll('"./demo"', '"./demo.ts"')
  .replaceAll('"./Globe"', '"./Globe.tsx"')
  .replaceAll('"./styles"', '"./styles.ts"');

const specs = await Promise.all([
  ["Veik8YX", "domain.ts", `${sourceRoot}/domain.ts`],
  ["aYEIoKG", "api.ts", `${sourceRoot}/api.ts`],
  ["dijx0ie", "demo.ts", `${sourceRoot}/demo.ts`],
  ["V6KrNFV", "Globe.tsx", `${sourceRoot}/Globe.tsx`],
  ["fTPoXvS", "styles.ts", `${sourceRoot}/styles.ts`],
  ["WCPztwo", "CarbonIQ.tsx", `${sourceRoot}/CarbonIQ.tsx`],
].map(async ([id, name, path]) => ({ id, name, content: withExtensions(await readFile(path, "utf8")) })));
const wrapper = withExtensions((await readFile("framer-src/CarbonIQFramer.tsx", "utf8"))
  .replace("../apps/web/src/carboniq/CarbonIQ", "./CarbonIQ.tsx"));
specs.push({ id: "cFHM6Da", name: "CarbonIQApp.tsx", content: wrapper });

const script = `const specs = ${JSON.stringify(specs)}
const results = []
for (const spec of specs) {
  let file = await framer.getCodeFile(spec.id)
  file = await file.setFileContent(spec.content)
  results.push({ id: file.id, path: await file.path, errors: (await file.typecheck({ strict: true })).slice(0, 6), exports: await file.exports })
}
console.log(JSON.stringify(results, null, 2))
`;

await writeFile("framer/update-source-modules.js", script);
console.log("Generated framer/update-source-modules.js");
