import { useCallback, useEffect, useRef, useState } from 'react'
import Decor from '../components/theatre/Decor'
import Personnage from '../components/theatre/Personnage'
import { genererEpisodeTheatre, listerEpisodesTheatre, lireEpisodeTheatre } from '../api/client'

const NOMS = { clio: 'Clio', marco: 'Marco' }
const VITESSE_FRAPPE_MS = 22
const PAUSE_APRES_LIGNE_MS = 1100

const VOIX_SUPPORTEE = typeof window !== 'undefined' && 'speechSynthesis' in window

export default function Theatre() {
  const [liste, setListe] = useState<any[]>([])
  const [episode, setEpisode] = useState<any>(null)
  const [sceneIndex, setSceneIndex] = useState(0)
  const [ligneIndex, setLigneIndex] = useState(0)
  const [texteAffiche, setTexteAffiche] = useState('')
  const [enPause, setEnPause] = useState(false)
  const [termine, setTermine] = useState(false)
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)
  const [sonActif, setSonActif] = useState(VOIX_SUPPORTEE)

  const minuteurRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const voixFrRef = useRef<SpeechSynthesisVoice[]>([])

  useEffect(() => {
    listerEpisodesTheatre().then(setListe)

    if (!VOIX_SUPPORTEE) return
    function chargerVoix() {
      voixFrRef.current = window.speechSynthesis.getVoices().filter((v) => v.lang.startsWith('fr'))
    }
    chargerVoix()
    window.speechSynthesis.addEventListener('voiceschanged', chargerVoix)
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', chargerVoix)
      window.speechSynthesis.cancel()
    }
  }, [])

  function nettoyerMinuteur() {
    if (minuteurRef.current) clearTimeout(minuteurRef.current)
    minuteurRef.current = null
  }

  const demarrerEpisode = useCallback((e: any) => {
    nettoyerMinuteur()
    if (VOIX_SUPPORTEE) window.speechSynthesis.cancel()
    setEpisode(e)
    setSceneIndex(0)
    setLigneIndex(0)
    setTexteAffiche('')
    setTermine(false)
    setEnPause(false)
    setErreur(null)
  }, [])

  async function choisirEpisode(id: string) {
    setChargement(true)
    setErreur(null)
    try {
      const e = await lireEpisodeTheatre(id)
      demarrerEpisode(e)
    } catch (err: any) {
      setErreur(err.message)
    } finally {
      setChargement(false)
    }
  }

  async function genererNouvelleHistoire() {
    setChargement(true)
    setErreur(null)
    try {
      const e = await genererEpisodeTheatre()
      demarrerEpisode(e)
    } catch (err: any) {
      setErreur(err.message)
    } finally {
      setChargement(false)
    }
  }

  const ligneCourante = episode?.scenes?.[sceneIndex]?.repliques?.[ligneIndex]
  const decorCourant = episode?.scenes?.[sceneIndex]?.decor

  // Effet machine à écrire : ré-affiche la réplique courante caractère par caractère, et la
  // fait lire à voix haute (Web Speech API — navigateur uniquement, aucun serveur impliqué) :
  // Clio et Marco reçoivent chacun une voix/hauteur différente pour rester distinguables.
  useEffect(() => {
    if (!ligneCourante) return
    setTexteAffiche('')
    let i = 0
    const texte = ligneCourante.texte
    const id = setInterval(() => {
      i += 1
      setTexteAffiche(texte.slice(0, i))
      if (i >= texte.length) clearInterval(id)
    }, VITESSE_FRAPPE_MS)

    if (VOIX_SUPPORTEE && sonActif) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(texte)
      utterance.lang = 'fr-FR'
      const voix = voixFrRef.current
      if (voix.length > 0) {
        utterance.voice = ligneCourante.personnage === 'clio' ? voix[0] : voix[voix.length - 1]
      }
      utterance.pitch = ligneCourante.personnage === 'clio' ? 1.25 : 0.8
      utterance.rate = 1.02
      window.speechSynthesis.speak(utterance)
    }

    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [episode, sceneIndex, ligneIndex, sonActif])

  function avancer() {
    if (!episode) return
    const scenes = episode.scenes
    const repliquesScene = scenes[sceneIndex].repliques
    if (ligneIndex + 1 < repliquesScene.length) {
      setLigneIndex((i) => i + 1)
    } else if (sceneIndex + 1 < scenes.length) {
      setSceneIndex((i) => i + 1)
      setLigneIndex(0)
    } else {
      setTermine(true)
    }
  }

  function reculer() {
    if (!episode) return
    if (ligneIndex > 0) {
      setLigneIndex((i) => i - 1)
    } else if (sceneIndex > 0) {
      const scenePrecedente = episode.scenes[sceneIndex - 1]
      setSceneIndex((i) => i - 1)
      setLigneIndex(scenePrecedente.repliques.length - 1)
    }
    setTermine(false)
  }

  useEffect(() => {
    if (!VOIX_SUPPORTEE) return
    if (enPause) window.speechSynthesis.pause()
    else window.speechSynthesis.resume()
  }, [enPause])

  // Avance automatique une fois la réplique entièrement affichée, sauf en pause.
  useEffect(() => {
    nettoyerMinuteur()
    if (!ligneCourante || enPause || termine) return
    if (texteAffiche.length < ligneCourante.texte.length) return
    minuteurRef.current = setTimeout(avancer, PAUSE_APRES_LIGNE_MS)
    return nettoyerMinuteur
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [texteAffiche, enPause, termine])

  return (
    <div className="page page-theatre">
      <h1>🎭 Le Théâtre de l'Histoire</h1>
      <p className="page-intro">
        Deux personnages, générés et animés par une IA, se racontent des histoires vraies —
        le décor et l'ambiance changent avec le récit. Les 5 premières histoires sont écrites à
        l'avance ; le bouton « Nouvelle histoire » en fait générer une nouvelle en direct, sur un
        sujet historique réel tiré au sort.
      </p>

      {!episode && (
        <div className="theatre-selection">
          <div className="exemples-chips">
            {liste.map((e) => (
              <button key={e.id} className="chip" onClick={() => choisirEpisode(e.id)} disabled={chargement}>
                {e.titre} ({e.annee})
              </button>
            ))}
          </div>
          <button onClick={genererNouvelleHistoire} disabled={chargement}>
            {chargement ? 'Écriture en cours…' : '✨ Nouvelle histoire (générée par une IA)'}
          </button>
          {erreur && <p className="erreur">{erreur}</p>}
        </div>
      )}

      {episode && (
        <div className="theatre-scene">
          {decorCourant && <Decor key={`${sceneIndex}-${decorCourant}`} decor={decorCourant} />}

          <div className="theatre-personnages">
            <Personnage
              type="clio"
              decor={decorCourant}
              parle={ligneCourante?.personnage === 'clio'}
              actif={!termine}
              variante={ligneIndex % 2 === 0}
            />
            <Personnage
              type="marco"
              decor={decorCourant}
              parle={ligneCourante?.personnage === 'marco'}
              actif={!termine}
              variante={ligneIndex % 2 === 0}
            />
          </div>

          {!termine && ligneCourante && (
            <div className="theatre-dialogue">
              <div className="theatre-dialogue-nom">{NOMS[ligneCourante.personnage as 'clio' | 'marco']}</div>
              <p className="theatre-dialogue-texte">{texteAffiche}</p>
            </div>
          )}

          {termine && (
            <div className="theatre-dialogue theatre-fin">
              <p>— Fin de l'histoire —</p>
            </div>
          )}

          <div className="theatre-controles">
            <button onClick={reculer} disabled={sceneIndex === 0 && ligneIndex === 0}>
              ◀ Précédent
            </button>
            <button onClick={() => setEnPause((p) => !p)}>{enPause ? '▶ Reprendre' : '⏸ Pause'}</button>
            <button onClick={avancer} disabled={termine}>
              Suivant ▶
            </button>
            {VOIX_SUPPORTEE && (
              <button
                onClick={() => {
                  setSonActif((s) => !s)
                  window.speechSynthesis.cancel()
                }}
              >
                {sonActif ? '🔊 Son' : '🔇 Muet'}
              </button>
            )}
            <button
              onClick={() => {
                nettoyerMinuteur()
                if (VOIX_SUPPORTEE) window.speechSynthesis.cancel()
                setEpisode(null)
              }}
            >
              Choisir une autre histoire
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
