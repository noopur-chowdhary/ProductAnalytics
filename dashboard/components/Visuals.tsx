"use client";

import {
  BarChart,
  Bar,
  CartesianGrid,
  Line,
  LineChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Row = Record<string, any>;

function empty(title: string) {
  return (
    <div className="surface chart-card">
      <div className="surface-title">{title}</div>
      <div className="empty-state">No chart data available</div>
    </div>
  );
}

function compact(value: number) {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function findStringKey(rows: Row[], candidates: string[]) {
  if (!rows.length) return undefined;

  for (const key of candidates) {
    if (key in rows[0]) return key;
  }

  return Object.keys(rows[0]).find((key) =>
    rows.some((row) => typeof row[key] === "string")
  );
}

function findNumberKey(rows: Row[], candidates: string[]) {
  if (!rows.length) return undefined;

  for (const key of candidates) {
    if (
      key in rows[0] &&
      rows.some((row) => typeof row[key] === "number")
    ) {
      return key;
    }
  }

  return Object.keys(rows[0]).find((key) =>
    rows.some((row) => typeof row[key] === "number")
  );
}

export function FunnelChart({ rows }: { rows: Row[] }) {
  if (!rows.length) return empty("Commerce Funnel");

  const labelKey = findStringKey(rows, [
    "stage",
    "event",
    "step",
    "name",
    "metric",
  ]);

  const valueKey = findNumberKey(rows, [
    "count",
    "events",
    "users",
    "visitors",
    "total",
    "value",
  ]);

  if (!valueKey) return empty("Commerce Funnel");

  const data = rows.map((row, index) => ({
    stage: labelKey ? String(row[labelKey]) : `Stage ${index + 1}`,
    value: Number(row[valueKey] ?? 0),
  }));

  return (
    <div className="surface chart-card">
      <div className="surface-title-row">
        <div>
          <div className="mini-label">RETAILROCKET</div>
          <div className="surface-title">Commerce Funnel</div>
        </div>

        <span className="pill">Behavior</span>
      </div>

      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 20, bottom: 10, left: 15 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis
              type="number"
              tickFormatter={compact}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="stage"
              width={95}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip formatter={(value: any) => compact(Number(value))} />
            <Bar
              dataKey="value"
              fill="#6255db"
              radius={[0, 8, 8, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function RetentionChart({ rows }: { rows: Row[] }) {
  if (!rows.length) {
    return empty("Retention by Variant");
  }

  const data = rows.map((row) => {
    const metric = String(row.metric ?? "retention");

    let label = metric;

    if (metric === "retention_1") {
      label = "Day 1";
    } else if (metric === "retention_7") {
      label = "Day 7";
    }

    return {
      metric: label,
      gate30: Number(row.gate_30_rate ?? 0) * 100,
      gate40: Number(row.gate_40_rate ?? 0) * 100,
    };
  });

  return (
    <div className="surface chart-card">
      <div className="surface-title-row">
        <div>
          <div className="mini-label">COOKIE CATS</div>
          <div className="surface-title">
            Retention by Variant
          </div>
        </div>

        <span className="pill">A/B test</span>
      </div>

      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{
              top: 10,
              right: 20,
              left: 5,
              bottom: 5,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="metric"
              axisLine={false}
              tickLine={false}
            />

            <YAxis
              tickFormatter={(value) => `${value}%`}
              axisLine={false}
              tickLine={false}
            />

            <Tooltip
              formatter={(value: any) =>
                `${Number(value).toFixed(2)}%`
              }
            />

            <Legend />

            <Bar
              dataKey="gate30"
              name="Gate 30"
              fill="#6255db"
              radius={[8, 8, 0, 0]}
            />

            <Bar
              dataKey="gate40"
              name="Gate 40"
              fill="#50a6c2"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


export function LiftChart({ rows }: { rows: Row[] }) {
  if (!rows.length) return empty("Propensity Lift");

  const keys = Object.keys(rows[0]);

  const liftKey =
    keys.find((key) => key.toLowerCase() === "lift") ||
    keys.find(
      (key) =>
        key.toLowerCase().includes("lift") &&
        !key.toLowerCase().includes("uplift")
    );

  const targetKey =
    keys.find((key) => key === "target_pct") ||
    keys.find((key) => key.includes("target_fraction")) ||
    keys.find((key) => key.includes("percentile")) ||
    keys.find((key) => key.includes("fraction"));

  if (!liftKey) return empty("Propensity Lift");

  const data = rows.slice(0, 20).map((row, index) => {
    let target: any = targetKey ? row[targetKey] : index + 1;

    if (
      targetKey?.includes("fraction") &&
      typeof target === "number" &&
      target <= 1
    ) {
      target *= 100;
    }

    return {
      target: typeof target === "number" ? `${target}%` : String(target),
      lift: Number(row[liftKey]),
    };
  });

  return (
    <div className="surface chart-card">
      <div className="surface-title-row">
        <div>
          <div className="mini-label">PROPENSITY</div>
          <div className="surface-title">Purchase Lift by Targeting Depth</div>
        </div>

        <span className="pill">Ranking</span>
      </div>

      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="target"
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
            />
            <Tooltip formatter={(value: any) => `${Number(value).toFixed(2)}×`} />
            <Line
              type="monotone"
              dataKey="lift"
              stroke="#6255db"
              strokeWidth={3}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function UpliftChart({ rows }: { rows: Row[] }) {
  if (!rows.length) return empty("Observed Uplift");

  const keys = Object.keys(rows[0]);

  const targetKey =
    keys.find((key) => key === "target_pct") ||
    keys.find((key) => key.includes("target_fraction"));

  const upliftKey =
    keys.find((key) => key === "observed_uplift_pp") ||
    keys.find((key) => key.includes("uplift_pp")) ||
    keys.find((key) => key === "observed_uplift") ||
    keys.find((key) => key.includes("uplift"));

  if (!upliftKey) return empty("Observed Uplift");

  const data = rows.map((row, index) => {
    let target: any = targetKey ? row[targetKey] : index + 1;

    if (
      targetKey?.includes("fraction") &&
      typeof target === "number" &&
      target <= 1
    ) {
      target *= 100;
    }

    let uplift = Number(row[upliftKey]);

    if (
      !upliftKey.includes("_pp") &&
      Math.abs(uplift) <= 1
    ) {
      uplift *= 100;
    }

    return {
      target: typeof target === "number" ? `${target}%` : String(target),
      uplift,
    };
  });

  return (
    <div className="surface chart-card">
      <div className="surface-title-row">
        <div>
          <div className="mini-label">CRITEO UPLIFT</div>
          <div className="surface-title">Observed Uplift by Targeting Depth</div>
        </div>

        <span className="pill">Causal</span>
      </div>

      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="target"
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tickFormatter={(value) => `${value}%`}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              formatter={(value: any) =>
                `${Number(value).toFixed(3)} pp`
              }
            />
            <Line
              type="monotone"
              dataKey="uplift"
              stroke="#e46b64"
              strokeWidth={3}
              dot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function CountriesChart({ rows }: { rows: Row[] }) {
  if (!rows.length) return empty("Top Markets");

  const countryKey = findStringKey(rows, [
    "country",
    "Country",
    "market",
    "name",
  ]);

  const revenueKey = findNumberKey(rows, [
    "revenue",
    "Revenue",
    "total_revenue",
    "sales",
  ]);

  if (!countryKey || !revenueKey) {
    return empty("Top Markets");
  }

  const data = rows
    .map((row) => ({
      country: String(row[countryKey]),
      revenue: Number(row[revenueKey]),
    }))
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 8);

  return (
    <div className="surface chart-card">
      <div className="surface-title-row">
        <div>
          <div className="mini-label">ONLINE RETAIL II</div>
          <div className="surface-title">Revenue by Market</div>
        </div>

        <span className="pill">Customers</span>
      </div>

      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ left: 15 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis
              type="number"
              tickFormatter={compact}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              dataKey="country"
              type="category"
              width={100}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip formatter={(value: any) => compact(Number(value))} />
            <Bar
              dataKey="revenue"
              fill="#50a6c2"
              radius={[0, 8, 8, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
