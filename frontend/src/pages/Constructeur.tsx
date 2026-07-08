import { useEffect, useState } from 'react'
import { executerGraphe, listerComposants, listerTemplates } from '../api/client'
import BrickCanvas from '../components/BrickCanvas'

function fusionnerExemple(template: any, exemple: any) {
  const nodes = template.nodes.map((n: any) => {
    const overrides = exemple.valeurs?.[n.id]
    return overrides ? { ...n, config: { ...n.config, ...overrides } } : n
  })
  return { ...template, nodes, _n: Date.now() }
}

export default function Constructeur() {
  const [composants, setComposants] = useState<any[]>([])
  const [templates, setTemplates] = useState<any[]>([])
  const [templateOuvert, setTemplateOuvert] = useState<string | null>(null)
  const [templateACharger, setTemplateACharger] = useState<any | null>(null)
  const [resultat, setResultat] = useState<any>(null)
  const [noeudSelectionne, setNoeudSelectionne] = useState<{ id: string; brique: string } | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    listerComposants().then(setComposants)
    listerTemplates().then(setTemplates)
  }, [])

  async function executer(
    nodes: { id: string; type: string; config: Record<string, unknown> }[],
    edges: { source: string; target: string }[],
  ) {
    setErreur(null)
    setResultat(null)
    setNoeudSelectionne(null)
    try {
      const r = await executerGraphe(nodes, edges)
      setResultat(r)
    } catch (e: any) {
      setErreur(e.message)
    }
  }

  const artefactNoeud = noeudSelectionne && resultat?.resultats_par_noeud?.[noeudSelectionne.id]

  return (
    <div className="page page-constructeur">
      <h1>Constructeur d'architecture</h1>
      <p className="page-intro">
        Le mode « architecte » : 10 modèles d'architecture réels, chacun avec ses avantages et ses
        inconvénients. Ouvrez-en un, choisissez un exemple pour le charger sur le canvas, puis
        exécutez et inspectez ce que produit chaque étape intermédiaire.
      </p>

      <div className="templates-liste">
        {templates.map((t) => {
          const ouvert = templateOuvert === t.id
          return (
            <div key={t.id} className={ouvert ? 'template-carte ouverte' : 'template-carte'}>
              <button className="template-entete" onClick={() => setTemplateOuvert(ouvert ? null : t.id)}>
                <strong>{t.titre}</strong>
                <span>{t.description}</span>
              </button>
              {ouvert && (
                <div className="template-details">
                  <div className="avantages-inconvenients">
                    <div>
                      <h5>✅ Avantages</h5>
                      <ul className="liste-simple">
                        {t.avantages.map((a: string, i: number) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h5>⚠️ Inconvénients</h5>
                      <ul className="liste-simple">
                        {t.inconvenients.map((a: string, i: number) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <p className="texte-muted">Charger sur le canvas avec l'exemple :</p>
                  <div className="exemples-chips">
                    {t.exemples.map((ex: any, i: number) => (
                      <button key={i} className="chip" onClick={() => setTemplateACharger(fusionnerExemple(t, ex))}>
                        {ex.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <BrickCanvas
        composants={composants}
        templateACharger={templateACharger}
        resultatsParNoeud={resultat?.resultats_par_noeud || null}
        onExecuter={executer}
        onNodeClick={(id, brique) => setNoeudSelectionne({ id, brique })}
      />

      {erreur && <p className="erreur">{erreur}</p>}

      {artefactNoeud && (
        <div className="explication-bloc">
          <h4>Ce qu'a produit ce nœud ({noeudSelectionne!.brique})</h4>
          <pre className="resultat">{JSON.stringify(artefactNoeud, null, 2)}</pre>
        </div>
      )}

      {resultat && (
        <div className="explication-bloc">
          <h4>Déroulé complet</h4>
          <ol>
            {resultat.etapes.map((e: any, i: number) => (
              <li key={i}>
                <strong>{e.brique}</strong> — {e.detail}
              </li>
            ))}
          </ol>
          {resultat.reponse_finale && (
            <>
              <h4>Réponse finale</h4>
              <p className="traduction-cible">{resultat.reponse_finale}</p>
            </>
          )}
        </div>
      )}
    </div>
  )
}
