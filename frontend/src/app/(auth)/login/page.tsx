"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import api, { setAccessToken } from "@/lib/api"
import { useAuthStore } from "@/store/auth"

export default function LoginPage() {
  const router = useRouter()
  const { setUser } = useAuthStore()
  const [email,    setEmail]    = useState("")
  const [password, setPassword] = useState("")
  const [error,    setError]    = useState("")
  const [loading,  setLoading]  = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError("")
    try {
      const { data: tokens } = await api.post("/auth/login", { email, password })
      setAccessToken(tokens.access_token)
      localStorage.setItem("refresh_token", tokens.refresh_token)
      const { data: me } = await api.get("/auth/me")
      setUser(me)
      router.push(me.role === "candidate" ? "/candidate" : "/recruiter")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Email ou mot de passe incorrect")
    } finally { setLoading(false) }
  }

  const input: React.CSSProperties = {
    width: "100%", height: "40px", padding: "0 12px",
    borderRadius: "8px", border: "1px solid #E8C4A8",
    background: "#FDF8F2", color: "#2C1A0E",
    fontSize: "13px", outline: "none", boxSizing: "border-box",
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#FDF8F2" }}>
      <div style={{ width: "100%", maxWidth: "360px", padding: "0 16px" }}>

        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
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
          <p style={{ fontSize: "13px", color: "#9A6B55", margin: 0 }}>
            Recrutement IA pour l&apos;Afrique
          </p>
        </div>

        {/* Card */}
        <div style={{ background: "#fff", border: "1px solid #E8C4A8", borderRadius: "14px", padding: "28px 24px" }}>
          <h2 style={{ fontSize: "15px", fontWeight: 700, color: "#2C1A0E", margin: "0 0 4px" }}>
            Connexion
          </h2>
          <p style={{ fontSize: "12px", color: "#9A6B55", margin: "0 0 22px" }}>
            Entrez vos identifiants pour acceder a votre espace
          </p>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <div>
              <label style={{ fontSize: "11px", fontWeight: 600, color: "#5C3320", display: "block", marginBottom: "6px" }}>
                Adresse email
              </label>
              <input style={input} type="email" placeholder="vous@exemple.com"
                value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
            <div>
              <label style={{ fontSize: "11px", fontWeight: 600, color: "#5C3320", display: "block", marginBottom: "6px" }}>
                Mot de passe
              </label>
              <input style={input} type="password" placeholder="••••••••"
                value={password} onChange={e => setPassword(e.target.value)} required />
            </div>

            {error && (
              <div style={{ background: "#FEF3E8", border: "1px solid #E8C4A8", borderRadius: "8px", padding: "10px 12px" }}>
                <p style={{ fontSize: "12px", color: "#C1440E", margin: 0 }}>{error}</p>
              </div>
            )}

            <button type="submit" disabled={loading} style={{
              height: "42px", background: loading ? "#D4622A" : "#C1440E",
              color: "#FDF4E7", border: "none", borderRadius: "8px",
              fontSize: "13px", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
              transition: "background 0.2s",
            }}>
              {loading ? "Connexion..." : "Se connecter"}
            </button>
          </form>

          <p style={{ textAlign: "center", fontSize: "12px", color: "#9A6B55", marginTop: "18px" }}>
            Pas de compte ?{" "}
            <Link href="/register" style={{ color: "#C1440E", textDecoration: "none", fontWeight: 600 }}>
              Creer un compte
            </Link>
          </p>
        </div>

        {/* Demo credentials */}
        <div style={{ background: "#FAE8D0", border: "1px solid #E8C4A8", borderRadius: "10px", padding: "14px 16px", marginTop: "16px" }}>
          <p style={{ fontSize: "11px", fontWeight: 700, color: "#5C3320", margin: "0 0 8px" }}>
            Comptes de demonstration
          </p>
          {[
            { role: "Candidat",  email: "candidate@gmail.com",  pass: "candidate123" },
            { role: "Recruteur", email: "recruiter@nexora.ma",  pass: "recruiter123" },
          ].map(c => (
            <div key={c.role} style={{ marginBottom: "5px" }}>
              <span style={{ fontSize: "11px", fontWeight: 700, color: "#C1440E" }}>{c.role}: </span>
              <span style={{ fontSize: "11px", color: "#5C3320", fontFamily: "monospace" }}>
                {c.email} / {c.pass}
              </span>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}