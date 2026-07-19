import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { UtensilsCrossed, Flame, Apple, Droplets, Loader2, RefreshCw } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
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

export default function Nutrition() {
  const { currentUser } = useUser()
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [yazioData, setYazioData] = useState(null)
  const [yazioDiary, setYazioDiary] = useState(null)
  const [loadingYazio, setLoadingYazio] = useState(false)

  useEffect(() => {
    loadYazioData()
  }, [])

  const loadYazioData = async () => {
    setLoadingYazio(true)
    try {
      const [summaryRes, diaryRes] = await Promise.all([
        api.getYazioDaily(),
        api.getYazioDiary()
      ])
      if (summaryRes.data) setYazioData(summaryRes.data)
      if (diaryRes.data) setYazioDiary(diaryRes.data)
    } catch (error) {
      console.error('Error loading Yazio data:', error)
    } finally {
      setLoadingYazio(false)
    }
  }

  const generatePlan = async () => {
    setLoading(true)
    try {
      const data = await api.generateNutritionPlan(currentUser?.id)
      setPlan(data.plan)
    } catch (error) {
      console.error('Error generating plan:', error)
    } finally {
      setLoading(false)
    }
  }

  const goals = yazioData?.goals || {}
  const summaryGoals = {
    calories: goals['energy.energy'] || 2200,
    protein: goals['nutrient.protein'] || 165,
    carbs: goals['nutrient.carb'] || 220,
    fat: goals['nutrient.fat'] || 73,
  }

  const macroCards = [
    { label: 'Kalorien', value: summaryGoals.calories, unit: 'kcal', icon: Flame, color: 'from-orange-400 to-red-500', percent: 100 },
    { label: 'Protein', value: summaryGoals.protein, unit: 'g', icon: Droplets, color: 'from-cyan-400 to-blue-500', percent: 30 },
    { label: 'Kohlenhydrate', value: summaryGoals.carbs, unit: 'g', icon: Apple, color: 'from-green-400 to-emerald-500', percent: 40 },
    { label: 'Fett', value: summaryGoals.fat, unit: 'g', icon: Droplets, color: 'from-purple-400 to-pink-500', percent: 30 },
  ]

  const mealGroups = {}
  if (yazioDiary && Array.isArray(yazioDiary)) {
    yazioDiary.forEach(item => {
      const meal = item.daytime || 'snack'
      if (!mealGroups[meal]) mealGroups[meal] = []
      mealGroups[meal].push(item)
    })
  }

  const mealLabels = { breakfast: 'Frühstück', lunch: 'Mittagessen', dinner: 'Abendessen', snack: 'Snacks' }
  const mealColors = { breakfast: 'from-yellow-400 to-orange-500', lunch: 'from-green-400 to-emerald-500', dinner: 'from-cyan-400 to-blue-500', snack: 'from-purple-400 to-pink-500' }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-6 lg:p-8">
      <motion.div variants={item} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">Ernährung</span>
          </h1>
          <p className="text-gray-400">Dein personalisierter Ernährungsplan</p>
        </div>
        <div className="flex gap-2">
          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={loadYazioData} disabled={loadingYazio} className="btn-secondary flex items-center gap-2">
            <RefreshCw className={`w-5 h-5 ${loadingYazio ? 'animate-spin' : ''}`} />
          </motion.button>
          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={generatePlan} disabled={loading} className="btn-primary flex items-center gap-2">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <RefreshCw className="w-5 h-5" />}
            Plan erstellen
          </motion.button>
        </div>
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {macroCards.map((macro, index) => (
          <motion.div key={macro.label} variants={item} whileHover={{ scale: 1.02 }} className="stat-card">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${macro.color} flex items-center justify-center mb-3`}>
              <macro.icon className="w-5 h-5 text-white" />
            </div>
            <p className="text-gray-400 text-sm mb-1">{macro.label}</p>
            <p className="text-2xl font-bold">
              {macro.value}
              <span className="text-sm text-gray-400 ml-1">{macro.unit}</span>
            </p>
            <div className="mt-2 h-1.5 bg-white/10 rounded-full overflow-hidden">
              <motion.div initial={{ width: 0 }} animate={{ width: `${macro.percent}%` }} transition={{ duration: 1, delay: index * 0.1 }} className={`h-full bg-gradient-to-r ${macro.color} rounded-full`} />
            </div>
          </motion.div>
        ))}
      </motion.div>

      {yazioDiary && yazioDiary.length > 0 ? (
        <motion.div variants={item} className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Heute gegessen</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(mealGroups).map(([meal, items]) => (
              <motion.div key={meal} variants={item} whileHover={{ scale: 1.02, y: -5 }} className="glass-card overflow-hidden">
                <div className={`h-2 bg-gradient-to-r ${mealColors[meal] || mealColors.snack}`} />
                <div className="p-5">
                  <h3 className="font-semibold text-lg mb-2">{mealLabels[meal] || meal}</h3>
                  <ul className="space-y-1 mb-3">
                    {items.slice(0, 5).map((item, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        {item.name || `Eintrag ${i + 1}`}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      ) : (
        <motion.div variants={item} className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Tagesplan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { time: 'Frühstück', items: ['Haferflocken mit Beeren', 'Griechischer Joghurt', 'Protein-Shake'], calories: 450, color: 'from-yellow-400 to-orange-500' },
              { time: 'Mittagessen', items: ['Hähnchenbrust', 'Vollkornreis', 'Gemüse'], calories: 650, color: 'from-green-400 to-emerald-500' },
              { time: 'Abendessen', items: ['Lachs', 'Süßkartoffel', 'Salat'], calories: 550, color: 'from-cyan-400 to-blue-500' },
              { time: 'Snacks', items: ['Nüsse', 'Protein-Riegel', 'Obst'], calories: 350, color: 'from-purple-400 to-pink-500' },
            ].map((meal) => (
              <motion.div key={meal.time} variants={item} whileHover={{ scale: 1.02, y: -5 }} className="glass-card overflow-hidden">
                <div className={`h-2 bg-gradient-to-r ${meal.color}`} />
                <div className="p-5">
                  <h3 className="font-semibold text-lg mb-2">{meal.time}</h3>
                  <ul className="space-y-1 mb-3">
                    {meal.items.map((item, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        {item}
                      </li>
                    ))}
                  </ul>
                  <p className="text-sm text-gray-400">
                    <span className="text-cyan-400 font-semibold">{meal.calories}</span> kcal
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {plan && (
        <motion.div variants={item} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <UtensilsCrossed className="w-5 h-5 text-cyan-400" />
            Dein personalisierter Plan
          </h2>
          <div className="markdown-content">
            <ReactMarkdown>{plan}</ReactMarkdown>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
