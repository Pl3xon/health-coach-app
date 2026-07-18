import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Scale, Droplets, Flame, Heart, Moon, Activity, Zap } from 'lucide-react'
import { api } from '../services/api'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
}

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState({ name: 'Kevin', weight: 80, height: 180, goals: ['Abnehmen', 'Muskelaufbau', 'Bauch weg'] })
  const [renpho, setRenpho] = useState({ connected: false, latest: null })
  const [googleFit, setGoogleFit] = useState(null)

  useEffect(() => {
    api.getDashboard().then(data => {
      if (data.profile) setProfile(data.profile)
      if (data.renpho) setRenpho(data.renpho)
      if (data.google_fit) setGoogleFit(data.google_fit)
    }).catch(() => {})
  }, [])

  const latest = renpho.latest || {}
  const gf = googleFit || {}

  const getSteps = () => {
    if (gf.steps && gf.steps.length > 0) {
      const todayBucket = gf.steps[gf.steps.length - 1]
      const val = todayBucket?.dataset?.[0]?.point?.[0]?.value?.[0]?.intVal
      return val !== undefined ? val.toLocaleString('de-DE') : '0'
    }
    return '0'
  }

  const getHeartRate = () => {
    if (gf.heart_rate && gf.heart_rate.length > 0) {
      for (let i = gf.heart_rate.length - 1; i >= 0; i--) {
        const bucket = gf.heart_rate[i]
        const points = bucket?.dataset?.[0]?.point
        if (points && points.length > 0) {
          const val = points[0]?.value?.[0]?.fpVal
          if (val && val > 0) return Math.round(val)
        }
      }
    }
    return '—'
  }

  const getCalories = () => {
    if (gf.calories && gf.calories.length > 0) {
      for (let i = gf.calories.length - 1; i >= 0; i--) {
        const bucket = gf.calories[i]
        const points = bucket?.dataset?.[0]?.point
        if (points && points.length > 0) {
          const val = points[0]?.value?.[0]?.fpVal
          if (val && val > 0) return Math.round(val).toLocaleString('de-DE')
        }
      }
    }
    return '—'
  }

  const getSleep = () => {
    if (gf.sleep && gf.sleep.length > 0) {
      for (let i = gf.sleep.length - 1; i >= 0; i--) {
        const bucket = gf.sleep[i]
        const points = bucket?.dataset?.[0]?.point
        if (points && points.length > 0) {
          const val = points[0]?.value?.[0]?.fpVal
          if (val && val > 0) return (val / 3600000).toFixed(1)
        }
      }
    }
    return '—'
  }

  const vitals = [
    { label: 'Gewicht', value: latest.weight ? String(latest.weight) : String(profile.weight), unit: 'kg', trend: 'down', icon: Scale, color: 'from-cyan-400 to-blue-500', shadow: 'shadow-neon' },
    { label: 'Körperfett', value: latest.bodyFat ? String(latest.bodyFat) : '—', unit: '%', trend: 'down', icon: Droplets, color: 'from-purple-400 to-pink-500', shadow: 'shadow-neon-purple' },
    { label: 'Muskelmasse', value: latest.muscleMass ? String(latest.muscleMass) : '—', unit: 'kg', trend: 'up', icon: Zap, color: 'from-green-400 to-emerald-500', shadow: 'shadow-neon-green' },
    { label: 'BMR', value: latest.bmr ? String(Math.round(latest.bmr)) : '—', unit: 'kcal', trend: 'up', icon: Flame, color: 'from-orange-400 to-red-500', shadow: 'shadow-neon' },
  ]

  const todayStats = [
    { label: 'Kalorien verbrannt', value: getCalories(), icon: Flame, color: 'text-orange-400' },
    { label: 'Herzfrequenz', value: getHeartRate(), unit: 'bpm', icon: Heart, color: 'text-red-400' },
    { label: 'Schritte', value: getSteps(), icon: Activity, color: 'text-cyan-400' },
    { label: 'Schlaf', value: getSleep(), unit: 'h', icon: Moon, color: 'text-purple-400' },
  ]

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-6 lg:p-8">
      <motion.div variants={item} className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Moin, <span className="gradient-text">{profile.name}</span></h1>
        <p className="text-gray-400">Hier ist dein Gesundheits-Update für heute</p>
      </motion.div>

      <motion.div variants={item} className="mb-8">
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-cyan-400" />Deine Ziele</h2>
          <div className="flex flex-wrap gap-3">
            {profile.goals.map((goal, index) => (
              <span key={index} className="px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 text-sm font-medium">{goal}</span>
            ))}
          </div>
        </div>
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {vitals.map((vital) => (
          <motion.div key={vital.label} variants={item} whileHover={{ scale: 1.02, y: -5 }} className={`stat-card ${vital.shadow}`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${vital.color} flex items-center justify-center`}>
                <vital.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-1">{vital.label}</p>
            <p className="text-3xl font-bold">{vital.value}<span className="text-lg text-gray-400 ml-1">{vital.unit}</span></p>
          </motion.div>
        ))}
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {todayStats.map((stat) => (
          <motion.div key={stat.label} variants={item} whileHover={{ scale: 1.02 }} className="glass-card p-5">
            <div className="flex items-center gap-3">
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
              <div>
                <p className="text-gray-400 text-sm">{stat.label}</p>
                <p className="text-2xl font-bold">{stat.value}{stat.unit && <span className="text-sm text-gray-400 ml-1">{stat.unit}</span>}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <motion.div variants={item}>
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Schnellaktionen</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button onClick={() => navigate('/workout')} className="btn-primary flex items-center justify-center gap-2"><Activity className="w-5 h-5" />Workout starten</button>
            <button onClick={() => navigate('/coach')} className="btn-secondary flex items-center justify-center gap-2"><Flame className="w-5 h-5" />Mahlzeit eintragen</button>
            <button onClick={() => navigate('/vitals')} className="btn-secondary flex items-center justify-center gap-2"><Scale className="w-5 h-5" />Wiegen</button>
            <button onClick={() => navigate('/vitals')} className="btn-secondary flex items-center justify-center gap-2"><Heart className="w-5 h-5" />Puls messen</button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
