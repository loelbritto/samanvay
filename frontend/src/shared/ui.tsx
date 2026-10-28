import type { ReactNode } from "react";
import { Icon } from "./Icon";
export { Icon } from "./Icon";

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function PageHeading({
  title,
  children,
  action,
}: {
  eyebrow?: string;
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <header className="page-heading">
      <div>
        <h1 tabIndex={-1} id="page-title">
          {title}
        </h1>
        <p className="subtitle">{children}</p>
      </div>
      {action}
    </header>
  );
}
export function Notice({
  children,
  tone = "blue",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return (
    <div className={`notice ${tone}`}>
      <Icon name="info" />
      <div>{children}</div>
    </div>
  );
}
export function EmptyState({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <Icon name="cases" size={28} />
      <h2>{title}</h2>
      <p>{children}</p>
      {action}
    </div>
  );
}
