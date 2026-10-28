export const navigation = [
  ["overview", "Work queue"],
  ["cases", "Complaints"],
  ["institutions", "Institutions"],
  ["coordination", "Coordination"],
  ["reports", "Reports"],
] as const;
export const utilities = [
  ["transfers", "Transfers"],
  ["notifications", "Notifications"],
  ["settings", "Help & demo"],
] as const;

export function parseRoute(hash: string) {
  const [path, query = ""] = (hash.replace(/^#/, "") || "/overview").split("?");
  const [section = "overview", id, tab] = path.split("/").filter(Boolean);
  return {
    section,
    id,
    timeline: tab === "timeline",
    query,
    label:
      [...navigation, ...utilities].find(([key]) => key === section)?.[1] ??
      "Page not found",
  };
}
