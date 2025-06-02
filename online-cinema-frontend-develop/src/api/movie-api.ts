import axios from 'axios'
import { Film } from '../interfaces'
import { API_URL, AUTH_URL } from '../config/api.config'

// const POSTER_CACHE_PREFIX = 'movie_poster_'
// const POSTER_CACHE_EXPIRY = 24 * 60 * 60 * 1000 // 24 часа

// Создаем отдельные экземпляры axios для разных сервисов
const mainApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const authApi = axios.create({
  baseURL: AUTH_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем перехватчик запросов для JWT (для обоих API)
const addAuthInterceptor = (apiInstance: any) => {
  apiInstance.interceptors.request.use(
    (config: any) => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error: any) => {
      return Promise.reject(error)
    },
  )

  apiInstance.interceptors.response.use(
    (response: any) => {
      console.log(`API Response [${response.config.url}]:`, {
        status: response.status,
        data: response.data,
        headers: response.headers,
      })
      return response
    },
    (error: any) => {
      console.error(`API Error [${error.config?.url}]:`, {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      })

      if (error.response?.status === 401) {
        console.log('Токен истек или недействителен, выполняется выход...')
        localStorage.removeItem('token')
        window.location.href = '/login'
      }

      return Promise.reject(error)
    },
  )
}

addAuthInterceptor(mainApi)
addAuthInterceptor(authApi)

// Функции для работы с кешем постеров (пока не используется)
// const getPosterFromCache = (url: string): string | null => {
//   try {
//     const cacheKey = POSTER_CACHE_PREFIX + btoa(url)
//     const cached = localStorage.getItem(cacheKey)
//     if (!cached) return null

//     const { data, timestamp } = JSON.parse(cached)
//     if (Date.now() - timestamp > POSTER_CACHE_EXPIRY) {
//       localStorage.removeItem(cacheKey)
//       return null
//     }

//     return data
//   } catch (error) {
//     console.error('Error reading from poster cache:', error)
//     return null
//   }
// }

// Функция кеширования постеров (пока не используется, но может пригодиться)
// const cachePoster = async (url: string): Promise<string> => {
//   try {
//     // Проверяем кеш
//     const cached = getPosterFromCache(url)
//     if (cached) return cached

//     // Для S3 URL используем режим no-cors
//     if (url.includes('s3.timeweb.cloud')) {
//       return url // Возвращаем оригинальный URL для S3
//     }

//     // Для остальных URL пробуем кешировать
//     try {
//       const response = await fetch(url)
//       const blob = await response.blob()
//       const reader = new FileReader()

//       return new Promise((resolve, reject) => {
//         reader.onloadend = () => {
//           try {
//             const base64data = reader.result as string
//             const cacheKey = POSTER_CACHE_PREFIX + btoa(url)
//             localStorage.setItem(
//               cacheKey,
//               JSON.stringify({
//                 data: base64data,
//                 timestamp: Date.now(),
//               }),
//             )
//             resolve(base64data)
//           } catch (error) {
//             console.error('Error caching poster:', error)
//             resolve(url) // Возвращаем оригинальный URL в случае ошибки
//           }
//         }
//         reader.onerror = reject
//         reader.readAsDataURL(blob)
//       })
//     } catch (error) {
//       console.error('Error caching poster:', error)
//       return url // Возвращаем оригинальный URL в случае ошибки
//     }
//   } catch (error) {
//     console.error('Error in cachePoster:', error)
//     return url // Возвращаем оригинальный URL в случае ошибки
//   }
// }

// Функция преобразования данных нового бекенда в формат Film
const convertBackendMovieToFilm = (movie: any): Film => {
  // Если есть poster_url из S3, используем его, иначе генерируем fallback
  let posterUrl = movie.poster_url
  if (!posterUrl) {
    posterUrl = `http://localhost:9000/cinema-files/movies/${movie.id}/poster.svg`
  }

  // Если есть backdrop_url из S3, используем его, иначе генерируем fallback
  let backdropUrl = movie.backdrop_url
  if (!backdropUrl) {
    backdropUrl = `http://localhost:9000/cinema-files/movies/${movie.id}/backdrop.jpg`
  }

  return {
    movie_id: movie.id,
    title: movie.title || '',
    description: movie.description || 'Описание отсутствует',
    release_date: movie.release_date || '',
    rating: movie.rating || 0,
    poster_url: posterUrl,
    backdrop_url: backdropUrl,
    video_url: movie.movie_url || '',
    duration: movie.duration || 0,
    genres: [], // В новом бекенде пока нет жанров в этом формате
  }
}

// Обработка фильмов
async function processMovies(movies: any[]): Promise<Film[]> {
  if (!movies || !Array.isArray(movies)) {
    console.warn('Invalid movies data:', movies)
    return []
  }

  return movies.map(convertBackendMovieToFilm)
}

// Функция для декодирования JWT токена (пока не используется, но может пригодиться)
// const decodeJWT = (token: string): any => {
//   try {
//     const base64Url = token.split('.')[1]
//     const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
//     const jsonPayload = decodeURIComponent(
//       atob(base64)
//         .split('')
//         .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
//         .join(''),
//     )
//     return JSON.parse(jsonPayload)
//   } catch (error) {
//     console.error('❌ Ошибка при декодировании JWT:', error)
//     return null
//   }
// }

interface LoginResponse {
  access_token: string
  user_type?: string
  username?: string
  user_id?: number
}

export const MovieService = {
  // Получение списка фильмов
  async getMovies(page: number = 1, size: number = 50) {
    try {
      const response = await mainApi.get<any[]>('/movies/', {
        params: { page, size },
      })
      const movies = await processMovies(response.data)

      // Для первых 10 фильмов загружаем детали, чтобы получить backdrop_url
      const moviesWithBackdrop = await Promise.all(
        movies.slice(0, 10).map(async (movie) => {
          try {
            const detailedMovie = await this.getMovie(movie.movie_id)
            return detailedMovie || movie
          } catch (error) {
            console.error(
              `Error loading details for movie ${movie.movie_id}:`,
              error,
            )
            return movie
          }
        }),
      )

      // Объединяем фильмы с backdrop'ами и остальные
      return [...moviesWithBackdrop, ...movies.slice(10)]
    } catch (error) {
      console.error('Error fetching movies:', error)
      return []
    }
  },

  // Получение информации о конкретном фильме
  async getMovie(movieId: number): Promise<Film | null> {
    try {
      const response = await mainApi.get<any>(`/movies/${movieId}`)
      if (response.data.message) {
        // Фильм не найден
        return null
      }
      return convertBackendMovieToFilm(response.data)
    } catch (error) {
      console.error('Error fetching movie:', error)
      return null
    }
  },

  // Получение рекомендаций (пока используем обычный список фильмов)
  async getRecommendations(count: number = 10) {
    try {
      console.warn(
        '⚠️ Рекомендации пока не реализованы в новом бекенде, возвращаем топ фильмы',
      )
      return await this.getTopRated()
    } catch (error) {
      console.error('❌ Ошибка при получении рекомендаций:', error)
      return []
    }
  },

  // Получение топ рейтинга
  async getTopRated() {
    try {
      const response = await mainApi.get<any[]>('/movies/')
      const movies = await processMovies(response.data)
      // Сортируем по рейтингу и берем первые 12
      return movies
        .sort((a, b) => (b.rating || 0) - (a.rating || 0))
        .slice(0, 12)
    } catch (error) {
      console.error('❌ Error fetching top rated movies:', error)
      return []
    }
  },

  // Поиск фильмов (пока простой поиск по названию)
  async searchMovies(query: string) {
    try {
      console.log('Searching for:', query)

      if (!query || typeof query !== 'string') {
        console.warn('Invalid search query:', query)
        return []
      }

      const trimmedQuery = query.trim().toLowerCase()
      if (!trimmedQuery) {
        return []
      }

      // Получаем все фильмы и фильтруем на клиенте

      const response = await mainApi.get<any[]>('/movies/')
      const allMovies = await processMovies(response.data)

      // Простой поиск по названию
      const filteredMovies = allMovies.filter((movie) =>
        movie.title.toLowerCase().includes(trimmedQuery),
      )

      console.log('Search results:', filteredMovies)
      return filteredMovies
    } catch (error) {
      console.error('❌ Error searching movies:', error)
      return []
    }
  },

  // Получение похожих фильмов
  async getSimilarMovies(movieId: number) {
    try {
      const response = await mainApi.get<any[]>(`/movies/${movieId}/similar`)
      const movies = await processMovies(response.data)
      return movies.slice(0, 12) // Берем первые 12 похожих фильмов
    } catch (error) {
      console.error('❌ Error fetching similar movies:', error)
      return []
    }
  },

  // Получение URL для стриминга
  getStreamUrl(movieId: string): string {
    return `${API_URL}/streaming/${movieId}`
  },

  // Прелоадинг топ фильмов
  async preloadTopMovies() {
    try {
      const response = await mainApi.get<any[]>('/movies/')
      // Запускаем прелоадинг в фоне
      processMovies(response.data).catch(console.error)
    } catch (error) {
      console.error('❌ Error preloading top movies:', error)
    }
  },

  // Аутентификация пользователя
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await authApi.post('/auth/login', {
      username,
      password,
    })
    return response.data
  },

  // Добавление нового фильма (пока не реализовано)
  async addMovie(formData: FormData) {
    try {
      console.warn('⚠️ Добавление фильмов пока не реализовано в новом бекенде')
      throw new Error('Функция добавления фильмов пока не доступна')
    } catch (error: any) {
      console.error('❌ Error adding movie:', error)
      throw error
    }
  },

  // Поиск фильмов через Elasticsearch (пока не реализовано)
  async elasticSearch(query: string, limit: number = 10) {
    try {
      console.warn('⚠️ Elasticsearch поиск пока не реализован в новом бекенде')
      return await this.searchMovies(query)
    } catch (error) {
      console.error('❌ Error searching movies with Elasticsearch:', error)
      return []
    }
  },

  // Получение всех фильмов с пагинацией
  async getAllMovies(page: number = 1, size: number = 24) {
    try {
      const response = await mainApi.get<any[]>('/movies/', {
        params: { page, size },
      })

      if (!response.data) {
        console.warn('Empty response data')
        return { movies: [], total: 0 }
      }

      const movies = await processMovies(response.data)

      return {
        movies,
        total: movies.length,
      }
    } catch (error) {
      console.error('❌ Error fetching all movies:', error)
      return { movies: [], total: 0 }
    }
  },
}
