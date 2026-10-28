export type User = {
  id: string;
  username: string;
  display_name: string;
  memberships: { role: string; bureau: string | null; region: string | null }[];
};
export type Session = {
  user: User;
  csrf_token: string;
  expires_at: string;
  synthetic: true;
};
export type Institution = {
  id: string;
  name: string;
  city: string;
  region: string;
  version: number;
  synthetic: boolean;
  aliases: { alias: string; provenance: string }[];
};
export type CaseRecord = {
  id: string;
  institution_id: string;
  institution_name: string;
  city: string;
  owner: { id: string; name: string; bureau: string };
  subject: string;
  category: string | null;
  lifecycle: string;
  received_date: string;
  expected_disposal_date: string | null;
  due_at: string | null;
  next_action: string;
  version: number;
  synthetic: boolean;
  can_read_narrative: boolean;
  can_assign: boolean;
  identity_status: string;
  last_action: string;
  last_action_at: string;
  escalation_level: number;
  transfer_state: string;
  description?: string | null;
  original_institution_text?: string | null;
  original_submission?: Record<string, unknown> | null;
  original_sha256?: string | null;
  complainant?: { token: string; contact: string | null } | null;
  attachments?: {
    id: string;
    filename: string;
    size: number;
    type: string;
    sha256: string;
    integrity_checked_at: string | null;
    download_url: string;
  }[];
  history?: {
    id: string;
    type: string;
    at: string;
    actor: string;
    reason: string;
    before_version: number;
    after_version: number;
  }[];
  assignments?: {
    owner: string;
    bureau: string;
    from: string;
    to: string | null;
    reason: string;
  }[];
  actions?: {
    kind: string;
    payload: Record<string, unknown> | null;
    version: number;
  }[];
  resolutions?: { id: string; text: string; at: string; version: number }[];
  pending_transfer?: string | null;
  capabilities?: Record<string, boolean>;
  can_review_pair?: boolean;
  facts?: Record<string, unknown>;
  identity_history?: {
    previous_institution_id: string;
    institution_id: string;
    original_text: string | null;
    reason: string;
    provenance: string;
    actor: string;
    version: number;
  }[];
};
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}
export async function api<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, { ...options, credentials: "same-origin" });
  } catch (error) {
    if (options.signal?.aborted) throw error;
    throw new ApiError(
      0,
      "The local server could not be reached. No success is confirmed. Retry after checking the connection.",
    );
  }
  if (!response.ok) {
    let message = "Request could not be completed.";
    try {
      const data = await response.json();
      message =
        typeof data.detail === "string"
          ? data.detail
          : "Check the required fields and their format.";
    } catch {
      /* preserve safe generic error */
    }
    if (response.status === 401 && !url.startsWith("/api/auth/"))
      window.dispatchEvent(new Event("session-expired"));
    throw new ApiError(response.status, message);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}
