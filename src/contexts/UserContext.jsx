import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const UserContext = createContext()

export function UserProvider({ children }) {
  const [users, setUsers] = useState([])
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await api.listUsers()
      setUsers(data.users || [])
      const saved = localStorage.getItem('vitalcoach_user')
      if (saved) {
        const found = (data.users || []).find(u => u.id === saved)
        if (found) setCurrentUser(found)
      }
    } catch (e) {
      console.error('Failed to load users:', e)
    } finally {
      setLoading(false)
    }
  }

  const selectUser = (user) => {
    setCurrentUser(user)
    localStorage.setItem('vitalcoach_user', user.id)
  }

  const logout = () => {
    setCurrentUser(null)
    localStorage.removeItem('vitalcoach_user')
  }

  const createUser = async (id, name, renphoEmail = '', renphoPassword = '', yazioEmail = '', yazioPassword = '') => {
    const user = await api.createUser(id, name, renphoEmail, renphoPassword, yazioEmail, yazioPassword)
    setUsers(prev => [...prev, user])
    return user
  }

  const deleteUser = async (userId) => {
    await api.deleteUser(userId)
    setUsers(prev => prev.filter(u => u.id !== userId))
    if (currentUser?.id === userId) logout()
  }

  return (
    <UserContext.Provider value={{ users, currentUser, loading, selectUser, logout, createUser, deleteUser, loadUsers }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  return useContext(UserContext)
}
