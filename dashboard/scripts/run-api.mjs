import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");
const isWindows = process.platform === "win32";

const venvPython = path.join(
  repoRoot,
  ".venv",
  isWindows ? "Scripts\\python.exe" : "bin/python",
);
const apiScript = path.join(repoRoot, "scripts", "run_api_only.py");

if (!fs.existsSync(venvPython)) {
  console.error(
    `[api] Python venv not found at ${venvPython}\n` +
    `[api] Create it from the repo root:  python -m venv .venv && .venv\\Scripts\\pip install -r requirements.txt`
  );
  process.exit(1);
}

const proc = spawn(venvPython, [apiScript], {
  cwd: repoRoot,
  stdio: "inherit",
});

const forwardSignal = (signal) => () => proc.kill(signal);
process.on("SIGINT", forwardSignal("SIGINT"));
process.on("SIGTERM", forwardSignal("SIGTERM"));
proc.on("close", (code) => process.exit(code ?? 0));
