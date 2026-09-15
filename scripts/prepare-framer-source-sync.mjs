import { readFile, writeFile } from "node:fs/promises";

const sourceRoot = "apps/web/src/carboniq";
const dependencies = await Promise.all(
  ["domain.ts", "api.ts", "demo.ts", "Globe.tsx", "styles.ts"].map(async name => ({
    name,
    content: await readFile(`${sourceRoot}/${name}`, "utf8"),
  })),
);
const main = await readFile(`${sourceRoot}/CarbonIQ.tsx`, "utf8");
const wrapper = (await readFile("framer-src/CarbonIQFramer.tsx", "utf8"))
  .replace("../apps/web/src/carboniq/CarbonIQ", "./CarbonIQ");

const script = `const dependencies = ${JSON.stringify(dependencies)}
const results = []
for (const spec of dependencies) {
  const file = await framer.createCodeFile(spec.name, spec.content)
  results.push({ id: file.id, path: await file.path, errors: await file.typecheck({ strict: true }) })
}
let mainFile = await framer.getCodeFile("WCPztwo")
mainFile = await mainFile.setFileContent(${JSON.stringify(main)})
results.push({ id: mainFile.id, path: await mainFile.path, errors: await mainFile.typecheck({ strict: true }) })
let wrapperFile = await framer.getCodeFile("cFHM6Da")
wrapperFile = await wrapperFile.rename("CarbonIQApp.tsx")
wrapperFile = await wrapperFile.setFileContent(${JSON.stringify(wrapper)})
results.push({ id: wrapperFile.id, path: await wrapperFile.path, errors: await wrapperFile.typecheck({ strict: true }), exports: await wrapperFile.exports })
console.log(JSON.stringify(results, null, 2))
`;

await writeFile("framer/sync-source-files.js", script);
console.log("Generated framer/sync-source-files.js");
