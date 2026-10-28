import { useEffect, useState } from "react";
import { api } from "../api";

/** Each request owns its cancellation signal. A previous URL can never publish into a new view. */
export function useResource<T>(url: string) {
  const [result, setResult] = useState<{
    url: string;
    data: T | null;
    error: string;
    loading: boolean;
  }>({ url, data: null, error: "", loading: true });
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const changed = () => setRevision((value) => value + 1);
    window.addEventListener("case-records-changed", changed);
    window.addEventListener("demo-clock-changed", changed);
    return () => {
      window.removeEventListener("case-records-changed", changed);
      window.removeEventListener("demo-clock-changed", changed);
    };
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    setResult({ url, data: null, error: "", loading: true });
    api<T>(url, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted)
          setResult({ url, data, error: "", loading: false });
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setResult({ url, data: null, error: error.message, loading: false });
      });
    return () => controller.abort();
  }, [url, revision]);
  return {
    ...(result.url === url ? result : { data: null, error: "", loading: true }),
    reload: () => setRevision((value) => value + 1),
  };
}
