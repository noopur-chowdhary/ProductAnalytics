import Link from "next/link";

const links = [
  ["Overview", "/"],
  ["Experiment", "/experiments"],
  ["Propensity", "/propensity"],
  ["Uplift", "/uplift"],
  ["Decisions", "/decisions"],
];

export default function Nav() {
  return <aside className="sidebar">
    <div className="brand">Product Pulse</div>
    <div className="subtitle">Analytics & Decision Platform</div>
    <nav>{links.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav>
  </aside>;
}
