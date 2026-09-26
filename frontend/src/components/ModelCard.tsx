import { useState } from 'react'
import { basculerFavori, estFavori } from '../stockageLocal'

type ModelCardProps = {
  modele: any
  onOuvrir: (modele: any) => void
}

// Répartit chaque famille sur l'une des 5 teintes déjà définies pour le Constructeur
// (--cat-source/traitement/stockage/modele/outil) — un hachage simple plutôt qu'une table de
// correspondance à tenir à jour à chaque nouvelle famille ajoutée au catalogue.
const TEINTES_FAMILLE = ['source', 'traitement', 'stockage', 'modele', 'outil']

function teinteFamille(famille: string): string {
  let h = 0
  for (let i = 0; i < famille.length; i++) h = (h * 31 + famille.charCodeAt(i)) >>> 0
  return TEINTES_FAMILLE[h % TEINTES_FAMILLE.length]
}

export default function ModelCard({ modele, onOuvrir }: ModelCardProps) {
  const [favori, setFavori] = useState(() => estFavori('modele', modele.id))
  const teinte = teinteFamille(modele.famille)

  return (
    <button className={`model-card model-card-teinte-${teinte}`} onClick={() => onOuvrir(modele)}>
      <div className="model-card-tete">
        <div className={`model-card-famille model-card-famille-${teinte}`}>{modele.famille.replace(/_/g, ' ')}</div>
        <span
          className={favori ? 'favori-etoile actif' : 'favori-etoile'}
          role="button"
          aria-label={favori ? 'Retirer des favoris' : 'Ajouter aux favoris'}
          onClick={(e) => {
            e.stopPropagation()
            setFavori(basculerFavori('modele', modele.id))
          }}
        >
          {favori ? '★' : '☆'}
        </span>
      </div>
      <h3>{modele.nom}</h3>
      <p className="model-card-secteur">{modele.secteur}</p>
      <p className="model-card-taille">{modele.taille}</p>
    </button>
  )
}
