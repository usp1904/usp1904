// noise-gate.js — OpenCode hook: stop noisy command output from filling context
// What it catches: installs, builds, test runs, progress bars (high-volume, low-signal)
// What it keeps: errors, failures, final summary (via tools/noise_gate.py)
// What it leaves: every other command untouched — short commands passthrough verbatim
import { join } from "path";

// Match noisy commands - keep list tight to avoid over-engineering (Rule 1)
const NOISY_RE = /(pip\s+install|pip3\s+install|uv\s+pip|npm\s+(install|ci|add|update)|yarn\s+(install|add)|pnpm\s+install|bun\s+install|npm\s+run\s+(build|test|start)|yarn\s+build|next\s+build|vite\s+build|tsc(\s|$)|webpack|esbuild|cargo\s+build|go\s+build|dotnet\s+build|docker\s+build|pytest|jest|vitest|mocha|playwright\s+test|python\s+-m\s+pytest|python\s+test_|npm\s+test|gradle|mvn\s+test|curl.*progress|wget)/i;

// PowerShell-safe wrapper: capture raw output to temp file, filter via Python, preserve exit code
function wrapNoisy(cmd, directory) {
  // Use forward slashes for Python path on Windows
  const filterPy = join(directory, "tools", "noise_gate.py").replace(/\\/g, "/");
  const tmp = `$env:TEMP + "\\opencode_noise_" + [guid]::NewGuid().ToString() + ".log"`;
  // Plumbing: run cmd, tee to raw file, then filter, then exit with original code
  // Use *>> to capture all streams (stdout+stderr) in PowerShell 7+
  return [
    `$__ng_tmp = ${tmp}`,
    `$__ng_filter = "${filterPy}"`,
    `& { ${cmd} } *>&1 | Tee-Object -FilePath $__ng_tmp | Out-Null; $__ng_ec = $LASTEXITCODE`,
    `python "$__ng_filter" "$__ng_tmp"; $__ng_filter_ec = $LASTEXITCODE`,
    // Prefer original exit code; if filter itself failed, surface that only if original succeeded
    `if ($__ng_ec -ne 0) { exit $__ng_ec } else { exit $__ng_filter_ec }`,
  ].join("; ");
}

export const NoiseGatePlugin = async ({ directory }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "bash") return;
      const cmd = output.args.command || "";
      // Leave everything else alone — if not noisy, do nothing
      if (!NOISY_RE.test(cmd)) return;
      // Don't double-wrap
      if (cmd.includes("noise_gate.py") || cmd.includes("__ng_tmp")) return;
      // Rewrite so only errors/failures/summary come back; drops progress spam
      output.args.command = wrapNoisy(cmd, directory);
    },
  };
};
