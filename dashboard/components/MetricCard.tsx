export default function MetricCard({title, value, detail}:{title:string; value:string; detail?:string}) {
  return <div className="card metric-card">
    <div className="eyebrow">{title}</div>
    <div className="metric-value">{value}</div>
    {detail && <div className="muted">{detail}</div>}
  </div>;
}
