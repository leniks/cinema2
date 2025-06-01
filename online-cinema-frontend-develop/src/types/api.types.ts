// Base types
export interface Movie {
  movie_id: number
  title: string
  title_ru: string
  description: string
  description_ru: string
  poster_url: string | null
  release_date?: string
  rating?: number
  genres?: number[]
}

export interface Genre {
  id: number
  name: string
  name_ru: string
}

export interface PaginationParams {
  page: number
  size: number
}

export interface LoginCredentials {
  username: string
  hashed_password: string
}

export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

// Request types
export interface MovieSearchRequest {
  movie: string
  language?: 'ru' | 'en'
}

export interface MovieInterestingRequest {
  movie_id: number
}

// Response types
export interface MoviesResponse extends ApiResponse<Movie[]> {}
export interface TopRatedMoviesResponse extends ApiResponse<Movie[]> {}
export interface SearchMoviesResponse extends ApiResponse<Movie[]> {}
export interface LoginResponse
  extends ApiResponse<{
    token?: string
    user_id?: number
  }> {}
