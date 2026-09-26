import { useCallback, useEffect, useRef, useState } from 'react'
import Decor from '../components/theatre/Decor'
import Personnage from '../components/theatre/Personnage'
import SchemaDiagram from '../components/voyage/SchemaDiagram'
import { genererVoixTheatre, listerChapitresVoyage } from '../api/client'

const NOMS = { clio: 'Clio', marco: 'Marco' }
const VITESSE_FRAPPE_MS = 22

const REACTION_AUDITEUR: Record<string, string> = {
  neutre: 'neutre',
  surprise: 'surprise',
  joyeux: 'joyeux',
  triste: 'inquiet',
  inquiet: 'inquiet',
}

// "Le Voyage de l'IA" reprend le même moteur de lecture que le Théâtre (machine à écrire
// synchronisée sur la voix Piper réelle, personnages/décor animés) mais applique à un seul
// récit continu qui traverse toutes les familles de modèles du site, chapitre par chapitre,
// avec un petit schéma animé à côté de chaque chapitre plutôt que de simples répliques.
export default function Voyage() {
  const [chapitres, setChapitres] = useState<any[]>([])
  const [demarre, setDemarre] = useState(false)
  const [chapitreIndex, setChapitreIndex] = useState(0)
  const [ligneIndex, setLigneIndex] = useState(0)
  const [texteAffiche, setTexteAffiche] = useState('')
  const [enPause, setEnPause] = useState(false)
  const [termine, setTermine] = useState(false)
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState<string | null>(null)
  const [sonActif, setSonActif] = useState(true)
  const [audioTermine, setAudioTermine] = useState(true)

  const minuteurRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const urlAudioRef = useRef<string | null>(null)

  useEffect(() => {
    listerChapitresVoyage()
      .then((c) => {
        setChapitres(c)
        // Récit continu (pas un menu d'histoires séparées comme le Théâtre) : démarre
        // directement au premier chapitre plutôt que de forcer un clic préalable.
        if (c.length > 0) setDemarre(true)
      })
      .catch(() => setErreur('Impossible de charger le voyage.'))
      .finally(() => setChargement(false))
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

  const allerAuChapitre = useCallback((index: number) => {
    nettoyerMinuteur()
    arreterAudio()
    setChapitreIndex(index)
    setLigneIndex(0)
    setTexteAffiche('')
    setTermine(false)
    setEnPause(false)
    setDemarre(true)
  }, [])

  const chapitreCourant = chapitres[chapitreIndex]
  const ligneCourante = chapitreCourant?.repliques?.[ligneIndex]

  // Même correctif que le Théâtre : la frappe démarre AVEC la lecture audio (dès que sa durée
  // réelle est connue) et épouse cette durée, plutôt que de tourner à une vitesse fixe
  // indépendante du moment où l'audio se met réellement à jouer.
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
          demarrerFrappe(dureeMs)
          audio.play().catch(() => setAudioTermine(true))
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
  }, [chapitreIndex, ligneIndex, sonActif])

  function avancer() {
    if (!chapitreCourant) return
    const repliques = chapitreCourant.repliques
    if (ligneIndex + 1 < repliques.length) {
      setLigneIndex((i) => i + 1)
    } else if (chapitreIndex + 1 < chapitres.length) {
      setChapitreIndex((i) => i + 1)
      setLigneIndex(0)
    } else {
      setTermine(true)
    }
  }

  function reculer() {
    if (!chapitreCourant) return
    if (ligneIndex > 0) {
      setLigneIndex((i) => i - 1)
    } else if (chapitreIndex > 0) {
      const chapitrePrecedent = chapitres[chapitreIndex - 1]
      setChapitreIndex((i) => i - 1)
      setLigneIndex(chapitrePrecedent.repliques.length - 1)
    }
    setTermine(false)
  }

  useEffect(() => {
    if (!audioRef.current) return
    if (enPause) audioRef.current.pause()
    else audioRef.current.play().catch(() => {})
  }, [enPause])

  useEffect(() => {
    nettoyerMinuteur()
    if (!ligneCourante || enPause || termine) return
    if (texteAffiche.length < ligneCourante.texte.length) return
    if (!audioTermine) return
    minuteurRef.current = setTimeout(avancer, 500)
    return nettoyerMinuteur
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [texteAffiche, enPause, termine, audioTermine])

  useEffect(() => arreterAudio, [])

  return (
    <div className="page page-theatre">
      <h1>🧭 Le Voyage de l'IA</h1>
      <p className="page-intro">
        Clio et Marco traversent, dans un seul récit continu, toutes les grandes familles de
        modèles présentes sur ce site — génératifs, embeddings, encodeurs spécialisés, vision,
        audio, algorithmes classiques, entraînement, puis la construction d'un agent — chacune
        illustrée par un petit schéma animé. Écrit à la main (pas généré en direct par une IA,
        pour garantir des explications fiables), narré par la même voix neuronale Piper que le
        Théâtre.
      </p>

      {chargement && <p>Chargement du voyage…</p>}
      {erreur && <p className="erreur">{erreur}</p>}

      {!chargement && chapitres.length > 0 && (
        <div className="voyage-nav-chapitres">
          {chapitres.map((c, i) => (
            <button
              key={c.id}
              className={
                'voyage-chapitre-chip' +
                (demarre && i === chapitreIndex && !termine ? ' actif' : '') +
                (demarre && (i < chapitreIndex || termine) ? ' termine' : '')
              }
              onClick={() => allerAuChapitre(i)}
            >
              {i + 1}. {c.titre}
            </button>
          ))}
        </div>
      )}

      {demarre && chapitreCourant && !termine && (
        <>
          <p className="voyage-progression">
            Chapitre {chapitreIndex + 1} / {chapitres.length} — {chapitreCourant.titre}
          </p>

          <div className="theatre-scene">
            <Decor key={`${chapitreIndex}-${chapitreCourant.decor}`} decor={chapitreCourant.decor} />

            <div className="theatre-personnages">
              <Personnage
                type="clio"
                decor={chapitreCourant.decor}
                parle={ligneCourante?.personnage === 'clio'}
                actif
                variante={ligneIndex % 2 === 0}
                emotion={
                  ligneCourante?.personnage === 'clio'
                    ? ligneCourante?.emotion
                    : REACTION_AUDITEUR[ligneCourante?.emotion || 'neutre']
                }
              />
              <Personnage
                type="marco"
                decor={chapitreCourant.decor}
                parle={ligneCourante?.personnage === 'marco'}
                actif
                variante={ligneIndex % 2 === 0}
                emotion={
                  ligneCourante?.personnage === 'marco'
                    ? ligneCourante?.emotion
                    : REACTION_AUDITEUR[ligneCourante?.emotion || 'neutre']
                }
              />
            </div>

            <div className="theatre-controles">
              <button onClick={reculer} disabled={chapitreIndex === 0 && ligneIndex === 0}>
                ◀ Précédent
              </button>
              <button onClick={() => setEnPause((p) => !p)}>{enPause ? '▶ Reprendre' : '⏸ Pause'}</button>
              <button onClick={avancer}>Suivant ▶</button>
              <button
                onClick={() => {
                  arreterAudio()
                  setSonActif((s) => !s)
                }}
              >
                {sonActif ? '🔊 Son' : '🔇 Muet'}
              </button>
            </div>
          </div>

          {ligneCourante && (
            <div className="theatre-dialogue">
              <div className="theatre-dialogue-nom">{NOMS[ligneCourante.personnage as 'clio' | 'marco']}</div>
              <p className="theatre-dialogue-texte">{texteAffiche}</p>
            </div>
          )}

          <div className="voyage-schema-bloc">
            <p className="voyage-schema-titre">Le principe, en un schéma</p>
            <SchemaDiagram key={chapitreIndex} etapes={chapitreCourant.schema} />
          </div>
        </>
      )}

      {termine && (
        <div className="voyage-fin">
          <p>— Fin du voyage —</p>
          <button onClick={() => allerAuChapitre(0)}>Revoir depuis le début</button>
        </div>
      )}
    </div>
  )
}
