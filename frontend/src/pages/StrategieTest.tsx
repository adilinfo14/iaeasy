import { useEffect, useState } from 'react'
import { listerStrategiesTest } from '../api/client'

export default function StrategieTest() {
  const [strategies, setStrategies] = useState<any[]>([])
  const [ouverte, setOuverte] = useState<string | null>(null)

  useEffect(() => {
    listerStrategiesTest().then(setStrategies)
  }, [])

  return (
    <div className="page page-strategie-test">
      <h1>☕ Stratégie de tests par famille de modèle</h1>
      <p className="page-intro">
        Un modèle qui répond avec assurance n'est pas forcément un modèle qui répond juste. Pour
        chacune des {strategies.length || 15} familles du catalogue, voici comment la vérifier
        sérieusement : les catégories de test à couvrir, les métriques à suivre, le piège le plus
        fréquent, et un cahier de test concret dont vous pouvez vous inspirer directement.
      </p>

      <div className="templates-liste">
        {strategies.map((s) => {
          const ouvert = ouverte === s.famille
          return (
            <div key={s.famille} className={ouvert ? 'template-carte ouverte' : 'template-carte'}>
              <button className="template-entete" onClick={() => setOuverte(ouvert ? null : s.famille)}>
                <strong>{s.titre}</strong>
                <span>{s.objectif}</span>
              </button>
              {ouvert && (
                <div className="template-details">
                  <h5>🧪 Catégories de test à couvrir</h5>
                  <ul className="liste-simple">
                    {s.categories_test.map((c: any, i: number) => (
                      <li key={i}>
                        <strong>{c.nom}</strong> — {c.description}
                      </li>
                    ))}
                  </ul>

                  <h5>📏 Métriques à suivre</h5>
                  <ul className="liste-simple">
                    {s.metriques.map((m: string, i: number) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>

                  <h5>⚠️ Piège fréquent</h5>
                  <p>{s.piege_frequent}</p>

                  <h5>📋 Cahier de test — exemples à reproduire</h5>
                  <div className="cahier-test-table-wrap">
                    <table className="cahier-test-table">
                      <thead>
                        <tr>
                          <th>Cas</th>
                          <th>Entrée</th>
                          <th>Attendu</th>
                          <th>Constat</th>
                        </tr>
                      </thead>
                      <tbody>
                        {s.cahier_exemple.map((c: any, i: number) => (
                          <tr key={i}>
                            <td>{c.cas}</td>
                            <td>{c.entree}</td>
                            <td>{c.attendu}</td>
                            <td>{c.constat}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
