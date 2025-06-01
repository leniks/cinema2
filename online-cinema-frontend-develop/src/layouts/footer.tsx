import { Container } from '../components/container'

export const Footer = () => {
  return (
    <footer className="mt-auto bg-header py-6">
      <Container>
        <div className="flex flex-col items-center gap-4">
          <p className="text-sm text-gray-400">
            © 2024 Movie App. Все права защищены.
          </p>
        </div>
      </Container>
    </footer>
  )
}
