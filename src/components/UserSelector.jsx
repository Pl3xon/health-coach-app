import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Plus, Trash2, LogOut, Heart } from 'lucide-react'
import { useUser } from '../contexts/UserContext'

export default function UserSelector() {
  const { users, currentUser, selectUser, logout, createUser, deleteUser } = useUser()
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newYazioEmail, setNewYazioEmail] = useState('')
  const [newYazioPassword, setNewYazioPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newName.trim()) return
    setLoading(true)
    try {
      const id = newName.toLowerCase().replace(/[^a-z0-9]/g, '-')
      await createUser(id, newName.trim(), newEmail, newPassword, newYazioEmail, newYazioPassword)
      setShowCreate(false)
      setNewName('')
      setNewEmail('')
      setNewPassword('')
      setNewYazioEmail('')
      setNewYazioPassword('')
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (currentUser) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="glass-card p-3 flex items-center gap-3"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-medium">{currentUser.name}</span>
          <button
            onClick={logout}
            className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-red-400 transition-colors"
            title="Abmelden"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center"
          >
            <Heart className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold gradient-text mb-2">VitalCoach</h1>
          <p className="text-gray-400">Wähle dein Profil</p>
        </div>

        {!showCreate ? (
          <div className="space-y-3">
            {users.map((user) => (
              <motion.button
                key={user.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => selectUser(user)}
                className="w-full glass-card p-4 flex items-center gap-4 hover:border-cyan-500/30 transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-purple-500/20 flex items-center justify-center">
                  <User className="w-6 h-6 text-cyan-400" />
                </div>
                <div className="flex-1 text-left">
                  <p className="font-semibold">{user.name}</p>
                  <p className="text-xs text-gray-500">{user.id}</p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm(user.name + ' wirklich löschen?')) {
                      deleteUser(user.id)
                    }
                  }}
                  className="p-2 rounded-lg hover:bg-red-500/20 text-gray-500 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </motion.button>
            ))}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowCreate(true)}
              className="w-full glass-card p-4 flex items-center justify-center gap-2 text-gray-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-all"
            >
              <Plus className="w-5 h-5" />
              <span>Neues Profil</span>
            </motion.button>
          </div>
        ) : (
          <motion.form
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            onSubmit={handleCreate}
            className="glass-card p-6 space-y-4"
          >
            <h2 className="text-lg font-semibold">Neues Profil erstellen</h2>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Name *</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500"
                placeholder="z.B. Max"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Renpho E-Mail (optional)</label>
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500"
                placeholder="name@email.com"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Renpho Passwort (optional)</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Yazio E-Mail (optional)</label>
              <input
                type="email"
                value={newYazioEmail}
                onChange={(e) => setNewYazioEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500"
                placeholder="name@email.com"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Yazio Passwort (optional)</label>
              <input
                type="password"
                value={newYazioPassword}
                onChange={(e) => setNewYazioPassword(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500"
                placeholder="••••••••"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="flex-1 btn-secondary"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                disabled={loading || !newName.trim()}
                className="flex-1 btn-primary"
              >
                {loading ? 'Erstelle...' : 'Erstellen'}
              </button>
            </div>
          </motion.form>
        )}
      </motion.div>
    </div>
  )
}
