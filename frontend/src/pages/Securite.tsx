import { useEffect, useState } from 'react'
import { listerSecurite } from '../api/client'

export default function Securite() {
  const [source, setSource] = useState('')
  const [risques, setRisques] = useState<any[]>([])
  const [ouvert, setOuvert] = useState<string | null>(null)

  useEffect(() => {
    listerSecurite().then((d) => {
      setSource(d.source)
      setRisques(d.risques)
    })
  }, [])

  return (
    <div className="page page-securite">
      <h1>🛡️ Sécurité des applications IA</h1>
      <p className="page-intro">
        Un agent d'intelligence artificielle ne se limite pas à commettre, à l'occasion, des
        erreurs de raisonnement : il constitue également une surface d'attaque à part entière,
        porteuse de risques qui lui sont propres. Les {risques.length || 10} catégories qui suivent
        en couvrent l'essentiel, chacune assortie des mesures concrètes qu'il convient de mettre en
        œuvre.
      </p>
      {source && <p className="texte-muted video-source">{source}</p>}

      <div className="templates-liste">
        {risques.map((r) => {
          const estOuvert = ouvert === r.id
          return (
            <div key={r.id} className={estOuvert ? 'template-carte ouverte' : 'template-carte'}>
              <button className="template-entete" onClick={() => setOuvert(estOuvert ? null : r.id)}>
                <strong>
                  {r.id} — {r.titre}
                </strong>
                <span>{r.risque}</span>
              </button>
              {estOuvert && (
                <div className="template-details">
                  {r.exemple_concret && (
                    <>
                      <h5>🕵️ Exemple concret</h5>
                      <p>{r.exemple_concret}</p>
                    </>
                  )}

                  <h5>✅ Bonnes pratiques</h5>
                  <ul className="liste-simple">
                    {r.bonnes_pratiques.map((b: string, i: number) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>

                  {r.lien_site && (
                    <>
                      <h5>🔗 Sur ce site</h5>
                      <p className="texte-muted">{r.lien_site}</p>
                    </>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
