import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

let accessToken: string | null = null

export const setAccessToken = (token: string | null) => { accessToken = token }
export const getAccessToken = () => accessToken

const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem("refresh_token")
        if (!refresh) throw new Error("no refresh")
        const { data } = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {
          refresh_token: refresh,
        })
        setAccessToken(data.access_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        setAccessToken(null)
        localStorage.removeItem("refresh_token")
        if (typeof window !== "undefined") window.location.href = "/login"
      }
    }
    return Promise.reject(error)
  }
)

export default api