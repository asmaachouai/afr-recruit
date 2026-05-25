"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import api from "@/lib/api"

const inputStyle = {
  width: "100%", height: "38px",
  padding: "0 12px", borderRadius: "8px",
  border: "1px solid #E8C4A8",
  background: "#FDF8F2", color: "#2C1A0E",
  fontSize: "13px", outline: "none",
  boxSizing: "border-box" as const,
}

const labelStyle = {
  fontSize: "11px", fontWeight: 600 as const,
  color: "#5C3320", display: "block" as const,
  marginBottom: "6px",
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
    setLoading(true)
    setError("")
    try {
      await api.post("/auth/register", form)
      router.push("/login")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Echec de l'inscription")
    } finally {
      setLoading(false)
    }
  }

  const ToggleGroup = ({
    options, value, onChange,
  }: {
    options: { value: string; label: string }[]
    value: string
    onChange: (v: string) => void
  }) => (
    <div style={{ display: "flex", gap: "8px" }}>
      {options.map(opt => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          style={{
            flex: 1, height: "36px",
            borderRadius: "8px", fontSize: "12px", fontWeight: 500,
            cursor: "pointer", transition: "all 0.15s",
            background: value === opt.value ? "#C1440E" : "transparent",
            color:      value === opt.value ? "#FDF4E7" : "#9A6B55",
            border:     value === opt.value ? "1px solid #C1440E" : "1px solid #E8C4A8",
          }}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )

  return (
    <div style={{
      minHeight: "100vh", display: "flex",
      alignItems: "center", justifyContent: "center",
      background: "#FDF8F2", padding: "24px 16px",
    }}>
      <div style={{ width: "100%", maxWidth: "380px" }}>

        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <div style={{
            width: "44px", height: "44px", borderRadius: "12px",
            background: "#C1440E", margin: "0 auto 12px",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ color: "#FDF4E7", fontWeight: 700, fontSize: "18px" }}>A</span>
          </div>
          <h1 style={{ fontSize: "18px", fontWeight: 700, color: "#2C1A0E", margin: "0 0 4px" }}>
            AFR-Recruit
          </h1>
          <p style={{ fontSize: "13px", color: "#9A6B55", margin: 0 }}>
            Creer un compte
          </p>
        </div>

        <div style={{
          background: "#FFFFFF", border: "1px solid #E8C4A8",
          borderRadius: "14px", padding: "28px 24px",
        }}>
          <form onSubmit={handleSubmit}>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>

              <div>
                <label style={labelStyle}>Nom complet</label>
                <input
                  style={inputStyle}
                  placeholder="Votre nom complet"
                  value={form.full_name}
                  onChange={e => setForm({ ...form, full_name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={labelStyle}>Adresse email</label>
                <input
                  style={inputStyle}
                  type="email"
                  placeholder="vous@exemple.com"
                  value={form.email}
                  onChange={e => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={labelStyle}>Mot de passe</label>
                <input
                  style={inputStyle}
                  type="password"
                  placeholder="Min 8 caracteres, inclure un chiffre"
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={labelStyle}>Type de compte</label>
                <ToggleGroup
                  options={[
                    { value: "candidate", label: "Candidat" },
                    { value: "recruiter", label: "Recruteur" },
                  ]}
                  value={form.role}
                  onChange={v => setForm({ ...form, role: v })}
                />
              </div>

              <div>
                <label style={labelStyle}>Langue preferee</label>
                <ToggleGroup
                  options={[
                    { value: "fr", label: "Francais" },
                    { value: "ar", label: "Arabe" },
                    { value: "en", label: "English" },
                  ]}
                  value={form.preferred_language}
                  onChange={v => setForm({ ...form, preferred_language: v })}
                />
              </div>

              {error && (
                <div style={{
                  background: "#FEF3E8", border: "1px solid #E8C4A8",
                  borderRadius: "8px", padding: "10px 12px",
                }}>
                  <p style={{ fontSize: "12px", color: "#C1440E", margin: 0 }}>{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%", height: "40px",
                  background: loading ? "#D4622A" : "#C1440E",
                  color: "#FDF4E7", border: "none",
                  borderRadius: "8px", fontSize: "13px",
                  fontWeight: 600, cursor: loading ? "not-allowed" : "pointer",
                }}
              >
                {loading ? "Creation..." : "Creer mon compte"}
              </button>
            </div>
          </form>

          <p style={{ textAlign: "center", fontSize: "12px", color: "#9A6B55", marginTop: "16px" }}>
            Deja un compte ?{" "}
            <Link href="/login" style={{ color: "#C1440E", textDecoration: "none", fontWeight: 500 }}>
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}