import { useState } from 'react'
import { effacerParcours, lireParcours } from '../stockageLocal'

const ICONE_TYPE: Record<string, string> = { brique: '🧱', modele: '🗂️' }

export default function MonParcours() {
  const [entrees, setEntrees] = useState(() => lireParcours())

  function formatDate(horodatage: number) {
    return new Date(horodatage).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' })
  }

  return (
    <div className="page page-mon-parcours">
      <h1>🕓 Mon parcours</h1>
      <p className="page-intro">
        L'historique des briques et modèles que vous avez essayés sur cet appareil — stocké
        uniquement dans ce navigateur, jamais envoyé au serveur, pour retrouver rapidement ce
        qui a déjà été exploré sans avoir à s'en souvenir soi-même.
      </p>

      {entrees.length === 0 && (
        <p className="texte-muted">
          Rien pour l'instant — essayez une brique dans le Parcours ou un modèle du Catalogue pour
          la voir apparaître ici.
        </p>
      )}

      {entrees.length > 0 && (
        <>
          <ul className="parcours-perso-liste">
            {entrees.map((e, i) => (
              <li key={i} className="parcours-perso-item">
                <span className="parcours-perso-icone">{ICONE_TYPE[e.type] || '•'}</span>
                <div className="parcours-perso-corps">
                  <div className="parcours-perso-ligne1">
                    <strong>{e.titre}</strong>
                    <span className="texte-muted">{formatDate(e.horodatage)}</span>
                  </div>
                  {e.detail && <span className="texte-muted">{e.detail}</span>}
                </div>
              </li>
            ))}
          </ul>
          <button
            className="parcours-perso-effacer"
            onClick={() => {
              effacerParcours()
              setEntrees([])
            }}
          >
            Effacer l'historique
          </button>
        </>
      )}
    </div>
  )
}
