import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { MovieService } from './api/movie-api'
import { AuthProvider } from './contexts/auth-context'
import { ProtectedRoute } from './components/protected-route'
import { LoginPage } from './pages/login'
import { HomePage } from './pages/home'
import { FilmPage } from './pages/film'
import { AdminPage } from './pages/admin'
import { SearchResultsPage } from './pages/search-results'
import { Header } from './components/header'
import { Footer } from './layouts/footer'
import { AllMoviesPage } from './pages/all-movies'

export const App = () => {
  useEffect(() => {
    MovieService.preloadTopMovies()
  }, [])

  return (
    <BrowserRouter
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <AuthProvider>
        <div className="flex min-h-screen flex-col bg-background text-white">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <div className="flex min-h-screen flex-col">
                    <Header />
                    <main className="flex-1 pt-20">
                      <Routes>
                        <Route index element={<HomePage />} />
                        <Route path="/movies" element={<AllMoviesPage />} />
                        <Route path="/movie/:id" element={<FilmPage />} />
                        <Route path="admin" element={<AdminPage />} />
                        <Route path="search" element={<SearchResultsPage />} />
                      </Routes>
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}
