"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import {
  LayoutDashboard, FileText, Briefcase,
  ShieldCheck, LogOut,
} from "lucide-react"

const candidateNav = [
  { href: "/candidate",              label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/candidate/cv",           label: "Mon CV",          icon: FileText        },
  { href: "/candidate/applications", label: "Candidatures",    icon: Briefcase       },
]

const recruiterNav = [
  { href: "/recruiter",           label: "Tableau de bord",   icon: LayoutDashboard },
  { href: "/recruiter/jobs",      label: "Offres d'emploi",   icon: Briefcase       },
  { href: "/recruiter/fairness",  label: "Rapports equite",   icon: ShieldCheck     },
]

export function Sidebar() {
  const pathname  = usePathname()
  const { user, logout } = useAuthStore()
  const navItems  = user?.role === "recruiter" ? recruiterNav : candidateNav
  const initials  = user?.full_name
    ?.split(" ").map(n => n[0]).slice(0, 2).join("") ?? "U"

  return (
    <aside
      className="w-60 h-screen flex flex-col fixed left-0 top-0 z-40"
      style={{ background: "#2C1A0E" }}
    >
      {/* Zellige accent bar */}
      <div style={{
        height: "3px",
        background: "linear-gradient(90deg,#C1440E 0%,#E8A020 33%,#D4622A 66%,#C17B6A 100%)",
      }} />

      {/* Logo */}
      <div style={{
        padding: "16px 20px",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}>
        <p style={{ fontSize: "15px", fontWeight: 600, color: "#FDF4E7", margin: 0 }}>
          AFR-Recruit
        </p>
        <p style={{ fontSize: "11px", color: "#9A6B55", margin: "2px 0 0" }}>
          Maroc & Afrique Francophone
        </p>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: "12px" }}>
        {navItems.map(item => {
          const Icon   = item.icon
          const active = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display:        "flex",
                alignItems:     "center",
                gap:            "10px",
                padding:        "8px 12px",
                borderRadius:   "8px",
                fontSize:       "13px",
                marginBottom:   "2px",
                textDecoration: "none",
                background:     active ? "#C1440E" : "transparent",
                color:          active ? "#FDF4E7" : "rgba(253,244,231,0.5)",
                transition:     "background 0.15s, color 0.15s",
              }}
            >
              <Icon size={15} style={{ flexShrink: 0 }} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* User footer */}
      <div style={{
        padding:     "12px",
        borderTop:   "1px solid rgba(255,255,255,0.08)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "8px 12px", marginBottom: "4px" }}>
          <div style={{
            width: "28px", height: "28px", borderRadius: "50%",
            background: "#C1440E", color: "#FDF4E7",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "11px", fontWeight: 600, flexShrink: 0,
          }}>
            {initials}
          </div>
          <div style={{ minWidth: 0 }}>
            <p style={{ fontSize: "12px", fontWeight: 500, color: "#FDF4E7", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user?.full_name}
            </p>
            <p style={{ fontSize: "11px", color: "#9A6B55", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user?.email}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          style={{
            display: "flex", alignItems: "center", gap: "10px",
            width: "100%", padding: "8px 12px", borderRadius: "8px",
            background: "transparent", border: "none", cursor: "pointer",
            fontSize: "13px", color: "rgba(253,244,231,0.4)",
          }}
        >
          <LogOut size={14} />
          Deconnexion
        </button>
      </div>
    </aside>
  )
}