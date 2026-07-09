import { useEffect, useState } from 'react'
import { listerModeles } from '../api/client'
import ModelCard from '../components/ModelCard'
import ModelDetailDrawer from '../components/ModelDetailDrawer'

export default function Catalogue() {
  const [modeles, setModeles] = useState<any[]>([])
  const [selection, setSelection] = useState<any | null>(null)
  const [filtreFamille, setFiltreFamille] = useState<string>('toutes')

  useEffect(() => {
    listerModeles().then(setModeles)
  }, [])

  const familles = ['toutes', ...Array.from(new Set(modeles.map((m) => m.famille)))]
  const visibles = filtreFamille === 'toutes' ? modeles : modeles.filter((m) => m.famille === filtreFamille)
  const nombreFamilles = familles.length - 1

  return (
    <div className="page">
      <h1>Catalogue de modèles</h1>
      <p className="page-intro">
        {modeles.length > 0
          ? `Le Catalogue réunit ${modeles.length} modèles répartis en ${nombreFamilles} familles d'intelligence artificielle, bien au-delà des seuls agents conversationnels. Chaque fiche s'attache à restituer, pour le modèle qu'elle présente, son secteur d'application, une description pédagogique, un lien vers son installation, des idées d'usage inspirantes et un cas concret à essayer en direct.`
          : 'Chargement du catalogue…'}
      </p>

      <div className="filtres">
        {familles.map((f) => (
          <button
            key={f}
            className={f === filtreFamille ? 'filtre actif' : 'filtre'}
            onClick={() => setFiltreFamille(f)}
          >
            {f.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      <div className="model-grid">
        {visibles.map((m) => (
          <ModelCard key={m.id} modele={m} onOuvrir={setSelection} />
        ))}
      </div>

      {selection && <ModelDetailDrawer modele={selection} onFermer={() => setSelection(null)} />}
    </div>
  )
}
