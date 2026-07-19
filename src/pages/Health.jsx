import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, Heart, Moon, Flame, Zap, Droplets, Apple, ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { api } from '../services/api'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } }
}

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card p-3 text-sm">
        <p className="text-gray-400 mb-1">{label}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color }} className="font-semibold">
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString('de-DE') : entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

function ChartCard({ title, data, dataKey, color, unit, icon: Icon, iconColor }) {
  if (!data || data.length === 0) return null
  return (
    <motion.div variants={item} className="glass-card p-5">
      <div className="flex items-center gap-2 mb-4">
        {Icon && <Icon className={`w-5 h-5 ${iconColor}`} />}
        <h3 className="font-semibold">{title}</h3>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="date"
            stroke="rgba(255,255,255,0.3)"
            tick={{ fontSize: 11 }}
            tickFormatter={(val) => {
              const d = new Date(val)
              return `${d.getDate()}.${d.getMonth() + 1}`
            }}
          />
          <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} width={50} />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="value"
            name={title}
            stroke={color}
            fill={`url(#gradient-${dataKey})`}
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
      {unit && <p className="text-xs text-gray-500 mt-2 text-right">{unit}</p>}
    </motion.div>
  )
}

function StatCard({ label, value, unit, icon: Icon, color }) {
  return (
    <motion.div variants={item} whileHover={{ scale: 1.02 }} className="stat-card">
      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center mb-3`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold">
        {value ?? '—'}
        {value && <span className="text-sm text-gray-400 ml-1">{unit}</span>}
      </p>
    </motion.div>
  )
}

export default function Health() {
  const navigate = useNavigate()
  const [history, setHistory] = useState(null)
  const [today, setToday] = useState(null)
  const [yazioData, setYazioData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [historyRes, dashboardRes, yazioRes] = await Promise.all([
        api.getGoogleFitHistory(30),
        api.getDashboard(),
        api.getYazioDaily()
      ])
      if (historyRes.data) setHistory(historyRes.data)
      if (dashboardRes.google_fit) setToday(dashboardRes.google_fit)
      if (yazioRes.data) setYazioData(yazioRes.data)
    } catch (error) {
      console.error('Error loading health data:', error)
    } finally {
      setLoading(false)
    }
  }

  const stepsData = history?.steps || []
  const caloriesData = history?.calories || []
  const heartRateData = history?.heart_rate || []
  const restingHRData = history?.resting_heart_rate || []
  const hrvData = history?.hrv || []
  const spo2Data = history?.spo2 || []
  const azmData = history?.active_zone_minutes || []

  const yazioGoals = yazioData?.goals || {}
  const calorieGoal = yazioGoals['energy.energy'] || 2200
  const carbGoal = yazioGoals['nutrient.carb'] || 220

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-6 lg:p-8">
      <motion.div variants={item} className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div>
            <h1 className="text-3xl font-bold mb-2">
              <span className="gradient-text">Gesundheit</span>
            </h1>
            <p className="text-gray-400">Alle deine Gesundheitsdaten im Überblick</p>
          </div>
        </div>
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={loadData} disabled={loading} className="btn-secondary flex items-center gap-2">
          <Activity className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          Aktualisieren
        </motion.button>
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Herzfrequenz" value={today?.heart_rate || null} unit="bpm" icon={Heart} color="from-red-400 to-pink-500" />
        <StatCard label="Ruhe-HF" value={today?.resting_heart_rate || null} unit="bpm" icon={Heart} color="from-orange-400 to-red-500" />
        <StatCard label="HRV" value={today?.hrv || null} unit="ms" icon={Activity} color="from-purple-400 to-pink-500" />
        <StatCard label="SpO2" value={today?.spo2 || null} unit="%" icon={Droplets} color="from-cyan-400 to-blue-500" />
        <StatCard label="Schritte" value={today?.steps_today || null} unit="" icon={Activity} color="from-green-400 to-emerald-500" />
        <StatCard label="Kalorien" value={today?.calories_today || null} unit="kcal" icon={Flame} color="from-orange-400 to-red-500" />
        <StatCard label="Aktivzonen" value={today?.active_zone_minutes || null} unit="min" icon={Zap} color="from-yellow-400 to-orange-500" />
        <StatCard label="Schlaf" value={today?.sleep_hours || null} unit="h" icon={Moon} color="from-indigo-400 to-purple-500" />
      </motion.div>

      {yazioData && (
        <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Kalorien (Ziel)" value={calorieGoal} unit="kcal" icon={Flame} color="from-orange-400 to-red-500" />
          <StatCard label="Kohlenhydrate (Ziel)" value={carbGoal} unit="g" icon={Apple} color="from-green-400 to-emerald-500" />
        </motion.div>
      )}

      <motion.div variants={item} className="mb-4">
        <h2 className="text-xl font-semibold mb-4">Verlauf (30 Tage)</h2>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <ChartCard title="Herzfrequenz" data={heartRateData} dataKey="heart_rate" color="#ef4444" unit="bpm" icon={Heart} iconColor="text-red-400" />
        <ChartCard title="Ruheherzfrequenz" data={restingHRData} dataKey="resting_hr" color="#f97316" unit="bpm" icon={Heart} iconColor="text-orange-400" />
        <ChartCard title="HRV" data={hrvData} dataKey="hrv" color="#a855f7" unit="ms" icon={Activity} iconColor="text-purple-400" />
        <ChartCard title="Sauerstoffsättigung" data={spo2Data} dataKey="spo2" color="#06b6d4" unit="%" icon={Droplets} iconColor="text-cyan-400" />
        <ChartCard title="Schritte" data={stepsData} dataKey="steps" color="#22c55e" unit="" icon={Activity} iconColor="text-green-400" />
        <ChartCard title="Verbrannte Kalorien" data={caloriesData} dataKey="calories" color="#f97316" unit="kcal" icon={Flame} iconColor="text-orange-400" />
        <ChartCard title="Aktivzonenminuten" data={azmData} dataKey="azm" color="#eab308" unit="min" icon={Zap} iconColor="text-yellow-400" />
      </div>
    </motion.div>
  )
}
