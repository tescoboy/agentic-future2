import { Routes, Route } from 'react-router-dom'
import { Container } from 'react-bootstrap'
import NavigationBar from './components/Navbar'
import Footer from './components/Footer'
import Discovery from './pages/Discovery'
import Activation from './pages/Activation'
import './App.css'

function App() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <NavigationBar />
      <main className="flex-grow-1">
        <Container className="py-4">
          <Routes>
            <Route path="/" element={<Discovery />} />
            <Route path="/activation" element={<Activation />} />
          </Routes>
        </Container>
      </main>
      <Footer />
    </div>
  )
}

export default App
