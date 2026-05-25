"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"

const MKC = {
  rust: "#C1440E", warm: "#FAE8D0", border: "#E8C4A8",
  dark: "#2C1A0E", muted: "#9A6B55", surface: "#FDF8F2", cream: "#FDF4E7",
  mid: "#5C3320",
}

const inputStyle: React.CSSProperties = {
  width: "100%", height: "38px",
  padding: "0 12px", borderRadius: "8px",
  border: `1px solid ${MKC.border}`,
  background: MKC.surface, color: MKC.dark,
  fontSize: "13px", outline: "none",
  boxSizing: "border-box",
}

const textareaStyle: React.CSSProperties = {
  width: "100%", padding: "10px 12px",
  borderRadius: "8px", border: `1px solid ${MKC.border}`,
  background: MKC.surface, color: MKC.dark,
  fontSize: "13px", outline: "none",
  resize: "vertical", boxSizing: "border-box",
  fontFamily: "inherit",
}

const labelStyle: React.CSSProperties = {
  fontSize: "11px", fontWeight: 600,
  color: MKC.mid, display: "block", marginBottom: "6px",
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={labelStyle}>{label}</label>
      {children}
    </div>
  )
}

export default function NewJobPage() {
  const { user, isLoading } = useRequireAuth("recruiter")
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState("")
  const [form, setForm] = useState({
    title: "", description: "", requirements: "",
    location: "", job_type: "full_time",
    required_skills: "", required_languages: ["fr"],
    experience_years_min: 0, is_remote: false, language: "fr",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    try {
      await api.post("/jobs", {
        ...form,
        required_skills: form.required_skills.split(",").map(s => s.trim()).filter(Boolean),
        experience_years_min: Number(form.experience_years_min),
      })
      router.push("/recruiter/jobs")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Echec de la creation")
    } finally {
      setLoading(false)
    }
  }

  if (isLoading) return null

  return (
    <>
      <Header title="Nouvelle offre d'emploi" description="Publiez un poste et lancez le matching IA" />
      <div style={{ padding: "24px", background: MKC.surface, minHeight: "calc(100vh - 52px)" }}>

        <div style={{ height: "3px", width: "80px", borderRadius: "2px", marginBottom: "24px",
          background: "linear-gradient(90deg,#C1440E 0%,#E8A020 50%,#C17B6A 100%)" }} />

        <div style={{ maxWidth: "600px" }}>
          <div style={{ background: "#fff", border: `1px solid ${MKC.border}`, borderRadius: "12px", padding: "24px" }}>
            <p style={{ fontSize: "13px", fontWeight: 600, color: MKC.dark, margin: "0 0 20px" }}>
              Details du poste
            </p>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <Field label="Titre du poste">
                <input style={inputStyle} value={form.title}
                  onChange={e => setForm({ ...form, title: e.target.value })}
                  placeholder="Ex: Developpeur Python Senior" required />
              </Field>

              <Field label="Description du poste">
                <textarea style={{ ...textareaStyle, minHeight: "100px" }} value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="Decrivez le role, l'equipe et les responsabilites..." required />
              </Field>

              <Field label="Exigences">
                <textarea style={{ ...textareaStyle, minHeight: "80px" }} value={form.requirements}
                  onChange={e => setForm({ ...form, requirements: e.target.value })}
                  placeholder="Ex: Python avance, FastAPI, 3 ans minimum..." />
              </Field>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <Field label="Localisation">
                  <input style={inputStyle} value={form.location}
                    onChange={e => setForm({ ...form, location: e.target.value })}
                    placeholder="Casablanca, Maroc" />
                </Field>
                <Field label="Experience minimum (ans)">
                  <input style={inputStyle} type="number" min={0}
                    value={form.experience_years_min}
                    onChange={e => setForm({ ...form, experience_years_min: Number(e.target.value) })} />
                </Field>
              </div>

              <Field label="Competences requises (separees par virgule)">
                <input style={inputStyle} value={form.required_skills}
                  onChange={e => setForm({ ...form, required_skills: e.target.value })}
                  placeholder="Python, FastAPI, PostgreSQL, React" />
              </Field>

              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <input
                  type="checkbox" id="remote" checked={form.is_remote}
                  onChange={e => setForm({ ...form, is_remote: e.target.checked })}
                  style={{ width: "16px", height: "16px", accentColor: MKC.rust, cursor: "pointer" }}
                />
                <label htmlFor="remote" style={{ fontSize: "13px", color: MKC.dark, cursor: "pointer" }}>
                  Poste en teletravail
                </label>
              </div>

              {error && (
                <div style={{ background: "#FEF3E8", border: `1px solid ${MKC.border}`, borderRadius: "8px", padding: "10px 12px" }}>
                  <p style={{ fontSize: "12px", color: MKC.rust, margin: 0 }}>{error}</p>
                </div>
              )}

              <div style={{ display: "flex", gap: "10px", paddingTop: "4px" }}>
                <button type="submit" disabled={loading} style={{
                  padding: "9px 24px", background: loading ? "#D4622A" : MKC.rust,
                  color: MKC.cream, border: "none", borderRadius: "8px",
                  fontSize: "13px", fontWeight: 600, cursor: loading ? "not-allowed" : "pointer",
                }}>
                  {loading ? "Publication..." : "Publier l'offre"}
                </button>
                <button type="button" onClick={() => router.back()} style={{
                  padding: "9px 20px", background: "transparent",
                  color: MKC.muted, border: `1px solid ${MKC.border}`,
                  borderRadius: "8px", fontSize: "13px", cursor: "pointer",
                }}>
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  )
}