const BASE = '/api'

// Le champ "detail" d'une erreur FastAPI est une chaîne pour une erreur métier (HTTPException),
// mais une LISTE d'objets pour une erreur de validation Pydantic (422) — l'interpoler tel quel
// dans un message produit "[object Object]", illisible pour l'utilisateur.
function messageErreur(err: any, defaut: string): string {
  if (typeof err?.detail === 'string') return err.detail
  if (Array.isArray(err?.detail) && typeof err.detail[0]?.msg === 'string') return err.detail[0].msg
  return defaut
}

export function obtenirVisiteurId() {
  let visiteurId = localStorage.getItem('iaeasy-visiteur-id')
  if (!visiteurId) {
    visiteurId = crypto.randomUUID()
    localStorage.setItem('iaeasy-visiteur-id', visiteurId)
  }
  return visiteurId
}

export async function enregistrerVisite() {
  const r = await fetch(`${BASE}/stats/visiteur`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ visiteur_id: obtenirVisiteurId() }),
  })
  return r.json()
}

export async function lireVisiteurs() {
  const r = await fetch(`${BASE}/stats/visiteur`)
  return r.json()
}

export async function listerModeles() {
  const r = await fetch(`${BASE}/catalogue`)
  return r.json()
}

export async function essayerModele(id: string, inputText?: string) {
  const r = await fetch(`${BASE}/catalogue/${id}/essayer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_text: inputText }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant l’exécution du modèle'))
  }
  return r.json()
}

export async function listerScenariosEntrainement() {
  const r = await fetch(`${BASE}/training/scenarios`)
  return r.json()
}

export async function apercuDonnees(scenarioId: string) {
  const r = await fetch(`${BASE}/training/scenarios/${scenarioId}/apercu`)
  return r.json()
}

export async function obtenirJobEntrainement(jobId: string) {
  const r = await fetch(`${BASE}/training/${jobId}`)
  return r.json()
}

export async function demarrerEntrainement(scenarioId: string) {
  const r = await fetch(`${BASE}/training/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId }),
  })
  return r.json()
}

export async function testerModeleEntraine(jobId: string, entree: string) {
  const r = await fetch(`${BASE}/training/${jobId}/tester`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entree }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le test du modèle'))
  }
  return r.json()
}

type PointLoss = { step: number; epoch: number; loss: number }
type FinEntrainement = { status: string; erreur: string | null }

export function suivreEntrainement(
  jobId: string,
  onLoss: (point: PointLoss) => void,
  onFin: (fin: FinEntrainement) => void,
  onOuverture?: () => void,
) {
  const source = new EventSource(`${BASE}/training/${jobId}/stream`)
  // Le flux SSE rejoue tout l'historique depuis le début à chaque (re)connexion — si le visiteur
  // change d'onglet/d'application sur mobile et que la connexion est coupée puis rétablie
  // (reconnexion automatique d'EventSource), 'open' se déclenche à nouveau : à l'appelant de
  // remettre son accumulateur à zéro pour éviter des points de courbe dupliqués.
  source.addEventListener('open', () => onOuverture?.())
  source.addEventListener('loss', (e) => onLoss(JSON.parse((e as MessageEvent).data)))
  source.addEventListener('fin', (e) => {
    onFin(JSON.parse((e as MessageEvent).data))
    source.close()
  })
  source.addEventListener('erreur', () => source.close())
  return () => source.close()
}

export async function listerBriques() {
  const r = await fetch(`${BASE}/agents/briques`)
  return r.json()
}

export async function listerCas() {
  const r = await fetch(`${BASE}/agents/cas`)
  return r.json()
}

export async function listerVideos() {
  const r = await fetch(`${BASE}/videos`)
  return r.json()
}

export async function listerSecurite() {
  const r = await fetch(`${BASE}/securite`)
  return r.json()
}

