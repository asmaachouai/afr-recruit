"use client"

import { useAuthStore } from "@/store/auth"

interface HeaderProps {
  title: string
  description?: string
}

export function Header({ title, description }: HeaderProps) {
  const { user } = useAuthStore()
  return (
    <header style={{
      height: "52px", flexShrink: 0,
      display: "flex", alignItems: "center",
      justifyContent: "space-between",
      padding: "0 24px",
      background: "#FFFFFF",
      borderBottom: "1px solid #E8C4A8",
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
        fontSize: "11px", fontWeight: 500,
        padding: "3px 10px", borderRadius: "20px",
        background: "#FAE8D0", color: "#C1440E",
        border: "1px solid #E8C4A8",
        textTransform: "capitalize",
      }}>
        {user?.role}
      </span>
    </header>
  )
}