"use client";
import {useEffect,useState} from "react"; import Table from "../../components/Table"; import {fetchJson} from "../../lib/api";
export default function Page(){ const [d,setD]=useState<any>(null); useEffect(()=>{fetchJson("/api/analytics/experiment").then(setD)},[]); return <><h1>Experimentation</h1><p className="lede">Cookie Cats gate_30 vs gate_40 retention experiment.</p><h2>Decision</h2><Table rows={d?.decision||[]}/><h2>Retention</h2><Table rows={d?.retention||[]}/><h2>Statistical Tests</h2><Table rows={d?.tests||[]}/></>; }
