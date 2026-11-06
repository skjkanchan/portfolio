import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ExperienceDetailPage from './pages/ExperienceDetailPage'
import ExperienceListPage from './pages/ExperienceListPage'
import HomePage from './pages/HomePage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="experiences" element={<ExperienceListPage />} />
          <Route path="experiences/:id" element={<ExperienceDetailPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
