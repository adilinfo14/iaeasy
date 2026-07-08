import { useEffect, useRef, useState } from 'react'
import { executerGraphe, listerComposants, listerTemplates } from '../api/client'
import BrickCanvas, { type BrickCanvasHandle } from '../components/BrickCanvas'
import Terme from '../components/Terme'

const TERME_PAR_COMPOSANT: Record<string, string> = {
  chunking: 'Chunking',
  base_vectorielle: 'Embedding',
  llm_agent: 'LLM',
  outil_mcp: 'MCP',
  agent_unique: 'Agent',
  multi_agent: 'Multi-agent',
  llm_seul: 'LLM',
  rag: 'RAG',
  moderation: 'Modération',
  verification: 'Vérificateur',
}

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
  const [briqueSelectionnee, setBriqueSelectionnee] = useState<string | null>(null)
  const [noeudSelectionne, setNoeudSelectionne] = useState<string | null>(null)
  const [configNoeudSelectionne, setConfigNoeudSelectionne] = useState<Record<string, any>>({})
  const [erreur, setErreur] = useState<string | null>(null)
  const canvasRef = useRef<BrickCanvasHandle>(null)

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
    try {
      const r = await executerGraphe(nodes, edges)
      setResultat(r)
    } catch (e: any) {
      setErreur(e.message)
    }
  }

  function afficherComposant(brique: string, noeudId: string | undefined, config: Record<string, any>) {
    setBriqueSelectionnee(brique)
    setNoeudSelectionne(noeudId ?? null)
    setConfigNoeudSelectionne(config || {})
  }

  function modifierConfig(cle: string, valeur: unknown) {
    if (!noeudSelectionne) return
    setConfigNoeudSelectionne((c) => ({ ...c, [cle]: valeur }))
    canvasRef.current?.modifierConfigNoeud(noeudSelectionne, cle, valeur)
  }

  function chargerExemple(template: any, exemple: any) {
    setResultat(null)
    setErreur(null)
    setBriqueSelectionnee(null)
    setNoeudSelectionne(null)
    setConfigNoeudSelectionne({})
    setTemplateACharger(fusionnerExemple(template, exemple))
  }

  const composantAffiche = composants.find((c) => c.id === briqueSelectionnee)
  const artefactNoeud = noeudSelectionne && resultat?.resultats_par_noeud?.[noeudSelectionne]

  return (
    <div className="page page-constructeur">
      <h1>Constructeur d'architecture</h1>
      <p className="page-intro">
        Le mode « architecte » : 10 modèles d'architecture réels, chacun avec ses avantages et ses
        inconvénients. Ouvrez-en un, choisissez un exemple pour le charger sur le canvas, puis
        <strong> cliquez sur chaque nœud pour voir et modifier ce qui lui est vraiment envoyé</strong>{' '}
        avant d'exécuter et d'inspecter ce que produit chaque étape intermédiaire.
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
                      <button key={i} className="chip" onClick={() => chargerExemple(t, ex)}>
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
        ref={canvasRef}
        composants={composants}
        templateACharger={templateACharger}
        resultatsParNoeud={resultat?.resultats_par_noeud || null}
        onExecuter={executer}
        onComposantInfo={afficherComposant}
      />

      {erreur && <p className="erreur">{erreur}</p>}

      {templateACharger && (
        <div className="explication-bloc">
          <h4>Comment ça marche, étape par étape</h4>
          <p className="texte-muted">
            Ce graphe n'a pas encore été exécuté — voici ce que chaque brique va faire, dans l'ordre,
            avec l'entrée qui lui sera réellement envoyée (modifiable en cliquant sur le nœud).
          </p>
          <ol className="liste-etapes-trace">
            {templateACharger.nodes.map((n: any, i: number) => {
              const c = composants.find((c) => c.id === n.type)
              const apercu = n.config?.prompt || n.config?.texte || n.config?.expression
              return (
                <li key={i}>
                  {c?.icone} <strong>{c?.titre || n.type}</strong> — {c?.description}
                  {apercu && <div className="apercu-config">Entrée : « {apercu} »</div>}
                </li>
              )
            })}
          </ol>
        </div>
      )}

      {composantAffiche && (
        <div className="explication-bloc">
          <h4>
            {composantAffiche.icone}{' '}
            {TERME_PAR_COMPOSANT[composantAffiche.id] ? (
              <Terme nom={TERME_PAR_COMPOSANT[composantAffiche.id]}>{composantAffiche.titre}</Terme>
            ) : (
              composantAffiche.titre
            )}
          </h4>
          <p>{composantAffiche.description}</p>
          <p className="texte-muted">
            <strong>Entrée / sortie :</strong> {composantAffiche.entree_sortie}
          </p>

          {composantAffiche.champs_config?.length > 0 && noeudSelectionne && (
            <div className="config-form">
              <h5>✏️ Entrée de ce nœud (modifiable)</h5>
              <p className="texte-muted">
                C'est ici que vous fournissez ce qui est vraiment envoyé à ce nœud — uniquement du texte
                (pas de fichier ni d'image ici, voir le Catalogue pour tester les modèles de vision).
                Cliquez un exemple pour le reprendre tel quel ou vous en inspirer, modifiez-le librement,
                puis cliquez « Exécuter le graphe » pour voir l'effet de votre saisie.
              </p>
              {composantAffiche.champs_config.map((champ: any) => (
                <label key={champ.cle} className="config-champ">
                  <span>{champ.label}</span>
                  {champ.exemples?.length > 0 && (
                    <div className="champ-exemples">
                      <span className="champ-exemples-label">💡 Exemples :</span>
                      {champ.exemples.map((ex: any, i: number) => (
                        <button
                          key={i}
                          type="button"
                          className="chip chip-exemple"
                          onClick={() => modifierConfig(champ.cle, ex.valeur)}
                        >
                          {ex.label}
                        </button>
                      ))}
                    </div>
                  )}
                  {champ.type === 'textarea' && (
                    <textarea
                      value={configNoeudSelectionne[champ.cle] ?? ''}
                      onChange={(e) => modifierConfig(champ.cle, e.target.value)}
                      placeholder={champ.exemples?.[0] ? `Ex : ${champ.exemples[0].valeur}` : ''}
                      rows={4}
                    />
                  )}
                  {champ.type === 'texte' && (
                    <input
                      type="text"
                      value={configNoeudSelectionne[champ.cle] ?? ''}
                      onChange={(e) => modifierConfig(champ.cle, e.target.value)}
                      placeholder={champ.exemples?.[0] ? `Ex : ${champ.exemples[0].valeur}` : ''}
                    />
                  )}
                  {champ.type === 'nombre' && (
                    <input
                      type="number"
                      value={configNoeudSelectionne[champ.cle] ?? champ.defaut ?? ''}
                      onChange={(e) => modifierConfig(champ.cle, Number(e.target.value))}
                    />
                  )}
                  {champ.type === 'select' && (
                    <select
                      value={configNoeudSelectionne[champ.cle] ?? champ.options?.[0] ?? ''}
                      onChange={(e) => modifierConfig(champ.cle, e.target.value)}
                    >
                      {champ.options.map((opt: string) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  )}
                </label>
              ))}
            </div>
          )}

          {artefactNoeud && (
            <>
              <h4>Ce que ce nœud a produit lors de la dernière exécution</h4>
              <pre className="resultat">{JSON.stringify(artefactNoeud, null, 2)}</pre>
            </>
          )}
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