export async function executerGraphe(nodes: unknown[], edges: unknown[]) {
  const r = await fetch(`${BASE}/agents/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes, edges }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant l’exécution du graphe'))
  }
  return r.json()
}

export async function listerComposants() {
  const r = await fetch(`${BASE}/agents/composants`)
  return r.json()
}

export async function listerTemplates() {
  const r = await fetch(`${BASE}/agents/templates`)
  return r.json()
}

export async function listerStrategiesTest() {
  const r = await fetch(`${BASE}/strategie-test`)
  return r.json()
}

export async function lireProgression() {
  const r = await fetch(`${BASE}/progress`)
  return r.json()
}

export async function debloquerBrique(id: string) {
  const r = await fetch(`${BASE}/progress/debloquer/${id}`, { method: 'POST' })
  return r.json()
}

export async function lireBadges() {
  const r = await fetch(`${BASE}/progress/badges`)
  return r.json()
}

export async function validerBadge(id: string) {
  const r = await fetch(`${BASE}/progress/badges/${id}`, { method: 'POST' })
  return r.json()
}

export async function listerGlossaire() {
  const r = await fetch(`${BASE}/glossaire`)
  return r.json()
}

export async function listerMetiers() {
  const r = await fetch(`${BASE}/metiers`)
  return r.json()
}

export async function demarrerChat(message: string, historique: { role: string; content: string }[]) {
  const r = await fetch(`${BASE}/aide/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, historique }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la discussion avec l'assistant"))
  }
  return r.json()
}

// Le flux SSE rejoue tous les morceaux depuis le début à chaque (re)connexion (utile si le
// visiteur change d'onglet/d'application sur mobile et que la connexion est coupée) — l'appelant
// doit remettre à zéro son accumulateur sur onOuverture pour éviter un texte dupliqué.
export function suivreChat(
  jobId: string,
  onMorceau: (delta: string) => void,
  onFin: (fin: { status: string; erreur: string | null; reponse?: string }) => void,
  onOuverture?: () => void,
) {
  const source = new EventSource(`${BASE}/aide/chat/${jobId}/stream`)
  source.addEventListener('open', () => onOuverture?.())
  source.addEventListener('morceau', (e) => onMorceau(JSON.parse((e as MessageEvent).data).delta))
  source.addEventListener('fin', (e) => {
    onFin(JSON.parse((e as MessageEvent).data))
    source.close()
  })
  source.addEventListener('erreur', () => source.close())
  return () => source.close()
}

export type StatsAvis = { total: number; moyenne: number | null; distribution: Record<string, number> }
export type Avis = { note: number; commentaire: string | null; horodatage: string }

export async function envoyerAvis(note: number, commentaire?: string): Promise<StatsAvis> {
  const r = await fetch(`${BASE}/avis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ visiteur_id: obtenirVisiteurId(), note, commentaire: commentaire || null }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant l'envoi de l'avis"))
  }
  return r.json()
}

export async function lireStatsAvis(): Promise<StatsAvis> {
  const r = await fetch(`${BASE}/avis/stats`)
  return r.json()
}

export async function listerAvis(): Promise<Avis[]> {
  const r = await fetch(`${BASE}/avis`)
  return r.json()
}

export async function listerModelesSimulateur() {
  const r = await fetch(`${BASE}/simulateur/modeles`)
  return r.json()
}

export async function demarrerComparaisonModeles(prompt?: string, modelesIds?: string[]) {
  const r = await fetch(`${BASE}/simulateur/comparer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: prompt || null, modeles_ids: modelesIds || null }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la comparaison'))
  }
  return r.json()
}

export function suivreComparaisonModeles(
  jobId: string,
  onModele: (resultat: any) => void,
  onFin: (fin: { status: string; erreur: string | null }) => void,
  onOuverture?: () => void,
) {
  const source = new EventSource(`${BASE}/simulateur/comparer/${jobId}/stream`)
  source.addEventListener('open', () => onOuverture?.())
  source.addEventListener('modele', (e) => onModele(JSON.parse((e as MessageEvent).data)))
  source.addEventListener('fin', (e) => {
    onFin(JSON.parse((e as MessageEvent).data))
    source.close()
  })
  source.addEventListener('erreur', () => source.close())
  return () => source.close()
}

export async function listerModelesEmbeddings() {
  const r = await fetch(`${BASE}/simulateur/modeles-embeddings`)
  return r.json()
}

