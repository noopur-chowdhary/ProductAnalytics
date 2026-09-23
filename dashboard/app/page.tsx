"use client";

import { useEffect, useState } from "react";
import { getDashboardData } from "../lib/api";
import {
  CountriesChart,
  FunnelChart,
  LiftChart,
  RetentionChart,
  UpliftChart,
} from "../components/Visuals";


type Row = Record<string, any>;

function rows(value: unknown): Row[] {
  return Array.isArray(value) ? value : [];
}

function pretty(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "number") {
    if (Number.isInteger(value)) {
      return new Intl.NumberFormat("en-US").format(value);
    }

    if (Math.abs(value) < 0.01) {
      return value.toFixed(4);
    }

    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 2,
    }).format(value);
  }

  return String(value);
}

function titleCase(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function Table({
  title,
  rows: tableRows,
}: {
  title: string;
  rows: Row[];
}) {
  if (!tableRows.length) {
    return (
      <div className="surface">
        <div className="surface-title">{title}</div>
        <div className="empty-state">No saved results available</div>
      </div>
    );
  }

  const columns = Object.keys(tableRows[0]);

  return (
    <div className="surface">
      <div className="surface-title-row">
        <div className="surface-title">{title}</div>
        <span className="row-count">{tableRows.length} rows</span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{titleCase(column)}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {tableRows.slice(0, 8).map((row, i) => (
              <tr key={i}>
                {columns.map((column) => (
                  <td key={column}>{pretty(row[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getFunnelLabel(row: Row, index: number) {
  for (const key of ["stage", "event", "step", "name", "metric"]) {
    if (row[key] !== undefined) {
      return String(row[key]);
    }
  }

  const stringValue = Object.values(row).find(
    (value) => typeof value === "string"
  );

  return stringValue ? String(stringValue) : `Stage ${index + 1}`;
}

function getFunnelNumber(row: Row) {
  for (const key of [
    "users",
    "visitors",
    "count",
    "events",
    "value",
    "total",
  ]) {
    if (typeof row[key] === "number") {
      return row[key];
    }
  }

  const numberValue = Object.values(row).find(
    (value) => typeof value === "number"
  );

  return typeof numberValue === "number" ? numberValue : 0;
}

function Funnel({ data }: { data: Row[] }) {
  if (!data.length) {
    return (
      <div className="surface">
        <div className="surface-title">Commerce Funnel</div>
        <div className="empty-state">
          No Retailrocket funnel data available
        </div>
      </div>
    );
  }

  const values = data.map(getFunnelNumber);
  const max = Math.max(...values, 1);

  return (
    <div className="surface funnel-card">
      <div className="surface-title-row">
        <div>
          <div className="mini-label">RETAILROCKET</div>
          <div className="surface-title">Commerce Funnel</div>
        </div>

        <span className="pill">Behavior analytics</span>
      </div>

      <div className="funnel">
        {data.map((row, index) => {
          const value = getFunnelNumber(row);
          const percent = Math.max((value / max) * 100, 4);

          return (
            <div className="funnel-item" key={index}>
              <div className="funnel-meta">
                <span>{getFunnelLabel(row, index)}</span>
                <strong>{pretty(value)}</strong>
              </div>

              <div className="funnel-track">
                <div
                  className="funnel-bar"
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function DecisionCard({
  row,
  index,
}: {
  row: Row;
  index: number;
}) {
  const icons = ["A/B", "↗", "R", "Δ"];

  return (
    <article className="decision-card">
      <div className="decision-top">
        <div className="decision-icon">{icons[index] ?? "•"}</div>
        <span>{pretty(row.capability)}</span>
      </div>

      <h3>{pretty(row.headline)}</h3>

      <p>{pretty(row.evidence)}</p>

      <div className="decision-footer">
        {pretty(row.interpretation)}
      </div>
    </article>
  );
}

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardData()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <main className="loading-screen">
        <div className="loader" />
        <strong>Loading ProductPulse</strong>
      </main>
    );
  }

  const cards = rows(data?.overview?.decision_cards);
  const registry = rows(data?.overview?.decision_registry);
  const funnel = rows(data?.retailrocketAnalytics?.funnel);

  const healthy = data?.health?.status === "ok";
  const errors = data?.errors ?? [];

  return (
    <>
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">P</div>
          <div>
            <strong>ProductPulse</strong>
            <span>Decision Intelligence</span>
          </div>
        </div>

        <nav>
          <a href="#overview">Overview</a>
          <a href="#behavior">Behavior</a>
          <a href="#experiments">Experiments</a>
          <a href="#uplift">Uplift</a>
          <a href="#customers">Customers</a>
        </nav>

        <div className={healthy ? "api-status live" : "api-status down"}>
          <span />
          {healthy ? "Live data" : "API offline"}
        </div>
      </header>

      <main className="dashboard">
        <section className="hero-compact">
          <div>
            <div className="mini-label">PRODUCT ANALYTICS PLATFORM</div>

            <h1>
              Turn product behavior into
              <span> decisions.</span>
            </h1>

            <p>
              Experiments, behavioral funnels, propensity ranking
              and causal targeting in one decision layer.
            </p>
          </div>

          <div className="hero-stat">
            <span>Capabilities</span>
            <strong>{registry.length || 4}</strong>
            <small>connected analytical workflows</small>
          </div>
        </section>

        {errors.length > 0 && (
          <div className="warning">
            <strong>Some result endpoints could not be loaded.</strong>
            <span>{errors.join(" · ")}</span>
          </div>
        )}

        <section id="overview">
          <div className="section-heading">
            <div>
              <div className="mini-label">DECISION INTELLIGENCE</div>
              <h2>What should the product team do?</h2>
            </div>

            <p>
              The strongest actionable result from each analytical
              capability.
            </p>
          </div>

          <div className="decision-grid">
            {cards.length ? (
              cards.map((card, index) => (
                <DecisionCard key={index} row={card} index={index} />
              ))
            ) : (
              <div className="empty-large">
                No decision results were returned by the API.
              </div>
            )}
          </div>
        </section>

        <section id="behavior">
          <div className="section-heading">
            <div>
              <div className="mini-label">BEHAVIOR</div>
              <h2>Where are users dropping off?</h2>
            </div>

            <p>
              Retailrocket behavior and short-term purchase propensity.
            </p>
          </div>

          <div className="grid-2">
            <FunnelChart rows={funnel} />

            <LiftChart
              rows={rows(data?.retailrocketPropensity?.policy)}
            />
          </div>

          <Table
            title="Retailrocket Behavior Overview"
            rows={rows(data?.retailrocketAnalytics?.overview)}
          />
        </section>

        <section id="experiments">
          <div className="section-heading">
            <div>
              <div className="mini-label">EXPERIMENTATION</div>
              <h2>Did the product change actually help?</h2>
            </div>

            <p>
              Randomized A/B testing using the Cookie Cats experiment.
            </p>
          </div>

          <div className="grid-2">
            <RetentionChart
              rows={rows(data?.experiment?.retention)}
            />

            <Table
              title="Experiment Decision"
              rows={rows(data?.experiment?.decision)}
            />
          </div>

          <Table
            title="Statistical Test Results"
            rows={rows(data?.experiment?.tests)}
          />
        </section>

        <section id="uplift">
          <div className="section-heading">
            <div>
              <div className="mini-label">CAUSAL TARGETING</div>
              <h2>Who should receive the intervention?</h2>
            </div>

            <p>
              Criteo uplift modeling separates likely converters from
              users actually influenced by treatment.
            </p>
          </div>

          <div className="grid-2">
            <UpliftChart
              rows={rows(data?.criteoUplift?.targeting)}
            />

            <Table
              title="Targeting Policy"
              rows={rows(data?.criteoUplift?.policy)}
            />
          </div>

          <Table
            title="Targeting Performance"
            rows={rows(data?.criteoUplift?.targeting)}
          />
        </section>

        <section id="customers">
          <div className="section-heading">
            <div>
              <div className="mini-label">CUSTOMERS</div>
              <h2>Where is customer value coming from?</h2>
            </div>

            <p>
              Revenue and repeat-purchase behavior from Online Retail II.
            </p>
          </div>

          <div className="grid-2">
            <Table
              title="Business Overview"
              rows={rows(data?.onlineRetail?.business_overview)}
            />

            <CountriesChart
              rows={rows(data?.onlineRetail?.top_countries)}
            />
          </div>

          <Table
            title="Customer Summary"
            rows={rows(data?.onlineRetail?.customer_summary)}
          />
        </section>

        <footer>
          <strong>ProductPulse</strong>
          <span>Analytics → Models → Decisions</span>
        </footer>
      </main>
    </>
  );
}
