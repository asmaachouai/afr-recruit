"use client"

import { useState } from "react"
import { Sidebar } from "@/components/layout/Sidebar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(true)

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#FDF8F2" }}>
      <Sidebar onToggle={setOpen} />
      <main style={{
        flex: 1,
        marginLeft:  open ? "240px" : "68px",
        transition:  "margin-left 0.3s cubic-bezier(0.4,0,0.2,1)",
        display:     "flex",
        flexDirection: "column",
        minHeight:   "100vh",
        minWidth:    0,
        overflowX:   "hidden",
      }}>
        {children}
      </main>
    </div>
  )
}