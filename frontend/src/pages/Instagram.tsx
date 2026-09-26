import { useEffect, useState } from 'react'
import {
  annulerPlanification,
  demarrerPublicationCarrousel,
  demarrerPublicationInstagram,
  demarrerPublicationReel,
  demarrerPublicationStory,
  enregistrerConnaissance,
  enregistrerPromptInstagram,
  genererCarrousel,
  genererLegendeInstagram,
  genererReel,
  genererStory,
  envoyerMessageDM,
  lireCommentairesInstagram,
  lireDashboardInstagram,
  lireHistoriqueInstagram,
  lireIndicateursInstagram,
  lireApercuSecteur,
  lireHistoriqueCompte,
  lireMessagesDM,
  lirePromptsInstagram,
  lireStatsLienBio,
  listerConnaissances,
  listerConversationsDM,
  listerEffets,
  listerMusiquesReel,
  listerPlanifications,
  planifierInstagram,
  prendreInstantaneCompte,
  publierMaintenantPlanification,
  rafraichirToutesLesStatsInstagram,
  reinitialiserConnaissance,
  reinitialiserPromptInstagram,
  statutPublicationCarrousel,
  statutPublicationInstagram,
  statutPublicationReel,
  statutPublicationStory,
  urlApercuEffet,
  urlApercuMusiqueReel,
  type ApercuSecteur,
  type CommentaireInstagram,
  type Connaissance,
  type ConversationDM,
  type DashboardInstagram,
  type EffetVisuel,
  type EntreeHistoriqueInstagram,
  type EntreePlanification,
  type IndicateursInstagram,
  type InstantaneCompte,
  type MessageDM,
  type MusiqueReel,
  type PromptsInstagram,
  type SlideCarrousel,
  type StatsLienBio,
} from '../api/client'

type Image =
  | 'aleatoire'
  | 'logo'
  | 'presentation'
  | 'monogramme'
  | 'signature'
  | 'motif'
  | 'strategie'
  | 'automatisation'
  | 'performance'
  | 'innovation'
  | 'partenariat'
  | 'excellence'
type Ton = 'direct' | 'pedagogique' | 'storytelling'
type Secteur = 'aucun' | 'btp' | 'banque_assurance' | 'agriculture' | 'rh_juridique' | 'ecommerce'
type Etape = 'formulaire' | 'apercu' | 'resultat'
type ModePost = 'simple' | 'carrousel' | 'story' | 'reel'

const OPTIONS_IMAGE: { id: Image; label: string; apercu: string | null }[] = [
  { id: 'aleatoire', label: 'Aléatoire', apercu: null },
  { id: 'logo', label: 'Logo TKonsulting', apercu: 'https://tkonsulting.fr/instagram/logo-1.jpg' },
  { id: 'presentation', label: 'Présentation', apercu: 'https://tkonsulting.fr/instagram/presentation-1.jpg' },
  // Templates issus de la charte graphique (noir & or, Cormorant Garamond + Inter, monogramme
  // officiel) — des visuels génériques pour un post sans photo dédiée.
  { id: 'monogramme', label: 'Monogramme', apercu: 'https://tkonsulting.fr/instagram/monogramme-2.jpg' },
  { id: 'signature', label: 'Signature', apercu: 'https://tkonsulting.fr/instagram/signature-2.jpg' },
  { id: 'motif', label: 'Motif', apercu: 'https://tkonsulting.fr/instagram/motif-2.jpg' },
  // Templates thématiques — un pictogramme de la charte par sujet de post, pour illustrer
  // directement le thème plutôt qu'un visuel générique.
  { id: 'strategie', label: 'Stratégie', apercu: 'https://tkonsulting.fr/instagram/strategie-1.jpg' },
  { id: 'automatisation', label: 'Automatisation', apercu: 'https://tkonsulting.fr/instagram/automatisation-1.jpg' },
  { id: 'performance', label: 'Performance', apercu: 'https://tkonsulting.fr/instagram/performance-1.jpg' },
  { id: 'innovation', label: 'Innovation', apercu: 'https://tkonsulting.fr/instagram/innovation-1.jpg' },
  { id: 'partenariat', label: 'Partenariat', apercu: 'https://tkonsulting.fr/instagram/partenariat-1.jpg' },
  { id: 'excellence', label: 'Excellence', apercu: 'https://tkonsulting.fr/instagram/excellence-1.jpg' },
]

const OPTIONS_TON: { id: Ton; label: string; description: string }[] = [
  { id: 'direct', label: 'Direct', description: 'Court, orienté résultats, sans formule creuse.' },
  { id: 'pedagogique', label: 'Pédagogique', description: 'Vulgarise un concept simplement.' },
  { id: 'storytelling', label: 'Storytelling', description: 'Ouvre sur une mise en situation concrète.' },
]

const OPTIONS_SECTEUR: { id: Secteur; label: string }[] = [
  { id: 'aucun', label: 'Généraliste' },
  { id: 'btp', label: 'BTP / Artisan' },
  { id: 'banque_assurance', label: 'Banque / Assurance' },
  { id: 'agriculture', label: 'Agriculture' },
  { id: 'rh_juridique', label: 'RH / Juridique' },
  { id: 'ecommerce', label: 'E-commerce' },
]

const SUJETS_EXEMPLES = [
  "l'automatisation des tâches répétitives pour une PME",
  "la valeur d'un audit stratégique avant un projet de transformation",
  'les bénéfices concrets du conseil en pilotage de projet',
  'pourquoi soigner son image de marque en 2026',
]

const SUJETS_EXEMPLES_CARROUSEL = [
  "l'IA comme moteur de recherche interne pour retrouver l'information de l'entreprise",
  'les bases de la gestion de la connaissance (knowledge management) en PME',
  "pourquoi un moteur de recherche classique ne suffit plus face au volume de documents",
]

const NOMS_TON: Record<string, string> = { direct: 'Direct', pedagogique: 'Pédagogique', storytelling: 'Storytelling' }
const NOMS_IMAGE: Record<string, string> = {
  aleatoire: 'Aléatoire',
  logo: 'Logo',
  presentation: 'Présentation',
  monogramme: 'Monogramme',
  signature: 'Signature',
  motif: 'Motif',
  strategie: 'Stratégie',
  automatisation: 'Automatisation',
  performance: 'Performance',
  innovation: 'Innovation',
  partenariat: 'Partenariat',
  excellence: 'Excellence',
  '': 'Aléatoire',
}
const NOMS_SECTEUR: Record<string, string> = {
  aucun: '',
  btp: 'BTP/Artisan',
  banque_assurance: 'Banque/Assurance',
  agriculture: 'Agriculture',
  rh_juridique: 'RH/Juridique',
  ecommerce: 'E-commerce',
}

