import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, Scale, Droplets, Flame, Zap, Heart, RefreshCw, Wifi, WifiOff, UtensilsCrossed } from 'lucide-react'
import { api } from '../services/api'
import { useUser } from '../contexts/UserContext'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
}

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
}

export default function Vitals() {
  const { currentUser } = useUser()
  const [renphoConnected, setRenphoConnected] = useState(false)
  const [googleFitConnected, setGoogleFitConnected] = useState(false)
  const [yazioConnected, setYazioConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [renphoData, setRenphoData] = useState(null)
  const [connecting, setConnecting] = useState(false)
  const [callbackError, setCallbackError] = useState(null)

  const checkConnections = async () => {
    setLoading(true)
    try {
      const [renphoRes, gfStatus, renphoLatest, yazioRes] = await Promise.all([
        api.getRenphoStatus(),
        api.getGoogleFitStatus(),
        api.getRenphoLatest(),
        api.getYazioStatus()
      ])
      setRenphoConnected(renphoRes.connected)
      setGoogleFitConnected(gfStatus.connected || false)
      setYazioConnected(yazioRes.connected || false)
      if (renphoLatest.measurement) setRenphoData(renphoLatest.measurement)
    } catch (error) {
      console.error('Error checking connections:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const error = params.get('error')
    if (error) {
      setCallbackError(`Google Fit Fehler: ${error}`)
      window.history.replaceState({}, '', '/vitals')
    } else if (code) {
      setConnecting(true)
      setCallbackError(null)
      api.googleFitCallback(code).then(res => {
        if (res.success) {
          window.history.replaceState({}, '', '/vitals')
          checkConnections()
        } else {
          setCallbackError(`Token-Tausch fehlgeschlagen: ${res.error || 'Unbekannter Fehler'}`)
          window.history.replaceState({}, '', '/vitals')
        }
      }).catch(err => {
        setCallbackError(`Callback Fehler: ${err.message}`)
        window.history.replaceState({}, '', '/vitals')
      }).finally(() => setConnecting(false))
    } else {
      checkConnections()
    }
  }, [])

  const connectGoogleFit = async () => {
    try {
      const res = await api.getGoogleFitUrl()
      if (res.url) {
        window.location.href = res.url
      }
    } catch (error) {
      console.error('Error getting Google Fit URL:', error)
    }
  }

  const r = renphoData || {}

  const bodyComposition = [
    { label: 'Gewicht', value: r.weight ? `${r.weight} kg` : '—', icon: Scale, color: 'text-cyan-400' },
    { label: 'Körperfett', value: r.bodyFat ? `${r.bodyFat}%` : '—', icon: Droplets, color: 'text-purple-400' },
    { label: 'Muskelmasse', value: r.muscleMass ? `${r.muscleMass} kg` : '—', icon: Zap, color: 'text-green-400' },
    { label: 'BMI', value: r.bmi ? String(r.bmi) : '—', icon: Activity, color: 'text-orange-400' },
    { label: 'BMR', value: r.bmr ? `${r.bmr} kcal` : '—', icon: Flame, color: 'text-red-400' },
    { label: 'Herzfrequenz', value: r.heartRate && r.heartRate > 0 ? `${r.heartRate} bpm` : '—', icon: Heart, color: 'text-pink-400' },
  ]

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-6 lg:p-8">
      <motion.div variants={item} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2"><span className="gradient-text">Vitaldaten</span></h1>
          <p className="text-gray-400">Übersicht deiner Gesundheitswerte</p>
        </div>
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={checkConnections} disabled={loading} className="btn-secondary flex items-center gap-2">
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          Aktualisieren
        </motion.button>
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className={`glass-card p-5 ${renphoConnected ? 'neon-glow-green' : ''}`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${renphoConnected ? 'bg-gradient-to-br from-green-400 to-emerald-500' : 'bg-gradient-to-br from-gray-500 to-gray-600'}`}>
              {renphoConnected ? <Wifi className="w-6 h-6 text-white" /> : <WifiOff className="w-6 h-6 text-white" />}
            </div>
            <div>
              <h3 className="font-semibold">Renpho Waage</h3>
              <p className={`text-sm ${renphoConnected ? 'text-green-400' : 'text-gray-400'}`}>{renphoConnected ? 'Verbunden' : 'Nicht verbunden'}</p>
            </div>
          </div>
        </div>
        <div className={`glass-card p-5 ${googleFitConnected ? 'neon-glow' : ''}`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${googleFitConnected ? 'bg-gradient-to-br from-cyan-400 to-blue-500' : 'bg-gradient-to-br from-gray-500 to-gray-600'}`}>
              {googleFitConnected ? <Activity className="w-6 h-6 text-white" /> : <WifiOff className="w-6 h-6 text-white" />}
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">Google Fit (Fitbit)</h3>
              <p className={`text-sm ${googleFitConnected ? 'text-cyan-400' : 'text-gray-400'}`}>
                {connecting ? 'Verbinde...' : googleFitConnected ? 'Verbunden' : 'Nicht verbunden'}
              </p>
            </div>
            {!googleFitConnected && !connecting && (
              <button onClick={connectGoogleFit} className="btn-primary text-sm px-4 py-2">
                Verbinden
              </button>
            )}
          </div>
        </div>
        <div className={`glass-card p-5 ${yazioConnected ? 'neon-glow' : ''}`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${yazioConnected ? 'bg-gradient-to-br from-orange-400 to-red-500' : 'bg-gradient-to-br from-gray-500 to-gray-600'}`}>
              {yazioConnected ? <UtensilsCrossed className="w-6 h-6 text-white" /> : <WifiOff className="w-6 h-6 text-white" />}
            </div>
            <div>
              <h3 className="font-semibold">Yazio</h3>
              <p className={`text-sm ${yazioConnected ? 'text-orange-400' : 'text-gray-400'}`}>{yazioConnected ? 'Verbunden' : 'Nicht verbunden'}</p>
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div variants={item} className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Körperzusammensetzung</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {bodyComposition.map((metric) => (
            <motion.div key={metric.label} variants={item} whileHover={{ scale: 1.05 }} className="stat-card text-center">
              <metric.icon className={`w-8 h-8 ${metric.color} mx-auto mb-2`} />
              <p className="text-sm text-gray-400 mb-1">{metric.label}</p>
              <p className="text-lg font-bold">{metric.value}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {r.date && (
        <motion.div variants={item} className="glass-card p-4 mb-6 text-center text-sm text-gray-400">
          Letzte Messung: {r.date}
        </motion.div>
      )}

      {callbackError && (
        <motion.div variants={item} className="glass-card p-4 mb-6 border border-red-500/30 bg-red-500/10 text-center text-sm text-red-400">
          {callbackError}
        </motion.div>
      )}
    </motion.div>
  )
}
