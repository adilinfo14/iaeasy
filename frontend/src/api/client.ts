const BASE = '/api'

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
    throw new Error(err.detail || 'Erreur pendant l’exécution du modèle')
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
    throw new Error(err.detail || 'Erreur pendant le test du modèle')
  }
  return r.json()
}

type PointLoss = { step: number; epoch: number; loss: number }
type FinEntrainement = { status: string; erreur: string | null }

export function suivreEntrainement(
  jobId: string,
  onLoss: (point: PointLoss) => void,
  onFin: (fin: FinEntrainement) => void,
) {
  const source = new EventSource(`${BASE}/training/${jobId}/stream`)
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

export async function executerGraphe(nodes: unknown[], edges: unknown[]) {
  const r = await fetch(`${BASE}/agents/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes, edges }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || 'Erreur pendant l’exécution du graphe')
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

export async function lireProgression() {
  const r = await fetch(`${BASE}/progress`)
  return r.json()
}

export async function debloquerBrique(id: string) {
  const r = await fetch(`${BASE}/progress/debloquer/${id}`, { method: 'POST' })
  return r.json()
}
