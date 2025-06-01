import { MediaType } from './media.types'

export interface MovieBase {
  id: number
  title: string
  title_ru?: string
  description: string
  description_ru?: string
  posterPath: string | null
}

export interface Movie extends MovieBase {
  mediaType: MediaType
  rating?: number
  releaseDate?: string
  genres: Genre[]
}

export interface Genre {
  id: number
  name: string
  name_ru?: string
}
