import { PageHeading } from "../shared/ui";

export function Unavailable({ section }: { section: string }) {
  return (
    <>
      <PageHeading eyebrow="Page not found" title="Let's get you back to work.">
        The page “{section}” is not available.
      </PageHeading>
      <a className="button primary" href="#/overview">
        Go to overview
      </a>
    </>
  );
}