export async function comparerEmbeddings(phraseA?: string, phraseB?: string, modelesIds?: string[]) {
  const r = await fetch(`${BASE}/simulateur/comparer-embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phrase_a: phraseA || null, phrase_b: phraseB || null, modeles_ids: modelesIds || null }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la comparaison des embeddings'))
  }
  return r.json()
}

export async function listerModelesClassification() {
  const r = await fetch(`${BASE}/simulateur/modeles-classification`)
  return r.json()
}

export async function comparerClassification(message?: string, modelesIds?: string[]) {
  const r = await fetch(`${BASE}/simulateur/comparer-classification`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: message || null, modeles_ids: modelesIds || null }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la comparaison des algorithmes'))
  }
  return r.json()
}

export async function listerModelesVision() {
  const r = await fetch(`${BASE}/simulateur/modeles-vision`)
  return r.json()
}

export async function comparerVision(modelesIds?: string[]) {
  const r = await fetch(`${BASE}/simulateur/comparer-vision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ modeles_ids: modelesIds || null }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la comparaison des modèles de vision'))
  }
  return r.json()
}

export type ReglagesChat = {
  chat_max_historique: number
  chat_longueur_max_message: number
  chat_longueur_max_message_historique: number
  chat_max_conversations_simultanees: number
}

export async function lireReglagesAdmin(motDePasse: string): Promise<ReglagesChat> {
  const r = await fetch(`${BASE}/admin/reglages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la lecture des réglages"))
  }
  return r.json()
}

export async function modifierReglagesAdmin(motDePasse: string, reglages: ReglagesChat): Promise<ReglagesChat> {
  const r = await fetch(`${BASE}/admin/reglages/modifier`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, ...reglages }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant l'enregistrement des réglages"))
  }
  return r.json()
}

export async function listerEpisodesTheatre() {
  const r = await fetch(`${BASE}/theatre/episodes`)
  return r.json()
}

export async function lireEpisodeTheatre(id: string) {
  const r = await fetch(`${BASE}/theatre/episodes/${id}`)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la lecture de l'histoire"))
  }
  return r.json()
}

export async function demarrerGenerationTheatre() {
  const r = await fetch(`${BASE}/theatre/generer`, { method: 'POST' })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant le lancement de la génération"))
  }
  return r.json()
}

export async function statutGenerationTheatre(jobId: string) {
  const r = await fetch(`${BASE}/theatre/generer/${jobId}`)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la génération de l'histoire"))
  }
  return r.json()
}

// Interroge le job toutes les 1,5s jusqu'à ce que l'épisode soit prêt — plutôt qu'une seule
// requête bloquante (~45s), ce qui survit à un changement d'onglet/d'application sur mobile
// pendant la génération (le traitement continue côté serveur quoi qu'il arrive au client).
export async function genererEpisodeTheatre() {
  const { job_id } = await demarrerGenerationTheatre()
  while (true) {
    await new Promise((resolve) => setTimeout(resolve, 1500))
    const statut = await statutGenerationTheatre(job_id)
    if (statut.status === 'termine') return statut.episode
    if (statut.status === 'erreur') throw new Error(statut.erreur || 'Erreur pendant la génération.')
  }
}

export async function situationBriefIA() {
  const r = await fetch(`${BASE}/brief-ia/mise-en-situation`)
  return r.json()
}

export async function demarrerBriefIA() {
  const r = await fetch(`${BASE}/brief-ia/demarrer`, { method: 'POST' })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la génération'))
  }
  return r.json() as Promise<{ job_id: string; thread_id: string }>
}

// Flux SSE de la génération du brief — mêmes conventions que suivreChat/suivreEntrainement :
// rejoue tout l'historique depuis le début à chaque (re)connexion, à l'appelant de repartir de
// zéro sur 'open' si besoin.
export function suivreBriefIA(
  jobId: string,
  onEtape: (etape: { etape: string; libelle: string; donnees: any }) => void,
  onFin: (fin: any) => void,
  onOuverture?: () => void,
) {
  const source = new EventSource(`${BASE}/brief-ia/${jobId}/stream`)
  source.addEventListener('open', () => onOuverture?.())
  source.addEventListener('etape', (e) => onEtape(JSON.parse((e as MessageEvent).data)))
  source.addEventListener('fin', (e) => {
    onFin(JSON.parse((e as MessageEvent).data))
    source.close()
  })
  source.addEventListener('erreur', () => source.close())
  return () => source.close()
}

export async function validerBriefIA(threadId: string, approuve: boolean, feedback?: string) {
  const r = await fetch(`${BASE}/brief-ia/${threadId}/valider`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approuve, feedback: feedback || null }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la validation'))
  }
  return r.json() as Promise<{ job_id: string }>
}

export async function genererLegendeInstagram(
  motDePasse: string,
  sujet: string,
  ton: string,
  secteur: string,
  connaissance: string = 'aucune',
) {
  const r = await fetch(`${BASE}/instagram/legende`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, sujet, ton, secteur, connaissance }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la génération de la légende'))
  }
  return r.json() as Promise<{ legende: string; regenere: boolean }>
}

export async function demarrerPublicationInstagram(
  motDePasse: string,
  sujet: string,
  image: string,
  ton: string,
  secteur: string,
  legende: string,
) {
  const r = await fetch(`${BASE}/instagram/publier`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, sujet, image, ton, secteur, legende }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la publication'))
  }
  return r.json()
}

export async function statutPublicationInstagram(jobId: string) {
  const r = await fetch(`${BASE}/instagram/publier/${jobId}`)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la publication'))
  }
  return r.json()
}

export type EntreeHistoriqueInstagram = {
  horodatage: number
  sujet: string
  image: string
  ton: string
  secteur?: string
  legende: string
  statut: 'publie' | 'erreur'
  resultat?: string
  erreur?: string
  duree_s: number
}

export async function lireHistoriqueInstagram(motDePasse: string): Promise<EntreeHistoriqueInstagram[]> {
  const r = await fetch(`${BASE}/instagram/historique`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la lecture de l'historique"))
  }
  return r.json()
}

export type IndicateursInstagram = { reach?: number; likes?: number; comments?: number; saved?: number; shares?: number }

export async function lireIndicateursInstagram(motDePasse: string, mediaId: string): Promise<IndicateursInstagram> {
  const r = await fetch(`${BASE}/instagram/insights`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, media_id: mediaId }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la récupération des indicateurs'))
  }
  return r.json()
}

export async function rafraichirToutesLesStatsInstagram(motDePasse: string): Promise<{ maj: number; total_publies: number }> {
  const r = await fetch(`${BASE}/instagram/insights/tout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le rafraîchissement des indicateurs'))
  }
  return r.json()
}

