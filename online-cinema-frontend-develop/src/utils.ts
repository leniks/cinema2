import { Film } from './interfaces'

export const mergeClassName = (...classNames: string[]) => {
  return classNames.filter((c) => !!c).join(' ')
}

export const formatResult = (obj: any): Film => {
  return {
    movie_id: obj.id || obj.movie_id,
    title: obj.title || obj.name || '',
    description: obj.overview || obj.description || '',
    release_date: obj.release_date || '',
    rating: obj.rating || 0,
    poster_url:
      obj.poster_url ||
      `https://image.tmdb.org/t/p/w500${obj.poster_path}` ||
      '',
    backdrop_url:
      obj.backdrop_url ||
      obj.trailer_url ||
      `https://image.tmdb.org/t/p/original${obj.backdrop_path}` ||
      null,
    video_url: obj.video_url || '',
    duration: obj.duration || 0,
    genres: obj.genres?.split('|') || [],
  }
}

export const isFilm = (film: unknown): film is Film => {
  return film !== null && typeof film === 'object' && 'movie_id' in film
}

export const tmdbImageSrc = (path: string) => {
  if (!path) return ''

  return `https://image.tmdb.org/t/p/original/${path}`
}

export const mergeFilms = (movies: Film[], tvs: Film[], limit = 6) => {
  const arrs: Film[] = []

  for (let i = 0; i < limit; i++) {
    let film: unknown

    if (i % 2 === 1) {
      if (tvs[i - 1]) {
        film = tvs[i - 1]
      }
    } else {
      if (movies[i - 1]) {
        film = tvs[i - 1]
      }
    }

    if (isFilm(film)) arrs.push(film)
  }

  return arrs
}

export const youtubeThumbnail = (key: string) => {
  return `https://img.youtube.com/vi/${key}/mqdefault.jpg`
}

export const formatDate = (val: string) => {
  const d = new Date(val)

  return d.getDate() + '/' + (d.getMonth() + 1) + '/' + d.getFullYear()
}
