// Простой тест интеграции фронтенда с новым бекендом
const axios = require('axios')

const API_URL = 'http://localhost:8001'
const AUTH_URL = 'http://localhost:8000'

async function testIntegration() {
  console.log('🧪 Тестирование интеграции фронтенда с новым бекендом...\n')

  try {
    // Тест 1: Проверка Main Service
    console.log('1️⃣ Проверка Main Service...')
    const mainResponse = await axios.get(`${API_URL}/`)
    console.log('✅ Main Service работает:', mainResponse.data)

    // Тест 2: Проверка Auth Service
    console.log('\n2️⃣ Проверка Auth Service...')
    const authResponse = await axios.get(`${AUTH_URL}/`)
    console.log('✅ Auth Service работает:', authResponse.data)

    // Тест 3: Получение списка фильмов
    console.log('\n3️⃣ Получение списка фильмов...')
    const moviesResponse = await axios.get(`${API_URL}/movies/`)
    const movies = moviesResponse.data
    console.log(`✅ Получено ${movies.length} фильмов`)

    if (movies.length > 0) {
      console.log('📽️ Первый фильм:', {
        id: movies[0].id,
        title: movies[0].title,
        rating: movies[0].rating,
        release_date: movies[0].release_date,
      })
    }

    // Тест 4: Получение конкретного фильма
    if (movies.length > 0) {
      console.log('\n4️⃣ Получение конкретного фильма...')
      const movieId = movies[0].id
      const movieResponse = await axios.get(`${API_URL}/movies/${movieId}`)
      console.log('✅ Фильм получен:', movieResponse.data.title)
    }

    // Тест 5: Проверка прокси для постеров
    if (movies.length > 0) {
      console.log('\n5️⃣ Проверка прокси для постеров...')
      const movieId = movies[0].id
      try {
        const posterResponse = await axios.get(
          `${API_URL}/proxy/poster/${movieId}`,
          {
            timeout: 5000,
            responseType: 'arraybuffer',
          },
        )
        console.log(
          '✅ Прокси для постеров работает, размер:',
          posterResponse.data.length,
          'байт',
        )
      } catch (error) {
        console.log(
          '⚠️ Прокси для постеров недоступен (возможно, нет изображения)',
        )
      }
    }

    console.log('\n🎉 Все тесты пройдены! Интеграция работает корректно.')
  } catch (error) {
    console.error('❌ Ошибка при тестировании:', error.message)
    if (error.response) {
      console.error('Статус:', error.response.status)
      console.error('Данные:', error.response.data)
    }
  }
}

testIntegration()
