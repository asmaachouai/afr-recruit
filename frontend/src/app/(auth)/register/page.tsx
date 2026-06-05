"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import api from "@/lib/api"

const input: React.CSSProperties = {
  width: "100%", height: "40px", padding: "0 12px",
  borderRadius: "8px", border: "1px solid #E8C4A8",
  background: "#FDF8F2", color: "#2C1A0E",
  fontSize: "13px", outline: "none", boxSizing: "border-box",
}

function Toggle({ options, value, onChange }: {
  options: { value: string; label: string }[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div style={{ display: "flex", gap: "8px" }}>
      {options.map(opt => (
        <button key={opt.value} type="button" onClick={() => onChange(opt.value)} style={{
          flex: 1, height: "38px", borderRadius: "8px",
          fontSize: "12px", fontWeight: 600, cursor: "pointer",
          background: value === opt.value ? "#C1440E" : "transparent",
          color:      value === opt.value ? "#FDF4E7" : "#9A6B55",
          border:     value === opt.value ? "1px solid #C1440E" : "1px solid #E8C4A8",
          transition: "all 0.15s",
        }}>
          {opt.label}
        </button>
      ))}
    </div>
  )
}

export default function RegisterPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    full_name: "", email: "", password: "",
    role: "candidate", preferred_language: "fr",
  })
  const [error,   setError]   = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError("")
    try {
      await api.post("/auth/register", form)
      router.push("/login")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Echec de l'inscription")
    } finally { setLoading(false) }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#FDF8F2", padding: "24px 16px" }}>
      <div style={{ width: "100%", maxWidth: "380px" }}>

        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <div style={{
            width: "48px", height: "48px", borderRadius: "14px",
            background: "#C1440E", margin: "0 auto 14px",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ color: "#FDF4E7", fontWeight: 800, fontSize: "20px" }}>A</span>
          </div>
          <h1 style={{ fontSize: "20px", fontWeight: 700, color: "#2C1A0E", margin: "0 0 4px" }}>
            AFR-Recruit
          </h1>
          <p style={{ fontSize: "13px", color: "#9A6B55", margin: 0 }}>Creer un compte</p>
        </div>

        <div style={{ background: "#fff", border: "1px solid #E8C4A8", borderRadius: "14px", padding: "28px 24px" }}>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>

            {[
              { label: "Nom complet",    key: "full_name", type: "text",     placeholder: "Votre nom complet"       },
              { label: "Adresse email",  key: "email",     type: "email",    placeholder: "vous@exemple.com"        },
              { label: "Mot de passe",   key: "password",  type: "password", placeholder: "Min 8 caracteres + chiffre" },
            ].map(f => (
              <div key={f.key}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#5C3320", display: "block", marginBottom: "6px" }}>
                  {f.label}
                </label>
                <input
                  style={input} type={f.type} placeholder={f.placeholder}
                  value={(form as any)[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  required
                />
              </div>
            ))}

            <div>
              <label style={{ fontSize: "11px", fontWeight: 600, color: "#5C3320", display: "block", marginBottom: "6px" }}>
                Type de compte
              </label>
              <Toggle
                options={[{ value: "candidate", label: "Candidat" }, { value: "recruiter", label: "Recruteur" }]}
                value={form.role}
                onChange={v => setForm({ ...form, role: v })}
              />
            </div>

            <div>
              <label style={{ fontSize: "11px", fontWeight: 600, color: "#5C3320", display: "block", marginBottom: "6px" }}>
                Langue preferee
              </label>
              <Toggle
                options={[
                  { value: "fr", label: "Francais" },
                  { value: "ar", label: "Arabe"    },
                  { value: "en", label: "English"  },
                ]}
                value={form.preferred_language}
                onChange={v => setForm({ ...form, preferred_language: v })}
              />
            </div>

            {error && (
              <div style={{ background: "#FEF3E8", border: "1px solid #E8C4A8", borderRadius: "8px", padding: "10px 12px" }}>
                <p style={{ fontSize: "12px", color: "#C1440E", margin: 0 }}>{error}</p>
              </div>
            )}

            <button type="submit" disabled={loading} style={{
              height: "42px", background: loading ? "#D4622A" : "#C1440E",
              color: "#FDF4E7", border: "none", borderRadius: "8px",
              fontSize: "13px", fontWeight: 700,
              cursor: loading ? "not-allowed" : "pointer",
            }}>
              {loading ? "Creation..." : "Creer mon compte"}
            </button>
          </form>

          <p style={{ textAlign: "center", fontSize: "12px", color: "#9A6B55", marginTop: "16px" }}>
            Deja un compte ?{" "}
            <Link href="/login" style={{ color: "#C1440E", textDecoration: "none", fontWeight: 600 }}>
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}