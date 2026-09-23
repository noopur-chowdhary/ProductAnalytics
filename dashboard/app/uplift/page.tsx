"use client";
import {useEffect,useState} from "react"; import Table from "../../components/Table"; import {fetchJson} from "../../lib/api";
export default function Page(){ const [d,setD]=useState<any>(null); useEffect(()=>{fetchJson("/api/uplift/criteo").then(setD)},[]); return <><h1>Uplift Modeling</h1><p className="lede">Who is more likely to convert because of treatment?</p><h2>Model Selection</h2><Table rows={d?.model_selection||[]}/><h2>Targeting Policy</h2><Table rows={d?.policy||[]}/><h2>Uplift by Decile</h2><Table rows={d?.deciles||[]}/></>; }
