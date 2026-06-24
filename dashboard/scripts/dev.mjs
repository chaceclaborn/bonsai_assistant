import { spawn } from "child_process";
import open from "open";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dashboardRoot = path.resolve(__dirname, "..");

const concurrentlyBin = path.join(
  dashboardRoot, "node_modules", "concurrently", "dist", "bin", "concurrently.js",
);

const proc = spawn(
  process.execPath,
  [
    concurrentlyBin,
    "--kill-others-on-fail",
    "--prefix", "[{name}]",
    "-n", "api,web",
    "-c", "blue,green",
    "npm:dev:api",
    "npm:dev:web",
  ],
  {
    cwd: dashboardRoot,
    stdio: ["inherit", "pipe", "pipe"],
    env: process.env,
  },
);

let browserOpened = false;

const watchForReady = (chunk) => {
  const text = chunk.toString();
  process.stdout.write(text);

  if (browserOpened) return;
  const match = text.match(/Local:\s+http:\/\/localhost:(\d+)/);
  if (match) {
    browserOpened = true;
    const url = `http://localhost:${match[1]}`;
    open(url).catch((err) =>
      console.error(`[dev] Failed to open ${url}: ${err.message}`),
    );
  }
};

proc.stdout.on("data", watchForReady);
proc.stderr.on("data", (chunk) => process.stderr.write(chunk.toString()));

const forwardSignal = (signal) => () => proc.kill(signal);
process.on("SIGINT", forwardSignal("SIGINT"));
process.on("SIGTERM", forwardSignal("SIGTERM"));
proc.on("close", (code) => process.exit(code ?? 0));
