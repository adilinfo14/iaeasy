import { useEffect, useRef, useState } from 'react'
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
import Securite from './pages/Securite'
import Simulateur from './pages/Simulateur'
import StrategieTest from './pages/StrategieTest'
import Videos from './pages/Videos'

const GROUPES_MENU = [
  {
    id: 'pratiquer',
    label: 'Pratiquer',
    liens: [
      { to: '/catalogue', label: 'Catalogue' },
      { to: '/entrainement', label: 'Entraînement' },
      { to: '/parcours', label: 'Parcours' },
      { to: '/constructeur', label: 'Constructeur' },
      { to: '/simulateur', label: 'Simulateur' },
    ],
  },
  {
    id: 'ressources',
    label: 'Ressources',
    liens: [
      { to: '/strategie-test', label: 'Stratégie de tests' },
      { to: '/securite', label: 'Sécurité' },
      { to: '/glossaire', label: 'Glossaire' },
      { to: '/metiers', label: 'Mon métier' },
      { to: '/videos', label: 'Vidéos' },
    ],
  },
]

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
  const [dropdownOuvert, setDropdownOuvert] = useState<string | null>(null)
  const location = useLocation()
  const navRef = useRef<HTMLElement>(null)

  useEffect(() => {
    enregistrerVisite()
  }, [])

  // Referme le menu mobile et les sous-menus dès qu'on navigue vers une nouvelle page (clic
  // sur un lien, bouton retour du navigateur...) plutôt que d'ajouter un onClick sur chaque lien.
  useEffect(() => {
    setMenuOuvert(false)
    setDropdownOuvert(null)
  }, [location.pathname])

  useEffect(() => {
    if (!dropdownOuvert) return
    function surClicExterieur(e: MouseEvent) {
      if (navRef.current && !navRef.current.contains(e.target as Node)) setDropdownOuvert(null)
    }
    function surEchap(e: KeyboardEvent) {
      if (e.key === 'Escape') setDropdownOuvert(null)
    }
    document.addEventListener('mousedown', surClicExterieur)
    window.addEventListener('keydown', surEchap)
    return () => {
      document.removeEventListener('mousedown', surClicExterieur)
      window.removeEventListener('keydown', surEchap)
    }
  }, [dropdownOuvert])

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
        <nav className={menuOuvert ? 'ouvert' : ''} ref={navRef}>
          {GROUPES_MENU.map((groupe) => {
            const actif = groupe.liens.some((l) => l.to === location.pathname)
            return (
              <div key={groupe.id} className="nav-dropdown">
                <button
                  type="button"
                  className={actif ? 'nav-dropdown-trigger actif' : 'nav-dropdown-trigger'}
                  onClick={() => setDropdownOuvert(dropdownOuvert === groupe.id ? null : groupe.id)}
                  aria-expanded={dropdownOuvert === groupe.id}
                >
                  {groupe.label} <span className="nav-dropdown-caret">▾</span>
                </button>
                <div className={dropdownOuvert === groupe.id ? 'nav-dropdown-panel ouvert' : 'nav-dropdown-panel'}>
                  {groupe.liens.map((l) => (
                    <NavLink key={l.to} to={l.to}>
                      {l.label}
                    </NavLink>
                  ))}
                </div>
              </div>
            )
          })}
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
          <Route path="/securite" element={<Securite />} />
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
