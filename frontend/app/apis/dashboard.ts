import api from "./axios"

export const getDashboardMetrixs = async () => {
  const res = await api.get("/api/v1/dashboard/")
  return res.data
}