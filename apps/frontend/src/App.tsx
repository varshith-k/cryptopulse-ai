const roadmap = [
  "FastAPI backend with auth, market APIs, and live streams",
  "Kafka + Spark pipeline for technical indicators",
  "React dashboard for prices, charts, alerts, and coin details",
  "Grounded AI insights with anomaly detection and summaries",
];

const services = [
  { name: "Frontend", detail: "React, TypeScript, Tailwind, Vite" },
  { name: "API", detail: "FastAPI, PostgreSQL, JWT, SSE/WebSockets" },
  { name: "Streaming", detail: "Kafka ingestion plus Spark ETL jobs" },
  { name: "AI Agent", detail: "Grounded market Q&A and summaries" },
];

export default function App() {
  return (
    <main className="min-h-screen bg-canvas text-slate-100">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-12">
        <header className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-glow backdrop-blur">
          <p className="font-body text-sm uppercase tracking-[0.3em] text-accent">
            CryptoPulse AI
          </p>
          <h1 className="mt-4 max-w-3xl font-display text-5xl leading-tight text-white sm:text-6xl">
            Live crypto intelligence built for full-stack, data engineering, and AI portfolios.
          </h1>
          <p className="mt-6 max-w-2xl font-body text-lg text-slate-300">
            This Phase 1 scaffold establishes the architecture for a production-style platform with
            streaming analytics, portfolio-grade APIs, and grounded AI market reasoning.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a className="rounded-full bg-accent px-5 py-3 font-body font-semibold text-slate-950" href="http://localhost:8000/docs">
              API Docs
            </a>
            <a className="rounded-full border border-white/20 px-5 py-3 font-body font-semibold text-white" href="http://localhost:8080/health">
              Agent Health
            </a>
          </div>
        </header>

        <section className="mt-10 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <div className="rounded-3xl border border-white/10 bg-panel/70 p-8">
            <p className="font-body text-sm uppercase tracking-[0.2em] text-signal">Build roadmap</p>
            <div className="mt-6 space-y-4">
              {roadmap.map((item, index) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="font-body text-xs uppercase tracking-[0.2em] text-slate-400">
                    Phase {index + 2}
                  </p>
                  <p className="mt-2 font-body text-base text-slate-100">{item}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-8">
            <p className="font-body text-sm uppercase tracking-[0.2em] text-accent">Service layout</p>
            <div className="mt-6 space-y-4">
              {services.map((service) => (
                <div key={service.name} className="rounded-2xl border border-white/10 bg-canvas/80 p-4">
                  <h2 className="font-display text-2xl text-white">{service.name}</h2>
                  <p className="mt-2 font-body text-sm text-slate-300">{service.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

