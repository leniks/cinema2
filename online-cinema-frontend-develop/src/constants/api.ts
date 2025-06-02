export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL,
  TIMEOUT: 5000,
  ENDPOINTS: {
    MOVIES: '/movies',
    GENRES: '/genres',
    SEARCH: '/search',
    RECOMMENDATIONS: '/recommendations',
  },
} as const