export type DashboardInstagram = {
  total: number
  publies: number
  echecs: number
  taux_succes: number | null
  par_type: Record<string, number>
  tendance_semaines: { semaine: string; nb: number }[]
  engagement_par_ton: Record<string, IndicateursInstagram | null>
  nb_avec_indicateurs: number
  meilleur_post: { sujet: string; horodatage: number; indicateurs: IndicateursInstagram } | null
}

export async function lireDashboardInstagram(motDePasse: string): Promise<DashboardInstagram> {
  const r = await fetch(`${BASE}/instagram/dashboard`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la lecture du tableau de bord'))
  }
  return r.json()
}

export type CommentaireInstagram = { id: string; text: string; username: string; timestamp: string; like_count?: number }

export async function lireCommentairesInstagram(motDePasse: string, mediaId: string): Promise<CommentaireInstagram[]> {
  const r = await fetch(`${BASE}/instagram/commentaires`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, media_id: mediaId }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la récupération des commentaires'))
  }
  return r.json()
}

export type ConversationDM = {
  id: string
  updated_time?: string
  participants?: { data: { id: string; username?: string }[] }
}

export type MessageDM = {
  id: string
  message?: string
  from?: { id: string; username?: string }
  created_time?: string
}

export async function listerConversationsDM(motDePasse: string): Promise<ConversationDM[]> {
  const r = await fetch(`${BASE}/instagram/dm/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la récupération des conversations'))
  }
  return r.json()
}

export async function lireMessagesDM(motDePasse: string, conversationId: string): Promise<MessageDM[]> {
  const r = await fetch(`${BASE}/instagram/dm/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, conversation_id: conversationId }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la récupération des messages'))
  }
  return r.json()
}

