import { useEffect, useState } from 'react'
import { demarrerBriefIA, situationBriefIA, suivreBriefIA, validerBriefIA } from '../api/client'

const LIBELLES_CHAMPS: Record<string, string> = {
  ton: 'Ton',
  palette: 'Palette',
  mots_interdits: 'Mots interdits',
  mention_obligatoire: 'Mention obligatoire',
}

function CarteEtape({ etape }: { etape: { etape: string; libelle: string; donnees: any } }) {
  const d = etape.donnees
  return (
    <div className="brief-ia-etape">
      <div className="brief-ia-etape-libelle">{etape.libelle}</div>
      {etape.etape === 'extract_marque' && (
        <ul className="brief-ia-etape-detail">
          {Object.entries(LIBELLES_CHAMPS).map(([champ, libelle]) => (
            <li key={champ}>
              <b>{libelle}</b> : {Array.isArray(d[champ]) ? d[champ].join(', ') || '—' : d[champ]}
            </li>
          ))}
        </ul>
      )}
      {etape.etape === 'map_sources' && (
        <ul className="brief-ia-etape-detail">
          {d.contexte.produits.map((p: any) => (
            <li key={p.sku}>
              {p.nom} — {p.prix.toFixed(2)} € <span className="chip">-{p.remise_pct}%</span>
            </li>
          ))}
          {d.contexte.avertissements.map((a: string, i: number) => (
            <li key={i} className="brief-ia-avertissement">
              ⚠ {a}
            </li>
          ))}
        </ul>
      )}
      {etape.etape === 'retrieve_examples' && (
        <ul className="brief-ia-etape-detail">
          {d.exemples.map((ex: any, i: number) => (
            <li key={i}>
              <b>{ex.titre}</b> — {ex.resume}
            </li>
          ))}
        </ul>
      )}
      {etape.etape === 'generate_brief' && (
        <ul className="brief-ia-etape-detail">
          <li>
            <b>{d.brouillon.titre}</b>
          </li>
          <li>{d.brouillon.message_cle}</li>
        </ul>
      )}
      {etape.etape === 'critique' && (
        <ul className="brief-ia-etape-detail">
          <li>
            Score : <b>{d.avis.score}/5</b> — {d.avis.valide ? 'validé par le relecteur' : 'à revoir'}
          </li>
          {d.avis.remarques.map((r: string, i: number) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

function BriefFinalCarte({ brief }: { brief: any }) {
  return (
    <div className="brief-ia-final">
      <h3>{brief.titre}</h3>
      <p>
        <b>Objectif</b> : {brief.objectif}
      </p>
      <p>
        <b>Message clé</b> : {brief.message_cle}
      </p>
      <p>
        <b>Produits vedettes</b> : {brief.produits_vedettes.join(', ')}
      </p>
      <p>
        <b>Ton</b> : {brief.ton}
      </p>
      <p>
        <b>Mentions obligatoires</b> : {brief.mentions_obligatoires.join(' — ')}
      </p>
      <p>
        <b>Formats</b> : {brief.formats.join(', ')} · <b>Durée</b> : {brief.duree_secondes}s
      </p>
      <p>
        <b>Appel à l'action</b> : {brief.appel_action}
      </p>
      <p>
        <b>Deadline</b> : {brief.deadline}
      </p>
    </div>
  )
}

export default function BriefIA() {
  const [situation, setSituation] = useState<any>(null)
  const [threadId, setThreadId] = useState<string | null>(null)
  const [etapes, setEtapes] = useState<any[]>([])
  const [attenteValidation, setAttenteValidation] = useState(false)
  const [brouillon, setBrouillon] = useState<any>(null)
  const [avis, setAvis] = useState<any>(null)
  const [avertissements, setAvertissements] = useState<string[]>([])
  const [briefFinal, setBriefFinal] = useState<any>(null)
  const [enCours, setEnCours] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    situationBriefIA().then(setSituation)
  }, [])

  function suivre(jobId: string) {
    setEnCours(true)
    suivreBriefIA(
      jobId,
      (etape) => setEtapes((prev) => [...prev, etape]),
      (fin) => {
        setEnCours(false)
        if (fin.status === 'erreur') {
          setErreur(fin.erreur || 'Erreur pendant la génération.')
          return
        }
        if (fin.attente_validation) {
          setAttenteValidation(true)
          setBrouillon(fin.brouillon)
          setAvis(fin.avis)
          setAvertissements(fin.avertissements || [])
        } else {
          setAttenteValidation(false)
          setBriefFinal(fin.brief_final)
        }
      },
      () => setEtapes([]),
    )
  }

  async function lancer() {
    setErreur(null)
    setBriefFinal(null)
    setAttenteValidation(false)
    setEtapes([])
    try {
      const { job_id, thread_id } = await demarrerBriefIA()
      setThreadId(thread_id)
      suivre(job_id)
    } catch (err: any) {
      setErreur(err.message)
    }
  }

  async function envoyerValidation(approuve: boolean) {
    if (!threadId) return
    setErreur(null)
    setAttenteValidation(false)
    try {
      const { job_id } = await validerBriefIA(threadId, approuve, approuve ? undefined : feedback)
      setFeedback('')
      suivre(job_id)
    } catch (err: any) {
      setErreur(err.message)
    }
  }

  return (
    <div className="page page-brief-ia">
      <h1>Brief IA</h1>
      <p className="page-intro">
        Un système agentique (Ollama, qwen2.5:7b-instruct) qui croise plusieurs sources de
        données e-commerce pour rédiger un brief créatif — puis attend ta validation avant de le
        considérer terminé, exactement comme il le ferait en production.
      </p>

      {situation && !threadId && (
        <div className="mise-en-situation">
          Tu es category manager chez une marque d'articles de randonnée. Les {situation.campagne.nom}{' '}
          démarrent le {situation.campagne.date_debut} sur les catégories{' '}
          {situation.campagne.categories_ciblees.join(' et ')}. Il te faut un brief pour l'équipe
          motion design — d'habitude tu croises le catalogue, le prix réel, le calendrier promo et
          la charte de marque à la main. Voyons ce que l'IA en fait.
        </div>
      )}

      {!threadId && (
        <button onClick={lancer} disabled={!situation}>
          Lancer la génération
        </button>
      )}

      {erreur && <p className="erreur">{erreur}</p>}

      {etapes.length > 0 && (
        <div className="brief-ia-timeline">
          {etapes.map((e, i) => (
            <CarteEtape key={i} etape={e} />
          ))}
          {enCours && <div className="brief-ia-etape brief-ia-etape-attente">…</div>}
        </div>
      )}

      {attenteValidation && brouillon && (
        <div className="brief-ia-validation">
          <h3>À toi de valider</h3>
          <BriefFinalCarte brief={brouillon} />
          <p className="texte-muted">
            Relecture automatique : {avis?.score}/5{' '}
            {avis?.valide ? '(validé)' : '(le relecteur a des remarques, visibles ci-dessus)'}
          </p>
          {avertissements.length > 0 && (
            <ul className="brief-ia-etape-detail">
              {avertissements.map((a, i) => (
                <li key={i} className="brief-ia-avertissement">
                  ⚠ {a}
                </li>
              ))}
            </ul>
          )}
          <div className="brief-ia-validation-actions">
            <button onClick={() => envoyerValidation(true)}>Approuver</button>
          </div>
          <textarea
            placeholder="Ce qui ne va pas, pour que l'IA corrige le brief…"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <button onClick={() => envoyerValidation(false)} disabled={!feedback.trim()}>
            Demander une révision
          </button>
        </div>
      )}

      {briefFinal && (
        <div>
          <h3>Brief final, approuvé</h3>
          <BriefFinalCarte brief={briefFinal} />
          <button
            onClick={() => {
              setThreadId(null)
              setBriefFinal(null)
              setEtapes([])
            }}
          >
            Relancer une génération
          </button>
        </div>
      )}
    </div>
  )
}
