import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/auth-context'

interface Props {
  children: React.ReactNode
}

export const ProtectedRoute = ({ children }: Props) => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    console.log('🔒 Доступ запрещен: перенаправление на страницу входа')
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
