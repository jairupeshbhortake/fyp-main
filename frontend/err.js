const child = require("child_process");
const fs = require("fs");
try {
  const result = child.execSync("npx vite build", { encoding: "utf-8" });
  fs.writeFileSync("build_output.txt", result);
} catch (e) {
  const errOutput = (e.stdout ? e.stdout : "") + "\n" + (e.stderr ? e.stderr : "");
  fs.writeFileSync("build_output.txt", errOutput);
}
