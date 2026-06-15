import { useEffect, useState } from "react";

import type { RealtimeAnomalyResponse } from "../types";

type State = {
  data: RealtimeAnomalyResponse | null;
  loading: boolean;
  error: string | null;
};

const INITIAL_STATE: State = {
  data: null,
  loading: true,
  error: null,
};

export function useRealtimeAnomalies(pollMs = 10000) {
  const [state, setState] = useState<State>(INITIAL_STATE);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response = await fetch("/api/v1/analytics/realtime-anomalies");
        if (!response.ok) {
          throw new Error(`Real-time anomaly request failed with status ${response.status}`);
        }

        const payload = (await response.json()) as RealtimeAnomalyResponse;
        if (active) {
          setState({ data: payload, loading: false, error: null });
        }
      } catch (error) {
        if (active) {
          setState({
            data: null,
            loading: false,
            error:
              error instanceof Error ? error.message : "Unable to load real-time anomalies.",
          });
        }
      }
    }

    load();
    const timer = window.setInterval(load, pollMs);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [pollMs]);

  return state;
}
