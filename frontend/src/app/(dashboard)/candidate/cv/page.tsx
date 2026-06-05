"use client"

import { useEffect, useRef, useState } from "react"
import { useRequireAuth } from "@/hooks/useAuth"
import { Header } from "@/components/layout/Header"
import api from "@/lib/api"
import { CVDocument } from "@/types"

const C = { rust:"#C1440E", warm:"#FAE8D0", border:"#E8C4A8", dark:"#2C1A0E", muted:"#9A6B55", surface:"#FDF8F2", cream:"#FDF4E7" }

function Zellige() {
  return <div style={{ height:"3px", width:"72px", borderRadius:"2px", marginBottom:"24px", background:"linear-gradient(90deg,#C1440E 0%,#E8A020 40%,#C17B6A 100%)" }} />
}

export default function CVPage() {
  const { user, isLoading } = useRequireAuth("candidate")
  const [cvs,         setCvs]         = useState<CVDocument[]>([])
  const [loading,     setLoading]     = useState(true)
  const [uploading,   setUploading]   = useState(false)
  const [uploadError, setUploadError] = useState("")
  const [expanded,    setExpanded]    = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const fetchCvs = () => {
    api.get("/candidates/cv").then(({ data }) => setCvs(data)).finally(() => setLoading(false))
  }

  useEffect(() => { if (user) fetchCvs() }, [user])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true); setUploadError("")
    const form = new FormData()
    form.append("file", file)
    try {
      await api.post("/candidates/cv/upload", form, { headers: { "Content-Type": "multipart/form-data" } })
      fetchCvs()
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Echec du telechargement")
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ""
    }
  }

  if (isLoading) return null

  return (
    <>
      <Header title="Mon CV" description="Deposez et gerez vos documents CV" />
      <div style={{ padding:"24px", background:C.surface, minHeight:"calc(100vh - 52px)", animation:"slideUp 0.3s ease" }}>
        <Zellige />

        {/* Upload zone */}
        <div style={{ background:"#fff", border:`2px dashed ${C.border}`, borderRadius:"14px", padding:"36px", textAlign:"center", marginBottom:"20px" }}>
          <div style={{ width:"48px", height:"48px", borderRadius:"12px", background:C.warm, margin:"0 auto 14px", display:"flex", alignItems:"center", justifyContent:"center" }}>
            <svg width="22" height="22" fill="none" stroke="#C1440E" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
          </div>
          <p style={{ fontSize:"14px", fontWeight:700, color:C.dark, margin:"0 0 5px" }}>Deposez votre CV</p>
          <p style={{ fontSize:"12px", color:C.muted, margin:"0 0 18px" }}>PDF, DOCX ou TXT — max 10 Mo</p>
          <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" onChange={handleUpload} style={{ display:"none" }} id="cv-upload" />
          <label htmlFor="cv-upload">
            <span style={{ display:"inline-block", padding:"9px 22px", background:uploading ? "#D4622A" : C.rust, color:C.cream, borderRadius:"9px", fontSize:"13px", fontWeight:700, cursor:uploading ? "not-allowed" : "pointer" }}>
              {uploading ? "Traitement..." : "Choisir un fichier"}
            </span>
          </label>
          {uploadError && <p style={{ fontSize:"12px", color:C.rust, marginTop:"12px" }}>{uploadError}</p>}
        </div>

        {/* CV list */}
        {loading ? (
          <div style={{ display:"flex", flexDirection:"column", gap:"10px" }}>
            {[1,2].map(i => <div key={i} style={{ height:"72px", background:C.warm, borderRadius:"10px" }} />)}
          </div>
        ) : cvs.length === 0 ? (
          <p style={{ textAlign:"center", color:C.muted, fontSize:"13px", padding:"40px 0" }}>Aucun CV depose pour le moment</p>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:"10px" }}>
            {cvs.map(cv => (
              <div key={cv.id} style={{ background:"#fff", border:`1px solid ${C.border}`, borderRadius:"12px", overflow:"hidden" }}>
                <div style={{ padding:"14px 16px", display:"flex", alignItems:"center", justifyContent:"space-between", cursor:"pointer" }}
                  onClick={() => setExpanded(expanded === cv.id ? null : cv.id)}>
                  <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
                    <div style={{ width:"36px", height:"36px", borderRadius:"9px", background:C.warm, display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
                      <svg width="16" height="16" fill="none" stroke="#C1440E" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
                      </svg>
                    </div>
                    <div>
                      <p style={{ fontSize:"13px", fontWeight:600, color:C.dark, margin:"0 0 2px" }}>{cv.original_filename}</p>
                      <p style={{ fontSize:"11px", color:C.muted, margin:0 }}>
                        {cv.detected_language?.toUpperCase() || "—"} • {new Date(cv.created_at).toLocaleDateString("fr-FR")}
                      </p>
                    </div>
                  </div>
                  <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
                    {cv.ats_score != null && (
                      <div style={{ textAlign:"right" }}>
                        <p style={{ fontSize:"15px", fontWeight:700, color:C.rust, margin:"0 0 1px" }}>{cv.ats_score.toFixed(0)}/100</p>
                        <p style={{ fontSize:"10px", color:C.muted, margin:0 }}>Grade {cv.ats_feedback?.grade}</p>
                      </div>
                    )}
                    <svg width="14" height="14" fill="none" stroke={C.muted} strokeWidth="2" viewBox="0 0 24 24"
                      style={{ transform:expanded === cv.id ? "rotate(180deg)" : "none", transition:"transform 0.2s" }}>
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </div>
                </div>

                {expanded === cv.id && (
                  <div style={{ borderTop:`1px solid ${C.border}`, padding:"14px 16px" }}>
                    {cv.parsed_data?.skills && cv.parsed_data.skills.length > 0 && (
                      <div style={{ marginBottom:"14px" }}>
                        <p style={{ fontSize:"11px", fontWeight:600, color:C.muted, textTransform:"uppercase", letterSpacing:"0.05em", margin:"0 0 8px" }}>Competences detectees</p>
                        <div style={{ display:"flex", flexWrap:"wrap", gap:"6px" }}>
                          {cv.parsed_data.skills.slice(0,16).map(skill => (
                            <span key={skill} style={{ fontSize:"11px", padding:"3px 10px", borderRadius:"20px", background:C.warm, color:C.rust, border:`1px solid ${C.border}`, fontWeight:500 }}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {cv.ats_feedback && (
                      <div>
                        <p style={{ fontSize:"11px", fontWeight:600, color:C.muted, textTransform:"uppercase", letterSpacing:"0.05em", margin:"0 0 8px" }}>Retour ATS</p>
                        {cv.ats_feedback.issues.map((issue, i) => (
                          <p key={i} style={{ fontSize:"12px", color:"#E8A020", margin:"4px 0", display:"flex", gap:"6px" }}>
                            <span style={{ flexShrink:0 }}>•</span>{issue}
                          </p>
                        ))}
                        {cv.ats_feedback.suggestions.slice(0,3).map((s, i) => (
                          <p key={i} style={{ fontSize:"12px", color:C.rust, margin:"4px 0", display:"flex", gap:"6px" }}>
                            <span style={{ flexShrink:0 }}>→</span>{s}
                          </p>
                        ))}
                      </div>
                    )}
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