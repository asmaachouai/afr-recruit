"use client"

import { useEffect, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"
import { CVDocument } from "@/types"
import Link from "next/link"

const MKC = {
  rust: "#C1440E", warm: "#FAE8D0", border: "#E8C4A8",
  dark: "#2C1A0E", muted: "#9A6B55", surface: "#FDF8F2",
  mid: "#5C3320", cream: "#FDF4E7",
}

function StatCard({ label, value, sub, accent }: {
  label: string; value: string; sub: string; accent: string
}) {
  return (
    <div style={{
      background: "#fff", border: `1px solid ${MKC.border}`,
      borderRadius: "10px", padding: "16px",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
        <p style={{ fontSize: "11px", fontWeight: 600, color: MKC.muted, textTransform: "uppercase", letterSpacing: "0.05em", margin: 0 }}>
          {label}
        </p>
        <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: accent, marginTop: "3px" }} />
      </div>
      <p style={{ fontSize: "22px", fontWeight: 700, color: MKC.dark, margin: "0 0 2px" }}>{value}</p>
      <p style={{ fontSize: "11px", color: MKC.muted, margin: 0 }}>{sub}</p>
    </div>
  )
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 70 ? MKC.rust : score >= 50 ? "#E8A020" : "#9A6B55"
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
        <span style={{ fontSize: "11px", color: MKC.muted }}>Compatibilite ATS</span>
        <span style={{ fontSize: "12px", fontWeight: 700, color: MKC.rust }}>{score.toFixed(0)}%</span>
      </div>
      <div style={{ height: "6px", background: MKC.warm, borderRadius: "3px" }}>
        <div style={{ height: "6px", borderRadius: "3px", background: color, width: `${score}%`, transition: "width 0.6s ease" }} />
      </div>
    </div>
  )
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

  const latestCv = cvs[0]

  return (
    <>
      <Header
        title={`Bonjour, ${user?.full_name?.split(" ")[0]}`}
        description="Apercu de votre profil de recrutement"
      />
      <div style={{ padding: "24px", background: MKC.surface, minHeight: "calc(100vh - 52px)" }}>

        {/* Zellige accent */}
        <div style={{
          height: "3px", borderRadius: "2px", marginBottom: "24px",
          background: "linear-gradient(90deg,#C1440E 0%,#E8A020 33%,#D4622A 66%,#C17B6A 100%)",
          width: "80px",
        }} />

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "12px", marginBottom: "20px" }}>
          <StatCard
            label="Statut CV"
            value={latestCv ? latestCv.status : "Aucun"}
            sub={latestCv?.detected_language?.toUpperCase() || "Deposez votre CV"}
            accent={MKC.rust}
          />
          <StatCard
            label="Score ATS"
            value={latestCv?.ats_score != null ? `${latestCv.ats_score.toFixed(0)}/100` : "—"}
            sub={latestCv?.ats_feedback?.grade ? `Grade ${latestCv.ats_feedback.grade}` : "Uploadez un CV"}
            accent="#E8A020"
          />
          <StatCard
            label="Documents"
            value={String(cvs.length)}
            sub="CV deposes"
            accent="#C17B6A"
          />
        </div>

        {/* Latest CV card */}
        <div style={{ background: "#fff", border: `1px solid ${MKC.border}`, borderRadius: "12px" }}>
          <div style={{
            padding: "14px 18px", borderBottom: `1px solid ${MKC.border}`,
            display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            <p style={{ fontSize: "13px", fontWeight: 600, color: MKC.dark, margin: 0 }}>
              Dernier CV
            </p>
            <Link href="/candidate/cv" style={{
              fontSize: "12px", color: MKC.rust, textDecoration: "none",
              padding: "5px 12px", border: `1px solid ${MKC.border}`,
              borderRadius: "7px", fontWeight: 500,
            }}>
              Gerer mes CV
            </Link>
          </div>
          <div style={{ padding: "16px 18px" }}>
            {loading ? (
              <div style={{ height: "60px", background: MKC.warm, borderRadius: "8px", animation: "pulse 1.5s infinite" }} />
            ) : latestCv ? (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "14px" }}>
                  <div>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: MKC.dark, margin: "0 0 2px" }}>
                      {latestCv.original_filename}
                    </p>
                    <p style={{ fontSize: "11px", color: MKC.muted, margin: 0 }}>
                      {new Date(latestCv.created_at).toLocaleDateString("fr-FR")}
                    </p>
                  </div>
                  <StatusPill status={latestCv.status} />
                </div>
                {latestCv.ats_score != null && <ScoreBar score={latestCv.ats_score} />}
                {latestCv.ats_feedback?.issues && (
                  <div style={{ marginTop: "12px" }}>
                    {latestCv.ats_feedback.issues.slice(0, 2).map((issue, i) => (
                      <p key={i} style={{ fontSize: "12px", color: "#E8A020", margin: "4px 0", display: "flex", gap: "6px" }}>
                        <span>•</span>{issue}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "28px 0" }}>
                <p style={{ fontSize: "13px", color: MKC.muted, margin: "0 0 14px" }}>
                  Deposez votre CV pour obtenir votre score ATS et les recommandations IA
                </p>
                <Link href="/candidate/cv" style={{
                  display: "inline-block",
                  padding: "8px 20px", background: MKC.rust, color: MKC.cream,
                  borderRadius: "8px", textDecoration: "none", fontSize: "13px", fontWeight: 600,
                }}>
                  Deposer un CV
                </Link>
              </div>
            )}
          </div>
        </div>

      </div>
    </>
  )
}

function StatusPill({ status }: { status: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    parsed:     { bg: "#EBF5F0", color: "#2A7A4B" },
    processing: { bg: "#FAE8D0", color: "#C1440E" },
    uploaded:   { bg: "#F5F5F5", color: "#6B7280" },
    failed:     { bg: "#FEF2F2", color: "#DC2626" },
  }
  const s = map[status] || map.uploaded
  return (
    <span style={{
      fontSize: "11px", fontWeight: 600,
      padding: "3px 10px", borderRadius: "20px",
      background: s.bg, color: s.color,
    }}>
      {status}
    </span>
  )
}