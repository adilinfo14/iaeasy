import { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import { enregistrerVisite } from './api/client'
import Accueil from './pages/Accueil'
import Catalogue from './pages/Catalogue'
import Constructeur from './pages/Constructeur'
import Entrainement from './pages/Entrainement'
import Glossaire from './pages/Glossaire'
import Parcours from './pages/Parcours'
import StrategieTest from './pages/StrategieTest'

function useTheme() {
  const [theme, setTheme] = useState<'sombre' | 'doux'>(
    () => (localStorage.getItem('iaeasy-theme') as 'sombre' | 'doux') || 'doux',
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

  useEffect(() => {
    enregistrerVisite()
  }, [])

  return (
    <div className="app">
      <header className="topnav">
        <NavLink to="/" className="brand">
          ☕ iaeasy
        </NavLink>
        <nav>
          <NavLink to="/catalogue">Catalogue</NavLink>
          <NavLink to="/entrainement">Entraînement</NavLink>
          <NavLink to="/parcours">Parcours</NavLink>
          <NavLink to="/constructeur">Constructeur</NavLink>
          <NavLink to="/strategie-test">Stratégie de tests</NavLink>
          <NavLink to="/glossaire">Glossaire</NavLink>
        </nav>
        <button
          className="theme-toggle"
          onClick={() => setTheme(theme === 'doux' ? 'sombre' : 'doux')}
          title={theme === 'doux' ? 'Passer en mode sombre' : 'Passer en mode doux'}
          aria-label="Changer d'ambiance"
        >
          {theme === 'doux' ? '🌙' : '☕'}
        </button>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Accueil />} />
          <Route path="/catalogue" element={<Catalogue />} />
          <Route path="/entrainement" element={<Entrainement />} />
          <Route path="/parcours" element={<Parcours />} />
          <Route path="/constructeur" element={<Constructeur />} />
          <Route path="/strategie-test" element={<StrategieTest />} />
          <Route path="/glossaire" element={<Glossaire />} />
        </Routes>
      </main>
    </div>
  )
}
