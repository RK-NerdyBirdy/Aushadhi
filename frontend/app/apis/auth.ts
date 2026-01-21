import api from "./axios"

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export const login = async (email: string, password: string) => {
  const res = await api.post(
    "/api/v1/auth/login",
    null,
    {
      params: {
        email: email,
        password: password,
      },
    }
  )

  return res.data
}

export const getMe = async () => {
  const res = await api.get("/api/v1/auth/me")
  return res.data
}