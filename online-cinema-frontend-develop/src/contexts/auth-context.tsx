import { createContext, useContext, ReactNode, useState } from 'react'

interface User {
  id: number
  name: string
  email: string
  role: string
  login: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (token: string, userData?: any) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
})

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const login = (token: string, userData?: any) => {
    // Декодируем JWT и получаем информацию о пользователе
    const decodedToken = decodeJWT(token)
    if (decodedToken || userData) {
      setUser({
        id: userData?.user_id || decodedToken?.sub || decodedToken?.id,
        name: userData?.name || decodedToken?.name || userData?.username || '',
        email: userData?.email || decodedToken?.email || '',
        role:
          userData?.user_type || userData?.role || decodedToken?.role || 'user',
        login:
          userData?.username ||
          decodedToken?.login ||
          decodedToken?.username ||
          '',
      })
      setIsAuthenticated(true)
      localStorage.setItem('token', token)
      // Сохраняем дополнительные данные пользователя
      if (userData?.user_type) {
        localStorage.setItem('user_type', userData.user_type)
      }
      if (userData?.username) {
        localStorage.setItem('username', userData.username)
      }
      if (userData?.user_id) {
        localStorage.setItem('user_id', userData.user_id.toString())
      }
    }
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('token')
    localStorage.removeItem('user_type')
    localStorage.removeItem('username')
    localStorage.removeItem('user_id')
  }

  // При инициализации проверяем сохраненные данные
  useState(() => {
    const token = localStorage.getItem('token')
    const savedUserType = localStorage.getItem('user_type')
    const savedUsername = localStorage.getItem('username')
    const savedUserId = localStorage.getItem('user_id')

    if (token) {
      const decodedToken = decodeJWT(token)
      if (decodedToken) {
        setUser({
          id: savedUserId
            ? parseInt(savedUserId)
            : decodedToken.sub || decodedToken.id,
          name: savedUsername || decodedToken.name || '',
          email: decodedToken.email || '',
          role: savedUserType || decodedToken.role || 'user',
          login:
            savedUsername || decodedToken.login || decodedToken.username || '',
        })
        setIsAuthenticated(true)
      }
    }
  })

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

// Вспомогательная функция для декодирования JWT
const decodeJWT = (token: string) => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join(''),
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Error decoding JWT:', error)
    return null
  }
}
