import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/auth-context'
import { Container } from '../components/container'
import { SearchResult } from '../components/search-result'

export const Header = () => {
  const [keyword, setKeyword] = useState('')
  const [showSearchResult, setShowSearchResult] = useState(false)
  const navigate = useNavigate()
  const { logout } = useAuth()
  const username = localStorage.getItem('username')
  const userType = localStorage.getItem('user_type')

  const handleSearch = useCallback(() => {
    if (keyword) {
      navigate(`/search?q=${keyword}`)
      setShowSearchResult(false)
    }
  }, [keyword, navigate])

  const handleWindowClick = useCallback((e: MouseEvent) => {
    if (!(e.target as HTMLElement).closest('.search-container')) {
      setShowSearchResult(false)
    }
  }, [])

  const handleLogout = () => {
    console.log('🚪 Выполняется выход из системы')
    logout()
    navigate('/login')
  }

  useEffect(() => {
    window.addEventListener('click', handleWindowClick)
    return () => window.removeEventListener('click', handleWindowClick)
  }, [handleWindowClick])

  return (
    <header className="fixed left-0 right-0 top-0 z-50 bg-header">
      <Container>
        <div className="flex items-center justify-between gap-8">
          <h1
            className="text-2xl font-bold text-primary cursor-pointer"
            onClick={() => navigate('/')}
          >
            Movie App
          </h1>

          <div className="search-container relative flex-1 max-w-md">
            <input
              type="text"
              className="w-full rounded-lg bg-body px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Поиск фильмов..."
              value={keyword}
              onChange={(e) => {
                setKeyword(e.target.value)
                setShowSearchResult(true)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSearch()
                }
              }}
            />
            {showSearchResult && keyword && (
              <SearchResult keyword={keyword} goToSearchPage={handleSearch} />
            )}
          </div>

          <div className="flex items-center gap-4">
            {username && (
              <div className="flex flex-col items-end">
                <span className="text-sm text-gray-400">{username}</span>
                <span className="text-xs text-gray-500">{userType}</span>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="rounded-md bg-primary/20 px-3 py-1 text-sm text-white hover:bg-primary/30 transition-colors"
            >
              Выйти
            </button>
          </div>
        </div>
      </Container>
    </header>
  )
}
