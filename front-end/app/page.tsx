"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "@/components/ui/calendar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Camera, Car, Bike, TrendingUp, CalendarIcon, RefreshCw, ArrowRight, ArrowLeft, ArrowUp, ArrowDown } from "lucide-react"

import { format } from "date-fns"
import CameraComponent from "./CameraComponent"



// Import your API hooks instead of using mock data
import { useTrafficData, useHealth } from "@/lib/hooks/useSimpleTraffic"

export default function TrafficDashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [selectedHour, setSelectedHour] = useState<string>("11")

  // Use real data from your API
  const { data: trafficData, loading, error, refresh } = useTrafficData()
  const { health, isOnline, refresh: refreshHealth } = useHealth()

  // Calculate real stats from API data
  const latestTraffic = trafficData.length > 0 ? trafficData[0] : null;

  const currentStats = latestTraffic ? {
    totalVehicles: latestTraffic.vehicle_count,
    cars: latestTraffic.car_count || Math.floor(latestTraffic.vehicle_count * 0.68),
    motorbikes: latestTraffic.motorbike_count || Math.floor(latestTraffic.vehicle_count * 0.32),
    inbound: (latestTraffic.lane1_in || 0),
    outbound: (latestTraffic.lane1_out || 0),
    status: latestTraffic.status,
    location: latestTraffic.location,
    lastUpdate: new Date(latestTraffic.timestamp),
  } : {
    totalVehicles: 0,
    cars: 0,
    motorbikes: 0,
    inbound: 0,
    outbound: 0,
    status: "unknown",
    location: "No data",
    lastUpdate: new Date(),
  }

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

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Loading traffic data...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={refresh}>Try Again</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Edge AI Traffic Monitor</h1>
            <p className="text-gray-600">Real-time traffic monitoring and analytics</p>
            {/* Show backend status */}
            {health && (
              <p className="text-sm text-gray-500">Database: {health.database}</p>
            )}
            {/* ADD THIS - Show current location and timestamp */}
            {latestTraffic && (
              <div className="text-sm space-y-1">
                <p className="text-blue-600">📍 Current Location: {latestTraffic.location}</p>
                <p className="text-green-600">🕒 Last Update: {new Date(latestTraffic.timestamp).toLocaleString()}</p>
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isOnline ? "bg-green-500" : "bg-gray-400"}`} />
              {isOnline ? "Live" : "Offline"}
            </Badge>
            <Button 
              onClick={() => {
                refresh()
                refreshHealth()
              }} 
              variant="outline" 
              size="sm"
            >
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
              Latest Camera Snapshot - {latestTraffic?.location || "No Location"}
            </CardTitle>
            <div className="text-sm text-gray-500">
              {latestTraffic ? (
                <>
                  Last captured: {new Date(latestTraffic.timestamp).toLocaleString()} • 
                  Status: <span className="font-medium">{latestTraffic.status}</span>
                </>
              ) : (
                "No recent captures available"
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
              {/* PASS THE TRAFFIC DATA TO CAMERA COMPONENT */}
              <CameraComponent 
                latestTraffic={latestTraffic}
                onRefresh={() => {
                  refresh();
                  refreshHealth();
                }}
              />
              
              {/* Info overlays */}
              <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-1 rounded-full text-sm">
                📷 {latestTraffic?.location || "Camera 01"}
              </div>
              
              {latestTraffic && (
                <div className="absolute top-4 right-4 bg-blue-600 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2">
                  <div className="w-2 h-2 bg-white rounded-full" />
                  {new Date(latestTraffic.timestamp).toLocaleTimeString()}
                </div>
              )}
              
              {latestTraffic && (
                <div className="absolute bottom-4 left-4 bg-black/70 text-white px-3 py-2 rounded text-sm">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Car className="w-4 h-4" />
                      <span>{currentStats.cars}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Bike className="w-4 h-4" />
                      <span>{currentStats.motorbikes}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      <span>{currentStats.totalVehicles} total</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Current Traffic Status - Using REAL DATA */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Vehicles</p>
                  <p className="text-3xl font-bold">{currentStats.totalVehicles}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
              <Badge className={getStatusBadge(currentStats.status)}>
                {currentStats.status.toUpperCase()}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Cars (Est.)</p>
                  <p className="text-3xl font-bold">{currentStats.cars}</p>
                </div>
                <Car className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Motorbikes (Est.)</p>
                  <p className="text-3xl font-bold">{currentStats.motorbikes}</p>
                </div>
                <Bike className="w-8 h-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600 mb-2">Traffic Flow (Est.)</p>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <ArrowRight className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="text-lg font-bold">{currentStats.inbound}</p>
                      <p className="text-xs text-gray-500">Inbound</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <ArrowLeft className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="text-lg font-bold">{currentStats.outbound}</p>
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
                <CardTitle>Real Traffic Data from API</CardTitle>
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
                  {trafficData.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500 mb-4">No traffic data available</p>
                      <Button onClick={refresh} variant="outline">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh Data
                      </Button>
                    </div>
                  ) : (
                  trafficData.map((data) => (
                    <div key={data._id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="text-lg font-semibold">{data.location}</div>
                        <Badge className={getStatusBadge(data.status)}>
                          {data.status.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-6">
                        {/* Separate car and motorbike counts with icons */}
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-1">
                            <Car className="w-4 h-4 text-green-600" />
                            <span className="text-sm">
                              {data.car_count || Math.floor(data.vehicle_count * 0.68)}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Bike className="w-4 h-4 text-orange-600" />
                            <span className="text-sm">
                              {data.motorbike_count || Math.floor(data.vehicle_count * 0.32)}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <TrendingUp className="w-4 h-4 text-blue-600" />
                            <span className="text-sm font-semibold">{data.vehicle_count}</span>
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          <div>
                            <div>{new Date(data.timestamp).toLocaleDateString()}</div>
                            <div className="font-medium">{new Date(data.timestamp).toLocaleTimeString()}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Traffic Volume Over Time</CardTitle>
              <p className="text-sm text-gray-600">Total vehicles detected throughout the day</p>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                {trafficData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trafficData.map(item => ({
                      time: new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                      vehicles: item.vehicle_count,
                      cars: item.car_count || Math.floor(item.vehicle_count * 0.68),
                      motorbikes: item.motorbike_count || Math.floor(item.vehicle_count * 0.32),
                      fullTime: new Date(item.timestamp).toLocaleString()
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="time" 
                        tick={{ fontSize: 12 }}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip 
                        labelFormatter={(label: any, payload: any[]) => 
                          payload?.[0]?.payload?.fullTime || label
                        }
                        formatter={(value: any, name: any) => [value, name === 'vehicles' ? 'Total Vehicles' : name === 'cars' ? 'Cars' : 'Motorbikes']}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="vehicles" 
                        stroke="#2563eb" 
                        strokeWidth={3}
                        name="Total Vehicles"
                        dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="cars" 
                        stroke="#16a34a" 
                        strokeWidth={2}
                        name="Cars"
                        dot={{ fill: '#16a34a', strokeWidth: 2, r: 3 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="motorbikes" 
                        stroke="#ea580c" 
                        strokeWidth={2}
                        name="Motorbikes"
                        dot={{ fill: '#ea580c', strokeWidth: 2, r: 3 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full bg-gray-100 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">No data available for chart</p>
                      <Button onClick={refresh} variant="outline" size="sm" className="mt-2">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Load Data
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Traffic Statistics Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <TrendingUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h3 className="font-semibold">Average Traffic</h3>
                <p className="text-2xl font-bold text-blue-600">
                  {trafficData.length > 0 ? Math.round(trafficData.reduce((sum, item) => sum + item.vehicle_count, 0) / trafficData.length) : 0}
                </p>
                <p className="text-sm text-gray-500">vehicles per reading</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <ArrowUp className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-semibold">Peak Traffic</h3>
                <p className="text-2xl font-bold text-green-600">
                  {trafficData.length > 0 ? Math.max(...trafficData.map(item => item.vehicle_count)) : 0}
                </p>
                <p className="text-sm text-gray-500">highest reading</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <ArrowDown className="w-8 h-8 text-orange-600 mx-auto mb-2" />
                <h3 className="font-semibold">Low Traffic</h3>
                <p className="text-2xl font-bold text-orange-600">
                  {trafficData.length > 0 ? Math.min(...trafficData.map(item => item.vehicle_count)) : 0}
                </p>
                <p className="text-sm text-gray-500">lowest reading</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        </Tabs>

        {/* Directional Traffic Flow */}
        <Card>
          <CardHeader>
            <CardTitle>Directional Traffic Flow (Estimated)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center p-6 border rounded-lg">
                <ArrowRight className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Inbound Traffic</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Cars:</span>
                    <span className="font-semibold">{currentStats.inbound}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Motorbikes:</span>
                    <span className="font-semibold">{currentStats.inbound}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span>Total:</span>
                    <span className="font-bold text-blue-600">{currentStats.inbound}</span>
                  </div>
                </div>
              </div>

              <div className="text-center p-6 border rounded-lg">
                <ArrowLeft className="w-12 h-12 text-purple-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Outbound Traffic</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Cars:</span>
                    <span className="font-semibold">{currentStats.outbound}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Motorbikes:</span>
                    <span className="font-semibold">{currentStats.outbound}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span>Total:</span>
                    <span className="font-bold text-purple-600">{currentStats.outbound}</span>
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