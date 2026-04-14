import { FormEvent, useEffect, useMemo, useState } from "react";

import { Sparkline } from "./components/Sparkline";
import { StatCard } from "./components/StatCard";
import { useMarketOverview } from "./hooks/useMarketOverview";
import {
  formatCompactNumber,
  formatPercent,
  formatTimestamp,
  formatUsd,
} from "./lib/format";
import type { AgentResponse, AlertRead, MarketAsset, TokenResponse, UserRead } from "./types";

const alertTypes = [
  { value: "price_above", label: "Price above" },
  { value: "price_below", label: "Price below" },
  { value: "volatility_spike", label: "Volatility spike" },
];

const starterPrompts = [
  "Summarize BTC market movement today.",
  "Which assets show unusual volatility?",
  "Compare ETH and SOL momentum this week.",
];

function buildSparklineValues(asset: MarketAsset): number[] {
  const base = asset.price_usd;
  const drift = asset.percent_change_24h / 100;
  const volatility = (asset.rolling_volatility ?? 2) / 100;

  return Array.from({ length: 12 }, (_, index) => {
    const phase = (index - 6) / 6;
    const oscillation = Math.sin(index * 0.9) * volatility * 0.55;
    const momentum = drift * phase;
    return base * (1 + momentum + oscillation);
  });
}

