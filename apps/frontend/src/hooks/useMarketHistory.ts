import { useEffect, useState } from "react";

import type { MarketHistoryResponse } from "../types";

type State = {
  data: MarketHistoryResponse | null;
  loading: boolean;
  error: string | null;
};

const INITIAL_STATE: State = {
  data: null,
  loading: true,
  error: null,
};

export function useMarketHistory(symbol: string | null, refreshKey?: string) {
  const [state, setState] = useState<State>(INITIAL_STATE);

  useEffect(() => {
    if (!symbol) {
      setState(INITIAL_STATE);
      return;
    }

    let active = true;
    setState((current) => ({ ...current, loading: true, error: null }));

    async function loadHistory() {
      try {
        const response = await fetch(
          `/api/v1/market/history?symbol=${encodeURIComponent(symbol)}&points=48`,
        );
        if (!response.ok) {
          throw new Error(`History request failed with status ${response.status}`);
        }

        const payload = (await response.json()) as MarketHistoryResponse;
        if (active) {
          setState({ data: payload, loading: false, error: null });
        }
      } catch (error) {
        if (active) {
          setState({
            data: null,
            loading: false,
            error: error instanceof Error ? error.message : "Unable to load market history.",
          });
        }
      }
    }

    void loadHistory();

    return () => {
      active = false;
    };
  }, [symbol, refreshKey]);

  return state;
}
