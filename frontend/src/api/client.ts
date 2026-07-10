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