export async function envoyerMessageDM(motDePasse: string, destinataireId: string, texte: string) {
  const r = await fetch(`${BASE}/instagram/dm/envoyer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, destinataire_id: destinataireId, texte }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant l'envoi du message"))
  }
  return r.json()
}

export type InstantaneCompte = {
  date: string
  followers_count: number
  follows_count: number
  media_count: number
  reach_jour: number
  profile_views_jour: number
}

export async function prendreInstantaneCompte(motDePasse: string): Promise<InstantaneCompte> {
  const r = await fetch(`${BASE}/instagram/compte/instantane`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la capture de l'instantané"))
  }
  return r.json()
}

export async function lireHistoriqueCompte(motDePasse: string): Promise<InstantaneCompte[]> {
  const r = await fetch(`${BASE}/instagram/compte/historique`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la lecture de l'historique du compte"))
  }
  return r.json()
}

export type StatsLienBio = {
  total_par_lien: Record<string, number>
  historique: { date: string; cle: string; clics: number }[]
  urls: Record<string, string>
  appareils: { mobile: number; bureau: number }
  heures: Record<string, number>
}

export async function lireStatsLienBio(motDePasse: string): Promise<StatsLienBio> {
  const r = await fetch(`${BASE}/instagram/lien/stats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la lecture des statistiques du lien en bio"))
  }
  return r.json()
}

export type SlideCarrousel = { titre: string; texte: string; image_url: string }

export type EffetVisuel = { id: string; label: string; categorie: string }

export async function listerEffets(): Promise<EffetVisuel[]> {
  const r = await fetch(`${BASE}/instagram/effets`)
  if (!r.ok) throw new Error('Erreur pendant la lecture des effets disponibles')
  return r.json()
}

export type Connaissance = { id: string; titre: string; texte: string }

export async function listerConnaissances(): Promise<Connaissance[]> {
  const r = await fetch(`${BASE}/instagram/connaissances`)
  if (!r.ok) throw new Error('Erreur pendant la lecture des connaissances disponibles')
  return r.json()
}

export async function enregistrerConnaissance(motDePasse: string, cle: string, titre: string, texte: string) {
  const r = await fetch(`${BASE}/instagram/connaissances/enregistrer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, cle, titre, texte }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant l'enregistrement de la connaissance"))
  }
  return r.json()
}

export async function reinitialiserConnaissance(motDePasse: string, cle: string) {
  const r = await fetch(`${BASE}/instagram/connaissances/reinitialiser`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, cle }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la réinitialisation de la connaissance'))
  }
  return r.json()
}

export function urlApercuEffet(id: string): string {
  return `${BASE}/instagram/effets/${id}/apercu`
}

export type ApercuSecteur = {
  cible: string
  hashtags_larges: string[]
  hashtags_niches: string[]
  nb_posts_historique: number
  nb_posts_avec_donnees: number
  reach_moyen: number | null
}

export async function lireApercuSecteur(motDePasse: string, secteur: string): Promise<ApercuSecteur> {
  const r = await fetch(`${BASE}/instagram/secteurs/apercu`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, secteur }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant la lecture de l'aperçu du secteur"))
  }
  return r.json()
}

export async function genererCarrousel(
  motDePasse: string,
  sujet: string,
  ton: string,
  secteur: string,
  nbSlides: number,
  effet: string,
  connaissance: string = 'aucune',
): Promise<{ carrousel_id: string; legende: string; slides: SlideCarrousel[] }> {
  const r = await fetch(`${BASE}/instagram/carrousel/generer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, sujet, ton, secteur, nb_slides: nbSlides, effet, connaissance }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la génération du carrousel'))
  }
  return r.json()
}

export async function demarrerPublicationCarrousel(
  motDePasse: string,
  carrouselId: string,
  nbSlides: number,
  legende: string,
) {
  const r = await fetch(`${BASE}/instagram/carrousel/publier`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, carrousel_id: carrouselId, nb_slides: nbSlides, legende }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la publication du carrousel'))
  }
  return r.json() as Promise<{ job_id: string }>
}

