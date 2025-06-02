import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
// import { MovieService } from '../api/movie-api' // Пока не используется

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']

export const AdminPage = () => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [genres, setGenres] = useState('')
  const [poster, setPoster] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [posterPreview, setPosterPreview] = useState<string>('')
  const navigate = useNavigate()

  const validateForm = () => {
    if (!title.trim()) {
      setError('Введите название фильма')
      return false
    }
    if (!description.trim()) {
      setError('Введите описание фильма')
      return false
    }
    if (!genres.trim()) {
      setError('Введите жанры фильма')
      return false
    }
    if (!poster) {
      setError('Загрузите постер фильма')
      return false
    }

    // Проверяем формат жанров
    const genresArray = genres.trim().split('|')
    if (genresArray.some((genre) => !genre.trim())) {
      setError('Некорректный формат жанров. Используйте разделитель |')
      return false
    }

    // Проверяем размер и формат постера
    if (poster.size === 0) {
      setError('Файл постера пуст')
      return false
    }

    if (poster.size > MAX_FILE_SIZE) {
      setError('Размер файла не должен превышать 5MB')
      return false
    }

    if (!ALLOWED_FILE_TYPES.includes(poster.type)) {
      setError('Поддерживаются только форматы: JPG, JPEG, PNG')
      return false
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (!validateForm()) {
        setIsLoading(false)
        return
      }

      // Создаем фейковый ID для фильма
      const fakeMovieId = Math.floor(Math.random() * 10000) + 1000

      // Сохраняем данные фильма в localStorage
      const fakeMovie = {
        movie_id: fakeMovieId,
        title: title.trim(),
        description: description.trim(),
        release_date: new Date().toISOString().split('T')[0],
        rating: 0,
        poster_url: posterPreview, // Используем превью как URL постера
        video_url: '',
        duration: 120,
        genres: genres.trim().split('|'),
      }

      localStorage.setItem(
        `fake_movie_${fakeMovieId}`,
        JSON.stringify(fakeMovie),
      )

      // Очищаем форму
      setTitle('')
      setDescription('')
      setGenres('')
      setPoster(null)
      setPosterPreview('')

      // Показываем сообщение об успехе
      alert('Фильм успешно добавлен!')

      // Перенаправляем на страницу фильма
      navigate(`/movie/${fakeMovieId}`)
    } catch (error: any) {
      console.error('Ошибка при добавлении фильма:', error)
      setError(error.message || 'Произошла ошибка при добавлении фильма')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePosterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) {
      setPoster(null)
      setPosterPreview('')
      return
    }

    // Проверка размера файла
    if (file.size > MAX_FILE_SIZE) {
      setError('Размер файла не должен превышать 5MB')
      setPoster(null)
      setPosterPreview('')
      return
    }

    // Проверка типа файла
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setError('Поддерживаются только форматы: JPG, JPEG, PNG')
      setPoster(null)
      setPosterPreview('')
      return
    }

    // Создаем превью
    const reader = new FileReader()
    reader.onloadend = () => {
      setPosterPreview(reader.result as string)
    }
    reader.onerror = () => {
      setError('Ошибка при чтении файла')
      setPoster(null)
      setPosterPreview('')
    }
    reader.readAsDataURL(file)

    setPoster(file)
    setError('')
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-3xl font-bold">Добавить новый фильм</h1>

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
        {error && (
          <div className="rounded-lg bg-red-500/10 p-4 text-red-500">
            {error}
          </div>
        )}

        <div>
          <label htmlFor="title" className="mb-2 block text-sm font-medium">
            Название фильма
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-lg bg-gray-800 p-3 text-white"
            placeholder="Введите название фильма"
          />
        </div>

        <div>
          <label
            htmlFor="description"
            className="mb-2 block text-sm font-medium"
          >
            Описание
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="h-32 w-full rounded-lg bg-gray-800 p-3 text-white"
            placeholder="Введите описание фильма"
          />
        </div>

        <div>
          <label htmlFor="genres" className="mb-2 block text-sm font-medium">
            Жанры
          </label>
          <input
            id="genres"
            type="text"
            value={genres}
            onChange={(e) => setGenres(e.target.value)}
            className="w-full rounded-lg bg-gray-800 p-3 text-white"
            placeholder="Введите жанры через |, например: Action|Drama|Thriller"
          />
          <p className="mt-1 text-sm text-gray-400">
            Разделяйте жанры символом |, например: Action|Drama|Thriller
          </p>
        </div>

        <div>
          <label htmlFor="poster" className="mb-2 block text-sm font-medium">
            Постер (JPG, JPEG, PNG, макс. 5MB)
          </label>
          <input
            id="poster"
            type="file"
            onChange={handlePosterChange}
            accept={ALLOWED_FILE_TYPES.join(',')}
            className="w-full rounded-lg bg-gray-800 p-3 text-white"
          />
          {posterPreview && (
            <div className="mt-4">
              <img
                src={posterPreview}
                alt="Предпросмотр постера"
                className="h-48 rounded-lg object-cover"
              />
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full rounded-lg bg-primary p-3 font-medium text-white hover:bg-primary/80 disabled:opacity-50"
        >
          {isLoading ? 'Добавление...' : 'Добавить фильм'}
        </button>
      </form>
    </div>
  )
}
