"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"

const C = { rust:"#C1440E", warm:"#FAE8D0", border:"#E8C4A8", dark:"#2C1A0E", muted:"#9A6B55", surface:"#FDF8F2", cream:"#FDF4E7", mid:"#5C3320" }

const inp: React.CSSProperties = { width:"100%", height:"40px", padding:"0 12px", borderRadius:"8px", border:`1px solid ${C.border}`, background:C.surface, color:C.dark, fontSize:"13px", outline:"none", boxSizing:"border-box" }
const ta:  React.CSSProperties = { ...inp, height:"auto", padding:"10px 12px", resize:"vertical", fontFamily:"inherit" }
const lbl: React.CSSProperties = { fontSize:"11px", fontWeight:600, color:C.mid, display:"block", marginBottom:"6px" }

function Zellige() {
  return <div style={{ height:"3px", width:"72px", borderRadius:"2px", marginBottom:"24px", background:"linear-gradient(90deg,#C1440E 0%,#E8A020 40%,#C17B6A 100%)" }} />
}

export default function NewJobPage() {
  const { user, isLoading } = useRequireAuth("recruiter")
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState("")
  const [form, setForm] = useState({
    title:"", description:"", requirements:"", location:"",
    job_type:"full_time", required_skills:"", required_languages:["fr"],
    experience_years_min:0, is_remote:false, language:"fr",
  })

  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError("")
    try {
      await api.post("/jobs", {
        ...form,
        required_skills: form.required_skills.split(",").map(s => s.trim()).filter(Boolean),
        experience_years_min: Number(form.experience_years_min),
      })
      router.push("/recruiter/jobs")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Echec de la creation")
    } finally { setLoading(false) }
  }

  if (isLoading) return null

  return (
    <>
      <Header title="Nouvelle offre d'emploi" description="Publiez un poste et lancez le matching IA" />
      <div style={{ padding:"24px", background:C.surface, minHeight:"calc(100vh - 52px)", animation:"slideUp 0.3s ease" }}>
        <Zellige />
        <div style={{ maxWidth:"600px" }}>
          <div style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"14px", padding:"26px" }}>
            <p style={{ fontSize:"14px", fontWeight:700, color:C.dark, margin:"0 0 22px" }}>Details du poste</p>
            <form onSubmit={handleSubmit} style={{ display:"flex", flexDirection:"column", gap:"16px" }}>

              <div><label style={lbl}>Titre du poste</label>
                <input style={inp} value={form.title} onChange={e => set("title", e.target.value)} placeholder="Ex: Developpeur Python Senior" required /></div>

              <div><label style={lbl}>Description</label>
                <textarea style={{ ...ta, minHeight:"100px" }} value={form.description} onChange={e => set("description", e.target.value)} placeholder="Decrivez le role, l'equipe et les responsabilites..." required /></div>

              <div><label style={lbl}>Exigences</label>
                <textarea style={{ ...ta, minHeight:"80px" }} value={form.requirements} onChange={e => set("requirements", e.target.value)} placeholder="Ex: Python avance, FastAPI, 3 ans minimum..." /></div>

              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"12px" }}>
                <div><label style={lbl}>Localisation</label>
                  <input style={inp} value={form.location} onChange={e => set("location", e.target.value)} placeholder="Casablanca, Maroc" /></div>
                <div><label style={lbl}>Experience min (ans)</label>
                  <input style={inp} type="number" min={0} value={form.experience_years_min} onChange={e => set("experience_years_min", e.target.value)} /></div>
              </div>

              <div><label style={lbl}>Competences requises (separees par virgule)</label>
                <input style={inp} value={form.required_skills} onChange={e => set("required_skills", e.target.value)} placeholder="Python, FastAPI, PostgreSQL, React" /></div>

              <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
                <input type="checkbox" id="remote" checked={form.is_remote} onChange={e => set("is_remote", e.target.checked)}
                  style={{ width:"16px", height:"16px", accentColor:C.rust, cursor:"pointer" }} />
                <label htmlFor="remote" style={{ fontSize:"13px", color:C.dark, cursor:"pointer" }}>Poste en teletravail</label>
              </div>

              {error && <div style={{ background:"#FEF3E8", border:`1px solid ${C.border}`, borderRadius:"8px", padding:"10px 12px" }}>
                <p style={{ fontSize:"12px", color:C.rust, margin:0 }}>{error}</p></div>}

              <div style={{ display:"flex", gap:"10px", paddingTop:"4px" }}>
                <button type="submit" disabled={loading} style={{ padding:"10px 24px", background:loading ? "#D4622A" : C.rust, color:C.cream, border:"none", borderRadius:"9px", fontSize:"13px", fontWeight:700, cursor:loading ? "not-allowed" : "pointer" }}>
                  {loading ? "Publication..." : "Publier l'offre"}
                </button>
                <button type="button" onClick={() => router.back()} style={{ padding:"10px 20px", background:"transparent", color:C.muted, border:`1px solid ${C.border}`, borderRadius:"9px", fontSize:"13px", cursor:"pointer" }}>
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