"use client"

import { useAuthStore } from "@/store/auth"

interface HeaderProps {
  title:        string
  description?: string
}

export function Header({ title, description }: HeaderProps) {
  const { user } = useAuthStore()
  return (
    <header style={{
      height:       "52px",
      display:      "flex",
      alignItems:   "center",
      justifyContent: "space-between",
      padding:      "0 24px",
      background:   "#FDF8F2",
      borderBottom: "1px solid #E8C4A8",
      flexShrink:   0,
    }}>
      <div>
        <h1 style={{ fontSize: "13px", fontWeight: 600, color: "#2C1A0E", margin: 0 }}>
          {title}
        </h1>
        {description && (
          <p style={{ fontSize: "11px", color: "#9A6B55", margin: "1px 0 0" }}>
            {description}
          </p>
        )}
      </div>
      <span style={{
        fontSize:     "11px",
        padding:      "3px 10px",
        borderRadius: "20px",
        background:   "#FAE8D0",
        color:        "#C1440E",
        border:       "1px solid #E8C4A8",
        fontWeight:   500,
        textTransform: "capitalize",
      }}>
        {user?.role}
      </span>
    </header>
  )
}