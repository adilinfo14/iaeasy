import { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import Accueil from './pages/Accueil'
import Catalogue from './pages/Catalogue'
import Constructeur from './pages/Constructeur'
import Entrainement from './pages/Entrainement'
import Parcours from './pages/Parcours'

function useTheme() {
  const [theme, setTheme] = useState<'sombre' | 'doux'>(
    () => (localStorage.getItem('iaeasy-theme') as 'sombre' | 'doux') || 'sombre',
  )

  useEffect(() => {
    if (theme === 'doux') {
      document.documentElement.setAttribute('data-theme', 'doux')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
    localStorage.setItem('iaeasy-theme', theme)
  }, [theme])

  return [theme, setTheme] as const
}

export default function App() {
  const [theme, setTheme] = useTheme()

  return (
    <div className="app">
      <header className="topnav">
        <NavLink to="/" className="brand">
          iaeasy
        </NavLink>
        <nav>
          <NavLink to="/catalogue">Catalogue</NavLink>
          <NavLink to="/entrainement">Entraînement</NavLink>
          <NavLink to="/parcours">Parcours</NavLink>
          <NavLink to="/constructeur">Constructeur</NavLink>
        </nav>
        <button
          className="theme-toggle"
          onClick={() => setTheme(theme === 'doux' ? 'sombre' : 'doux')}
          title="Changer d'ambiance"
        >
          {theme === 'doux' ? '🌙 Mode sombre' : '☕ Mode doux'}
        </button>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Accueil />} />
          <Route path="/catalogue" element={<Catalogue />} />
          <Route path="/entrainement" element={<Entrainement />} />
          <Route path="/parcours" element={<Parcours />} />
          <Route path="/constructeur" element={<Constructeur />} />
        </Routes>
      </main>
    </div>
  )
}
