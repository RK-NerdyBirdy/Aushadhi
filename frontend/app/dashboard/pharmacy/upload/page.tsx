"use client"

import { useState } from "react"
import { UploadCloud, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

export default function UploadPage() {
  const [salesFile, setSalesFile] = useState<File | null>(null)
  const [stockFile, setStockFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!salesFile || !stockFile) {
      toast.error("Please upload both CSV files")
      return
    }

    const formData = new FormData()
    formData.append("sales_csv", salesFile)
    formData.append("stock_csv", stockFile)

    try {
      setLoading(true)

      const res = await fetch("http://localhost:8000/pharmacy/upload", {
        method: "POST",
        body: formData,
      })

      if (!res.ok) throw new Error("Upload failed")

      toast.success("Files uploaded successfully")
    } catch (err) {
      toast.error("Upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl">

      <h1 className="text-3xl font-bold">
        Upload Pharmacy Data
      </h1>

      <p className="text-muted-foreground">
        Upload your historical sales data and current stock information
        in CSV format.
      </p>

      <div className="grid md:grid-cols-2 gap-6">

        {/* SALES HISTORY */}
        <Card>
          <CardHeader>
            <CardTitle>Sales History CSV</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">

            <div className="border-2 border-dashed rounded-lg p-6 text-center">
              <UploadCloud className="mx-auto h-8 w-8 text-muted-foreground" />

              <p className="mt-2 text-sm">
                Upload sales history file
              </p>

              <p className="text-xs text-muted-foreground mt-1">
                Columns: med_id, med_name, date_of_sale, quantity
              </p>

              <Input
                type="file"
                accept=".csv"
                className="mt-4 cursor-pointer"
                onChange={(e) =>
                  setSalesFile(e.target.files?.[0] || null)
                }
              />
            </div>

            {salesFile && (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle size={16} />
                {salesFile.name}
              </div>
            )}
          </CardContent>
        </Card>

        {/* CURRENT STOCK */}
        <Card>
          <CardHeader>
            <CardTitle>Current Stock CSV</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">

            <div className="border-2 border-dashed rounded-lg p-6 text-center">
              <UploadCloud className="mx-auto h-8 w-8 text-muted-foreground" />

              <p className="mt-2 text-sm">
                Upload current stock file
              </p>

              <p className="text-xs text-muted-foreground mt-1">
                Columns: med_id, med_name, current_stock
              </p>

              <Input
                type="file"
                accept=".csv"
                className="mt-4 cursor-pointer"
                onChange={(e) =>
                  setStockFile(e.target.files?.[0] || null)
                }
              />
            </div>

            {stockFile && (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle size={16} />
                {stockFile.name}
              </div>
            )}
          </CardContent>
        </Card>

      </div>

      {/* SUBMIT */}
        <div className="pt-4">
            <Button
            size="lg"
            onClick={handleUpload}
            disabled={loading}
            className="text-white hover:text-gray-400 transition-colors duration-200"
            >
            {loading ? "Uploading..." : "Upload Files"}
            </Button>
        </div>

    </div>
  )
}