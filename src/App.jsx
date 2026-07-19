import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink, useSearchParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  LayoutDashboard, MessageCircle, UtensilsCrossed, 
  Dumbbell, Activity, Settings, Menu, X, Heart,
  TrendingUp, User, Stethoscope, LogOut
} from 'lucide-react'

import { UserProvider, useUser } from './contexts/UserContext'
import UserSelector from './components/UserSelector'
import Dashboard from './pages/Dashboard'
import Coach from './pages/Coach'
import Nutrition from './pages/Nutrition'
import Workout from './pages/Workout'
import Vitals from './pages/Vitals'
import Profile from './pages/Profile'
import Health from './pages/Health'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/health', icon: Stethoscope, label: 'Gesundheit' },
  { path: '/coach', icon: MessageCircle, label: 'AI Coach' },
  { path: '/nutrition', icon: UtensilsCrossed, label: 'Ernährung' },
  { path: '/workout', icon: Dumbbell, label: 'Workout' },
  { path: '/vitals', icon: Activity, label: 'Vitaldaten' },
  { path: '/profile', icon: User, label: 'Profil' },
]

function GoogleFitCallbackRedirect() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')
    const params = new URLSearchParams()
    if (code) params.set('code', code)
    if (error) params.set('error', error)
    navigate(`/vitals?${params.toString()}`, { replace: true })
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-400">Google Fit wird verbunden...</p>
    </div>
  )
}

function FitbitCallbackRedirect() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')
    const params = new URLSearchParams()
    if (code) params.set('code', code)
    if (error) params.set('error', error)
    navigate(`/vitals?${params.toString()}`, { replace: true })
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-400">Fitbit wird über Google verbunden...</p>
    </div>
  )
}

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { logout, currentUser } = useUser()

  return (
    <div className="min-h-screen flex">
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 glass-card"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: sidebarOpen ? 0 : -280 }}
        className={`sidebar fixed lg:static w-[280px] h-screen z-40 flex flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } transition-transform duration-300`}
      >
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
              <Heart className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">VitalCoach</h1>
              <p className="text-xs text-gray-500">Gesundheits-Cockpit</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive 
                    ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border border-cyan-500/30' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <item.icon size={20} />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="glass-card p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{currentUser?.name || 'User'}</p>
                <p className="text-xs text-gray-500">Eingeloggt</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all"
            >
              <LogOut className="w-4 h-4" />
              Abmelden
            </button>
          </div>
        </div>
      </motion.aside>

      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="flex-1 min-h-screen" style={{ paddingTop: 'env(safe-area-inset-top)' }}>
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/health" element={<Health />} />
            <Route path="/coach" element={<Coach />} />
            <Route path="/nutrition" element={<Nutrition />} />
            <Route path="/workout" element={<Workout />} />
            <Route path="/vitals" element={<Vitals />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </AnimatePresence>
      </main>
      
      <UserSelector />
    </div>
  )
}

function AppContent() {
  const { currentUser, loading } = useUser()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center"
          >
            <Heart className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold gradient-text mb-2">VitalCoach</h1>
          <p className="text-gray-400">Dein Gesundheits-Cockpit wird geladen...</p>
        </motion.div>
      </div>
    )
  }

  if (!currentUser) {
    return <UserSelector />
  }

  return <AppLayout />
}

function App() {
  return (
    <Router>
      <UserProvider>
        <Routes>
          <Route path="/auth/google-fit" element={<GoogleFitCallbackRedirect />} />
          <Route path="/auth/fitbit" element={<FitbitCallbackRedirect />} />
          <Route path="*" element={<AppContent />} />
        </Routes>
      </UserProvider>
    </Router>
  )
}

export default App
