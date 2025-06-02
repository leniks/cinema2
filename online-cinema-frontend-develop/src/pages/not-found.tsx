import { useNavigate } from 'react-router-dom'

import { Container } from '../components/container'

export const NotFoundPage = () => {
  const navigate = useNavigate()

  return (
    <Container>
      <div className="flex h-[400px] flex-col items-center justify-center gap-4">
        <h1 className="text-4xl font-bold">404</h1>
        <p className="text-xl text-gray-400">Страница не найдена</p>
        <button
          onClick={() => navigate('/')}
          className="rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary/80"
        >
          Вернуться на главную
        </button>
      </div>
    </Container>
  )
}
