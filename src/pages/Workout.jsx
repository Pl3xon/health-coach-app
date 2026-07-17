import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Dumbbell, Clock, Target, Loader2, ChevronDown, ChevronUp, Youtube } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../services/api'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
}

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
}

const workoutCategories = [
  {
    name: 'Bauch & Core', icon: '🎯', color: 'from-cyan-400 to-blue-500',
    exercises: [
      { name: 'Plank', sets: '3x 30-60s', image: 'https://images.unsplash.com/photo-1566241142559-40e1dab266c6?w=400', youtube: 'https://www.youtube.com/results?search_query=plank+exercise+proper+form' },
      { name: 'Crunches', sets: '3x 15', image: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400', youtube: 'https://www.youtube.com/results?search_query=crunches+proper+form' },
      { name: 'Mountain Climbers', sets: '3x 20', image: 'https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=400', youtube: 'https://www.youtube.com/results?search_query=mountain+climbers+exercise' },
      { name: 'Leg Raises', sets: '3x 12', image: 'https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=400', youtube: 'https://www.youtube.com/results?search_query=leg+raises+exercise' },
    ]
  },
  {
    name: 'Brust & Arme', icon: '💪', color: 'from-purple-400 to-pink-500',
    exercises: [
      { name: 'Push-Ups', sets: '3x 12-15', image: 'https://images.unsplash.com/photo-1598971861713-54ad10a2c8e2?w=400', youtube: 'https://www.youtube.com/results?search_query=push+ups+proper+form' },
      { name: 'Diamond Push-Ups', sets: '3x 10', image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400', youtube: 'https://www.youtube.com/results?search_query=diamond+push+ups' },
      { name: 'Tricep Dips', sets: '3x 12', image: 'https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=400', youtube: 'https://www.youtube.com/results?search_query=tricep+dips+chair' },
      { name: 'Pike Push-Ups', sets: '3x 8', image: 'https://images.unsplash.com/photo-1597452485669-2c7bb5fef90d?w=400', youtube: 'https://www.youtube.com/results?search_query=pike+push+ups' },
    ]
  },
  {
    name: 'Beine & Po', icon: '🦵', color: 'from-green-400 to-emerald-500',
    exercises: [
      { name: 'Squats', sets: '4x 15', image: 'https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400', youtube: 'https://www.youtube.com/results?search_query=squats+proper+form' },
      { name: 'Lunges', sets: '3x 12 each', image: 'https://images.unsplash.com/photo-1434682881908-b43d0467b798?w=400', youtube: 'https://www.youtube.com/results?search_query=lunges+exercise' },
      { name: 'Glute Bridges', sets: '3x 15', image: 'https://images.unsplash.com/photo-1597452485669-2c7bb5fef90d?w=400', youtube: 'https://www.youtube.com/results?search_query=glute+bridges' },
      { name: 'Calf Raises', sets: '3x 20', image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400', youtube: 'https://www.youtube.com/results?search_query=calf+raises' },
    ]
  },
  {
    name: 'Ganzkörper', icon: '🔥', color: 'from-orange-400 to-red-500',
    exercises: [
      { name: 'Burpees', sets: '3x 10', image: 'https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=400', youtube: 'https://www.youtube.com/results?search_query=burpees+exercise' },
      { name: 'Jumping Jacks', sets: '3x 30s', image: 'https://images.unsplash.com/photo-1538805060514-97d9cc17730c?w=400', youtube: 'https://www.youtube.com/results?search_query=jumping+jacks' },
      { name: 'High Knees', sets: '3x 30s', image: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400', youtube: 'https://www.youtube.com/results?search_query=high+knees+exercise' },
      { name: 'Squat Jumps', sets: '3x 12', image: 'https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400', youtube: 'https://www.youtube.com/results?search_query=squat+jumps' },
    ]
  }
]

export default function Workout() {
  const [expandedCategory, setExpandedCategory] = useState('Bauch & Core')
  const [aiPlan, setAiPlan] = useState(null)
  const [loading, setLoading] = useState(false)

  const generateAiPlan = async () => {
    setLoading(true)
    try {
      const data = await api.generateWorkoutPlan()
      setAiPlan(data.plan)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-6 lg:p-8">
      <motion.div variants={item} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">Home Workout</span>
          </h1>
          <p className="text-gray-400">Kein Equipment nötig - trainiere überall</p>
        </div>
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={generateAiPlan} disabled={loading} className="btn-primary flex items-center gap-2">
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Dumbbell className="w-5 h-5" />}
          KI-Plan erstellen
        </motion.button>
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-3 gap-4 mb-8">
        <div className="stat-card text-center">
          <Target className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">4</p>
          <p className="text-sm text-gray-400">Kategorien</p>
        </div>
        <div className="stat-card text-center">
          <Dumbbell className="w-8 h-8 text-purple-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">16</p>
          <p className="text-sm text-gray-400">Übungen</p>
        </div>
        <div className="stat-card text-center">
          <Clock className="w-8 h-8 text-green-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">30</p>
          <p className="text-sm text-gray-400">Min / Tag</p>
        </div>
      </motion.div>

      <motion.div variants={item} className="space-y-4 mb-8">
        {workoutCategories.map((category) => (
          <motion.div key={category.name} variants={item} className="glass-card overflow-hidden">
            <button onClick={() => setExpandedCategory(expandedCategory === category.name ? null : category.name)} className="w-full p-5 flex items-center justify-between hover:bg-white/5 transition-colors">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{category.icon}</span>
                <div className="text-left">
                  <h3 className="font-semibold text-lg">{category.name}</h3>
                  <p className="text-sm text-gray-400">{category.exercises.length} Übungen</p>
                </div>
              </div>
              {expandedCategory === category.name ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
            </button>
            <AnimatePresence>
              {expandedCategory === category.name && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }} className="overflow-hidden">
                  <div className="p-5 pt-0 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {category.exercises.map((exercise, index) => (
                      <motion.div key={exercise.name} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }} className="flex gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors group">
                        <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0">
                          <img src={exercise.image} alt={exercise.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300" onError={(e) => { e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%231a1f35" width="100" height="100"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2300d4ff" font-size="24">💪</text></svg>' }} />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold mb-1">{exercise.name}</h4>
                          <p className="text-sm text-gray-400 mb-2">{exercise.sets}</p>
                          <a href={exercise.youtube} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs text-red-400 hover:text-red-300 transition-colors">
                            <Youtube className="w-4 h-4" />
                            Video ansehen
                          </a>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </motion.div>

      {aiPlan && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Dumbbell className="w-5 h-5 text-cyan-400" />
            Dein KI-Workout-Plan
          </h2>
          <div className="markdown-content">
            <ReactMarkdown>{aiPlan}</ReactMarkdown>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
