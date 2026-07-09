import { useEffect, useMemo, useState } from 'react'
import { listerGlossaire } from '../api/client'

export default function Glossaire() {
  const [termes, setTermes] = useState<any[]>([])
  const [recherche, setRecherche] = useState('')

  useEffect(() => {
    listerGlossaire().then(setTermes)
  }, [])

  const filtres = useMemo(() => {
    const q = recherche.trim().toLowerCase()
    if (!q) return termes
    return termes.filter(
      (t) => t.terme.toLowerCase().includes(q) || t.definition_simple.toLowerCase().includes(q),
    )
  }, [termes, recherche])

  const parCategorie = useMemo(() => {
    const groupes: Record<string, any[]> = {}
    for (const t of filtres) {
      groupes[t.categorie] = groupes[t.categorie] || []
      groupes[t.categorie].push(t)
    }
    return groupes
  }, [filtres])

  return (
    <div className="page page-glossaire">
      <h1>📖 Glossaire IA — expliqué simplement</h1>
      <p className="page-intro">
        Le Glossaire s'attache à restituer, en langage courant et sans jargon superflu, chacun des
        termes techniques employés sur ce site — qu'il s'agisse d'une notion générale
        d'intelligence artificielle, d'une famille de modèles ou d'un modèle du Catalogue pris
        individuellement. Ces définitions demeurent également accessibles au survol du symbole{' '}
        <strong>ⓘ</strong>, partout où un terme technique apparaît.
      </p>

      <input
        type="text"
        className="glossaire-recherche"
        placeholder="Rechercher un terme (ex : token, RAG, loss...)"
        value={recherche}
        onChange={(e) => setRecherche(e.target.value)}
      />

      {Object.keys(parCategorie).length === 0 && (
        <p className="texte-muted">Aucun terme ne correspond à « {recherche} ».</p>
      )}

      {Object.entries(parCategorie).map(([categorie, liste]) => (
        <div key={categorie} className="glossaire-categorie">
          <h3>{categorie}</h3>
          <div className="glossaire-grille">
            {liste.map((t) => (
              <div key={t.terme} className="glossaire-carte">
                <h4>{t.terme}</h4>
                <p>{t.definition_simple}</p>
                {t.ou_le_voir && <p className="glossaire-ou-voir">👉 {t.ou_le_voir}</p>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
