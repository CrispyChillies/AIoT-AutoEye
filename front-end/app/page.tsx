"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "@/components/ui/calendar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Camera, Car, Bike, TrendingUp, CalendarIcon, RefreshCw, ArrowRight, ArrowLeft } from "lucide-react"
import { format } from "date-fns"

// Mock data for demonstration
const mockTrafficData = {
  current: {
    totalVehicles: 47,
    cars: 32,
    motorbikes: 15,
    inbound: 28,
    outbound: 19,
    status: "moderate",
    lastUpdate: new Date(),
  },
  historical: [
    { time: "08:00", cars: 45, motorbikes: 23, total: 68, status: "heavy" },
    { time: "09:00", cars: 38, motorbikes: 18, total: 56, status: "moderate" },
    { time: "10:00", cars: 25, motorbikes: 12, total: 37, status: "light" },
    { time: "11:00", cars: 32, motorbikes: 15, total: 47, status: "moderate" },
  ],
}

export default function TrafficDashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [selectedHour, setSelectedHour] = useState<string>("11")
  const [isLive, setIsLive] = useState(true)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "light":
        return "bg-green-500"
      case "moderate":
        return "bg-yellow-500"
      case "heavy":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      light: "bg-green-100 text-green-800",
      moderate: "bg-yellow-100 text-yellow-800",
      heavy: "bg-red-100 text-red-800",
    }
    return colors[status as keyof typeof colors] || "bg-gray-100 text-gray-800"
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Edge AI Traffic Monitor</h1>
            <p className="text-gray-600">Real-time traffic monitoring and analytics</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isLive ? "bg-green-500" : "bg-gray-400"}`} />
              {isLive ? "Live" : "Offline"}
            </Badge>
            <Button onClick={() => setIsLive(!isLive)} variant="outline" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Live Camera Feed */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              Live Camera Feed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
              <img
                src="/placeholder.svg?height=400&width=800"
                alt="Live traffic camera feed"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-1 rounded-full text-sm">
                Camera 01 - Main Street
              </div>
              <div className="absolute top-4 right-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                LIVE
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Current Traffic Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Vehicles</p>
                  <p className="text-3xl font-bold">{mockTrafficData.current.totalVehicles}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
              <Badge className={getStatusBadge(mockTrafficData.current.status)}>
                {mockTrafficData.current.status.toUpperCase()}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Cars</p>
                  <p className="text-3xl font-bold">{mockTrafficData.current.cars}</p>
                </div>
                <Car className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Motorbikes</p>
                  <p className="text-3xl font-bold">{mockTrafficData.current.motorbikes}</p>
                </div>
                <Bike className="w-8 h-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600 mb-2">Traffic Flow</p>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <ArrowRight className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="text-lg font-bold">{mockTrafficData.current.inbound}</p>
                      <p className="text-xs text-gray-500">Inbound</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <ArrowLeft className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="text-lg font-bold">{mockTrafficData.current.outbound}</p>
                      <p className="text-xs text-gray-500">Outbound</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Historical Data and Analytics */}
        <Tabs defaultValue="history" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="history">Traffic History</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Historical Traffic Data</CardTitle>
                <div className="flex items-center gap-4">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-[240px] justify-start text-left font-normal">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {selectedDate ? format(selectedDate, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={selectedDate}
                        onSelect={(date) => date && setSelectedDate(date)}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>

                  <Select value={selectedHour} onValueChange={setSelectedHour}>
                    <SelectTrigger className="w-[120px]">
                      <SelectValue placeholder="Hour" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.from({ length: 24 }, (_, i) => (
                        <SelectItem key={i} value={i.toString().padStart(2, "0")}>
                          {i.toString().padStart(2, "0")}:00
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockTrafficData.historical.map((data, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="text-lg font-semibold">{data.time}</div>
                        <Badge className={getStatusBadge(data.status)}>{data.status.toUpperCase()}</Badge>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                          <Car className="w-4 h-4 text-green-600" />
                          <span>{data.cars}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Bike className="w-4 h-4 text-orange-600" />
                          <span>{data.motorbikes}</span>
                        </div>
                        <div className="font-semibold">Total: {data.total}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Traffic Volume Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <p className="text-gray-500">Traffic volume chart would be displayed here</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Vehicle Type Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Car className="w-5 h-5 text-green-600" />
                        <span>Cars</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-green-600 h-2 rounded-full" style={{ width: "68%" }} />
                        </div>
                        <span className="text-sm font-medium">68%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Bike className="w-5 h-5 text-orange-600" />
                        <span>Motorbikes</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-orange-600 h-2 rounded-full" style={{ width: "32%" }} />
                        </div>
                        <span className="text-sm font-medium">32%</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Directional Traffic Flow */}
        <Card>
          <CardHeader>
            <CardTitle>Directional Traffic Flow</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center p-6 border rounded-lg">
                <ArrowRight className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Inbound Traffic</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Cars:</span>
                    <span className="font-semibold">18</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Motorbikes:</span>
                    <span className="font-semibold">10</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span>Total:</span>
                    <span className="font-bold text-blue-600">28</span>
                  </div>
                </div>
              </div>

              <div className="text-center p-6 border rounded-lg">
                <ArrowLeft className="w-12 h-12 text-purple-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Outbound Traffic</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Cars:</span>
                    <span className="font-semibold">14</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Motorbikes:</span>
                    <span className="font-semibold">5</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span>Total:</span>
                    <span className="font-bold text-purple-600">19</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
