import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));

const candidates = process.platform === "win32"
  ? [
      join(root, ".venv", "Scripts", "python.exe"),
      "python3",
      "python",
    ]
  : [
      join(root, ".venv", "bin", "python"),
      "python3",
      "python",
    ];

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Usage: node scripts/run-python.mjs <python args...>");
  process.exit(2);
}

for (const candidate of candidates) {
  if (candidate.includes(".venv") && !existsSync(candidate)) {
    continue;
  }

  const result = spawnSync(candidate, args, {
    stdio: "inherit",
    shell: false,
  });

  if (result.error) {
    if (result.error.code === "ENOENT") {
      continue;
    }
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 0);
}

console.error("No usable Python interpreter found. Create .venv or install python3/python.");
process.exit(1);