export async function statutPublicationCarrousel(jobId: string) {
  const r = await fetch(`${BASE}/instagram/carrousel/publier/${jobId}`)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la publication du carrousel'))
  }
  return r.json()
}

export type EntreePlanification = {
  id: string
  cree_le: number
  type: 'simple' | 'carrousel' | 'story' | 'reel'
  statut: 'brouillon' | 'programme' | 'en_cours' | 'publie' | 'erreur'
  programme_pour: number | null
  sujet: string
  ton: string
  secteur: string
  legende: string
  image: string
  carrousel_id: string
  nb_slides: number
  story_id: string
  reel_id: string
  erreur?: string
}

export async function planifierInstagram(
  motDePasse: string,
  params: {
    type: 'simple' | 'carrousel' | 'story' | 'reel'
    sujet?: string
    ton?: string
    secteur?: string
    legende?: string
    image?: string
    carrouselId?: string
    nbSlides?: number
    storyId?: string
    reelId?: string
    programmePour?: number | null
  },
): Promise<{ id: string }> {
  const r = await fetch(`${BASE}/instagram/planifier`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mot_de_passe: motDePasse,
      type: params.type,
      sujet: params.sujet || '',
      ton: params.ton || 'direct',
      secteur: params.secteur || 'aucun',
      legende: params.legende || '',
      image: params.image || 'aleatoire',
      carrousel_id: params.carrouselId || '',
      nb_slides: params.nbSlides || 0,
      story_id: params.storyId || '',
      reel_id: params.reelId || '',
      programme_pour: params.programmePour ?? null,
    }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la planification'))
  }
  return r.json()
}

export async function listerPlanifications(motDePasse: string): Promise<EntreePlanification[]> {
  const r = await fetch(`${BASE}/instagram/planifier/liste`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la lecture de la file d’attente'))
  }
  return r.json()
}

export async function annulerPlanification(motDePasse: string, id: string) {
  const r = await fetch(`${BASE}/instagram/planifier/${id}/annuler`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant l'annulation"))
  }
  return r.json()
}

export async function publierMaintenantPlanification(motDePasse: string, id: string) {
  const r = await fetch(`${BASE}/instagram/planifier/${id}/publier_maintenant`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la publication'))
  }
  return r.json()
}

export async function genererStory(
  motDePasse: string,
  sujet: string,
  ton: string,
  secteur: string,
  nbScenes: number,
  effet: string,
  connaissance: string = 'aucune',
): Promise<{ story_id: string; story_ids: string[]; textes: string[]; image_urls: string[] }> {
  const r = await fetch(`${BASE}/instagram/story/generer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, sujet, ton, secteur, nb_scenes: nbScenes, effet, connaissance }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la génération de la story'))
  }
  return r.json()
}

export async function demarrerPublicationStory(motDePasse: string, storyId: string) {
  const r = await fetch(`${BASE}/instagram/story/publier`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, story_id: storyId }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la publication'))
  }
  return r.json() as Promise<{ job_id: string }>
}

export async function statutPublicationStory(jobId: string) {
  const r = await fetch(`${BASE}/instagram/story/publier/${jobId}`)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la publication de la story'))
  }
  return r.json()
}

export type MusiqueReel = { id: string; label: string; categorie: string }

export async function listerMusiquesReel(): Promise<MusiqueReel[]> {
  const r = await fetch(`${BASE}/instagram/reel/musiques`)
  if (!r.ok) throw new Error('Erreur pendant la lecture des musiques disponibles')
  return r.json()
}

export function urlApercuMusiqueReel(id: string): string {
  return `${BASE}/instagram/reel/musiques/${id}.mp3`
}

export type PromptsInstagram = { legende: string; story: string; carrousel: string }

export async function lirePromptsInstagram(
  motDePasse: string,
): Promise<{ prompts: PromptsInstagram; defauts: PromptsInstagram }> {
  const r = await fetch(`${BASE}/instagram/prompts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la lecture des prompts'))
  }
  return r.json()
}

