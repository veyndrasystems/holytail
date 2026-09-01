#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

function readInput() {
  const raw = fs.readFileSync(0, "utf8").trim();
  if (!raw) {
    return {};
  }
  return JSON.parse(raw);
}

try {
  const input = readInput();
  const event = input.hook_event_name;
  if (event !== "SessionStart") {
    process.exit(0);
  }

  const pluginRoot = process.env.PLUGIN_ROOT
    || process.env.CLAUDE_PLUGIN_ROOT
    || path.resolve(__dirname, "..");
  const contextPath = path.join(
    pluginRoot,
    "skills",
    "holytail",
    "references",
    "routing-context.md",
  );
  const context = fs.readFileSync(contextPath, "utf8").trim();
  const output = {
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: context,
    },
  };

  output.systemMessage = "HOLYTAIL:ROUTING · evidence=hook_observed";

  process.stdout.write(JSON.stringify(output));
} catch (error) {
  process.stderr.write(`Holytail routing hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
