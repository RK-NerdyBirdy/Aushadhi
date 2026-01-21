import api from "./axios"

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