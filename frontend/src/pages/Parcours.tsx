import { Fragment, useEffect, useState } from 'react'
import {
  debloquerBrique,
  executerGraphe,
  lireBadges,
  lireProgression,
  listerBriques,
  listerCas,
  validerBadge,
} from '../api/client'
import Quiz from '../components/Quiz'

function casDeBrique(brique: any, casId: string) {
  return brique.cas?.find((c: any) => c.id === casId) || brique.cas?.[0]
}

export default function Parcours() {
  const [briques, setBriques] = useState<any[]>([])
  const [casDisponibles, setCasDisponibles] = useState<any[]>([])
  const [casChoisi, setCasChoisi] = useState('btp')
  const [debloquees, setDebloquees] = useState<string[]>([])
  const [badges, setBadges] = useState<string[]>([])
  const [resultats, setResultats] = useState<Record<string, any>>({})
  const [enCours, setEnCours] = useState<string | null>(null)

  // Entrées libres par brique — préremplies selon le cas sectoriel choisi (voir choisirCas)
  const [promptLlm, setPromptLlm] = useState("Explique en une phrase ce qu'est un LLM.")
  const [questionRag, setQuestionRag] = useState('Quelles sont les conditions de garantie ?')
  const [documentUtilisateur, setDocumentUtilisateur] = useState(
    'La garantie décennale couvre les dommages de gros œuvre pendant 10 ans après réception des travaux.',
  )
  const [outilChoisi, setOutilChoisi] = useState<'calculatrice' | 'recherche'>('calculatrice')
  const [expressionOutil, setExpressionOutil] = useState('45 * 3.5 + 45 * 2.25')
  const [tacheAgent, setTacheAgent] = useState('Combien font 15 fois (2 + 6) ?')
  const [tacheMultiAgent, setTacheMultiAgent] = useState(
    "Rédige un message pour expliquer à un client ce qu'est un agent IA.",
  )

  useEffect(() => {
    listerBriques().then(setBriques)
    listerCas().then(setCasDisponibles)
    lireProgression().then((p) => setDebloquees(p.debloquees))
    lireBadges().then((b) => setBadges(b.badges))
  }, [])

  function choisirCas(id: string, listeBriques: any[]) {
    setCasChoisi(id)
    setResultats({})
    for (const b of listeBriques) {
      const c = casDeBrique(b, id)
      const d = c?.entree_defaut || {}
      if (b.id === 'llm_seul' && d.prompt) setPromptLlm(d.prompt)
      if (b.id === 'rag') {
        if (d.prompt) setQuestionRag(d.prompt)
        if (d.document_utilisateur) setDocumentUtilisateur(d.document_utilisateur)
      }
      if (b.id === 'outil_mcp') {
        setOutilChoisi('calculatrice')
        if (d.expression) setExpressionOutil(d.expression)
      }
      if (b.id === 'agent_unique' && d.prompt) setTacheAgent(d.prompt)
      if (b.id === 'multi_agent' && d.prompt) setTacheMultiAgent(d.prompt)
    }
  }

  async function reussirQuiz(briqueId: string) {
    const b = await validerBadge(briqueId)
    setBadges(b.badges)
  }

  function construireGraphe(brique: any) {
    switch (brique.id) {
      case 'llm_seul':
        return { nodes: [{ id: '1', type: 'llm_seul', config: { prompt: promptLlm } }], edges: [] }
      case 'rag':
        return {
          nodes: [
            {
              id: '1',
              type: 'rag',
              config: { prompt: questionRag, document_utilisateur: documentUtilisateur },
            },
          ],
          edges: [],
        }
      case 'outil_mcp':
        return {
          nodes: [
            {
              id: '1',
              type: 'outil_mcp',
              config: { outil: outilChoisi, expression: expressionOutil, prompt: expressionOutil },
            },
          ],
          edges: [],
        }
      case 'agent_unique':
        return { nodes: [{ id: '1', type: 'agent_unique', config: { prompt: tacheAgent } }], edges: [] }
      case 'multi_agent':
        return { nodes: [{ id: '1', type: 'multi_agent', config: { prompt: tacheMultiAgent } }], edges: [] }
      default:
        return { nodes: [], edges: [] }
    }
  }

  async function essayerBrique(brique: any) {
    setEnCours(brique.id)
    try {
      const graphe = construireGraphe(brique)
      const resultat = await executerGraphe(graphe.nodes, graphe.edges)
      setResultats((r) => ({ ...r, [brique.id]: resultat }))
      const suivante = nextBriqueId(briques, brique.id)
      const p = await debloquerBrique(suivante)
      setDebloquees(p.debloquees)
    } catch (e: any) {
      setResultats((r) => ({ ...r, [brique.id]: { erreur: e.message } }))
    } finally {
      setEnCours(null)
    }
  }

  function renderEntree(brique: any) {
    switch (brique.id) {
      case 'llm_seul':
        return (
          <textarea
            className="input-texte"
            rows={2}
            value={promptLlm}
            onChange={(e) => setPromptLlm(e.target.value)}
          />
        )
      case 'rag':
        return (
          <>
            <label className="texte-muted">Votre question :</label>
            <textarea
              className="input-texte"
              rows={2}
              value={questionRag}
              onChange={(e) => setQuestionRag(e.target.value)}
            />
            <label className="texte-muted">Ajoutez votre propre document au corpus de l'entreprise :</label>
            <textarea
              className="input-texte"
              rows={2}
              value={documentUtilisateur}
              onChange={(e) => setDocumentUtilisateur(e.target.value)}
            />
          </>
        )
      case 'outil_mcp':
        return (
          <>
            <div className="exemples-chips">
              <button
                className={outilChoisi === 'calculatrice' ? 'chip actif' : 'chip'}
                onClick={() => setOutilChoisi('calculatrice')}
              >
                Calculatrice
              </button>
              <button
                className={outilChoisi === 'recherche' ? 'chip actif' : 'chip'}
                onClick={() => setOutilChoisi('recherche')}
              >
                Recherche documentaire
              </button>
            </div>
            <textarea
              className="input-texte"
              rows={2}
              value={expressionOutil}
              onChange={(e) => setExpressionOutil(e.target.value)}
              placeholder={outilChoisi === 'calculatrice' ? 'Ex: 45 * 3.5' : 'Ex: Qu\'est-ce que MCP ?'}
            />
          </>
        )
      case 'agent_unique':
        return (
          <textarea
            className="input-texte"
            rows={2}
            value={tacheAgent}
            onChange={(e) => setTacheAgent(e.target.value)}
          />
        )
      case 'multi_agent':
        return (
          <textarea
            className="input-texte"
            rows={2}
            value={tacheMultiAgent}
            onChange={(e) => setTacheMultiAgent(e.target.value)}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="page">
      <h1>Parcours — construis ton assistant, brique par brique</h1>
      <p className="page-intro">
        Le Parcours fait progresser, étape après étape, la construction d'un assistant
        conversationnel : chaque brique ajoute une capacité concrète et en débloque une nouvelle.
        Cinq secteurs peuvent être choisis ci-dessous pour ancrer cette progression dans un contexte
        professionnel réel — BTP, banque, agriculture, ressources humaines ou e-commerce — sans que
        ce choix ne modifie jamais ce que chaque brique démontre sur le plan technique.
      </p>

      {casDisponibles.length > 0 && (
        <div className="exemples-categories">
          {casDisponibles.map((c) => (
            <button
              key={c.id}
              className={c.id === casChoisi ? 'chip actif' : 'chip'}
              onClick={() => choisirCas(c.id, briques)}
            >
              {c.icone} {c.secteur}
            </button>
          ))}
        </div>
      )}

      <ol className="parcours-liste">
        {briques.map((b) => {
          const debloquee = debloquees.includes(b.id)
          const prerequisOk = (b.prerequis as string[]).every((p) => debloquees.includes(p))
          const resultat = resultats[b.id]
          const cas = casDeBrique(b, casChoisi)
          return (
            <li
              key={b.id}
              className={debloquee ? 'etape debloquee' : prerequisOk ? 'etape disponible' : 'etape verrouillee'}
            >
              <h3>
                {b.icone} {b.ordre}. {b.titre} {badges.includes(b.id) && <span title="Badge obtenu">🏅</span>}
              </h3>
              <p className="mise-en-situation">{cas?.mise_en_situation}</p>

              <div className="avant-apres">
                <div className="avant-apres-carte avant">
                  <span className="avant-apres-label">Avant</span>
                  <p>{cas?.avant}</p>
                </div>
                <div className="avant-apres-fleche">→</div>
                <div className="avant-apres-carte apres">
                  <span className="avant-apres-label">Après cette brique</span>
                  <p>{cas?.apres}</p>
                </div>
              </div>

              <p className="texte-muted">Comment ça marche, étape par étape :</p>
              <div className="schema-flow">
                {b.schema.map((s: any, i: number) => (
                  <Fragment key={i}>
                    <div className="schema-etape">
                      <div className="schema-icone">{s.icone}</div>
                      <div className="schema-label">{s.label}</div>
                    </div>
                    {i < b.schema.length - 1 && <div className="schema-fleche">→</div>}
                  </Fragment>
                ))}
              </div>

              {prerequisOk ? (
                <>
                  {renderEntree(b)}
                  <button onClick={() => essayerBrique(b)} disabled={enCours === b.id}>
                    {enCours === b.id ? 'Exécution…' : 'Essayer cette brique'}
                  </button>
                </>
              ) : (
                <p className="verrou">🔒 Termine l'étape précédente pour débloquer.</p>
              )}

              {resultat && !resultat.erreur && (
                <div className="explication-bloc">
                  <h4>Déroulé</h4>
                  <ol className="liste-etapes-trace">
                    {resultat.etapes.map((e: any, i: number) => (
                      <li key={i}>{e.detail}</li>
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
              {resultat?.erreur && <p className="erreur">{resultat.erreur}</p>}

              {resultat && !resultat.erreur && b.quiz && (
                <Quiz
                  questions={b.quiz}
                  dejaReussi={badges.includes(b.id)}
                  onReussite={() => reussirQuiz(b.id)}
                />
              )}
            </li>
          )
        })}
      </ol>
    </div>
  )
}

function nextBriqueId(briques: any[], courant: string): string {
  const idx = briques.findIndex((b) => b.id === courant)
  return briques[idx + 1]?.id ?? courant
}