// Publie directement sur Instagram depuis iaeasy — appelle en arrière-plan le workflow n8n déjà
// construit (publication Graph API), avec une interface plus riche que le simple formulaire n8n :
// choix du ton éditorial, aperçu de la légende AVANT envoi (ce qui est validé ici est exactement
// ce qui part — le workflow n8n n'en régénère plus une différente), et historique consultable.
export default function Instagram() {
  const [motDePasse, setMotDePasse] = useState('')
  const [connecte, setConnecte] = useState(false)
  const [erreurConnexion, setErreurConnexion] = useState<string | null>(null)

  const [etape, setEtape] = useState<Etape>('formulaire')
  const [etapeFormulaire, setEtapeFormulaire] = useState<'format' | 'contenu' | 'personnaliser'>('format')
  const [modePost, setModePost] = useState<ModePost>('simple')
  const [sujet, setSujet] = useState('')
  const [image, setImage] = useState<Image>('aleatoire')
  const [ton, setTon] = useState<Ton>('direct')
  const [secteur, setSecteur] = useState<Secteur>('aucun')
  const [apercuSecteur, setApercuSecteur] = useState<ApercuSecteur | null>(null)
  const [apercuSecteurChargement, setApercuSecteurChargement] = useState(false)
  const [connaissancesDisponibles, setConnaissancesDisponibles] = useState<Connaissance[]>([])
  const [connaissance, setConnaissance] = useState('aucune')
  const [connaissancesEnCoursEdition, setConnaissancesEnCoursEdition] = useState<Record<string, string>>({})
  const [connaissanceEnCoursSauvegarde, setConnaissanceEnCoursSauvegarde] = useState<string | null>(null)
  const [effetApercuAgrandi, setEffetApercuAgrandi] = useState<string | null>(null)
  const [legende, setLegende] = useState('')
  const [legendeRegeneree, setLegendeRegeneree] = useState(false)
  const [nbSlides, setNbSlides] = useState(5)
  const [carrouselId, setCarrouselId] = useState('')
  const [slides, setSlides] = useState<SlideCarrousel[]>([])
  const [nbScenesStory, setNbScenesStory] = useState(1)
  const [storyId, setStoryId] = useState('')
  const [storyTextes, setStoryTextes] = useState<string[]>([])
  const [storyImageUrls, setStoryImageUrls] = useState<string[]>([])
  const [musiques, setMusiques] = useState<MusiqueReel[]>([])
  const [musique, setMusique] = useState('')
  const [musiqueEnEcoute, setMusiqueEnEcoute] = useState<string | null>(null)
  const [audioApercu] = useState(() => (typeof Audio !== 'undefined' ? new Audio() : null))
  const [nbScenesReel, setNbScenesReel] = useState(1)
  const [reelId, setReelId] = useState('')
  const [reelTexte, setReelTexte] = useState('')
  const [reelVideoUrl, setReelVideoUrl] = useState('')

  const [enCours, setEnCours] = useState(false)
  const [etapeTexte, setEtapeTexte] = useState('')
  const [erreur, setErreur] = useState<string | null>(null)
  const [resultat, setResultat] = useState<string | null>(null)

  // Un seul panneau de menu actif à la fois (comme des onglets) — jamais 5 booléens indépendants
  // qui pouvaient rester "ouverts" simultanément et se superposer visuellement.
  const [panneauActif, setPanneauActif] = useState<
    'publication' | 'historique' | 'messages' | 'fileAttente' | 'dashboard' | 'prompts'
  >('publication')
  const historiqueOuvert = panneauActif === 'historique'
  const messagesOuvert = panneauActif === 'messages'
  const fileAttenteOuverte = panneauActif === 'fileAttente'
  const dashboardOuvert = panneauActif === 'dashboard'
  const promptsOuvert = panneauActif === 'prompts'

  const [historique, setHistorique] = useState<EntreeHistoriqueInstagram[] | null>(null)
  const [historiqueChargement, setHistoriqueChargement] = useState(false)
  const [indicateurs, setIndicateurs] = useState<Record<number, IndicateursInstagram | 'chargement' | 'erreur'>>({})
  const [commentaires, setCommentaires] = useState<Record<number, CommentaireInstagram[] | 'chargement' | 'erreur'>>({})

  const [conversations, setConversations] = useState<ConversationDM[] | null>(null)
  const [conversationsChargement, setConversationsChargement] = useState(false)
  const [conversationOuverte, setConversationOuverte] = useState<string | null>(null)
  const [messagesThread, setMessagesThread] = useState<Record<string, MessageDM[] | 'chargement' | 'erreur'>>({})
  const [reponseTexte, setReponseTexte] = useState('')
  const [envoiEnCours, setEnvoiEnCours] = useState(false)

  const [fileAttente, setFileAttente] = useState<EntreePlanification[] | null>(null)
  const [fileAttenteChargement, setFileAttenteChargement] = useState(false)
  const [dateProgrammation, setDateProgrammation] = useState('')

  const [dashboard, setDashboard] = useState<DashboardInstagram | null>(null)
  const [dashboardChargement, setDashboardChargement] = useState(false)
  const [rafraichissementTout, setRafraichissementTout] = useState(false)
  const [historiqueCompte, setHistoriqueCompte] = useState<InstantaneCompte[] | null>(null)
  const [instantaneEnCours, setInstantaneEnCours] = useState(false)

  const [prompts, setPrompts] = useState<PromptsInstagram | null>(null)
  const [promptsDefauts, setPromptsDefauts] = useState<PromptsInstagram | null>(null)
  const [promptsChargement, setPromptsChargement] = useState(false)
  const [promptEnCours, setPromptEnCours] = useState<string | null>(null)
  const [statsLienBio, setStatsLienBio] = useState<StatsLienBio | null>(null)
  const [lienBioCopie, setLienBioCopie] = useState<string | null>(null)
  const [effetsDisponibles, setEffetsDisponibles] = useState<EffetVisuel[]>([])
  const [effet, setEffet] = useState('')

  useEffect(() => {
    listerMusiquesReel()
      .then((m) => {
        setMusiques(m)
        if (m.length > 0) setMusique(m[0].id)
      })
      .catch(() => {})
    listerEffets()
      .then((e) => {
        setEffetsDisponibles(e)
        if (e.length > 0) {
          setEffet(e[0].id)
          setEffetApercuAgrandi(e[0].id)
        }
      })
      .catch(() => {})
    listerConnaissances()
      .then((c) => {
        setConnaissancesDisponibles(c)
        setConnaissancesEnCoursEdition(Object.fromEntries(c.map((x) => [x.id, x.texte])))
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!connecte) return
    setApercuSecteurChargement(true)
    lireApercuSecteur(motDePasse, secteur)
      .then(setApercuSecteur)
      .catch(() => setApercuSecteur(null))
      .finally(() => setApercuSecteurChargement(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secteur, connecte])

  function connexion() {
    if (!motDePasse.trim()) return
    setErreurConnexion(null)
    setConnecte(true)
  }

  async function genererApercu() {
    setEnCours(true)
    setErreur(null)
    try {
      const r = await genererLegendeInstagram(motDePasse, sujet, ton, secteur, connaissance)
      setLegende(r.legende)
      setLegendeRegeneree(r.regenere)
      setEtape('apercu')
    } catch (e: any) {
      if (e.message === 'Mot de passe incorrect.') setConnecte(false)
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  async function genererApercuCarrousel() {
    setEnCours(true)
    setErreur(null)
    try {
      const r = await genererCarrousel(motDePasse, sujet, ton, secteur, nbSlides, effet, connaissance)
      setCarrouselId(r.carrousel_id)
      setSlides(r.slides)
      setLegende(r.legende)
      setEtape('apercu')
    } catch (e: any) {
      if (e.message === 'Mot de passe incorrect.') setConnecte(false)
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  async function genererApercuStory() {
    setEnCours(true)
    setErreur(null)
    try {
      const r = await genererStory(motDePasse, sujet, ton, secteur, nbScenesStory, effet, connaissance)
      setStoryId(r.story_id)
      setStoryTextes(r.textes)
      setStoryImageUrls(r.image_urls)
      setEtape('apercu')
    } catch (e: any) {
      if (e.message === 'Mot de passe incorrect.') setConnecte(false)
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  async function genererApercuReel() {
    setEnCours(true)
    setErreur(null)
    try {
      const r = await genererReel(motDePasse, sujet, ton, secteur, musique, nbScenesReel, effet, connaissance)
      setReelId(r.reel_id)
      setReelTexte(r.texte)
      setReelVideoUrl(r.video_url)
      setLegende(r.legende)
      setEtape('apercu')
    } catch (e: any) {
      if (e.message === 'Mot de passe incorrect.') setConnecte(false)
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  async function confirmerPublication() {
    setEnCours(true)
    setErreur(null)
    const libellesEnCours: Record<ModePost, string> = {
      simple: 'Publication en cours sur Instagram…',
      carrousel: 'Publication du carrousel en cours sur Instagram…',
      story: 'Publication de la story en cours sur Instagram…',
      reel: 'Publication du reel en cours sur Instagram… (peut prendre jusqu’à 2 minutes)',
    }
    setEtapeTexte(libellesEnCours[modePost])
    try {
      const { job_id } =
        modePost === 'carrousel'
          ? await demarrerPublicationCarrousel(motDePasse, carrouselId, slides.length, legende)
          : modePost === 'story'
            ? await demarrerPublicationStory(motDePasse, storyId)
            : modePost === 'reel'
              ? await demarrerPublicationReel(motDePasse, reelId, legende)
              : await demarrerPublicationInstagram(motDePasse, sujet, image, ton, secteur, legende)
      while (true) {
        await new Promise((r) => setTimeout(r, 2000))
        const statut =
          modePost === 'carrousel'
            ? await statutPublicationCarrousel(job_id)
            : modePost === 'story'
              ? await statutPublicationStory(job_id)
              : modePost === 'reel'
                ? await statutPublicationReel(job_id)
                : await statutPublicationInstagram(job_id)
        if (statut.status === 'termine') {
          setResultat(statut.resultat || 'Publié.')
          setEtape('resultat')
          break
        }
        if (statut.status === 'erreur') {
          if (statut.erreur === 'Mot de passe incorrect.') setConnecte(false)
          throw new Error(statut.erreur || 'Erreur pendant la publication.')
        }
      }
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setEnCours(false)
      setEtapeTexte('')
    }
  }

  function recommencer() {
    setEtape('formulaire')
    setEtapeFormulaire('format')
    setSujet('')
    setLegende('')
    setResultat(null)
    setErreur(null)
    setCarrouselId('')
    setSlides([])
    setStoryId('')
    setStoryTextes([])
    setStoryImageUrls([])
    setReelId('')
    setReelTexte('')
    setReelVideoUrl('')
  }

  async function chargerFileAttente() {
    setFileAttenteChargement(true)
    try {
      setFileAttente(await listerPlanifications(motDePasse))
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setFileAttenteChargement(false)
    }
  }

  async function chargerDashboard() {
    setDashboardChargement(true)
    try {
      setDashboard(await lireDashboardInstagram(motDePasse))
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setDashboardChargement(false)
    }
  }

  async function chargerHistoriqueCompte() {
    try {
      setHistoriqueCompte(await lireHistoriqueCompte(motDePasse))
    } catch (e: any) {
      setErreur(e.message)
    }
  }

  async function chargerStatsLienBio() {
    try {
      setStatsLienBio(await lireStatsLienBio(motDePasse))
    } catch (e: any) {
      setErreur(e.message)
    }
  }

  async function ouvrirDashboard() {
    const ouverture = !dashboardOuvert
    setPanneauActif(ouverture ? 'dashboard' : 'publication')
    if (ouverture) {
      await chargerDashboard()
      await chargerHistoriqueCompte()
      await chargerStatsLienBio()
    }
  }

  async function ouvrirPrompts() {
    const ouverture = !promptsOuvert
    setPanneauActif(ouverture ? 'prompts' : 'publication')
    if (ouverture && !prompts) {
      setPromptsChargement(true)
      try {
        const r = await lirePromptsInstagram(motDePasse)
        setPrompts(r.prompts)
        setPromptsDefauts(r.defauts)
      } catch (e: any) {
        setErreur(e.message)
      } finally {
        setPromptsChargement(false)
      }
    }
  }

  async function enregistrerPrompt(type: keyof PromptsInstagram) {
    if (!prompts) return
    setPromptEnCours(type)
    setErreur(null)
    try {
      await enregistrerPromptInstagram(motDePasse, type, prompts[type])
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setPromptEnCours(null)
    }
  }

  async function reinitialiserPrompt(type: keyof PromptsInstagram) {
    if (!promptsDefauts) return
    setPromptEnCours(type)
    setErreur(null)
    try {
      await reinitialiserPromptInstagram(motDePasse, type)
      setPrompts((p) => (p ? { ...p, [type]: promptsDefauts[type] } : p))
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setPromptEnCours(null)
    }
  }

  async function enregistrerConnaissanceUI(cle: string) {
    setConnaissanceEnCoursSauvegarde(cle)
    setErreur(null)
    try {
      const item = connaissancesDisponibles.find((c) => c.id === cle)
      const titre = item?.titre || cle
      const texte = connaissancesEnCoursEdition[cle] ?? ''
      await enregistrerConnaissance(motDePasse, cle, titre, texte)
      setConnaissancesDisponibles((liste) => liste.map((c) => (c.id === cle ? { ...c, texte } : c)))
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setConnaissanceEnCoursSauvegarde(null)
    }
  }

  async function reinitialiserConnaissanceUI(cle: string) {
    setConnaissanceEnCoursSauvegarde(cle)
    setErreur(null)
    try {
      await reinitialiserConnaissance(motDePasse, cle)
      const frais = await listerConnaissances()
      setConnaissancesDisponibles(frais)
      setConnaissancesEnCoursEdition(Object.fromEntries(frais.map((x) => [x.id, x.texte])))
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setConnaissanceEnCoursSauvegarde(null)
    }
  }

  function ecouterMusique(id: string) {
    if (!audioApercu) return
    if (musiqueEnEcoute === id) {
      audioApercu.pause()
      setMusiqueEnEcoute(null)
      return
    }
    audioApercu.src = urlApercuMusiqueReel(id)
    audioApercu.currentTime = 0
    audioApercu.play().catch(() => setErreur("Impossible de lire l'aperçu audio."))
    setMusiqueEnEcoute(id)
    audioApercu.onended = () => setMusiqueEnEcoute(null)
  }

  async function copierLienBio(cle: string) {
    if (!statsLienBio) return
    try {
      await navigator.clipboard.writeText(statsLienBio.urls[cle])
      setLienBioCopie(cle)
      setTimeout(() => setLienBioCopie(null), 2000)
    } catch {
      setErreur('Impossible de copier le lien automatiquement — sélectionne-le et copie-le manuellement.')
    }
  }

  async function prendreInstantane() {
    setInstantaneEnCours(true)
    setErreur(null)
    try {
      await prendreInstantaneCompte(motDePasse)
      await chargerHistoriqueCompte()
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setInstantaneEnCours(false)
    }
  }

  async function rafraichirToutesLesStats() {
    setRafraichissementTout(true)
    try {
      await rafraichirToutesLesStatsInstagram(motDePasse)
      await chargerDashboard()
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setRafraichissementTout(false)
    }
  }

  async function ouvrirFileAttente() {
    const ouverture = !fileAttenteOuverte
    setPanneauActif(ouverture ? 'fileAttente' : 'publication')
    if (ouverture) await chargerFileAttente()
  }

  async function enregistrerPlanification(programmePour: number | null) {
    setEnCours(true)
    setErreur(null)
    try {
      if (modePost === 'carrousel') {
        await planifierInstagram(motDePasse, {
          type: 'carrousel',
          legende,
          carrouselId,
          nbSlides: slides.length,
          programmePour,
        })
      } else if (modePost === 'story') {
        await planifierInstagram(motDePasse, { type: 'story', sujet, storyId, programmePour })
      } else if (modePost === 'reel') {
        await planifierInstagram(motDePasse, { type: 'reel', sujet, reelId, legende, programmePour })
      } else {
        await planifierInstagram(motDePasse, { type: 'simple', sujet, ton, secteur, legende, image, programmePour })
      }
      recommencer()
      setPanneauActif('fileAttente')
      await chargerFileAttente()
    } catch (e: any) {
      if (e.message === 'Mot de passe incorrect.') setConnecte(false)
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  async function annulerEntreeFileAttente(id: string) {
    try {
      await annulerPlanification(motDePasse, id)
      chargerFileAttente()
    } catch (e: any) {
      setErreur(e.message)
    }
  }

  async function publierEntreeFileAttenteMaintenant(id: string) {
    try {
      await publierMaintenantPlanification(motDePasse, id)
      chargerFileAttente()
    } catch (e: any) {
      setErreur(e.message)
    }
  }

  async function ouvrirHistorique() {
    const ouverture = !historiqueOuvert
    setPanneauActif(ouverture ? 'historique' : 'publication')
    if (ouverture && !historique) {
      setHistoriqueChargement(true)
      try {
        setHistorique(await lireHistoriqueInstagram(motDePasse))
      } catch (e: any) {
        setErreur(e.message)
      } finally {
        setHistoriqueChargement(false)
      }
    }
  }

  function idPublication(source: string | null): string | null {
    if (!source) return null
    try {
      return JSON.parse(source).id || null
    } catch {
      return null
    }
  }

  function formatDate(horodatage: number) {
    return new Date(horodatage * 1000).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' })
  }

  async function rafraichirStats(index: number, mediaId: string) {
    setIndicateurs((prev) => ({ ...prev, [index]: 'chargement' }))
    try {
      const donnees = await lireIndicateursInstagram(motDePasse, mediaId)
      setIndicateurs((prev) => ({ ...prev, [index]: donnees }))
    } catch {
      setIndicateurs((prev) => ({ ...prev, [index]: 'erreur' }))
    }
  }

  async function basculerCommentaires(index: number, mediaId: string) {
    if (commentaires[index]) {
      setCommentaires((prev) => {
        const copie = { ...prev }
        delete copie[index]
        return copie
      })
      return
    }
    setCommentaires((prev) => ({ ...prev, [index]: 'chargement' }))
    try {
      const donnees = await lireCommentairesInstagram(motDePasse, mediaId)
      setCommentaires((prev) => ({ ...prev, [index]: donnees }))
    } catch {
      setCommentaires((prev) => ({ ...prev, [index]: 'erreur' }))
    }
  }

  async function ouvrirMessages() {
    const ouverture = !messagesOuvert
    setPanneauActif(ouverture ? 'messages' : 'publication')
    if (ouverture && !conversations) {
      setConversationsChargement(true)
      try {
        setConversations(await listerConversationsDM(motDePasse))
      } catch (e: any) {
        setErreur(e.message)
      } finally {
        setConversationsChargement(false)
      }
    }
  }

  function correspondantDe(conv: ConversationDM) {
    const participants = conv.participants?.data || []
    return participants.find((p) => p.username && p.username !== 'tkonsulting') || participants[0]
  }

  async function basculerConversation(conv: ConversationDM) {
    if (conversationOuverte === conv.id) {
      setConversationOuverte(null)
      return
    }
    setConversationOuverte(conv.id)
    setReponseTexte('')
    if (!messagesThread[conv.id]) {
      setMessagesThread((prev) => ({ ...prev, [conv.id]: 'chargement' }))
      try {
        const donnees = await lireMessagesDM(motDePasse, conv.id)
        setMessagesThread((prev) => ({ ...prev, [conv.id]: donnees }))
      } catch {
        setMessagesThread((prev) => ({ ...prev, [conv.id]: 'erreur' }))
      }
    }
  }

  async function envoyerReponseDM(conv: ConversationDM) {
    const destinataire = correspondantDe(conv)
    if (!destinataire || !reponseTexte.trim()) return
    setEnvoiEnCours(true)
    setErreur(null)
    try {
      await envoyerMessageDM(motDePasse, destinataire.id, reponseTexte.trim())
      setReponseTexte('')
      const donnees = await lireMessagesDM(motDePasse, conv.id)
      setMessagesThread((prev) => ({ ...prev, [conv.id]: donnees }))
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setEnvoiEnCours(false)
    }
  }

  const apercuImage = OPTIONS_IMAGE.find((o) => o.id === image)?.apercu || OPTIONS_IMAGE[1].apercu

  if (!connecte) {
    return (
      <div className="page page-admin">
        <h1>📸 Publier sur Instagram</h1>
        <p className="page-intro">Accès réservé — saisissez le mot de passe pour continuer.</p>
        <div className="admin-connexion">
          <input
            type="password"
            value={motDePasse}
            onChange={(e) => setMotDePasse(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && connexion()}
            placeholder="Mot de passe"
          />
          <button onClick={connexion} disabled={!motDePasse}>
            Se connecter
          </button>
        </div>
        {erreurConnexion && <p className="erreur">{erreurConnexion}</p>}
      </div>
    )
  }

  return (
    <div className="page page-admin">
      <div className="insta-entete">
        <div>
          <h1>📸 Publier sur Instagram — @tkonsulting</h1>
          <p className="page-intro">
            Décris le sujet, choisis un ton et un visuel : une légende est générée puis relue par
            un second passage IA (garde-fou de ton) avant de t'être montrée — ce que tu valides ici
            est exactement ce qui part sur Instagram, rien n'est régénéré en cours de route.
          </p>
        </div>
        <div className="insta-entete-boutons">
          <button
            className={'insta-historique-bouton' + (panneauActif === 'publication' ? ' actif' : '')}
            onClick={() => setPanneauActif('publication')}
          >
            ✍️ Publication
          </button>
          <button className={'insta-historique-bouton' + (messagesOuvert ? ' actif' : '')} onClick={ouvrirMessages}>
            💌 Messages
          </button>
          <button className={'insta-historique-bouton' + (dashboardOuvert ? ' actif' : '')} onClick={ouvrirDashboard}>
            📊 Tableau de bord
          </button>
          <button className={'insta-historique-bouton' + (fileAttenteOuverte ? ' actif' : '')} onClick={ouvrirFileAttente}>
            📋 File d’attente
          </button>
          <button className={'insta-historique-bouton' + (historiqueOuvert ? ' actif' : '')} onClick={ouvrirHistorique}>
            🕓 Historique
          </button>
          <button className={'insta-historique-bouton' + (promptsOuvert ? ' actif' : '')} onClick={ouvrirPrompts}>
            🧠 Prompts
          </button>
        </div>
      </div>

      {promptsOuvert && (
        <div className="insta-historique">
          <p className="texte-muted note">
            Le prompt exact envoyé à Claude pour générer le texte, modifiable par toi. "Accroche courte" sert à la
            fois à une story à 1 carte et à un reel à 1 scène ; "Plan multi-slides" sert au carrousel, à un reel à
            plusieurs scènes et à une story à plusieurs cartes — les modifier change donc plusieurs formats à la fois.
          </p>
          {promptsChargement && <p className="texte-muted note">Chargement…</p>}
          {prompts && (
            <>
              {(
                [
                  ['legende', 'Légende (post simple)'],
                  ['story', 'Accroche courte (story 1 carte / reel 1 scène)'],
                  ['carrousel', 'Plan multi-slides (carrousel / reel plusieurs scènes / story plusieurs cartes)'],
                ] as [keyof PromptsInstagram, string][]
              ).map(([type, label]) => (
                <div key={type} style={{ marginBottom: '1rem' }}>
                  <p className="insta-label" style={{ fontSize: '0.85rem' }}>{label}</p>
                  <textarea
                    className="insta-sujet"
                    value={prompts[type]}
                    onChange={(e) => setPrompts((p) => (p ? { ...p, [type]: e.target.value } : p))}
                    rows={8}
                    disabled={promptEnCours === type}
                  />
                  <p className="texte-muted note">
                    Variables disponibles : {'{{SUJET}}'}, {'{{TON}}'}, {'{{SECTEUR}}'}, {'{{HASHTAGS}}'}, {'{{CONNAISSANCE}}'}
                    {type === 'carrousel' ? ', {{NB_SLIDES}}' : ''} — remplacées automatiquement à la génération.
                  </p>
                  <div className="insta-apercu-actions">
                    <button onClick={() => enregistrerPrompt(type)} disabled={promptEnCours === type}>
                      {promptEnCours === type ? 'Enregistrement…' : '💾 Enregistrer'}
                    </button>
                    <button onClick={() => reinitialiserPrompt(type)} disabled={promptEnCours === type}>
                      ↺ Réinitialiser au défaut
                    </button>
                  </div>
                </div>
              ))}
            </>
          )}

          {connaissancesDisponibles.length > 0 && (
            <>
              <p className="insta-label" style={{ marginTop: '1.2rem' }}>Connaissances par sujet</p>
              <p className="texte-muted note">
                Les faits réels réutilisés dans le prompt (variable {'{{CONNAISSANCE}}'}) quand tu choisis un sujet à
                l'étape Contenu — jamais inventés, jamais mélangés à un autre sujet.
              </p>
              {connaissancesDisponibles.map((c) => (
                <div key={c.id} style={{ marginBottom: '1rem' }}>
                  <p className="insta-label" style={{ fontSize: '0.85rem' }}>{c.titre}</p>
                  <textarea
                    className="insta-sujet"
                    value={connaissancesEnCoursEdition[c.id] ?? c.texte}
                    onChange={(e) =>
                      setConnaissancesEnCoursEdition((v) => ({ ...v, [c.id]: e.target.value }))
                    }
                    rows={6}
                    disabled={connaissanceEnCoursSauvegarde === c.id}
                  />
                  <div className="insta-apercu-actions">
                    <button onClick={() => enregistrerConnaissanceUI(c.id)} disabled={connaissanceEnCoursSauvegarde === c.id}>
                      {connaissanceEnCoursSauvegarde === c.id ? 'Enregistrement…' : '💾 Enregistrer'}
                    </button>
                    <button
                      onClick={() => reinitialiserConnaissanceUI(c.id)}
                      disabled={connaissanceEnCoursSauvegarde === c.id}
                    >
                      ↺ Réinitialiser au défaut
                    </button>
                  </div>
                </div>
              ))}
            </>
          )}
          {erreur && <p className="erreur">{erreur}</p>}
        </div>
      )}

      {messagesOuvert && (
        <div className="insta-historique">
          <p className="texte-muted note">
            Messages privés reçus sur @tkonsulting — chaque réponse est écrite et envoyée par toi, rien n'est
            automatisé.
          </p>
          {conversationsChargement && <p className="texte-muted">Chargement…</p>}
          {conversations && conversations.length === 0 && <p className="texte-muted">Aucun message pour l'instant.</p>}
          {conversations && conversations.length > 0 && (
            <ul className="insta-historique-liste">
              {conversations.map((conv) => {
                const correspondant = correspondantDe(conv)
                const fil = messagesThread[conv.id]
                return (
                  <li key={conv.id} className="insta-historique-item">
                    <div className="insta-historique-corps">
                      <div className="insta-historique-ligne1">
                        <strong>@{correspondant?.username || 'inconnu'}</strong>
                        <button type="button" className="chip" onClick={() => basculerConversation(conv)}>
                          {conversationOuverte === conv.id ? '✖ Fermer' : '💬 Ouvrir'}
                        </button>
                      </div>
                      {conversationOuverte === conv.id && (
                        <>
                          {fil === 'chargement' && <p className="texte-muted note">Chargement…</p>}
                          {fil === 'erreur' && <p className="erreur">Messages indisponibles.</p>}
                          {Array.isArray(fil) && (
                            <ul className="insta-commentaires-liste">
                              {fil.length === 0 && <li className="texte-muted note">Aucun message.</li>}
                              {[...fil].reverse().map((m) => (
                                <li key={m.id} className="insta-commentaire-item">
                                  <strong>{m.from?.username === 'tkonsulting' ? 'Toi' : '@' + (m.from?.username || '?')}</strong>{' '}
                                  <span>{m.message}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                          <div className="insta-reponse-dm">
                            <textarea
                              value={reponseTexte}
                              onChange={(e) => setReponseTexte(e.target.value)}
                              placeholder="Écrire une réponse…"
                              rows={2}
                              disabled={envoiEnCours}
                            />
                            <button
                              type="button"
                              onClick={() => envoyerReponseDM(conv)}
                              disabled={envoiEnCours || !reponseTexte.trim()}
                            >
                              {envoiEnCours ? 'Envoi…' : '📤 Envoyer'}
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      )}

      {dashboardOuvert && (
        <div className="insta-dashboard">
          {dashboardChargement && <p className="texte-muted">Chargement…</p>}
          {dashboard && (
            <>
              <div className="insta-dashboard-cartes">
                <div className="stat-carte">
                  <span className="stat-carte-chiffre">{dashboard.publies}/{dashboard.total}</span>
                  <span className="stat-carte-label">publications réussies</span>
                </div>
                <div className="stat-carte">
                  <span className="stat-carte-chiffre">{dashboard.taux_succes ?? '—'}%</span>
                  <span className="stat-carte-label">taux de succès</span>
                </div>
                {Object.entries(dashboard.par_type).map(([type, n]) => (
                  <div className="stat-carte" key={type}>
                    <span className="stat-carte-chiffre">{n}</span>
                    <span className="stat-carte-label">
                      {{ simple: '📷 posts', carrousel: '📚 carrousels', story: '🎬 stories', reel: '🎥 reels' }[type] || type}
                    </span>
                  </div>
                ))}
              </div>

              <div className="insta-dashboard-bloc">
                <div className="insta-dashboard-bloc-entete">
                  <p className="insta-label">Croissance du compte</p>
                  <button type="button" className="chip" onClick={prendreInstantane} disabled={instantaneEnCours}>
                    {instantaneEnCours ? 'Capture…' : '📸 Prendre un instantané'}
                  </button>
                </div>
                {!historiqueCompte || historiqueCompte.length === 0 ? (
                  <p className="texte-muted note">
                    Aucun instantané pour l'instant — un est capturé automatiquement chaque jour, ou clique sur le
                    bouton pour en prendre un maintenant.
                  </p>
                ) : (
                  <>
                    <div className="insta-dashboard-cartes">
                      <div className="stat-carte">
                        <span className="stat-carte-chiffre">
                          {historiqueCompte[historiqueCompte.length - 1].followers_count}
                        </span>
                        <span className="stat-carte-label">abonnés</span>
                      </div>
                      <div className="stat-carte">
                        <span className="stat-carte-chiffre">
                          {historiqueCompte[historiqueCompte.length - 1].reach_jour}
                        </span>
                        <span className="stat-carte-label">portée (dernier jour)</span>
                      </div>
                      <div className="stat-carte">
                        <span className="stat-carte-chiffre">
                          {historiqueCompte[historiqueCompte.length - 1].profile_views_jour}
                        </span>
                        <span className="stat-carte-label">visites de profil (dernier jour)</span>
                      </div>
                    </div>
                    {historiqueCompte.length > 1 && (
                      <div className="insta-tendance-barres" style={{ marginTop: '0.8rem' }}>
                        {historiqueCompte.slice(-14).map((h) => {
                          const max = Math.max(...historiqueCompte.slice(-14).map((x) => x.followers_count), 1)
                          return (
                            <div key={h.date} className="insta-tendance-barre-colonne">
                              <div
                                className="insta-tendance-barre"
                                style={{ height: `${(h.followers_count / max) * 100}%` }}
                                title={`${h.date} — ${h.followers_count} abonnés`}
                              />
                              <span className="texte-muted insta-tendance-label">{h.date.slice(5)}</span>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className="insta-dashboard-bloc">
                <p className="insta-label">Liens en bio</p>
                {!statsLienBio ? (
                  <p className="texte-muted note">Chargement…</p>
                ) : (
                  <>
                    <p className="texte-muted note">
                      Remplace tes liens actuels dans les paramètres du profil Instagram (jusqu'à 5 liens externes
                      possibles) par ceux-ci, pour savoir combien de visiteurs Instagram amène vraiment sur chaque
                      site — pas seulement combien ont vu un post.
                    </p>
                    {Object.entries(statsLienBio.urls).map(([cle, url]) => {
                      const label =
                        { tkonsulting: 'TKonsulting.fr', lesensia: 'Lesensia.com', iaeasy: 'iaeasy (l\'appli)' }[cle] ||
                        cle
                      const historiqueLien = statsLienBio.historique.filter((h) => h.cle === cle).slice(-14)
                      const max = Math.max(...historiqueLien.map((x) => x.clics), 1)
                      return (
                        <div key={cle} style={{ marginTop: '0.8rem' }}>
                          <p className="texte-muted note" style={{ margin: '0 0 0.3rem', fontWeight: 600 }}>
                            {label} — {statsLienBio.total_par_lien[cle] ?? 0} clic(s) au total
                          </p>
                          <div className="insta-lien-bio-copie">
                            <code>{url}</code>
                            <button type="button" className="chip" onClick={() => copierLienBio(cle)}>
                              {lienBioCopie === cle ? '✅ Copié' : '📋 Copier'}
                            </button>
                          </div>
                          {historiqueLien.length > 1 && (
                            <div className="insta-tendance-barres" style={{ marginTop: '0.5rem' }}>
                              {historiqueLien.map((h) => (
                                <div key={h.date} className="insta-tendance-barre-colonne">
                                  <div
                                    className="insta-tendance-barre"
                                    style={{ height: `${(h.clics / max) * 100}%` }}
                                    title={`${h.date} — ${h.clics} clic(s)`}
                                  />
                                  <span className="texte-muted insta-tendance-label">{h.date.slice(5)}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )
                    })}

                    {(() => {
                      const totalAppareils = statsLienBio.appareils.mobile + statsLienBio.appareils.bureau
                      const heures = Object.entries(statsLienBio.heures)
                        .map(([h, n]) => ({ heure: Number(h), n }))
                        .sort((a, b) => a.heure - b.heure)
                      const maxHeure = Math.max(...heures.map((h) => h.n), 1)
                      if (totalAppareils === 0) return null
                      return (
                        <div style={{ marginTop: '1.2rem', borderTop: '1px solid var(--border)', paddingTop: '0.8rem' }}>
                          <p className="insta-label" style={{ fontSize: '0.85rem' }}>
                            Répartition anonyme des clics (tous liens confondus)
                          </p>
                          <p className="texte-muted note">
                            Instagram ne transmet aucune identité sur un clic — seulement le type d'appareil et
                            l'heure, jamais qui a cliqué.
                          </p>
                          <div className="insta-dashboard-cartes" style={{ marginTop: '0.5rem' }}>
                            <div className="stat-carte">
                              <span className="stat-carte-chiffre">
                                {Math.round((statsLienBio.appareils.mobile / totalAppareils) * 100)}%
                              </span>
                              <span className="stat-carte-label">📱 mobile</span>
                            </div>
                            <div className="stat-carte">
                              <span className="stat-carte-chiffre">
                                {Math.round((statsLienBio.appareils.bureau / totalAppareils) * 100)}%
                              </span>
                              <span className="stat-carte-label">💻 bureau</span>
                            </div>
                          </div>
                          <div className="insta-tendance-barres" style={{ marginTop: '0.8rem' }}>
                            {heures.map((h) => (
                              <div key={h.heure} className="insta-tendance-barre-colonne">
                                <div
                                  className="insta-tendance-barre"
                                  style={{ height: `${(h.n / maxHeure) * 100}%` }}
                                  title={`${h.heure}h — ${h.n} clic(s)`}
                                />
                                {h.heure % 3 === 0 && (
                                  <span className="texte-muted insta-tendance-label">{h.heure}h</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    })()}
                  </>
                )}
              </div>

              {dashboard.tendance_semaines.length > 0 && (
                <div className="insta-dashboard-bloc">
                  <p className="insta-label">Publications par semaine</p>
                  <div className="insta-tendance-barres">
                    {dashboard.tendance_semaines.map((s) => {
                      const max = Math.max(...dashboard.tendance_semaines.map((x) => x.nb), 1)
                      return (
                        <div key={s.semaine} className="insta-tendance-barre-colonne">
                          <div className="insta-tendance-barre" style={{ height: `${(s.nb / max) * 100}%` }} title={`${s.nb} publication(s)`} />
                          <span className="texte-muted insta-tendance-label">{s.semaine.replace(/^\d{4}-S/, 'S')}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              <div className="insta-dashboard-bloc">
                <div className="insta-dashboard-bloc-entete">
                  <p className="insta-label">Engagement moyen par ton éditorial</p>
                  <button type="button" className="chip" onClick={rafraichirToutesLesStats} disabled={rafraichissementTout}>
                    {rafraichissementTout ? 'Rafraîchissement…' : '🔄 Rafraîchir toutes les stats'}
                  </button>
                </div>
                {dashboard.nb_avec_indicateurs === 0 ? (
                  <p className="texte-muted note">
                    Aucune statistique en cache pour l'instant — clique sur « Rafraîchir toutes les stats » (Instagram ne
                    les transmet jamais tout seul).
                  </p>
                ) : (
                  <table className="insta-dashboard-table">
                    <thead>
                      <tr>
                        <th>Ton</th>
                        <th>Portée</th>
                        <th>Likes</th>
                        <th>Commentaires</th>
                        <th>Enregistrements</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(dashboard.engagement_par_ton).map(([ton, ind]) => (
                        <tr key={ton}>
                          <td>{NOMS_TON[ton] || ton}</td>
                          <td>{ind?.reach ?? 0}</td>
                          <td>{ind?.likes ?? 0}</td>
                          <td>{ind?.comments ?? 0}</td>
                          <td>{ind?.saved ?? 0}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {dashboard.meilleur_post && (
                <div className="insta-dashboard-bloc">
                  <p className="insta-label">Meilleure publication (portée)</p>
                  <p>
                    <strong>{dashboard.meilleur_post.sujet}</strong> — {formatDate(dashboard.meilleur_post.horodatage)}
                    <br />
                    <span className="texte-muted">
                      👁 {dashboard.meilleur_post.indicateurs.reach ?? 0} · ❤ {dashboard.meilleur_post.indicateurs.likes ?? 0} · 💬{' '}
                      {dashboard.meilleur_post.indicateurs.comments ?? 0}
                    </span>
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {fileAttenteOuverte && (
        <div className="insta-historique">
          {fileAttenteChargement && <p className="texte-muted">Chargement…</p>}
          {fileAttente && fileAttente.length === 0 && (
            <p className="texte-muted">Aucun brouillon ni post programmé pour l'instant.</p>
          )}
          {fileAttente && fileAttente.length > 0 && (
            <ul className="insta-historique-liste">
              {fileAttente.map((e) => (
                <li key={e.id} className="insta-historique-item">
                  <span className={'insta-statut-pastille ' + (e.statut === 'erreur' ? 'ko' : e.statut === 'publie' ? 'ok' : '')} />
                  <div className="insta-historique-corps">
                    <div className="insta-historique-ligne1">
                      <strong>
                        {e.type === 'carrousel'
                          ? '📚 Carrousel'
                          : e.type === 'story'
                            ? '🎬 Story'
                            : e.type === 'reel'
                              ? '🎥 Reel'
                              : '📷 ' + (e.sujet || 'Post')}
                      </strong>
                      <span className="texte-muted">
                        {e.statut === 'programme' && e.programme_pour
                          ? 'Programmé · ' + new Date(e.programme_pour * 1000).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' })
                          : e.statut === 'brouillon'
                            ? 'Brouillon'
                            : e.statut === 'en_cours'
                              ? 'Publication en cours…'
                              : e.statut === 'publie'
                                ? 'Publié'
                                : 'Échec : ' + e.erreur}
                      </span>
                    </div>
                    <div className="texte-muted">{e.legende.slice(0, 90)}{e.legende.length > 90 ? '…' : ''}</div>
                    {(e.statut === 'brouillon' || e.statut === 'programme') && (
                      <div className="insta-stats-ligne">
                        <button type="button" className="chip" onClick={() => publierEntreeFileAttenteMaintenant(e.id)}>
                          📤 Publier maintenant
                        </button>
                        <button type="button" className="chip" onClick={() => annulerEntreeFileAttente(e.id)}>
                          ✖ Annuler
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {historiqueOuvert && (
        <div className="insta-historique">
          {historiqueChargement && <p className="texte-muted">Chargement…</p>}
          {historique && historique.length === 0 && <p className="texte-muted">Aucune publication pour l'instant.</p>}
          {historique && historique.length > 0 && (
            <ul className="insta-historique-liste">
              {historique.map((h, i) => {
                const mediaId = h.statut === 'publie' ? idPublication(h.resultat || null) : null
                const stats = indicateurs[i]
                return (
                  <li key={i} className="insta-historique-item">
                    <span className={'insta-statut-pastille ' + (h.statut === 'publie' ? 'ok' : 'ko')} />
                    <div className="insta-historique-corps">
                      <div className="insta-historique-ligne1">
                        <strong>{h.sujet}</strong>
                        <span className="texte-muted">{formatDate(h.horodatage)}</span>
                      </div>
                      <div className="texte-muted">
                        {NOMS_TON[h.ton] || h.ton}
                        {h.secteur && NOMS_SECTEUR[h.secteur] ? ` · ${NOMS_SECTEUR[h.secteur]}` : ''} ·{' '}
                        {NOMS_IMAGE[h.image] ?? h.image}
                        {h.statut === 'publie' ? (mediaId ? ` · publié (#${mediaId})` : ' · publié') : ` · échec : ${h.erreur}`}
                      </div>
                      {mediaId && (
                        <div className="insta-stats-ligne">
                          {!stats && (
                            <button type="button" className="chip" onClick={() => rafraichirStats(i, mediaId)}>
                              📊 Rafraîchir les stats
                            </button>
                          )}
                          {stats === 'chargement' && <span className="texte-muted note">Chargement…</span>}
                          {stats === 'erreur' && <span className="erreur">Indicateurs indisponibles.</span>}
                          {stats && typeof stats === 'object' && (
                            <span className="texte-muted">
                              👁 {stats.reach ?? 0} · ❤ {stats.likes ?? 0} · 💬 {stats.comments ?? 0} · 🔖 {stats.saved ?? 0} · ↗{' '}
                              {stats.shares ?? 0}
                            </span>
                          )}
                          <button type="button" className="chip" onClick={() => basculerCommentaires(i, mediaId)}>
                            {commentaires[i] ? '✖ Fermer les commentaires' : '💬 Voir les commentaires'}
                          </button>
                        </div>
                      )}
                      {mediaId && commentaires[i] === 'chargement' && <p className="texte-muted note">Chargement…</p>}
                      {mediaId && commentaires[i] === 'erreur' && <p className="erreur">Commentaires indisponibles.</p>}
                      {mediaId && Array.isArray(commentaires[i]) && (
                        <ul className="insta-commentaires-liste">
                          {(commentaires[i] as CommentaireInstagram[]).length === 0 && (
                            <li className="texte-muted note">Aucun commentaire pour l'instant.</li>
                          )}
                          {(commentaires[i] as CommentaireInstagram[]).map((c) => (
                            <li key={c.id} className="insta-commentaire-item">
                              <strong>@{c.username}</strong> <span>{c.text}</span>
                              {typeof c.like_count === 'number' && c.like_count > 0 && (
                                <span className="texte-muted"> · ❤ {c.like_count}</span>
                              )}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      )}

      {panneauActif === 'publication' && etape === 'formulaire' && (
        <div className="admin-formulaire insta-formulaire">
          <div className="insta-etapes">
            <button
              type="button"
              className={'insta-etape-item' + (etapeFormulaire === 'format' ? ' actif' : '') + (etapeFormulaire !== 'format' ? ' fait' : '')}
              onClick={() => setEtapeFormulaire('format')}
            >
              <span className="insta-etape-numero">1</span>
              <span className="insta-etape-label">Format</span>
            </button>
            <span className="insta-etape-trait" />
            <button
              type="button"
              className={'insta-etape-item' + (etapeFormulaire === 'contenu' ? ' actif' : '') + (etapeFormulaire === 'personnaliser' ? ' fait' : '')}
              onClick={() => setEtapeFormulaire('contenu')}
            >
              <span className="insta-etape-numero">2</span>
              <span className="insta-etape-label">Contenu</span>
            </button>
            <span className="insta-etape-trait" />
            <button
              type="button"
              className={'insta-etape-item' + (etapeFormulaire === 'personnaliser' ? ' actif' : '')}
              onClick={() => sujet.trim().length >= 3 && setEtapeFormulaire('personnaliser')}
              disabled={sujet.trim().length < 3}
            >
              <span className="insta-etape-numero">3</span>
              <span className="insta-etape-label">Personnaliser</span>
            </button>
          </div>

          {etapeFormulaire === 'format' && (
            <>
              <div>
                <span className="insta-label">Type de publication</span>
                <div className="insta-tons">
                  <button
                    type="button"
                    className={'insta-ton-carte' + (modePost === 'simple' ? ' actif' : '')}
                    onClick={() => setModePost('simple')}
                    disabled={enCours}
                  >
                    <span className="insta-ton-label">📷 Post simple</span>
                    <span className="insta-ton-desc">Une image + une légende — annonce courte.</span>
                  </button>
                  <button
                    type="button"
                    className={'insta-ton-carte' + (modePost === 'carrousel' ? ' actif' : '')}
                    onClick={() => setModePost('carrousel')}
                    disabled={enCours}
                  >
                    <span className="insta-ton-label">📚 Carrousel</span>
                    <span className="insta-ton-desc">Un mini-article en plusieurs slides — contenu de fond.</span>
                  </button>
                  <button
                    type="button"
                    className={'insta-ton-carte' + (modePost === 'story' ? ' actif' : '')}
                    onClick={() => setModePost('story')}
                    disabled={enCours}
                  >
                    <span className="insta-ton-label">🎬 Story</span>
                    <span className="insta-ton-desc">Une accroche courte plein écran — disparaît en 24h.</span>
                  </button>
                  <button
                    type="button"
                    className={'insta-ton-carte' + (modePost === 'reel' ? ' actif' : '')}
                    onClick={() => setModePost('reel')}
                    disabled={enCours}
                  >
                    <span className="insta-ton-label">🎥 Reel</span>
                    <span className="insta-ton-desc">Vidéo verticale ~14s, animée et sonorisée (musique libre de droits).</span>
                  </button>
                </div>
              </div>

              <div className="insta-etape-nav">
                <span />
                <button type="button" onClick={() => setEtapeFormulaire('contenu')}>
                  Suivant →
                </button>
              </div>
            </>
          )}

          {etapeFormulaire === 'contenu' && (
            <>
              <label>
                Sujet du post
                <textarea
                  className="insta-sujet"
                  value={sujet}
                  onChange={(e) => setSujet(e.target.value)}
                  placeholder="Ex. : l'automatisation des tâches répétitives pour une PME"
                  rows={4}
                  disabled={enCours}
                />
              </label>

              <div className="champ-exemples">
                <span className="config-champ champ-exemples-label">Exemples :</span>
                {(modePost === 'carrousel' ? SUJETS_EXEMPLES_CARROUSEL : SUJETS_EXEMPLES).map((s) => (
                  <button key={s} type="button" className="chip chip-exemple" onClick={() => setSujet(s)} disabled={enCours}>
                    {s}
                  </button>
                ))}
              </div>

              <div>
                <span className="insta-label">Ton éditorial</span>
                <div className="insta-tons">
                  {OPTIONS_TON.map((opt) => (
                    <button
                      key={opt.id}
                      type="button"
                      className={'insta-ton-carte' + (ton === opt.id ? ' actif' : '')}
                      onClick={() => setTon(opt.id)}
                      disabled={enCours}
                    >
                      <span className="insta-ton-label">{opt.label}</span>
                      <span className="insta-ton-desc">{opt.description}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <span className="insta-label">Cibler un secteur (optionnel)</span>
                <div className="insta-secteurs">
                  {OPTIONS_SECTEUR.map((opt) => (
                    <button
                      key={opt.id}
                      type="button"
                      className={'chip' + (secteur === opt.id ? ' actif' : '')}
                      onClick={() => setSecteur(opt.id)}
                      disabled={enCours}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
                <p className="texte-muted note">
                  La légende s'adresse alors directement à ce type de prospect, avec une invitation discrète à échanger.
                </p>

                {apercuSecteurChargement && <p className="texte-muted note">Chargement de l'aperçu…</p>}
                {apercuSecteur && !apercuSecteurChargement && (
                  <div className="insta-apercu-secteur">
                    <p className="texte-muted note" style={{ margin: 0 }}>
                      {apercuSecteur.cible
                        ? `Les hashtags et le ton de la légende visent spécifiquement ${apercuSecteur.cible}.`
                        : "Aucun secteur choisi : hashtags et légende restent génériques (PME/TPE au sens large)."}
                    </p>
                    <div className="insta-apercu-secteur-hashtags">
                      {apercuSecteur.hashtags_larges.map((h) => (
                        <span key={h} className="chip insta-hashtag-large" title="Hashtag large — apporte de la portée">
                          {h}
                        </span>
                      ))}
                      {apercuSecteur.hashtags_niches.map((h) => (
                        <span key={h} className="chip insta-hashtag-niche" title="Hashtag ciblé — apporte de la pertinence">
                          {h}
                        </span>
                      ))}
                    </div>
                    <p className="texte-muted note">
                      2 à 3 de ces hashtags larges + 2 à 3 ciblés seront choisis par l'IA à la génération (jamais inventés).
                    </p>
                    <p className="texte-muted note">
                      {apercuSecteur.nb_posts_avec_donnees > 0
                        ? `D'après tes ${apercuSecteur.nb_posts_avec_donnees} post(s) précédent(s) sur ce secteur avec des statistiques disponibles, la portée moyenne réelle a été de ${apercuSecteur.reach_moyen} comptes touchés.`
                        : apercuSecteur.nb_posts_historique > 0
                          ? `${apercuSecteur.nb_posts_historique} post(s) déjà publié(s) sur ce secteur, mais pas encore de statistiques récupérées (utilise "Rafraîchir les stats" dans le Tableau de bord).`
                          : "Pas encore de post publié sur ce secteur — aucune estimation de portée n'est inventée, seulement des chiffres réels une fois que tu auras publié."}
                    </p>
                  </div>
                )}
              </div>

              {connaissancesDisponibles.length > 0 && (
                <div>
                  <span className="insta-label">Connaissance à mobiliser (optionnel)</span>
                  <div className="insta-secteurs">
                    <button
                      type="button"
                      className={'chip' + (connaissance === 'aucune' ? ' actif' : '')}
                      onClick={() => setConnaissance('aucune')}
                      disabled={enCours}
                    >
                      Aucune
                    </button>
                    {connaissancesDisponibles.map((c) => (
                      <button
                        key={c.id}
                        type="button"
                        className={'chip' + (connaissance === c.id ? ' actif' : '')}
                        onClick={() => setConnaissance(c.id)}
                        disabled={enCours}
                      >
                        {c.titre}
                      </button>
                    ))}
                  </div>
                  <p className="texte-muted note">
                    Si choisi, le texte s'appuie sur les vrais faits enregistrés pour ce sujet (voir l'onglet Prompts
                    pour les modifier) — jamais inventés au-delà.
                  </p>
                </div>
              )}

              <div className="insta-etape-nav">
                <button type="button" onClick={() => setEtapeFormulaire('format')}>
                  ← Précédent
                </button>
                <button type="button" onClick={() => setEtapeFormulaire('personnaliser')} disabled={sujet.trim().length < 3}>
                  Suivant →
                </button>
              </div>
            </>
          )}

          {etapeFormulaire === 'personnaliser' && (
            <>
          {modePost === 'simple' && (
            <div>
              <span className="insta-label">Visuel</span>
              <div className="insta-images-grille">
                {OPTIONS_IMAGE.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    className={'insta-image-carte' + (image === opt.id ? ' actif' : '')}
                    onClick={() => setImage(opt.id)}
                    disabled={enCours}
                  >
                    {opt.apercu ? <img src={opt.apercu} alt={opt.label} /> : <div className="insta-image-alea">🎲</div>}
                    <span>{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {modePost === 'carrousel' && (
            <div>
              <span className="insta-label">Nombre de slides</span>
              <div className="insta-secteurs">
                {[3, 4, 5, 6, 7, 8].map((n) => (
                  <button
                    key={n}
                    type="button"
                    className={'chip' + (nbSlides === n ? ' actif' : '')}
                    onClick={() => setNbSlides(n)}
                    disabled={enCours}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <p className="texte-muted note">
                Chaque slide est générée et illustrée automatiquement (charte noir & or, pictogrammes de la marque).
              </p>
            </div>
          )}

          {modePost === 'story' && (
            <div>
              <span className="insta-label">Nombre de cartes</span>
              <div className="insta-secteurs">
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <button
                    key={n}
                    type="button"
                    className={'chip' + (nbScenesStory === n ? ' actif' : '')}
                    onClick={() => setNbScenesStory(n)}
                    disabled={enCours}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <p className="texte-muted note">
                {nbScenesStory <= 1
                  ? "Le visuel (format 1080×1920, charte noir & or) et l'accroche sont générés automatiquement à partir du sujet."
                  : `${nbScenesStory} cartes publiées à la suite (Instagram ne permet pas plusieurs écrans dans une seule story) — une accroche par carte, comme un carrousel.`}
              </p>
            </div>
          )}

          {modePost === 'reel' && (
            <div>
              <span className="insta-label">Nombre de scènes</span>
              <div className="insta-secteurs">
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <button
                    key={n}
                    type="button"
                    className={'chip' + (nbScenesReel === n ? ' actif' : '')}
                    onClick={() => setNbScenesReel(n)}
                    disabled={enCours}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <p className="texte-muted note">
                {nbScenesReel <= 1
                  ? 'Une seule accroche, sur tout le reel.'
                  : `${nbScenesReel} scènes enchaînées (façon carrousel vidéo), une accroche par scène.`}
              </p>
              <span className="insta-label">Ambiance musicale (libre de droits)</span>
              {Object.entries(
                musiques.reduce<Record<string, MusiqueReel[]>>((groupes, m) => {
                  if (!groupes[m.categorie]) groupes[m.categorie] = []
                  groupes[m.categorie].push(m)
                  return groupes
                }, {}),
              ).map(([categorie, liste]) => (
                <div key={categorie} style={{ marginBottom: '0.5rem' }}>
                  <span className="texte-muted note" style={{ display: 'block', margin: '0.3rem 0 0.2rem' }}>
                    {categorie}
                  </span>
                  <div className="insta-secteurs">
                    {liste.map((m) => (
                      <span key={m.id} className="insta-musique-chip">
                        <button
                          type="button"
                          className={'chip' + (musique === m.id ? ' actif' : '')}
                          onClick={() => setMusique(m.id)}
                          disabled={enCours}
                        >
                          {m.label}
                        </button>
                        <button
                          type="button"
                          className="insta-musique-ecouter"
                          onClick={() => ecouterMusique(m.id)}
                          title="Écouter un aperçu"
                        >
                          {musiqueEnEcoute === m.id ? '⏸' : '▶'}
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              <p className="texte-muted note">
                Le visuel (format 1080×1920, charte noir & or, léger effet de zoom) et l'accroche sont générés
                automatiquement à partir du sujet.
              </p>
            </div>
          )}

          {modePost !== 'simple' && effetsDisponibles.length > 0 && (
            <div>
              <span className="insta-label">Effet de fond ({effetsDisponibles.length} disponibles)</span>
              {effetApercuAgrandi && (
                <div className="insta-effet-apercu-grand">
                  <img
                    src={urlApercuEffet(effetApercuAgrandi)}
                    alt={effetsDisponibles.find((e) => e.id === effetApercuAgrandi)?.label || ''}
                  />
                  <span className="texte-muted note">
                    {effetsDisponibles.find((e) => e.id === effetApercuAgrandi)?.label}
                  </span>
                </div>
              )}
              {Object.entries(
                effetsDisponibles.reduce<Record<string, EffetVisuel[]>>((groupes, e) => {
                  if (!groupes[e.categorie]) groupes[e.categorie] = []
                  groupes[e.categorie].push(e)
                  return groupes
                }, {}),
              ).map(([categorie, liste]) => (
                <div key={categorie} style={{ marginBottom: '0.7rem' }}>
                  <span className="texte-muted note" style={{ display: 'block', margin: '0.3rem 0 0.2rem' }}>
                    {categorie}
                  </span>
                  <div className="insta-effets-grille">
                    {liste.map((e) => (
                      <button
                        key={e.id}
                        type="button"
                        className={'insta-effet-vignette' + (effet === e.id ? ' actif' : '')}
                        onClick={() => {
                          setEffet(e.id)
                          setEffetApercuAgrandi(e.id)
                        }}
                        disabled={enCours}
                      >
                        <img src={urlApercuEffet(e.id)} alt={e.label} loading="lazy" />
                        <span>{e.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="insta-etape-nav">
            <button type="button" onClick={() => setEtapeFormulaire('contenu')} disabled={enCours}>
              ← Précédent
            </button>
            <button
              onClick={{ simple: genererApercu, carrousel: genererApercuCarrousel, story: genererApercuStory, reel: genererApercuReel }[modePost]}
              disabled={enCours || sujet.trim().length < 3}
            >
              {enCours
                ? {
                    simple: 'Génération de la légende…',
                    carrousel: 'Génération du carrousel…',
                    story: 'Génération de la story…',
                    reel: 'Génération du reel… (jusqu’à 20s)',
                  }[modePost]
                : {
                    simple: '✍️ Générer la légende',
                    carrousel: '📚 Générer le carrousel',
                    story: '🎬 Générer la story',
                    reel: '🎥 Générer le reel',
                  }[modePost]}
            </button>
          </div>

          {erreur && <p className="erreur">{erreur}</p>}
            </>
          )}
        </div>
      )}

      {panneauActif === 'publication' && etape === 'apercu' && modePost === 'carrousel' && (
        <div className="insta-apercu">
          <p className="insta-label">Aperçu — {slides.length} slides, exactement ce qui sera publié</p>
          <div className="insta-mockup">
            <div className="insta-mockup-entete">
              <div className="insta-mockup-avatar" />
              <span>tkonsulting</span>
            </div>
            <div className="insta-carrousel-galerie">
              {slides.map((s, i) => (
                <div key={i} className="insta-carrousel-slide">
                  <img src={s.image_url} alt={s.titre || `Slide ${i + 1}`} />
                  <span className="texte-muted">{i + 1} / {slides.length}</span>
                </div>
              ))}
            </div>
            <p className="insta-mockup-legende">
              <strong>tkonsulting</strong> {legende}
            </p>
          </div>

          <div className="insta-apercu-actions">
            <button
              onClick={() => {
                setEtape('formulaire')
                setEtapeFormulaire('contenu')
              }}
              disabled={enCours}
            >
              ◀ Modifier le sujet
            </button>
            <button onClick={genererApercuCarrousel} disabled={enCours}>
              🔁 Régénérer le carrousel
            </button>
            <button onClick={confirmerPublication} disabled={enCours}>
              {enCours ? etapeTexte || 'Publication…' : '📤 Publier maintenant'}
            </button>
          </div>

          <div className="insta-apercu-actions insta-planification-ligne">
            <button onClick={() => enregistrerPlanification(null)} disabled={enCours}>
              💾 Enregistrer en brouillon
            </button>
            <input
              type="datetime-local"
              value={dateProgrammation}
              onChange={(e) => setDateProgrammation(e.target.value)}
              disabled={enCours}
            />
            <button
              onClick={() => enregistrerPlanification(new Date(dateProgrammation).getTime() / 1000)}
              disabled={enCours || !dateProgrammation}
            >
              🕓 Programmer
            </button>
          </div>

          {enCours && <p className="texte-muted note">Ça peut prendre 30 à 90 secondes, merci de patienter.</p>}
          {erreur && <p className="erreur">{erreur}</p>}
        </div>
      )}

      {panneauActif === 'publication' && etape === 'apercu' && modePost === 'story' && (
        <div className="insta-apercu">
          <p className="insta-label">
            Aperçu — {storyImageUrls.length > 1 ? `${storyImageUrls.length} cartes publiées à la suite` : 'pas de légende sur une story, juste ce visuel'}
          </p>
          {storyImageUrls.length <= 1 ? (
            <div className="insta-mockup insta-mockup-story">
              <div className="insta-mockup-entete">
                <div className="insta-mockup-avatar" />
                <span>tkonsulting</span>
              </div>
              <img className="insta-mockup-image insta-mockup-story-image" src={storyImageUrls[0]} alt={storyTextes[0]} />
            </div>
          ) : (
            <div className="insta-mockup">
              <div className="insta-mockup-entete">
                <div className="insta-mockup-avatar" />
                <span>tkonsulting</span>
              </div>
              <div className="insta-carrousel-galerie">
                {storyImageUrls.map((url, i) => (
                  <div key={i} className="insta-carrousel-slide">
                    <img className="insta-mockup-story-image" src={url} alt={storyTextes[i] || `Carte ${i + 1}`} />
                    <span className="texte-muted">{i + 1} / {storyImageUrls.length}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="insta-apercu-actions">
            <button
              onClick={() => {
                setEtape('formulaire')
                setEtapeFormulaire('contenu')
              }}
              disabled={enCours}
            >
              ◀ Modifier le sujet
            </button>
            <button onClick={genererApercuStory} disabled={enCours}>
              🔁 Régénérer la story
            </button>
            <button onClick={confirmerPublication} disabled={enCours}>
              {enCours ? etapeTexte || 'Publication…' : '📤 Publier maintenant'}
            </button>
          </div>

          <div className="insta-apercu-actions insta-planification-ligne">
            <button onClick={() => enregistrerPlanification(null)} disabled={enCours}>
              💾 Enregistrer en brouillon
            </button>
            <input
              type="datetime-local"
              value={dateProgrammation}
              onChange={(e) => setDateProgrammation(e.target.value)}
              disabled={enCours}
            />
            <button
              onClick={() => enregistrerPlanification(new Date(dateProgrammation).getTime() / 1000)}
              disabled={enCours || !dateProgrammation}
            >
              🕓 Programmer
            </button>
          </div>

          {enCours && <p className="texte-muted note">Ça peut prendre 30 à 90 secondes, merci de patienter.</p>}
          {erreur && <p className="erreur">{erreur}</p>}
        </div>
      )}

      {panneauActif === 'publication' && etape === 'apercu' && modePost === 'reel' && (
        <div className="insta-apercu">
          <p className="insta-label">Aperçu — vidéo générée, légende optionnelle</p>
          <div className="insta-mockup insta-mockup-story">
            <div className="insta-mockup-entete">
              <div className="insta-mockup-avatar" />
              <span>tkonsulting</span>
            </div>
            {/* muted + playsInline nécessaires pour un autoplay fiable dans la plupart des navigateurs */}
            <video
              className="insta-mockup-image insta-mockup-story-image"
              src={reelVideoUrl}
              controls
              autoPlay
              muted
              loop
              playsInline
            />
          </div>

          <label>
            Légende (optionnelle)
            <textarea
              className="insta-sujet"
              value={legende}
              onChange={(e) => setLegende(e.target.value)}
              placeholder="Ex. : hashtags, invitation à échanger…"
              rows={3}
              disabled={enCours}
            />
          </label>

          <div className="insta-apercu-actions">
            <button
              onClick={() => {
                setEtape('formulaire')
                setEtapeFormulaire('contenu')
              }}
              disabled={enCours}
            >
              ◀ Modifier le sujet
            </button>
            <button onClick={genererApercuReel} disabled={enCours}>
              🔁 Régénérer le reel
            </button>
            <button onClick={confirmerPublication} disabled={enCours}>
              {enCours ? etapeTexte || 'Publication…' : '📤 Publier maintenant'}
            </button>
          </div>

          <div className="insta-apercu-actions insta-planification-ligne">
            <button onClick={() => enregistrerPlanification(null)} disabled={enCours}>
              💾 Enregistrer en brouillon
            </button>
            <input
              type="datetime-local"
              value={dateProgrammation}
              onChange={(e) => setDateProgrammation(e.target.value)}
              disabled={enCours}
            />
            <button
              onClick={() => enregistrerPlanification(new Date(dateProgrammation).getTime() / 1000)}
              disabled={enCours || !dateProgrammation}
            >
              🕓 Programmer
            </button>
          </div>

          {enCours && <p className="texte-muted note">La publication d'un reel peut prendre jusqu'à 2 minutes (traitement vidéo par Instagram).</p>}
          {erreur && <p className="erreur">{erreur}</p>}
        </div>
      )}

      {panneauActif === 'publication' && etape === 'apercu' && modePost === 'simple' && (
        <div className="insta-apercu">
          <p className="insta-label">Aperçu — c'est exactement ce qui sera publié</p>
          <div className="insta-mockup">
            <div className="insta-mockup-entete">
              <div className="insta-mockup-avatar" />
              <span>tkonsulting</span>
            </div>
            <img className="insta-mockup-image" src={apercuImage || undefined} alt="Visuel choisi" />
            <p className="insta-mockup-legende">
              <strong>tkonsulting</strong> {legende}
            </p>
          </div>

          {legendeRegeneree && (
            <p className="texte-muted note">
              La première version proposait un ton trop commercial — le garde-fou l'a fait régénérer automatiquement.
            </p>
          )}

          <div className="insta-apercu-actions">
            <button
              onClick={() => {
                setEtape('formulaire')
                setEtapeFormulaire('contenu')
              }}
              disabled={enCours}
            >
              ◀ Modifier le sujet
            </button>
            <button onClick={genererApercu} disabled={enCours}>
              🔁 Régénérer la légende
            </button>
            <button onClick={confirmerPublication} disabled={enCours}>
              {enCours ? etapeTexte || 'Publication…' : '📤 Publier maintenant'}
            </button>
          </div>

          <div className="insta-apercu-actions insta-planification-ligne">
            <button onClick={() => enregistrerPlanification(null)} disabled={enCours}>
              💾 Enregistrer en brouillon
            </button>
            <input
              type="datetime-local"
              value={dateProgrammation}
              onChange={(e) => setDateProgrammation(e.target.value)}
              disabled={enCours}
            />
            <button
              onClick={() => enregistrerPlanification(new Date(dateProgrammation).getTime() / 1000)}
              disabled={enCours || !dateProgrammation}
            >
              🕓 Programmer
            </button>
          </div>

          {enCours && <p className="texte-muted note">Ça peut prendre 30 à 90 secondes, merci de patienter.</p>}
          {erreur && <p className="erreur">{erreur}</p>}
        </div>
      )}

      {etape === 'resultat' && resultat && (
        <div className="admin-formulaire insta-succes">
          <p className="admin-ok">✅ Publié avec succès sur Instagram !</p>
          {idPublication(resultat) && (
            <p className="texte-muted">
              Identifiant de la publication : <code>{idPublication(resultat)}</code>
            </p>
          )}
          <a className="metier-lien" href="https://www.instagram.com/tkonsulting/" target="_blank" rel="noreferrer">
            Voir le profil Instagram →
          </a>
          <button onClick={recommencer}>Publier un autre post</button>
        </div>
      )}
    </div>
  )
}
