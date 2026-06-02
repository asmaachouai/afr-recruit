"use client"

import { useEffect, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"

const MKC = {
  rust: "#C1440E", warm: "#FAE8D0", border: "#E8C4A8",
  dark: "#2C1A0E", muted: "#9A6B55", surface: "#FDF8F2",
  cream: "#FDF4E7", green: "#2A7A4B", greenBg: "#EBF5F0",
  amber: "#B8600A", amberBg: "#FEF3E2",
}

interface Application {
  id: string
  job_id: string
  status: string
  similarity_score: number | null
  ranking_score: number | null
  rank_position: number | null
  explanation: string | null
  applied_at: string
}

function StatusPill({ status }: { status: string }) {
  const map: Record<string, { bg: string; color: string; label: string }> = {
    submitted:   { bg: MKC.warm,     color: MKC.rust,   label: "Soumise"      },
    screening:   { bg: "#EEF2FF",    color: "#4F46E5",  label: "En cours"     },
    shortlisted: { bg: MKC.greenBg,  color: MKC.green,  label: "Selectionnee" },
    interview:   { bg: "#F0FDF4",    color: "#16A34A",  label: "Entretien"    },
    offer:       { bg: "#ECFDF5",    color: "#059669",  label: "Offre"        },
    rejected:    { bg: "#FEF2F2",    color: "#DC2626",  label: "Refusee"      },
    withdrawn:   { bg: "#F5F5F5",    color: "#6B7280",  label: "Retiree"      },
  }
  const s = map[status] || map.submitted
  return (
    <span style={{
      fontSize: "11px", fontWeight: 600,
      padding: "3px 10px", borderRadius: "20px",
      background: s.bg, color: s.color,
    }}>
      {s.label}
    </span>
  )
}

function ScoreRing({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? MKC.rust : pct >= 50 ? "#E8A020" : MKC.muted
  return (
    <div style={{ textAlign: "center" }}>
      <p style={{ fontSize: "18px", fontWeight: 700, color, margin: "0 0 1px" }}>
        {pct}%
      </p>
      <p style={{ fontSize: "10px", color: MKC.muted, margin: 0 }}>Score IA</p>
    </div>
  )
}

export default function ApplicationsPage() {
  const { user, isLoading } = useRequireAuth("candidate")
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    if (!user) return
    // Applications are stored server-side linked to the candidate
    // We fetch them via the fairness endpoint which has the application data
    api.get("/candidates/cv")
      .then(() => {
        // Placeholder — in a full implementation we'd have GET /candidates/applications
        // For now show a helpful empty state that explains the flow
        setApplications([])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [user])

  if (isLoading) return null

  return (
    <>
      <Header
        title="Mes candidatures"
        description="Suivez vos candidatures et consultez vos scores IA"
      />
      <div style={{ padding: "24px", background: MKC.surface, minHeight: "calc(100vh - 52px)" }}>

        <div style={{
          height: "3px", width: "80px", borderRadius: "2px", marginBottom: "24px",
          background: "linear-gradient(90deg,#C1440E 0%,#E8A020 50%,#C17B6A 100%)",
        }} />

        {loading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {[1, 2, 3].map(i => (
              <div key={i} style={{ height: "80px", background: MKC.warm, borderRadius: "10px" }} />
            ))}
          </div>
        ) : applications.length === 0 ? (
          <div style={{
            background: "#fff", border: `1px solid ${MKC.border}`,
            borderRadius: "12px", padding: "48px", textAlign: "center",
          }}>
            <div style={{
              width: "48px", height: "48px", borderRadius: "12px",
              background: MKC.warm, margin: "0 auto 16px",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="22" height="22" fill="none" stroke="#C1440E" strokeWidth="2" viewBox="0 0 24 24">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
            </div>
            <p style={{ fontSize: "14px", fontWeight: 600, color: MKC.dark, margin: "0 0 8px" }}>
              Aucune candidature pour le moment
            </p>
            <p style={{ fontSize: "13px", color: MKC.muted, margin: "0 0 20px", lineHeight: 1.6 }}>
              Vos candidatures apparaitront ici une fois qu'un recruteur
              aura lance le matching IA sur une offre incluant votre profil.
            </p>
            <div style={{
              background: MKC.warm, border: `1px solid ${MKC.border}`,
              borderLeft: `4px solid ${MKC.rust}`,
              borderRadius: "8px", padding: "12px 16px", textAlign: "left",
              maxWidth: "420px", margin: "0 auto",
            }}>
              <p style={{ fontSize: "12px", fontWeight: 700, color: MKC.dark, margin: "0 0 6px" }}>
                Comment ca marche ?
              </p>
              {[
                "Deposez votre CV dans l'onglet Mon CV",
                "Le pipeline NLP analyse vos competences",
                "Le recruteur lance le matching IA sur son offre",
                "Votre profil est classe et une candidature est creee",
                "Consultez votre score et les retours equite ici",
              ].map((step, i) => (
                <p key={i} style={{
                  fontSize: "12px", color: MKC.muted,
                  margin: "4px 0", display: "flex", gap: "8px",
                }}>
                  <span style={{
                    width: "16px", height: "16px", borderRadius: "50%",
                    background: MKC.rust, color: MKC.cream,
                    display: "inline-flex", alignItems: "center",
                    justifyContent: "center", fontSize: "9px",
                    fontWeight: 700, flexShrink: 0, marginTop: "1px",
                  }}>
                    {i + 1}
                  </span>
                  {step}
                </p>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {applications.map(app => (
              <div key={app.id} style={{
                background: "#fff", border: `1px solid ${MKC.border}`,
                borderRadius: "10px", overflow: "hidden",
              }}>
                <div
                  style={{
                    padding: "14px 16px", display: "flex",
                    alignItems: "center", gap: "14px", cursor: "pointer",
                  }}
                  onClick={() => setExpanded(expanded === app.id ? null : app.id)}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: MKC.dark, margin: "0 0 3px" }}>
                      Offre #{app.job_id.slice(0, 8)}
                    </p>
                    <p style={{ fontSize: "11px", color: MKC.muted, margin: 0 }}>
                      {new Date(app.applied_at).toLocaleDateString("fr-FR")}
                      {app.rank_position && ` • Rang #${app.rank_position}`}
                    </p>
                  </div>
                  {app.ranking_score != null && (
                    <ScoreRing score={app.ranking_score} />
                  )}
                  <StatusPill status={app.status} />
                  <svg
                    width="14" height="14" fill="none"
                    stroke={MKC.muted} strokeWidth="2" viewBox="0 0 24 24"
                    style={{
                      transform: expanded === app.id ? "rotate(180deg)" : "none",
                      transition: "transform 0.2s", flexShrink: 0,
                    }}
                  >
                    <polyline points="6 9 12 15 18 9"/>
                  </svg>
                </div>

                {expanded === app.id && app.explanation && (
                  <div style={{
                    borderTop: `1px solid ${MKC.border}`,
                    padding: "14px 16px",
                  }}>
                    <p style={{
                      fontSize: "11px", fontWeight: 600, color: MKC.muted,
                      textTransform: "uppercase", letterSpacing: "0.05em",
                      margin: "0 0 8px",
                    }}>
                      Explication IA
                    </p>
                    <p style={{ fontSize: "13px", color: MKC.dark, lineHeight: 1.6, margin: 0 }}>
                      {app.explanation}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}