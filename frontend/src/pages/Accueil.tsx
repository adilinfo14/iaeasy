import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { lireProgression, lireVisiteurs, listerBriques } from '../api/client'

const MODULES = [
  {
    to: '/catalogue',
    icone: '🗂️',
    titre: 'Catalogue',
    pitch: "19 modèles, 15 familles d'IA différentes — pas seulement des chatbots.",
  },
  {
    to: '/parcours',
    icone: '🧭',
    titre: 'Parcours',
    pitch: 'Construis ton assistant brique par brique, avec une vraie mise en situation.',
    recommande: true,
  },
  {
    to: '/entrainement',
    icone: '📉',
    titre: 'Entraînement',
    pitch: 'Regarde une vraie courbe de loss descendre, sur 3 cas d\'usage concrets.',
  },
  {
    to: '/constructeur',
    icone: '🏗️',
    titre: 'Constructeur',
    pitch: "Mode architecte : assemble un vrai RAG, un agent, un pipeline multi-agent.",
  },
  {
    to: '/strategie-test',
    icone: '🧪',
    titre: 'Stratégie de tests',
    pitch: "Comment vérifier sérieusement chaque famille de modèle — cahiers de test à réutiliser.",
  },
]

export default function Accueil() {
  const [debloquees, setDebloquees] = useState(0)
  const [total, setTotal] = useState(5)
  const [visiteurs, setVisiteurs] = useState<number | null>(null)

  useEffect(() => {
    listerBriques().then((b) => setTotal(b.length))
    lireProgression().then((p) => setDebloquees(p.debloquees.length))
    lireVisiteurs().then((v) => setVisiteurs(v.total_visiteurs_uniques))
  }, [])

  return (
    <div className="page page-accueil">
      <h1>☕ iaeasy — apprends l'IA en la construisant</h1>
      <p className="page-intro">
        Une plateforme 100% souveraine (auto-hébergée, modèles open-source) pour comprendre l'IA
        en la manipulant réellement : essayer des modèles, entraîner un algorithme sous tes yeux,
        et construire ta propre architecture d'agent.
      </p>

      <div className="progression-globale">
        <span>🔓 {debloquees}/{total} briques débloquées dans le Parcours</span>
        {visiteurs != null && <span> · 👀 {visiteurs} visiteur{visiteurs > 1 ? 's' : ''} unique{visiteurs > 1 ? 's' : ''}</span>}
      </div>

      <div className="modules-grille">
        {MODULES.map((m) => (
          <Link key={m.to} to={m.to} className="module-carte">
            {m.recommande && <span className="module-badge">Commence ici</span>}
            <div className="module-icone">{m.icone}</div>
            <h3>{m.titre}</h3>
            <p>{m.pitch}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
