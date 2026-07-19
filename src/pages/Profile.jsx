import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { User, Save, Target, Ruler, Scale, Calendar, Activity } from 'lucide-react'
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

export default function Profile() {
  const { currentUser } = useUser()
  const [profile, setProfile] = useState({
    name: 'Kevin',
    weight: 80,
    height: 180,
    age: 28,
    gender: 'männlich',
    goals: ['Abnehmen', 'Muskelaufbau', 'Bauch weg'],
    fitness_level: 'Anfänger',
    activity_level: 'Moderat'
  })

  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (!currentUser) return
    api.getProfile(currentUser.id).then(data => {
      if (data && data.name) setProfile(data)
    }).catch(() => {})
  }, [currentUser])

  const availableGoals = [
    'Abnehmen', 'Muskelaufbau', 'Ausdauer verbessern', 
    'Bauch weg', 'Allgemeine Fitness', 'Stressabbau',
    'Flexibilität', 'Kraft steigern'
  ]

  const fitnessLevels = ['Anfänger', 'Fortgeschritten', 'Profi']
  const activityLevels = ['Sedentär', 'Leicht aktiv', 'Moderat', 'Sehr aktiv', 'Extrem aktiv']

  const handleSave = async () => {
    try {
      await api.updateProfile({ ...profile, user_id: currentUser?.id })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (error) {
      console.error('Error saving profile:', error)
    }
  }

  const toggleGoal = (goal) => {
    setProfile(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }))
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="p-6 lg:p-8 max-w-4xl mx-auto"
    >
      {/* Header */}
      <motion.div variants={item} className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">Profil</span>
        </h1>
        <p className="text-gray-400">Verwalte deine persönlichen Daten</p>
      </motion.div>

      {/* Profile Card */}
      <motion.div variants={item} className="glass-card p-6 mb-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
            <User className="w-10 h-10 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">{profile.name}</h2>
            <p className="text-gray-400">{profile.age} Jahre | {profile.gender}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Name */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Name</label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
              className="input-field"
            />
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Alter</label>
            <input
              type="number"
              value={profile.age}
              onChange={(e) => setProfile(prev => ({ ...prev, age: parseInt(e.target.value) || 0 }))}
              className="input-field"
            />
          </div>

          {/* Height */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Größe (cm)</label>
            <input
              type="number"
              value={profile.height}
              onChange={(e) => setProfile(prev => ({ ...prev, height: parseFloat(e.target.value) || 0 }))}
              className="input-field"
            />
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Geschlecht</label>
            <select
              value={profile.gender}
              onChange={(e) => setProfile(prev => ({ ...prev, gender: e.target.value }))}
              className="input-field"
            >
              <option value="männlich">Männlich</option>
              <option value="weiblich">Weiblich</option>
              <option value="divers">Divers</option>
            </select>
          </div>

          {/* Fitness Level */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Fitnesslevel</label>
            <select
              value={profile.fitness_level}
              onChange={(e) => setProfile(prev => ({ ...prev, fitness_level: e.target.value }))}
              className="input-field"
            >
              {fitnessLevels.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>

          {/* Activity Level */}
          <div className="md:col-span-2">
            <label className="block text-sm text-gray-400 mb-2">Aktivitätslevel</label>
            <select
              value={profile.activity_level}
              onChange={(e) => setProfile(prev => ({ ...prev, activity_level: e.target.value }))}
              className="input-field"
            >
              {activityLevels.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>
        </div>
      </motion.div>

      {/* Goals */}
      <motion.div variants={item} className="glass-card p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-cyan-400" />
          Deine Ziele
        </h3>
        <div className="flex flex-wrap gap-3">
          {availableGoals.map((goal) => (
            <button
              key={goal}
              onClick={() => toggleGoal(goal)}
              className={`px-4 py-2 rounded-full transition-all duration-200 ${
                profile.goals.includes(goal)
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                  : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
              }`}
            >
              {goal}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div variants={item} className="flex justify-end">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSave}
          className={`btn-primary flex items-center gap-2 ${saved ? 'bg-green-500' : ''}`}
        >
          <Save className="w-5 h-5" />
          {saved ? 'Gespeichert!' : 'Speichern'}
        </motion.button>
      </motion.div>
    </motion.div>
  )
}
