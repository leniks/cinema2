// Конфигурация для нового бекенда
export const API_URL =
  (process as any).env.REACT_APP_API_URL || 'http://localhost:8001'
export const AUTH_URL =
  (process as any).env.REACT_APP_AUTH_URL || 'http://localhost:8000'
export const MINIO_URL =
  (process as any).env.REACT_APP_MINIO_URL || 'http://localhost:9000'
export const MINIO_BUCKET =
  (process as any).env.REACT_APP_MINIO_BUCKET || 'cinema-files'

// Прокси для постеров (избегаем CORS проблемы)
export const POSTER_PROXY_URL = `${API_URL}/proxy/poster`

export const API_ENDPOINTS = {
  // Movies (Main Service - port 8001)
  MOVIES: '/movies',
  MOVIES_BY_ID: '/movies',

  // Auth (Auth Service - port 8000)
  AUTH_LOGIN: '/auth/login',
  AUTH_REGISTER: '/auth/register',
  AUTH_LOGOUT: '/auth/logout',
  AUTH_ME: '/auth/me',

  // Files (Main Service - port 8001)
  FILES_UPLOAD: '/files/upload',
  FILES_DELETE: '/files/delete',
} as const

export const DEFAULT_PAGINATION = {
  page: 1,
  size: 50,
} as const

// Функция для получения URL постера через прокси
export const getPosterUrl = (movieId: number): string => {
  return `${POSTER_PROXY_URL}/${movieId}`
}

// Функция для получения прямого URL файла из MinIO
export const getMinioFileUrl = (filePath: string): string => {
  return `${MINIO_URL}/${MINIO_BUCKET}/${filePath}`
}