export async function enregistrerPromptInstagram(motDePasse: string, type: string, texte: string) {
  const r = await fetch(`${BASE}/instagram/prompts/enregistrer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, type, texte }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, "Erreur pendant l'enregistrement du prompt"))
  }
  return r.json()
}

export async function reinitialiserPromptInstagram(motDePasse: string, type: string) {
  const r = await fetch(`${BASE}/instagram/prompts/reinitialiser`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, type }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la réinitialisation du prompt'))
  }
  return r.json()
}

export async function genererReel(
  motDePasse: string,
  sujet: string,
  ton: string,
  secteur: string,
  musique: string,
  nbScenes: number,
  effet: string,
  connaissance: string = 'aucune',
): Promise<{ reel_id: string; texte: string; legende: string; video_url: string }> {
  const r = await fetch(`${BASE}/instagram/reel/generer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mot_de_passe: motDePasse, sujet, ton, secteur, musique, nb_scenes: nbScenes, effet, connaissance,
    }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la génération du reel'))
  }
  return r.json()
}

export async function demarrerPublicationReel(motDePasse: string, reelId: string, legende: string) {
  const r = await fetch(`${BASE}/instagram/reel/publier`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, reel_id: reelId, legende }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la publication'))
  }
  return r.json() as Promise<{ job_id: string }>
}

export async function statutPublicationReel(jobId: string) {
  const r = await fetch(`${BASE}/instagram/reel/publier/${jobId}`)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la publication du reel'))
  }
  return r.json()
}

export async function listerChapitresVoyage() {
  const r = await fetch(`${BASE}/voyage/chapitres`)
  return r.json()
}

// Voix neuronale auto-hébergée (Piper, synthétisée côté serveur) — renvoie une URL d'objet
// (à révoquer par l'appelant une fois la lecture terminée) plutôt que la voix très inégale du
// navigateur (Web Speech API), jugée insuffisante en conditions réelles.
export async function genererVoixTheatre(texte: string, personnage: string): Promise<string> {
  const r = await fetch(`${BASE}/theatre/voix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texte, personnage }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la synthèse vocale'))
  }
  const blob = await r.blob()
  return URL.createObjectURL(blob)
}

export type Mission = {
  id: string
  intitule: string
  entreprise: string
  ville: string
  pays: 'France' | 'Maroc'
  famille: 'conseil_it' | 'drone'
  type_contrat: 'freelance' | 'cdi'
  remuneration: string
  lien: string
  source: string
  date_collecte: string
}

export type StatsMissions = {
  total: number
  par_pays: Record<string, number>
  par_famille: Record<string, number>
  par_type_contrat: Record<string, number>
  par_source: Record<string, number>
  par_mois: Record<string, number>
  derniere_collecte: string | null
}

export async function listerMissions(motDePasse: string): Promise<Mission[]> {
  const r = await fetch(`${BASE}/chasseur-mission/missions/lister`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la lecture des missions'))
  }
  return r.json()
}

export async function statsMissions(motDePasse: string): Promise<StatsMissions> {
  const r = await fetch(`${BASE}/chasseur-mission/stats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la lecture des statistiques'))
  }
  return r.json()
}

export type ResultatRechercheMissions = {
  statut: 'en_cours' | 'termine' | 'erreur'
  resultat: {
    ajoutees: number
    ignorees_doublons: number
    total: number
    rejetees: number
    notes: string
    recherches_effectuees: number
  } | null
  erreur: string | null
}

export async function lancerRechercheMissions(
  motDePasse: string,
  motsCles: string,
  pays: ('France' | 'Maroc')[],
): Promise<{ job_id: string }> {
  const r = await fetch(`${BASE}/chasseur-mission/rechercher`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse, mots_cles: motsCles, pays }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant le lancement de la recherche'))
  }
  return r.json()
}

export async function statutRechercheMissions(jobId: string, motDePasse: string): Promise<ResultatRechercheMissions> {
  const r = await fetch(`${BASE}/chasseur-mission/rechercher/${jobId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mot_de_passe: motDePasse }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(messageErreur(err, 'Erreur pendant la recherche'))
  }
  return r.json()
}
