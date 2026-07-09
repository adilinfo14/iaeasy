import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listerMetiers } from '../api/client'

export default function Metiers() {
  const [metiers, setMetiers] = useState<any[]>([])
  const [ouvert, setOuvert] = useState<string | null>(null)
  const [secteurActif, setSecteurActif] = useState('tous')

  useEffect(() => {
    listerMetiers().then(setMetiers)
  }, [])

  const secteurs = useMemo(() => ['tous', ...Array.from(new Set(metiers.map((m) => m.secteur)))], [metiers])
  const visibles = secteurActif === 'tous' ? metiers : metiers.filter((m) => m.secteur === secteurActif)
  const totalCasUsage = useMemo(() => metiers.reduce((n, m) => n + m.cas_usage.length, 0), [metiers])

  return (
    <div className="page page-metiers">
      <h1>🧭 L'IA dans mon métier</h1>
      <p className="page-intro">
        Sans jargon ni promesse abstraite, cette rubrique réunit {totalCasUsage || 48} cas d'usage
        concrets, déjà présents sur le site et classés par secteur puis par métier, chacun assorti
        d'un lien permettant de l'essayer directement.
      </p>

      <div className="exemples-categories">
        {secteurs.map((s) => (
          <button
            key={s}
            className={s === secteurActif ? 'chip actif' : 'chip'}
            onClick={() => setSecteurActif(s)}
          >
            {s === 'tous' ? 'Tous les secteurs' : s}
          </button>
        ))}
      </div>

      <div className="templates-liste">
        {visibles.map((m) => {
          const estOuvert = ouvert === m.id
          return (
            <div key={m.id} className={estOuvert ? 'template-carte ouverte' : 'template-carte'}>
              <button className="template-entete" onClick={() => setOuvert(estOuvert ? null : m.id)}>
                <strong>{m.icone} {m.titre}</strong>
                <span>{m.description}</span>
              </button>
              {estOuvert && (
                <div className="template-details">
                  {m.cas_usage.map((c: any, i: number) => (
                    <div key={i} className="metier-cas">
                      <h5>{c.titre}</h5>
                      <p>{c.description}</p>
                      <Link to={c.page} className="metier-lien">
                        {c.texte_lien}
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
