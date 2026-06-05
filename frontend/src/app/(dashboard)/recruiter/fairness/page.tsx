"use client"

import { useEffect, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"
import { Job, JobFairnessReport } from "@/types"

const C = { rust:"#C1440E", warm:"#FAE8D0", border:"#E8C4A8", dark:"#2C1A0E", muted:"#9A6B55", surface:"#FDF8F2", cream:"#FDF4E7", green:"#2A7A4B", greenBg:"#EBF5F0", amber:"#B8600A", amberBg:"#FEF3E2" }

function Zellige() {
  return <div style={{ height:"3px", width:"72px", borderRadius:"2px", marginBottom:"24px", background:"linear-gradient(90deg,#C1440E 0%,#E8A020 40%,#C17B6A 100%)" }} />
}

export default function FairnessPage() {
  const { user, isLoading } = useRequireAuth("recruiter")
  const [jobs,      setJobs]      = useState<Job[]>([])
  const [reports,   setReports]   = useState<Record<string, JobFairnessReport>>({})
  const [loading,   setLoading]   = useState(true)
  const [analyzing, setAnalyzing] = useState<string | null>(null)

  useEffect(() => {
    if (!user) return
    api.get("/jobs").then(({ data }) => setJobs(data)).finally(() => setLoading(false))
  }, [user])

  const runAnalysis = async (jobId: string) => {
    setAnalyzing(jobId)
    try {
      const { data } = await api.post(`/fairness/job/${jobId}/analyze-all`)
      setReports(prev => ({ ...prev, [jobId]: data }))
    } catch {}
    finally { setAnalyzing(null) }
  }

  if (isLoading) return null

  return (
    <>
      <Header title="Rapports d'equite" description="Detection de biais et analyse d'impact disparate" />
      <div style={{ padding:"24px", background:C.surface, minHeight:"calc(100vh - 52px)", animation:"slideUp 0.3s ease" }}>
        <Zellige />

        {/* Info */}
        <div style={{ background:C.warm, border:`1px solid ${C.border}`, borderLeft:`4px solid ${C.rust}`, borderRadius:"8px", padding:"14px 16px", marginBottom:"20px" }}>
          <p style={{ fontSize:"12px", fontWeight:700, color:C.dark, margin:"0 0 4px" }}>Regle des 4/5 — Standard EEOC</p>
          <p style={{ fontSize:"12px", color:C.muted, margin:0, lineHeight:1.7 }}>
            Si le taux de selection d'un groupe linguistique est inferieur a 80% du groupe le mieux classe,
            un impact disparate est detecte. Aide a identifier les biais involontaires contre les candidats francophones ou arabophones.
          </p>
        </div>

        {loading ? (
          <div style={{ display:"flex", flexDirection:"column", gap:"10px" }}>
            {[1,2].map(i => <div key={i} style={{ height:"100px", background:C.warm, borderRadius:"10px" }} />)}
          </div>
        ) : jobs.length === 0 ? (
          <div style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"12px", padding:"48px", textAlign:"center" }}>
            <p style={{ fontSize:"13px", color:C.muted }}>Aucune offre a analyser</p>
          </div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:"12px" }}>
            {jobs.map(job => {
              const report = reports[job.id]
              return (
                <div key={job.id} style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"12px", overflow:"hidden" }}>
                  <div style={{ padding:"16px", display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:"16px" }}>
                    <div>
                      <p style={{ fontSize:"14px", fontWeight:700, color:C.dark, margin:"0 0 6px" }}>{job.title}</p>
                      {report && (
                        <div style={{ display:"flex", alignItems:"center", gap:"8px" }}>
                          <span style={{ fontSize:"11px", fontWeight:600, padding:"2px 10px", borderRadius:"20px", background:report.overall_fair ? C.greenBg : C.amberBg, color:report.overall_fair ? C.green : C.amber }}>
                            {report.overall_fair ? "Equitable" : "Biais detecte"}
                          </span>
                          <span style={{ fontSize:"12px", color:C.muted }}>Ratio DI: {report.disparate_impact_ratio.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => runAnalysis(job.id)}
                      disabled={analyzing === job.id}
                      style={{ padding:"8px 16px", flexShrink:0, background:C.warm, color:C.rust, border:`1px solid ${C.border}`, borderRadius:"9px", fontSize:"12px", fontWeight:700, cursor:analyzing === job.id ? "not-allowed" : "pointer" }}
                    >
                      {analyzing === job.id ? "Analyse..." : "Lancer l'analyse"}
                    </button>
                  </div>

                  {report && (
                    <div style={{ borderTop:`1px solid ${C.border}`, padding:"14px 16px" }}>
                      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"10px", marginBottom:"12px" }}>
                        {[
                          { label:"Candidatures", value:String(report.total_applications),             warn:false                                     },
                          { label:"Signalees",     value:String(report.flagged_applications),           warn:report.flagged_applications > 0           },
                          { label:"Ratio DI",      value:report.disparate_impact_ratio.toFixed(2),      warn:report.disparate_impact_ratio < 0.8       },
                        ].map(m => (
                          <div key={m.label} style={{ background:C.surface, borderRadius:"8px", padding:"10px 12px" }}>
                            <p style={{ fontSize:"10px", color:C.muted, margin:"0 0 3px" }}>{m.label}</p>
                            <p style={{ fontSize:"16px", fontWeight:700, margin:0, color:m.warn ? C.amber : C.dark }}>{m.value}</p>
                          </div>
                        ))}
                      </div>

                      {Object.keys(report.language_distribution).length > 0 && (
                        <div style={{ marginBottom:"10px" }}>
                          <p style={{ fontSize:"11px", color:C.muted, margin:"0 0 6px" }}>Distribution linguistique</p>
                          <div style={{ display:"flex", gap:"6px", flexWrap:"wrap" }}>
                            {Object.entries(report.language_distribution).map(([lang, count]) => (
                              <span key={lang} style={{ fontSize:"11px", padding:"3px 10px", borderRadius:"20px", background:C.warm, color:C.rust, border:`1px solid ${C.border}`, fontWeight:500 }}>
                                {lang.toUpperCase()}: {count}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {report.recommendations.slice(0,2).map((rec, i) => (
                        <p key={i} style={{ fontSize:"12px", color:C.muted, margin:"4px 0", display:"flex", gap:"6px", lineHeight:1.6 }}>
                          <span style={{ flexShrink:0, color:C.rust }}>•</span>{rec}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </>
  )
}