"use client"

import { useEffect, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"
import { Job } from "@/types"
import Link from "next/link"

const MKC = {
  rust: "#C1440E", warm: "#FAE8D0", border: "#E8C4A8",
  dark: "#2C1A0E", muted: "#9A6B55", surface: "#FDF8F2", cream: "#FDF4E7",
}

export default function RecruiterDashboard() {
  const { user, isLoading } = useRequireAuth("recruiter")
  const [jobs,    setJobs]    = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    api.get("/jobs").then(({ data }) => setJobs(data)).finally(() => setLoading(false))
  }, [user])

  if (isLoading) return null

  return (
    <>
      <Header
        title={`Bonjour, ${user?.full_name?.split(" ")[0]}`}
        description="Gerez vos offres et consultez les candidats classes par IA"
      />
      <div style={{ padding: "24px", background: MKC.surface, minHeight: "calc(100vh - 52px)" }}>

        <div style={{ height: "3px", width: "80px", borderRadius: "2px", marginBottom: "24px",
          background: "linear-gradient(90deg,#C1440E 0%,#E8A020 50%,#C17B6A 100%)" }} />

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "12px", marginBottom: "20px" }}>
          {[
            { label: "Offres actives",    value: String(jobs.length), sub: "Publiees",         accent: MKC.rust    },
            { label: "Matching IA",       value: "Actif",             sub: "Multilingue",      accent: "#E8A020"   },
            { label: "Equite",            value: "Surveille",         sub: "Detection biais",  accent: "#C17B6A"   },
          ].map(s => (
            <div key={s.label} style={{ background: "#fff", border: `1px solid ${MKC.border}`, borderRadius: "10px", padding: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                <p style={{ fontSize: "11px", fontWeight: 600, color: MKC.muted, textTransform: "uppercase", letterSpacing: "0.05em", margin: 0 }}>
                  {s.label}
                </p>
                <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: s.accent, marginTop: "3px" }} />
              </div>
              <p style={{ fontSize: "20px", fontWeight: 700, color: MKC.dark, margin: "0 0 2px" }}>{s.value}</p>
              <p style={{ fontSize: "11px", color: MKC.muted, margin: 0 }}>{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Recent jobs */}
        <div style={{ background: "#fff", border: `1px solid ${MKC.border}`, borderRadius: "12px" }}>
          <div style={{
            padding: "14px 18px", borderBottom: `1px solid ${MKC.border}`,
            display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            <p style={{ fontSize: "13px", fontWeight: 600, color: MKC.dark, margin: 0 }}>
              Offres recentes
            </p>
            <Link href="/recruiter/jobs/new" style={{
              display: "flex", alignItems: "center", gap: "6px",
              padding: "6px 14px", background: MKC.rust, color: MKC.cream,
              borderRadius: "8px", textDecoration: "none", fontSize: "12px", fontWeight: 600,
            }}>
              + Nouvelle offre
            </Link>
          </div>
          <div style={{ padding: "8px 0" }}>
            {loading ? (
              <div style={{ padding: "12px 18px" }}>
                {[1, 2, 3].map(i => (
                  <div key={i} style={{ height: "44px", background: MKC.warm, borderRadius: "8px", marginBottom: "8px" }} />
                ))}
              </div>
            ) : jobs.length === 0 ? (
              <div style={{ textAlign: "center", padding: "36px 0" }}>
                <p style={{ fontSize: "13px", color: MKC.muted, margin: "0 0 14px" }}>
                  Aucune offre publiee
                </p>
                <Link href="/recruiter/jobs/new" style={{
                  padding: "8px 20px", background: MKC.rust, color: MKC.cream,
                  borderRadius: "8px", textDecoration: "none", fontSize: "12px", fontWeight: 600,
                }}>
                  Publier une offre
                </Link>
              </div>
            ) : (
              jobs.slice(0, 5).map((job, i) => (
                <div key={job.id} style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 18px",
                  borderBottom: i < Math.min(jobs.length, 5) - 1 ? `1px solid ${MKC.border}` : "none",
                }}>
                  <div>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: MKC.dark, margin: "0 0 2px" }}>
                      {job.title}
                    </p>
                    <p style={{ fontSize: "11px", color: MKC.muted, margin: 0 }}>
                      {job.location || "Remote"} • {job.required_skills?.slice(0, 3).join(", ")}
                    </p>
                  </div>
                  <Link href={`/recruiter/jobs`} style={{
                    fontSize: "12px", color: MKC.rust,
                    padding: "4px 12px", border: `1px solid ${MKC.border}`,
                    borderRadius: "7px", textDecoration: "none", fontWeight: 500,
                  }}>
                    Voir
                  </Link>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </>
  )
}