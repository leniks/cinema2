import { ReactNode } from 'react'

export interface CustomComponentProps {
  children?: ReactNode
  className?: string
}

export interface Film {
  movie_id: number
  title: string
  description: string
  release_date: string
  rating: number
  poster_url: string | null
  backdrop_url: string | null
  video_url: string
  duration: number
  genres: string[]
}

// Интерфейс для данных нового бекенда
export interface BackendMovie {
  id: number
  title: string
  description: string
  release_date: string
  rating: number
  poster_url: string | null
  backdrop_url: string | null
  movie_url: string
  duration: number
  created_at: string
  updated_at: string
}

export interface SearchResponse {
  films: Film[]
  totalPages: number
}

export interface User {
  id: number
  name: string
  email: string
  role?: string
  login?: string
}

export interface MovieCardProps {
  movie: Film
  onClick?: () => void
}

export interface SliderProps {
  title: string
  movies: Film[]
  loading?: boolean
}

// Интерфейс для аутентификации
export interface AuthResponse {
  access_token: string
  user_type?: string
  username?: string
  user_id?: number
}
