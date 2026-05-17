"use client";

import { useEffect, useState } from "react";
import { supabaseBrowser } from "@/utils/supabase/browser";

const LOGO = "https://static.wixstatic.com/media/98f2c5_10c22a0527574cd38fc480acd8716345~mv2.png/v1/fill/w_1628,h_287,al_c,q_90,enc_avif,quality_auto/ThrivingScholars_edited_edited_edited_pn.png";
const STAMP = "2026-02-26 15:47:34 UTC";

export default function LogoutPage() {
  const [msg, setMsg] = useState("Signing you out…");

  useEffect(() => {
    (async () => {
      try {
        const sb = supabaseBrowser();
        await sb.auth.signOut();
      } catch (e) {
        // fallback: still redirect
      } finally {
        window.location.replace("/login?loggedout=1");
      }
    })();
  }, []);

  return (
    <main style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",padding:24,background:"#fffaf2",fontFamily:"system-ui"}}>
      <div style={{maxWidth:520,width:"100%",background:"#fff",border:"1px solid #e5e7eb",borderRadius:16,boxShadow:"0 10px 22px rgba(15,23,42,.08)",padding:18,position:"relative",overflow:"hidden",textAlign:"center"}}>
        <div style={{position:"absolute",left:0,top:0,bottom:0,width:8,background:"#f59e0b"}}></div>
        <img src={LOGO} alt="Thriving Scholars" style={{height:34,width:"auto",display:"block",margin:"0 auto 10px"}} />
        <h1 style={{margin:0,fontSize:22,fontWeight:900,color:"#0b1220"}}>{msg}</h1>
        <p style={{margin:"6px 0 0",color:"#475569",lineHeight:1.6}}>Redirecting to login.</p>
        <div style={{marginTop:12,fontSize:11,color:"#64748b"}}>Build: {STAMP}</div>
      </div>
    </main>
  );
}