export default function App() {
  const { data, loading, error } = useMarketOverview();
  const [selectedSymbol, setSelectedSymbol] = useState("SOL");
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<UserRead | null>(null);
  const [alerts, setAlerts] = useState<AlertRead[]>([]);
  const [alertsError, setAlertsError] = useState<string | null>(null);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [alertSymbol, setAlertSymbol] = useState("BTC");
  const [alertType, setAlertType] = useState("price_above");
  const [alertThreshold, setAlertThreshold] = useState("70000");
  const [alertSuccess, setAlertSuccess] = useState<string | null>(null);
  const [question, setQuestion] = useState(starterPrompts[0]);
  const [agentAnswer, setAgentAnswer] = useState<AgentResponse | null>(null);
  const [agentLoading, setAgentLoading] = useState(false);
  const [agentError, setAgentError] = useState<string | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");

  const assets = data?.assets ?? [];
  const selectedAsset =
    assets.find((asset) => asset.symbol === selectedSymbol) ?? assets[0] ?? null;

  const positiveAssets = assets.filter((asset) => asset.percent_change_24h > 0).length;
  const averageRsi = useMemo(() => {
    const rsiValues = assets
      .map((asset) => asset.rsi_14)
      .filter((value): value is number => value !== null);
    if (rsiValues.length === 0) {
      return null;
    }

    return rsiValues.reduce((total, value) => total + value, 0) / rsiValues.length;
  }, [assets]);

  useEffect(() => {
    const storedToken = window.localStorage.getItem("cryptopulse_token");
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  useEffect(() => {
    if (!token) {
      setCurrentUser(null);
      setAlerts([]);
      window.localStorage.removeItem("cryptopulse_token");
      return;
    }

    window.localStorage.setItem("cryptopulse_token", token);
    void loadCurrentUser(token);
    void loadAlerts(token);
  }, [token]);

  async function loadCurrentUser(accessToken: string) {
    try {
      const response = await fetch("/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!response.ok) {
        throw new Error(`Profile request failed with status ${response.status}`);
      }

      const payload = (await response.json()) as UserRead;
      setCurrentUser(payload);
    } catch (nextError) {
      setAuthError(
        nextError instanceof Error ? nextError.message : "Unable to load authenticated profile.",
      );
    }
  }

  async function loadAlerts(accessToken: string) {
    const response = await fetch("/api/v1/alerts", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      throw new Error(`Alert fetch failed with status ${response.status}`);
    }

    const payload = (await response.json()) as AlertRead[];
    setAlerts(payload);
  }

  async function submitAlert(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setAlertsError("Sign in before creating an alert.");
      return;
    }

    setAlertsLoading(true);
    setAlertsError(null);
    setAlertSuccess(null);

    try {
      const response = await fetch("/api/v1/alerts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol: alertSymbol,
          alert_type: alertType,
          threshold: Number(alertThreshold),
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail ?? `Alert creation failed with status ${response.status}`);
      }

      setAlertSuccess("Alert created successfully.");
      await loadAlerts(token);
    } catch (nextError) {
      setAlertsError(
        nextError instanceof Error ? nextError.message : "Unable to create the alert.",
      );
    } finally {
      setAlertsLoading(false);
    }
  }

  async function queryAgent(nextQuestion?: string) {
    const prompt = nextQuestion ?? question;
    setQuestion(prompt);
    setAgentLoading(true);
    setAgentError(null);

    try {
      const response = await fetch("/agent/insights/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: prompt }),
      });

      if (!response.ok) {
        throw new Error(`Agent request failed with status ${response.status}`);
      }

      const payload = (await response.json()) as AgentResponse;
      setAgentAnswer(payload);
    } catch (nextError) {
      setAgentError(
        nextError instanceof Error ? nextError.message : "Unable to retrieve AI insight.",
      );
    } finally {
      setAgentLoading(false);
    }
  }

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthSuccess(null);

    try {
      if (authMode === "register") {
        const registerResponse = await fetch("/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: authEmail, password: authPassword }),
        });

        if (!registerResponse.ok) {
          const payload = await registerResponse.json().catch(() => null);
          throw new Error(payload?.detail ?? `Registration failed with status ${registerResponse.status}`);
        }

        setAuthSuccess("Account created. Signing you in now.");
        setAuthMode("login");
      }

      const loginResponse = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: authEmail, password: authPassword }),
      });

      if (!loginResponse.ok) {
        const payload = await loginResponse.json().catch(() => null);
        throw new Error(payload?.detail ?? `Login failed with status ${loginResponse.status}`);
      }

      const payload = (await loginResponse.json()) as TokenResponse;
      setToken(payload.access_token);
      setAuthSuccess("Signed in successfully.");
    } catch (nextError) {
      setAuthError(nextError instanceof Error ? nextError.message : "Unable to complete authentication.");
    } finally {
      setAuthLoading(false);
    }
  }

  function signOut() {
    setToken(null);
    setAuthSuccess("Signed out.");
    setAlertsError(null);
    setAlertSuccess(null);
  }

  return (
    <main className="min-h-screen bg-canvas text-slate-100">
      <div className="mx-auto max-w-7xl px-5 py-6 sm:px-8">
        <header className="overflow-hidden rounded-[2rem] border border-white/10 bg-panel-deep p-6 shadow-glow">
          <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-accent">
                  CryptoPulse AI
                </span>
                <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-400">
                  Live market intelligence platform
                </span>
              </div>
              <h1 className="mt-5 max-w-4xl font-display text-4xl leading-tight text-white sm:text-6xl">
                A full-stack crypto command center with live market context, alert workflows, and
                AI-assisted reasoning.
              </h1>
              <p className="mt-5 max-w-2xl text-base text-slate-300 sm:text-lg">
                Track market leaders, inspect technical context, configure alerts, and ask
                data-grounded questions through a production-style interface designed for local
                deployment and engineering portfolio demos.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a className="button-primary" href="#dashboard">
                  Open dashboard
                </a>
                <a className="button-secondary" href="http://localhost:8000/docs">
                  API docs
                </a>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-1">
              <StatCard
                label="Tracked assets"
                value={assets.length > 0 ? String(assets.length) : "--"}
              />
              <StatCard
                label="Positive movers"
                value={assets.length > 0 ? String(positiveAssets) : "--"}
                tone="positive"
              />
              <StatCard
                label="Average RSI"
                value={averageRsi !== null ? averageRsi.toFixed(1) : "--"}
              />
            </div>
          </div>
        </header>

        <section
          id="dashboard"
          className="mt-8 grid gap-6 xl:grid-cols-[1.35fr_0.95fr]"
        >
          <div className="space-y-6">
            <section className="panel">
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="eyebrow">Live market dashboard</p>
                  <h2 className="section-title">Market overview</h2>
                  <p className="section-copy">
                    Latest backend snapshot, ranked by 24-hour momentum.
                  </p>
                </div>
                <div className="text-sm text-slate-400">
                  {data ? `Updated ${formatTimestamp(data.generated_at)}` : "Waiting for data"}
                </div>
              </div>

              {loading ? (
                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  {Array.from({ length: 4 }, (_, index) => (
                    <div key={index} className="skeleton-card" />
                  ))}
                </div>
              ) : error ? (
                <div className="mt-6 rounded-3xl border border-rose-400/30 bg-rose-500/10 p-5 text-rose-200">
                  {error}
                </div>
              ) : assets.length === 0 ? (
                <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-6 text-slate-300">
                  No market assets are available yet.
                </div>
              ) : (
                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  {assets.map((asset) => {
                    const isSelected = selectedAsset?.symbol === asset.symbol;
                    const tone =
                      asset.percent_change_24h >= 0 ? "text-emerald-300" : "text-rose-300";

                    return (
                      <button
                        key={asset.symbol}
                        type="button"
                        onClick={() => setSelectedSymbol(asset.symbol)}
                        className={`rounded-[1.75rem] border p-5 text-left transition ${
                          isSelected
                            ? "border-accent/60 bg-accent/8 shadow-glow-soft"
                            : "border-white/10 bg-white/5 hover:border-white/25"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">
                              {asset.symbol}
                            </p>
                            <h3 className="mt-2 font-display text-2xl text-white">
                              {asset.name}
                            </h3>
                          </div>
                          <span className={`text-sm font-semibold ${tone}`}>
                            {formatPercent(asset.percent_change_24h)}
                          </span>
                        </div>
                        <p className="mt-4 font-display text-3xl text-white">
                          {formatUsd(asset.price_usd)}
                        </p>
                        <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
                          <div>
                            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                              Volume
                            </p>
                            <p className="mt-1">{formatCompactNumber(asset.volume_24h)}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                              RSI
                            </p>
                            <p className="mt-1">{asset.rsi_14?.toFixed(1) ?? "--"}</p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </section>

            <section className="panel">
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="eyebrow">Coin detail</p>
                  <h2 className="section-title">
                    {selectedAsset ? `${selectedAsset.name} detail` : "Select an asset"}
                  </h2>
                  <p className="section-copy">
                    Focused detail view with price path proxy, trend context, and technical signal
                    summary.
                  </p>
                </div>
              </div>

              {selectedAsset ? (
                <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                  <div className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                          Trend chart
                        </p>
                        <p className="mt-2 font-display text-2xl text-white">
                          {selectedAsset.symbol} intraday proxy
                        </p>
                      </div>
                      <span
                        className={`rounded-full px-3 py-1 text-sm ${
                          selectedAsset.percent_change_24h >= 0
                            ? "bg-emerald-400/10 text-emerald-300"
                            : "bg-rose-500/10 text-rose-300"
                        }`}
                      >
                        {formatPercent(selectedAsset.percent_change_24h)}
                      </span>
                    </div>
                    <div className="mt-5 rounded-[1.5rem] border border-white/10 bg-canvas/70 p-4">
                      <Sparkline
                        values={buildSparklineValues(selectedAsset)}
                        tone={selectedAsset.percent_change_24h >= 0 ? "positive" : "negative"}
                      />
                    </div>
                    <div className="mt-5 grid gap-4 sm:grid-cols-3">
                      <StatCard label="Price" value={formatUsd(selectedAsset.price_usd)} />
                      <StatCard
                        label="Market cap"
                        value={formatCompactNumber(selectedAsset.market_cap)}
                      />
                      <StatCard
                        label="Volatility"
                        value={
                          selectedAsset.rolling_volatility !== null
                            ? `${selectedAsset.rolling_volatility.toFixed(2)}`
                            : "--"
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5">
                      <p className="eyebrow">Technical indicators</p>
                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        <div className="metric-card">
                          <span>RSI 14</span>
                          <strong>{selectedAsset.rsi_14?.toFixed(1) ?? "--"}</strong>
                        </div>
                        <div className="metric-card">
                          <span>Rolling volatility</span>
                          <strong>
                            {selectedAsset.rolling_volatility?.toFixed(2) ?? "--"}
                          </strong>
                        </div>
                        <div className="metric-card">
                          <span>24h volume</span>
                          <strong>{formatCompactNumber(selectedAsset.volume_24h)}</strong>
                        </div>
                        <div className="metric-card">
                          <span>24h move</span>
                          <strong>{formatPercent(selectedAsset.percent_change_24h)}</strong>
                        </div>
                      </div>
                    </div>

                    <div className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5">
                      <p className="eyebrow">Trend summary</p>
                      <p className="mt-4 text-base leading-7 text-slate-200">
                        {selectedAsset.trend}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-6 text-slate-300">
                  Select a market card above to inspect the coin detail view.
                </div>
              )}
            </section>

            <section className="panel">
              <p className="eyebrow">AI insight feed</p>
              <h2 className="section-title">Grounded market context</h2>
              <div className="mt-5 grid gap-4 md:grid-cols-2">
                {(data?.insights ?? []).map((insight) => (
                  <div
                    key={insight.title}
                    className="rounded-[1.5rem] border border-white/10 bg-white/5 p-5"
                  >
                    <h3 className="font-display text-2xl text-white">{insight.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-300">{insight.content}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="space-y-6">
            <section className="panel">
              <p className="eyebrow">Alert configuration</p>
              <h2 className="section-title">Demo alert workflow</h2>
              <p className="section-copy">
                Create an account or sign in, inspect your saved alerts, and create threshold rules
                against the live backend.
              </p>

              <div className="mt-5 rounded-[1.75rem] border border-white/10 bg-white/5 p-5">
                <div className="flex gap-3">
                  <button
                    type="button"
                    className={authMode === "login" ? "button-primary flex-1" : "button-secondary flex-1"}
                    onClick={() => setAuthMode("login")}
                  >
                    Sign in
                  </button>
                  <button
                    type="button"
                    className={authMode === "register" ? "button-primary flex-1" : "button-secondary flex-1"}
                    onClick={() => setAuthMode("register")}
                  >
                    Create account
                  </button>
                </div>

                <form className="mt-4 space-y-4" onSubmit={submitAuth}>
                  <label className="field">
                    <span>Email</span>
                    <input
                      type="email"
                      value={authEmail}
                      onChange={(event) => setAuthEmail(event.target.value)}
                      placeholder="you@example.com"
                    />
                  </label>
                  <label className="field">
                    <span>Password</span>
                    <input
                      type="password"
                      value={authPassword}
                      onChange={(event) => setAuthPassword(event.target.value)}
                      placeholder="Enter a secure password"
                    />
                  </label>
                  <button className="button-primary w-full" type="submit" disabled={authLoading}>
                    {authLoading
                      ? "Processing..."
                      : authMode === "login"
                        ? "Sign in"
                        : "Create account and sign in"}
                  </button>
                </form>

                {!currentUser ? (
                  <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-[1.25rem] border border-white/10 bg-canvas/60 p-4">
                    <p className="text-sm text-slate-400">
                      Local sample account available for demos: <span className="text-white">demo@cryptopulse.ai</span>
                    </p>
                    <button
                      type="button"
                      className="button-secondary"
                      onClick={() => {
                        setAuthMode("login");
                        setAuthEmail("demo@cryptopulse.ai");
                        setAuthPassword("DemoPass123!");
                      }}
                    >
                      Use sample account
                    </button>
                  </div>
                ) : null}

                {currentUser ? (
                  <div className="mt-4 flex items-center justify-between gap-3 rounded-[1.25rem] border border-emerald-400/20 bg-emerald-400/10 p-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">Authenticated</p>
                      <p className="mt-1 text-sm text-white">{currentUser.email}</p>
                    </div>
                    <button type="button" className="button-secondary" onClick={signOut}>
                      Sign out
                    </button>
                  </div>
                ) : null}

                {authSuccess ? <p className="mt-4 text-sm text-emerald-300">{authSuccess}</p> : null}
                {authError ? <p className="mt-4 text-sm text-rose-300">{authError}</p> : null}
              </div>

              <form className="mt-5 space-y-4" onSubmit={submitAlert}>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="field">
                    <span>Symbol</span>
                    <select value={alertSymbol} onChange={(event) => setAlertSymbol(event.target.value)}>
                      {assets.map((asset) => (
                        <option key={asset.symbol} value={asset.symbol}>
                          {asset.symbol}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Alert type</span>
                    <select value={alertType} onChange={(event) => setAlertType(event.target.value)}>
                      {alertTypes.map((item) => (
                        <option key={item.value} value={item.value}>
                          {item.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <label className="field">
                  <span>Threshold</span>
                  <input
                    value={alertThreshold}
                    onChange={(event) => setAlertThreshold(event.target.value)}
                    placeholder="70000"
                    inputMode="decimal"
                  />
                </label>
                <button className="button-secondary w-full" type="submit" disabled={alertsLoading}>
                  Save alert
                </button>
              </form>

              {alertSuccess ? <p className="mt-4 text-sm text-emerald-300">{alertSuccess}</p> : null}
              {alertsError ? <p className="mt-4 text-sm text-rose-300">{alertsError}</p> : null}

              <div className="mt-6 space-y-3">
                {alerts.length > 0 ? (
                  alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className="rounded-[1.5rem] border border-white/10 bg-white/5 p-4"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-display text-xl text-white">{alert.symbol}</p>
                          <p className="mt-1 text-sm text-slate-400">
                            {alert.alert_type} {alert.threshold !== null ? formatUsd(alert.threshold) : ""}
                          </p>
                        </div>
                        <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-emerald-300">
                          active
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-[1.5rem] border border-dashed border-white/10 p-4 text-sm text-slate-400">
                    Sign in to load alerts for the current account.
                  </div>
                )}
              </div>
            </section>

            <section className="panel">
              <p className="eyebrow">AI insights chat</p>
              <h2 className="section-title">Agent panel</h2>
              <p className="section-copy">
                Ask the current agent service a market question and view its grounded response.
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                {starterPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => void queryAgent(prompt)}
                    className="rounded-full border border-white/10 px-3 py-2 text-sm text-slate-300 transition hover:border-accent/60 hover:text-white"
                  >
                    {prompt}
                  </button>
                ))}
              </div>

              <div className="mt-5 space-y-4">
                <label className="field">
                  <span>Your question</span>
                  <textarea
                    rows={4}
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="What coins are trending upward in the last 24 hours?"
                  />
                </label>
                <button
                  className="button-primary w-full"
                  type="button"
                  onClick={() => void queryAgent()}
                  disabled={agentLoading}
                >
                  {agentLoading ? "Thinking..." : "Ask agent"}
                </button>
              </div>

              {agentError ? <p className="mt-4 text-sm text-rose-300">{agentError}</p> : null}

              <div className="mt-6 rounded-[1.75rem] border border-white/10 bg-white/5 p-5">
                {agentAnswer ? (
                  <>
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Response</p>
                    <p className="mt-3 text-base leading-7 text-slate-200">{agentAnswer.answer}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {agentAnswer.sources.map((source) => (
                        <span
                          key={source}
                          className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-400"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-slate-400">
                    Run a prompt to populate the AI insight panel.
                  </p>
                )}
              </div>
            </section>
          </div>
        </section>
      </div>
    </main>
  );
}
