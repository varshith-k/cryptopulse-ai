import { useEffect, useState } from "react";

import type { MarketOverviewResponse } from "../types";

type State = {
  data: MarketOverviewResponse | null;
  loading: boolean;
  error: string | null;
};

const INITIAL_STATE: State = {
  data: null,
  loading: true,
  error: null,
};

export function useMarketOverview() {
  const [state, setState] = useState<State>(INITIAL_STATE);

  useEffect(() => {
    let active = true;

    async function loadOverview() {
      try {
        const response = await fetch("/api/v1/market/overview");
        if (!response.ok) {
          throw new Error(`Market request failed with status ${response.status}`);
        }

        const payload = (await response.json()) as MarketOverviewResponse;
        if (active) {
          setState({ data: payload, loading: false, error: null });
        }
      } catch (error) {
        if (active) {
          setState({
            data: null,
            loading: false,
            error: error instanceof Error ? error.message : "Unable to load market overview.",
          });
        }
      }
    }

    loadOverview();

    const stream = new EventSource("/api/v1/market/stream");
    stream.addEventListener("market_overview", (event) => {
      try {
        const payload = JSON.parse(event.data) as MarketOverviewResponse;
        if (active) {
          setState({ data: payload, loading: false, error: null });
        }
      } catch {
        if (active) {
          setState((current) => ({
            ...current,
            error: "Live stream delivered unreadable data.",
          }));
        }
      }
    });
    stream.onerror = () => {
      stream.close();
    };

    return () => {
      active = false;
      stream.close();
    };
  }, []);

  return state;
}
