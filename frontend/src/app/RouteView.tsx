import type { Session } from "../api";
import { parseRoute } from "./navigation";
import { WorkQueue } from "../features/workspace/WorkQueue";
import {
  LiveCases,
  LiveDetail,
  LiveInstitutions,
  LiveIntake,
  Unavailable,
} from "../screens/LiveScreens";
import { TransferInbox } from "../screens/WorkflowScreens";
import {
  LiveCoordination,
  IdentityTools,
} from "../screens/CoordinationScreens";
import {
  LiveReports,
  LiveNotifications,
  LiveSettings,
} from "../screens/OperationsScreens";

export function RouteView({
  route,
  session,
}: {
  route: ReturnType<typeof parseRoute>;
  session: Session;
}) {
  const { section, id, timeline, query } = route;
  switch (section) {
    case "overview":
      return <WorkQueue session={session} />;
    case "cases":
      return id === "new" ? (
        <LiveIntake session={session} />
      ) : id ? (
        <LiveDetail id={id} timeline={timeline} session={session} />
      ) : (
        <LiveCases query={new URLSearchParams(query)} session={session} />
      );
    case "transfers":
      return <TransferInbox session={session} />;
    case "coordination":
      return (
        <LiveCoordination
          session={session}
          institutionId={
            new URLSearchParams(query).get("institution") ?? undefined
          }
          initialView={
            new URLSearchParams(query).get("view") === "reviews"
              ? "reviews"
              : "plans"
          }
        />
      );
    case "institutions":
      return (
        <>
          <LiveInstitutions id={id} />
          <IdentityTools session={session} institutionId={id} />
        </>
      );
    case "reports":
      return <LiveReports />;
    case "notifications":
      return <LiveNotifications session={session} />;
    case "settings":
      return <LiveSettings session={session} />;
    default:
      return <Unavailable section={section} />;
  }
}
