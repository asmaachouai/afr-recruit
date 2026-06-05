"use client"

import { useEffect, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"
import { Job, MatchResponse } from "@/types"
import Link from "next/link"

const C = { rust:"#C1440E", warm:"#FAE8D0", border:"#E8C4A8", dark:"#2C1A0E", muted:"#9A6B55", surface:"#FDF8F2", cream:"#FDF4E7", green:"#2A7A4B", greenBg:"#EBF5F0" }

function Zellige() {
  return <div style={{ height:"3px", width:"72px", borderRadius:"2px", marginBottom:"24px", background:"linear-gradient(90deg,#C1440E 0%,#E8A020 40%,#C17B6A 100%)" }} />
}

export default function JobsPage() {
  const { user, isLoading } = useRequireAuth("recruiter")
  const [jobs,         setJobs]         = useState<Job[]>([])
  const [loading,      setLoading]      = useState(true)
  const [matching,     setMatching]     = useState<string | null>(null)
  const [matchResults, setMatchResults] = useState<Record<string, MatchResponse>>({})

  useEffect(() => {
    if (!user) return
    api.get("/jobs").then(({ data }) => setJobs(data)).finally(() => setLoading(false))
  }, [user])

  const runMatch = async (jobId: string) => {
    setMatching(jobId)
    try {
      const { data } = await api.post(`/jobs/${jobId}/match`)
      setMatchResults(prev => ({ ...prev, [jobId]: data }))
    } catch {}
    finally { setMatching(null) }
  }

  if (isLoading) return null

  return (
    <>
      <Header title="Offres d'emploi" description="Gerez et lancez le matching IA candidats" />
      <div style={{ padding:"24px", background:C.surface, minHeight:"calc(100vh - 52px)", animation:"slideUp 0.3s ease" }}>
        <Zellige />

        <div style={{ display:"flex", justifyContent:"flex-end", marginBottom:"16px" }}>
          <Link href="/recruiter/jobs/new" style={{ padding:"8px 18px", background:C.rust, color:C.cream, borderRadius:"9px", textDecoration:"none", fontSize:"13px", fontWeight:700 }}>
            + Nouvelle offre
          </Link>
        </div>

        {loading ? (
          <div style={{ display:"flex", flexDirection:"column", gap:"10px" }}>
            {[1,2,3].map(i => <div key={i} style={{ height:"100px", background:C.warm, borderRadius:"10px" }} />)}
          </div>
        ) : jobs.length === 0 ? (
          <div style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"12px", padding:"48px", textAlign:"center" }}>
            <p style={{ fontSize:"13px", color:C.muted }}>Aucune offre publiee</p>
          </div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:"12px" }}>
            {jobs.map(job => {
              const result = matchResults[job.id]
              return (
                <div key={job.id} style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"12px", overflow:"hidden" }}>
                  <div style={{ padding:"16px", display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:"16px" }}>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ display:"flex", alignItems:"center", gap:"8px", marginBottom:"4px" }}>
                        <p style={{ fontSize:"14px", fontWeight:700, color:C.dark, margin:0 }}>{job.title}</p>
                        {job.is_remote && (
                          <span style={{ fontSize:"10px", fontWeight:600, padding:"2px 8px", borderRadius:"20px", background:C.greenBg, color:C.green }}>Remote</span>
                        )}
                      </div>
                      <p style={{ fontSize:"12px", color:C.muted, margin:"0 0 10px" }}>{job.location || "Non specifie"} • {job.experience_years_min}+ ans</p>
                      <div style={{ display:"flex", flexWrap:"wrap", gap:"5px" }}>
                        {job.required_skills?.slice(0,6).map(skill => (
                          <span key={skill} style={{ fontSize:"11px", padding:"2px 9px", borderRadius:"20px", background:C.warm, color:C.rust, border:`1px solid ${C.border}`, fontWeight:500 }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button
                      onClick={() => runMatch(job.id)}
                      disabled={matching === job.id}
                      style={{ padding:"8px 16px", flexShrink:0, background:C.warm, color:C.rust, border:`1px solid ${C.border}`, borderRadius:"9px", fontSize:"12px", fontWeight:700, cursor:matching === job.id ? "not-allowed" : "pointer" }}
                    >
                      {matching === job.id ? "Matching..." : "Lancer le matching IA"}
                    </button>
                  </div>

                  {result && result.matches.length > 0 && (
                    <div style={{ borderTop:`1px solid ${C.border}`, padding:"14px 16px" }}>
                      <p style={{ fontSize:"11px", fontWeight:600, color:C.muted, textTransform:"uppercase", letterSpacing:"0.05em", margin:"0 0 10px" }}>
                        {result.total_candidates} candidat{result.total_candidates > 1 ? "s" : ""} classe{result.total_candidates > 1 ? "s" : ""}
                      </p>
                      <div style={{ display:"flex", flexDirection:"column", gap:"6px" }}>
                        {result.matches.slice(0,4).map(match => (
                          <div key={match.candidate_id} style={{ display:"flex", alignItems:"center", gap:"10px", background:C.surface, borderRadius:"8px", padding:"10px 12px" }}>
                            <span style={{ fontSize:"12px", fontWeight:700, color:C.muted, width:"20px", flexShrink:0 }}>#{match.rank_position}</span>
                            <div style={{ flex:1, minWidth:0 }}>
                              <p style={{ fontSize:"13px", fontWeight:600, color:C.dark, margin:"0 0 1px" }}>{match.full_name}</p>
                              <p style={{ fontSize:"11px", color:C.muted, margin:0, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                                {match.skills_matched.slice(0,4).join(", ")}
                              </p>
                            </div>
                            <div style={{ textAlign:"right", flexShrink:0 }}>
                              <p style={{ fontSize:"14px", fontWeight:700, color:C.rust, margin:"0 0 1px" }}>{(match.ranking_score * 100).toFixed(0)}%</p>
                              <p style={{ fontSize:"10px", color:C.muted, margin:0 }}>{match.detected_language?.toUpperCase()}</p>
                            </div>
                          </div>
                        ))}
                      </div>
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