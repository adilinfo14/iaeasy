// Favoris + « Mon parcours » : entièrement côté client (localStorage), sans backend — cohérent
// avec visiteur_id/thème déjà stockés ainsi, et ça évite de faire remonter au serveur le détail
// de ce qu'un visiteur consulte (rien de plus que ce qui est déjà suivi aujourd'hui).

const CLE_FAVORIS = 'iaeasy-favoris'
const CLE_PARCOURS = 'iaeasy-mon-parcours'
const MAX_PARCOURS = 50

export type TypeFavori = 'modele' | 'terme'
type Favoris = Record<TypeFavori, string[]>

function lireFavoris(): Favoris {
  try {
    const brut = localStorage.getItem(CLE_FAVORIS)
    if (!brut) return { modele: [], terme: [] }
    const d = JSON.parse(brut)
    return { modele: d.modele || [], terme: d.terme || [] }
  } catch {
    return { modele: [], terme: [] }
  }
}

export function estFavori(type: TypeFavori, id: string): boolean {
  return lireFavoris()[type].includes(id)
}

export function basculerFavori(type: TypeFavori, id: string): boolean {
  const favoris = lireFavoris()
  const liste = favoris[type]
  const idx = liste.indexOf(id)
  if (idx === -1) liste.push(id)
  else liste.splice(idx, 1)
  localStorage.setItem(CLE_FAVORIS, JSON.stringify(favoris))
  return idx === -1
}

export function listerFavoris(type: TypeFavori): string[] {
  return lireFavoris()[type]
}

export type EntreeParcours = {
  type: 'brique' | 'modele'
  id: string
  titre: string
  detail?: string
  horodatage: number
}

export function ajouterEntreeParcours(entree: Omit<EntreeParcours, 'horodatage'>) {
  try {
    const brut = localStorage.getItem(CLE_PARCOURS)
    const liste: EntreeParcours[] = brut ? JSON.parse(brut) : []
    liste.unshift({ ...entree, horodatage: Date.now() })
    localStorage.setItem(CLE_PARCOURS, JSON.stringify(liste.slice(0, MAX_PARCOURS)))
  } catch {
    // localStorage indisponible (navigation privée stricte, quota) — l'historique perso n'est
    // qu'un confort, pas de raison de casser le reste de l'app pour ça.
  }
}

export function lireParcours(): EntreeParcours[] {
  try {
    const brut = localStorage.getItem(CLE_PARCOURS)
    return brut ? JSON.parse(brut) : []
  } catch {
    return []
  }
}

export function effacerParcours() {
  localStorage.removeItem(CLE_PARCOURS)
}
