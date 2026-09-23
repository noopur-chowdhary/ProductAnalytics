export default function Table({rows}:{rows:any[]}) {
  if (!rows?.length) return <div className="muted">No data.</div>;
  const columns = Object.keys(rows[0]);
  return <div className="table-wrap"><table><thead><tr>{columns.map(c => <th key={c}>{c}</th>)}</tr></thead>
    <tbody>{rows.map((row, i) => <tr key={i}>{columns.map(c => <td key={c}>{String(row[c] ?? "")}</td>)}</tr>)}</tbody>
  </table></div>;
}
