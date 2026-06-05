"use client"

import { useEffect, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"
import { CVDocument } from "@/types"
import Link from "next/link"

const C = { rust:"#C1440E", warm:"#FAE8D0", border:"#E8C4A8", dark:"#2C1A0E", muted:"#9A6B55", surface:"#FDF8F2", cream:"#FDF4E7" }

function Card({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return <div style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"12px", ...style }}>{children}</div>
}

function Zellige() {
  return <div style={{ height:"3px", width:"72px", borderRadius:"2px", marginBottom:"24px", background:"linear-gradient(90deg,#C1440E 0%,#E8A020 40%,#C17B6A 100%)" }} />
}

function StatusPill({ status }: { status: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    parsed:     { bg:"#EBF5F0", color:"#2A7A4B" },
    processing: { bg:C.warm,    color:C.rust     },
    uploaded:   { bg:"#F5F5F5", color:"#6B7280"  },
    failed:     { bg:"#FEF2F2", color:"#DC2626"  },
  }
  const s = map[status] || map.uploaded
  return <span style={{ fontSize:"11px", fontWeight:600, padding:"3px 10px", borderRadius:"20px", background:s.bg, color:s.color }}>{status}</span>
}

export default function CandidateDashboard() {
  const { user, isLoading } = useRequireAuth("candidate")
  const [cvs,     setCvs]     = useState<CVDocument[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    api.get("/candidates/cv").then(({ data }) => setCvs(data)).finally(() => setLoading(false))
  }, [user])

  if (isLoading) return null

  const cv = cvs[0]

  return (
    <>
      <Header title={`Bonjour, ${user?.full_name?.split(" ")[0]}`} description="Apercu de votre profil de recrutement" />
      <div style={{ padding:"24px", background:C.surface, minHeight:"calc(100vh - 52px)", animation:"slideUp 0.3s ease" }}>
        <Zellige />

        {/* Stats row */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"12px", marginBottom:"20px" }}>
          {[
            { label:"Statut CV",    value: cv ? cv.status : "Aucun",                              sub: cv?.detected_language?.toUpperCase() || "Deposez votre CV", dot:"#C1440E" },
            { label:"Score ATS",    value: cv?.ats_score != null ? `${cv.ats_score.toFixed(0)}/100` : "—", sub: cv?.ats_feedback?.grade ? `Grade ${cv.ats_feedback.grade}` : "Uploadez un CV", dot:"#E8A020" },
            { label:"Documents",    value: String(cvs.length),                                    sub:"CV deposes", dot:"#C17B6A" },
          ].map(s => (
            <Card key={s.label} style={{ padding:"16px" }}>
              <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"10px" }}>
                <span style={{ fontSize:"11px", fontWeight:600, color:C.muted, textTransform:"uppercase", letterSpacing:"0.05em" }}>{s.label}</span>
                <div style={{ width:"7px", height:"7px", borderRadius:"50%", background:s.dot, marginTop:"2px" }} />
              </div>
              <p style={{ fontSize:"22px", fontWeight:700, color:C.dark, margin:"0 0 2px" }}>{s.value}</p>
              <p style={{ fontSize:"11px", color:C.muted, margin:0 }}>{s.sub}</p>
            </Card>
          ))}
        </div>

        {/* Latest CV */}
        <Card>
          <div style={{ padding:"14px 18px", borderBottom:`1px solid ${C.border}`, display:"flex", justifyContent:"space-between", alignItems:"center" }}>
            <p style={{ fontSize:"13px", fontWeight:700, color:C.dark, margin:0 }}>Dernier CV</p>
            <Link href="/candidate/cv" style={{ fontSize:"12px", color:C.rust, padding:"5px 14px", border:`1px solid ${C.border}`, borderRadius:"8px", textDecoration:"none", fontWeight:600 }}>
              Gerer mes CV
            </Link>
          </div>
          <div style={{ padding:"18px" }}>
            {loading ? (
              <div style={{ height:"60px", background:C.warm, borderRadius:"8px" }} />
            ) : cv ? (
              <>
                <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"14px" }}>
                  <div>
                    <p style={{ fontSize:"13px", fontWeight:600, color:C.dark, margin:"0 0 3px" }}>{cv.original_filename}</p>
                    <p style={{ fontSize:"11px", color:C.muted, margin:0 }}>{new Date(cv.created_at).toLocaleDateString("fr-FR")}</p>
                  </div>
                  <StatusPill status={cv.status} />
                </div>
                {cv.ats_score != null && (
                  <>
                    <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"6px" }}>
                      <span style={{ fontSize:"11px", color:C.muted }}>Compatibilite ATS</span>
                      <span style={{ fontSize:"12px", fontWeight:700, color:C.rust }}>{cv.ats_score.toFixed(0)}%</span>
                    </div>
                    <div style={{ height:"6px", background:C.warm, borderRadius:"3px", marginBottom:"12px" }}>
                      <div style={{ height:"6px", borderRadius:"3px", background:C.rust, width:`${cv.ats_score}%`, transition:"width 0.6s ease" }} />
                    </div>
                  </>
                )}
                {cv.ats_feedback?.issues.slice(0,2).map((issue, i) => (
                  <p key={i} style={{ fontSize:"12px", color:"#E8A020", margin:"4px 0", display:"flex", gap:"6px" }}>
                    <span>•</span>{issue}
                  </p>
                ))}
              </>
            ) : (
              <div style={{ textAlign:"center", padding:"24px 0" }}>
                <p style={{ fontSize:"13px", color:C.muted, margin:"0 0 14px" }}>Deposez votre CV pour obtenir votre score ATS et les recommandations IA</p>
                <Link href="/candidate/cv" style={{ padding:"8px 20px", background:C.rust, color:C.cream, borderRadius:"8px", textDecoration:"none", fontSize:"13px", fontWeight:700 }}>
                  Deposer un CV
                </Link>
              </div>
            )}
          </div>
        </Card>

      </div>
    </>
  )
}