"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import {
  LayoutDashboard, FileText, Briefcase,
  ShieldCheck, LogOut, ChevronLeft, ChevronRight,
} from "lucide-react"

const candidateNav = [
  { href: "/candidate",              label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/candidate/cv",           label: "Mon CV",          icon: FileText        },
  { href: "/candidate/applications", label: "Candidatures",    icon: Briefcase       },
]

const recruiterNav = [
  { href: "/recruiter",          label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/recruiter/jobs",     label: "Offres d'emploi", icon: Briefcase       },
  { href: "/recruiter/fairness", label: "Rapports equite", icon: ShieldCheck     },
]

interface SidebarProps {
  onToggle?: (open: boolean) => void
}

export function Sidebar({ onToggle }: SidebarProps) {
  const pathname  = usePathname()
  const { user, logout } = useAuthStore()
  const [open, setOpen] = useState(true)

  const navItems = user?.role === "recruiter" ? recruiterNav : candidateNav
  const initials = user?.full_name?.split(" ").map(n => n[0]).slice(0, 2).join("") ?? "U"

  const toggle = () => {
    const next = !open
    setOpen(next)
    onToggle?.(next)
  }

  return (
    <aside style={{
      position:      "fixed",
      left:          0, top: 0,
      height:        "100vh",
      width:         open ? "240px" : "68px",
      minWidth:      open ? "240px" : "68px",
      background:    "#2C1A0E",
      display:       "flex",
      flexDirection: "column",
      zIndex:        50,
      transition:    "width 0.3s cubic-bezier(0.4,0,0.2,1), min-width 0.3s cubic-bezier(0.4,0,0.2,1)",
      overflowX:     "hidden",
    }}>

      {/* Zellige bar */}
      <div style={{
        height:     "3px",
        flexShrink: 0,
        background: "linear-gradient(90deg,#C1440E 0%,#E8A020 33%,#D4622A 66%,#C17B6A 100%)",
      }} />

      {/* Header */}
      <div style={{
        height:         "58px",
        flexShrink:     0,
        display:        "flex",
        alignItems:     "center",
        justifyContent: open ? "space-between" : "center",
        padding:        "0 14px",
        borderBottom:   "1px solid rgba(255,255,255,0.08)",
      }}>
        {open && (
          <div style={{ overflow: "hidden", animation: "fadeIn 0.2s ease" }}>
            <p style={{ fontSize: "14px", fontWeight: 700, color: "#FDF4E7", margin: 0, whiteSpace: "nowrap" }}>
              AFR-Recruit
            </p>
            <p style={{ fontSize: "10px", color: "#9A6B55", margin: "1px 0 0", whiteSpace: "nowrap" }}>
              Maroc & Afrique Francophone
            </p>
          </div>
        )}
        <button
          onClick={toggle}
          style={{
            width: "28px", height: "28px", borderRadius: "6px",
            background: "rgba(255,255,255,0.06)", border: "none",
            cursor: "pointer", display: "flex", alignItems: "center",
            justifyContent: "center", color: "#FDF4E7", flexShrink: 0,
          }}
        >
          {open ? <ChevronLeft size={15} /> : <ChevronRight size={15} />}
        </button>
      </div>

      {/* Nav */}
      <nav style={{
        flex: 1, padding: "10px",
        display: "flex", flexDirection: "column", gap: "2px",
        overflowY: "auto", overflowX: "hidden",
      }}>
        {navItems.map(item => {
          const Icon   = item.icon
          const active = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              title={!open ? item.label : undefined}
              style={{
                display:        "flex",
                alignItems:     "center",
                gap:            "10px",
                padding:        "9px 10px",
                justifyContent: open ? "flex-start" : "center",
                borderRadius:   "8px",
                fontSize:       "13px",
                fontWeight:     active ? 600 : 400,
                textDecoration: "none",
                background:     active ? "#C1440E" : "transparent",
                color:          active ? "#FDF4E7" : "rgba(253,244,231,0.55)",
                transition:     "background 0.15s, color 0.15s",
                whiteSpace:     "nowrap",
                overflow:       "hidden",
              }}
            >
              <Icon size={16} style={{ flexShrink: 0 }} />
              {open && (
                <span style={{ animation: "fadeIn 0.15s ease", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {item.label}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding: "10px", borderTop: "1px solid rgba(255,255,255,0.08)", flexShrink: 0 }}>
        <div style={{
          display: "flex", alignItems: "center", gap: "9px",
          padding: "8px 10px", marginBottom: "3px",
          justifyContent: open ? "flex-start" : "center",
          overflow: "hidden",
        }}>
          <div style={{
            width: "28px", height: "28px", borderRadius: "50%",
            background: "#C1440E", color: "#FDF4E7",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "11px", fontWeight: 700, flexShrink: 0,
          }}>
            {initials}
          </div>
          {open && (
            <div style={{ minWidth: 0, overflow: "hidden", animation: "fadeIn 0.2s ease" }}>
              <p style={{ fontSize: "12px", fontWeight: 500, color: "#FDF4E7", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {user?.full_name}
              </p>
              <p style={{ fontSize: "11px", color: "#9A6B55", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {user?.email}
              </p>
            </div>
          )}
        </div>
        <button
          onClick={logout}
          title={!open ? "Deconnexion" : undefined}
          style={{
            display: "flex", alignItems: "center", gap: "10px",
            width: "100%", padding: "8px 10px", borderRadius: "8px",
            background: "transparent", border: "none", cursor: "pointer",
            fontSize: "13px", color: "rgba(253,244,231,0.4)",
            justifyContent: open ? "flex-start" : "center",
          }}
        >
          <LogOut size={14} style={{ flexShrink: 0 }} />
          {open && <span style={{ whiteSpace: "nowrap", animation: "fadeIn 0.2s ease" }}>Deconnexion</span>}
        </button>
      </div>
    </aside>
  )
}