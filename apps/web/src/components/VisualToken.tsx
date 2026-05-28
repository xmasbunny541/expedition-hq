import type { Agent } from "../types";

export const stateLabel: Record<string, string> = {
  awake: "Awake",
  on_call: "On Call",
  dormant: "Dormant",
  blocked: "Blocked",
  test_mode: "Test Mode",
  temporary_route: "Temporary Route",
  fragile_link: "Fragile Link",
  blueprint: "Blueprint",
  sleeping: "Sleeping",
  stable: "Stable",
  working_local: "Working Local"
};

const classToken: Record<string, string> = {
  specialist: "AI",
  candidate_specialist: "AI",
  automation: "AU",
  construct: "CT",
  route_bridge: "RT",
  interface: "UI",
  station: "ST",
  archive: "AR",
  data_source: "DS"
};

export function displayName(agent: Agent) {
  return agent.visual_name || agent.display_name;
}

export function visualTokenLabel(agent?: Agent, fallback = "HQ") {
  if (!agent) return fallback;
  return classToken[agent.visual_class] ?? fallback;
}

export function VisualToken({
  agent,
  label,
  kind = agent?.allowed_as_little_guy ? "specialist" : "system",
  state = agent?.ui_state ?? "stable",
  size = "normal"
}: {
  agent?: Agent;
  label?: string;
  kind?: "specialist" | "system" | "room" | "report";
  state?: string;
  size?: "small" | "normal" | "large";
}) {
  return (
    <span className={`visual-token token-${kind} token-${size} state-${state}`}>
      {label ?? visualTokenLabel(agent)}
    </span>
  );
}
