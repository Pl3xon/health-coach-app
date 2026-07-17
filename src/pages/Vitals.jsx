import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, Scale, Droplets, Flame, Zap, Heart, 
  RefreshCw, Wifi, WifiOff, TrendingUp, TrendingDown
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
}

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
}

const mockWeightData = [
  { date: 'Mo', weight: 83.2 },
  { date: 'Di', weight: 83.0 },
  { date: 'Mi', weight: 82.8 },
  { date: 'Do', weight: 82.9 },
  { date: 'Fr', weight: 82.5 },
  { date: 'Sa', weight: 82.3 },
  { date: 'So', weight: 82.5 },
]

const mockBodyFatData = [
  { date: 'Mo', fat: 25.2 },
  { date: 'Di', fat: 25.1 },
  { date: 'Mi', fat: 25.0 },
  { date: 'Do', fat: 24.9 },
  { date: 'Fr', fat: 24.8 },
  { date: 'Sa', fat: 24.7 },
  { date: 'So', fat: 24.8 },
]

export default function Vitals() {
  const [renphoConnected, setRenphoConnected] = useState(false)
  const [googleFitConnected, setGoogleFitConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [measurements, setMeasurements] = useState([])

  const checkConnections = async () => {
    setLoading(true)
    try {
      const [renphoRes, fitRes] = await Promise.all([
        fetch('/api/renpho/status'),
        fetch('/api/google-fit/status')
      ])
      const renphoData = await renphoRes.json()
      const fitData = await fitRes.json()
      setRenphoConnected(renphoData.connected)
      setGoogleFitConnected(fitData.connected)
    } catch (error) {
      console.error('Error checking connections:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkConnections()
  }, [])

  const bodyComposition = [
    { label: 'Gewicht', value: '82.5 kg', icon: Scale, color: 'text-cyan-400', change: '-1.2 kg', trend: 'down' },
    { label: 'Körperfett', value: '24.8%', icon: Droplets, color: 'text-purple-400', change: '-0.5%', trend: 'down' },
    { label: 'Muskelmasse', value: '38.2 kg', icon: Zap, color: 'text-green-400', change: '+0.3 kg', trend: 'up' },
    { label: 'BMI', value: '25.5', icon: Activity, color: 'text-orange-400', change: '-0.4', trend: 'down' },
    { label: 'BMR', value: '1,785 kcal', icon: Flame, color: 'text-red-400', change: '+12', trend: 'up' },
    { label: 'Herzfrequenz', value: '72 bpm', icon: Heart, color: 'text-pink-400', change: '-2', trend: 'down' },
  ]

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="p-6 lg:p-8"
    >
      {/* Header */}
      <motion.div variants={item} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">Vitaldaten</span>
          </h1>
          <p className="text-gray-400">Übersicht deiner Gesundheitswerte</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={checkConnections}
          disabled={loading}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          Aktualisieren
        </motion.button>
      </motion.div>

      {/* Connection Status */}
      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className={`glass-card p-5 ${renphoConnected ? 'neon-glow-green' : ''}`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              renphoConnected 
                ? 'bg-gradient-to-br from-green-400 to-emerald-500' 
                : 'bg-gradient-to-br from-gray-500 to-gray-600'
            }`}>
              {renphoConnected ? (
                <Wifi className="w-6 h-6 text-white" />
              ) : (
                <WifiOff className="w-6 h-6 text-white" />
              )}
            </div>
            <div>
              <h3 className="font-semibold">Renpho Waage</h3>
              <p className={`text-sm ${renphoConnected ? 'text-green-400' : 'text-gray-400'}`}>
                {renphoConnected ? 'Verbunden' : 'Nicht verbunden'}
              </p>
            </div>
          </div>
        </div>

        <div className={`glass-card p-5 ${googleFitConnected ? 'neon-glow' : ''}`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              googleFitConnected 
                ? 'bg-gradient-to-br from-cyan-400 to-blue-500' 
                : 'bg-gradient-to-br from-gray-500 to-gray-600'
            }`}>
              {googleFitConnected ? (
                <Activity className="w-6 h-6 text-white" />
              ) : (
                <WifiOff className="w-6 h-6 text-white" />
              )}
            </div>
            <div>
              <h3 className="font-semibold">Google Fit</h3>
              <p className={`text-sm ${googleFitConnected ? 'text-cyan-400' : 'text-gray-400'}`}>
                {googleFitConnected ? 'Verbunden' : 'Nicht verbunden'}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Body Composition */}
      <motion.div variants={item} className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Körperzusammensetzung</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {bodyComposition.map((metric, index) => (
            <motion.div
              key={metric.label}
              variants={item}
              whileHover={{ scale: 1.05 }}
              className="stat-card text-center"
            >
              <metric.icon className={`w-8 h-8 ${metric.color} mx-auto mb-2`} />
              <p className="text-sm text-gray-400 mb-1">{metric.label}</p>
              <p className="text-lg font-bold">{metric.value}</p>
              <div className={`flex items-center justify-center gap-1 text-xs mt-1 ${
                metric.trend === 'down' ? 'text-green-400' : 'text-cyan-400'
              }`}>
                {metric.trend === 'down' ? (
                  <TrendingDown className="w-3 h-3" />
                ) : (
                  <TrendingUp className="w-3 h-3" />
                )}
                {metric.change}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Charts */}
      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weight Chart */}
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Scale className="w-5 h-5 text-cyan-400" />
            Gewichtsverlauf
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockWeightData}>
                <defs>
                  <linearGradient id="weightGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                <Tooltip 
                  contentStyle={{ 
                    background: '#1a1f35', 
                    border: '1px solid rgba(0,212,255,0.3)',
                    borderRadius: '8px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="weight" 
                  stroke="#00d4ff" 
                  fillOpacity={1} 
                  fill="url(#weightGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Body Fat Chart */}
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-purple-400" />
            Körperfett-Verlauf
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockBodyFatData}>
                <defs>
                  <linearGradient id="fatGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                <Tooltip 
                  contentStyle={{ 
                    background: '#1a1f35', 
                    border: '1px solid rgba(168,85,247,0.3)',
                    borderRadius: '8px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="fat" 
                  stroke="#a855f7" 
                  fillOpacity={1} 
                  fill="url(#fatGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
