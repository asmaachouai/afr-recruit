"use client"

import { Sidebar } from "@/components/layout/Sidebar"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 ml-60 flex flex-col min-h-screen overflow-auto">
        {children}
      </main>
    </div>
  )
}