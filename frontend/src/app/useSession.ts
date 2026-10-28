import { useEffect, useState } from "react";
import { api } from "../api";
import type { Session } from "../api";

export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    api<Session>("/api/auth/session", { signal: controller.signal })
      .then((value) => {
        if (!controller.signal.aborted) {
          setSession(value);
          setError("");
        }
      })
      .catch((error) => {
        if (!controller.signal.aborted) {
          setSession(null);
          setError(error.status === 401 ? "" : error.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [revision]);
  useEffect(() => {
    const expired = () => {
      setSession(null);
      setError(
        "Your session ended. Sign in again to continue. Unsaved changes have not been recorded.",
      );
    };
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, []);
  async function logout() {
    if (!session) return;
    try {
      await api("/api/auth/logout", {
        method: "POST",
        headers: { "X-CSRF-Token": session.csrf_token },
      });
      setSession(null);
      setError("");
    } catch (error) {
      setError((error as Error).message);
    }
  }
  return {
    session,
    loading,
    error,
    logout,
    retry: () => setRevision((v) => v + 1),
    login: (value: Session) => {
      setSession(value);
      setError("");
    },
  };
}
