import { useEffect, useState } from 'react'
import { NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { enregistrerVisite } from './api/client'
import AssistantAide from './components/AssistantAide'
import Accueil from './pages/Accueil'
import Avis from './pages/Avis'
import Catalogue from './pages/Catalogue'
import Constructeur from './pages/Constructeur'
import Entrainement from './pages/Entrainement'
import Glossaire from './pages/Glossaire'
import Metiers from './pages/Metiers'
import Parcours from './pages/Parcours'
import Simulateur from './pages/Simulateur'
import StrategieTest from './pages/StrategieTest'
import Videos from './pages/Videos'

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
  const [menuOuvert, setMenuOuvert] = useState(false)
  const location = useLocation()

  useEffect(() => {
    enregistrerVisite()
  }, [])

  // Referme le menu mobile dès qu'on navigue vers une nouvelle page (clic sur un lien,
  // bouton retour du navigateur...) plutôt que d'ajouter un onClick sur chaque NavLink.
  useEffect(() => {
    setMenuOuvert(false)
  }, [location.pathname])

  return (
    <div className="app">
      <header className="topnav">
        <NavLink to="/" className="brand">
          ☕ iaeasy
        </NavLink>
        <button
          className="menu-toggle"
          onClick={() => setMenuOuvert((v) => !v)}
          aria-label={menuOuvert ? 'Fermer le menu' : 'Ouvrir le menu'}
          aria-expanded={menuOuvert}
        >
          {menuOuvert ? '✕' : '☰'}
        </button>
        <nav className={menuOuvert ? 'ouvert' : ''}>
          <NavLink to="/catalogue">Catalogue</NavLink>
          <NavLink to="/entrainement">Entraînement</NavLink>
          <NavLink to="/parcours">Parcours</NavLink>
          <NavLink to="/constructeur">Constructeur</NavLink>
          <NavLink to="/strategie-test">Stratégie de tests</NavLink>
          <NavLink to="/glossaire">Glossaire</NavLink>
          <NavLink to="/metiers">Mon métier</NavLink>
          <NavLink to="/simulateur">Simulateur</NavLink>
          <NavLink to="/videos">Vidéos</NavLink>
          <NavLink to="/avis">Avis</NavLink>
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
          <Route path="/metiers" element={<Metiers />} />
          <Route path="/simulateur" element={<Simulateur />} />
          <Route path="/videos" element={<Videos />} />
          <Route path="/avis" element={<Avis />} />
        </Routes>
      </main>
      <AssistantAide />
    </div>
  )
}
