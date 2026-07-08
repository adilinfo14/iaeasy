import { useEffect, useState, type ReactNode } from 'react'
import { listerGlossaire } from '../api/client'

let cache: any[] | null = null
let enCours: Promise<any[]> | null = null

async function chargerGlossaire() {
  if (cache) return cache
  if (!enCours) enCours = listerGlossaire()
  cache = await enCours
  return cache
}

function trouverDefinition(termes: any[], nom: string) {
  const cible = nom.toLowerCase()
  return (
    termes.find((t) => t.terme.toLowerCase() === cible) ||
    termes.find((t) => t.terme.toLowerCase().startsWith(cible)) ||
    termes.find((t) => t.terme.toLowerCase().includes(cible)) ||
    null
  )
}

type Props = { nom: string; children: ReactNode }

export default function Terme({ nom, children }: Props) {
  const [def, setDef] = useState<any | null>(null)
  const [ouvert, setOuvert] = useState(false)

  useEffect(() => {
    let actif = true
    chargerGlossaire().then((termes) => {
      if (actif) setDef(trouverDefinition(termes, nom))
    })
    return () => {
      actif = false
    }
  }, [nom])

  if (!def) return <>{children}</>

  return (
    <span className="terme-glossaire">
      <button type="button" className="terme-declencheur" onClick={() => setOuvert(!ouvert)}>
        {children}
        <sup>ⓘ</sup>
      </button>
      {ouvert && (
        <span className="terme-popover">
          <strong>{def.terme}</strong>
          <p>{def.definition_simple}</p>
          {def.ou_le_voir && <p className="terme-ou">👉 {def.ou_le_voir}</p>}
        </span>
      )}
    </span>
  )
}
