import { useCallback, useEffect, useRef, useState } from 'react'
import Decor from '../components/theatre/Decor'
import Personnage from '../components/theatre/Personnage'
import {
  genererEpisodeTheatre,
  genererVoixTheatre,
  listerEpisodesTheatre,
  lireEpisodeTheatre,
} from '../api/client'

const NOMS = { clio: 'Clio', marco: 'Marco' }
const VITESSE_FRAPPE_MS = 22
const PAUSE_APRES_LIGNE_MS = 500

// Le personnage qui écoute réagit lui aussi, plutôt que de rester figé en "neutre" pendant
// toute la réplique de l'autre — dérivé de l'émotion du locuteur (générée par l'IA ou écrite à
// la main), sans données supplémentaires à produire.
const REACTION_AUDITEUR: Record<string, string> = {
  neutre: 'neutre',
  surprise: 'surprise',
  joyeux: 'joyeux',
  triste: 'inquiet',
  inquiet: 'inquiet',
}

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
  const [sonActif, setSonActif] = useState(true)
  const [audioTermine, setAudioTermine] = useState(true)

  const minuteurRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const urlAudioRef = useRef<string | null>(null)

  useEffect(() => {
    listerEpisodesTheatre().then(setListe)
  }, [])

  function nettoyerMinuteur() {
    if (minuteurRef.current) clearTimeout(minuteurRef.current)
    minuteurRef.current = null
  }

  function arreterAudio() {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    if (urlAudioRef.current) {
      URL.revokeObjectURL(urlAudioRef.current)
      urlAudioRef.current = null
    }
  }

  const demarrerEpisode = useCallback((e: any) => {
    nettoyerMinuteur()
    arreterAudio()
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

  // Effet machine à écrire + narration vocale (voix neuronale Piper, générée côté serveur).
  // Corrige un décalage signalé en conditions réelles ("le son ne correspond pas à ce qui est
  // écrit") : la frappe démarrait immédiatement à une vitesse fixe pendant que l'audio ne se
  // mettait à jouer qu'une fois récupéré (délai réseau variable) — les deux couraient à des
  // rythmes indépendants. Désormais la frappe démarre AVEC la lecture audio (dès que sa durée
  // réelle est connue) et sa vitesse est recalculée pour épouser cette durée.
  useEffect(() => {
    if (!ligneCourante) return
    setTexteAffiche('')
    const texte = ligneCourante.texte
    arreterAudio()

    let idFrappe: ReturnType<typeof setInterval> | null = null
    let annule = false

    const demarrerFrappe = (dureeMs: number) => {
      const intervalle = Math.max(12, Math.min(60, dureeMs / Math.max(texte.length, 1)))
      let i = 0
      idFrappe = setInterval(() => {
        i += 1
        setTexteAffiche(texte.slice(0, i))
        if (i >= texte.length && idFrappe) clearInterval(idFrappe)
      }, intervalle)
    }

    if (!sonActif) {
      setAudioTermine(true)
      demarrerFrappe(texte.length * VITESSE_FRAPPE_MS)
      return () => {
        annule = true
        if (idFrappe) clearInterval(idFrappe)
      }
    }

    setAudioTermine(false)
    genererVoixTheatre(texte, ligneCourante.personnage)
      .then((url) => {
        if (annule) return
        urlAudioRef.current = url
        const audio = new Audio(url)
        audioRef.current = audio
        audio.onended = () => setAudioTermine(true)
        audio.onerror = () => {
          setAudioTermine(true)
          if (!idFrappe) demarrerFrappe(texte.length * VITESSE_FRAPPE_MS)
        }
        audio.onloadedmetadata = () => {
          if (annule) return
          const dureeMs = isFinite(audio.duration) && audio.duration > 0 ? audio.duration * 1000 : texte.length * VITESSE_FRAPPE_MS
          // La frappe ne démarre qu'une fois que play() confirme que la lecture a RÉELLEMENT
          // commencé (promesse résolue), pas dès que les métadonnées sont chargées — entre les
          // deux, le pipeline audio du navigateur peut mettre quelques dizaines à centaines de ms
          // à démarrer, un décalage qui restait perceptible (signalé en conditions réelles).
          audio
            .play()
            .then(() => {
              if (annule) return
              demarrerFrappe(dureeMs)
            })
            .catch(() => {
              setAudioTermine(true)
              if (!annule) demarrerFrappe(dureeMs)
            })
        }
      })
      .catch(() => {
        if (annule) return
        setAudioTermine(true)
        demarrerFrappe(texte.length * VITESSE_FRAPPE_MS)
      })

    return () => {
      annule = true
      if (idFrappe) clearInterval(idFrappe)
    }
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
    if (!audioRef.current) return
    if (enPause) audioRef.current.pause()
    else audioRef.current.play().catch(() => {})
  }, [enPause])

  // Avance automatique une fois le texte affiché en entier ET la voix réellement terminée
  // (ou désactivée) — corrige le son qui se coupait avant la fin du texte.
  useEffect(() => {
    nettoyerMinuteur()
    if (!ligneCourante || enPause || termine) return
    if (texteAffiche.length < ligneCourante.texte.length) return
    if (!audioTermine) return
    minuteurRef.current = setTimeout(avancer, PAUSE_APRES_LIGNE_MS)
    return nettoyerMinuteur
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [texteAffiche, enPause, termine, audioTermine])

  useEffect(() => arreterAudio, [])

  return (
    <div className="page page-theatre">
      <h1>🎭 Le Théâtre de l'Histoire</h1>
      <p className="page-intro">
        Deux personnages, générés et animés par une IA, se racontent des histoires vraies — le
        décor et l'ambiance changent avec le récit, une voix neuronale auto-hébergée (Piper) les
        fait parler, et l'IA associe une émotion réelle à chaque réplique (surprise, joie,
        tristesse, inquiétude...) qui change l'expression du personnage — y compris celle qui
        écoute. Les 5 premières histoires sont écrites à l'avance ; le bouton « Nouvelle histoire »
        en fait générer une nouvelle en direct, sur un sujet historique réel tiré au sort.
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
              parle={ligneCourante?.personnage === 'clio' && !termine}
              actif={!termine}
              variante={ligneIndex % 2 === 0}
              emotion={
                ligneCourante?.personnage === 'clio'
                  ? ligneCourante?.emotion
                  : REACTION_AUDITEUR[ligneCourante?.emotion || 'neutre']
              }
            />
            <Personnage
              type="marco"
              decor={decorCourant}
              parle={ligneCourante?.personnage === 'marco' && !termine}
              actif={!termine}
              variante={ligneIndex % 2 === 0}
              emotion={
                ligneCourante?.personnage === 'marco'
                  ? ligneCourante?.emotion
                  : REACTION_AUDITEUR[ligneCourante?.emotion || 'neutre']
              }
            />
          </div>

          <div className="theatre-controles">
            <button onClick={reculer} disabled={sceneIndex === 0 && ligneIndex === 0}>
              ◀ Précédent
            </button>
            <button onClick={() => setEnPause((p) => !p)}>{enPause ? '▶ Reprendre' : '⏸ Pause'}</button>
            <button onClick={avancer} disabled={termine}>
              Suivant ▶
            </button>
            <button
              onClick={() => {
                arreterAudio()
                setSonActif((s) => !s)
              }}
            >
              {sonActif ? '🔊 Son' : '🔇 Muet'}
            </button>
            <button
              onClick={() => {
                nettoyerMinuteur()
                arreterAudio()
                setEpisode(null)
              }}
            >
              Choisir une autre histoire
            </button>
          </div>
        </div>
      )}

      {/* Texte hors du cadre visuel — plus lisible, et ne recouvre plus le décor/les personnages
          (demandé après retour utilisateur : "mets le texte à l'extérieur de l'écran"). */}
      {episode && !termine && ligneCourante && (
        <div className="theatre-dialogue">
          <div className="theatre-dialogue-nom">{NOMS[ligneCourante.personnage as 'clio' | 'marco']}</div>
          <p className="theatre-dialogue-texte">{texteAffiche}</p>
        </div>
      )}

      {episode && termine && (
        <div className="theatre-dialogue theatre-fin">
          <p>— Fin de l'histoire —</p>
        </div>
      )}
    </div>
  )
}
