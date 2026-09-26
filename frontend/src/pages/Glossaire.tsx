import { useEffect, useMemo, useState } from 'react'
import { listerGlossaire } from '../api/client'
import { basculerFavori, estFavori } from '../stockageLocal'

export default function Glossaire() {
  const [termes, setTermes] = useState<any[]>([])
  const [recherche, setRecherche] = useState('')
  const [seulementFavoris, setSeulementFavoris] = useState(false)
  const [version, setVersion] = useState(0) // force un re-rendu après un clic sur une étoile

  useEffect(() => {
    listerGlossaire().then(setTermes)
  }, [])

  function basculer(terme: string) {
    basculerFavori('terme', terme)
    setVersion((v) => v + 1)
  }

  const filtres = useMemo(() => {
    const q = recherche.trim().toLowerCase()
    let base = termes
    if (q) {
      base = base.filter(
        (t) => t.terme.toLowerCase().includes(q) || t.definition_simple.toLowerCase().includes(q),
      )
    }
    if (seulementFavoris) base = base.filter((t) => estFavori('terme', t.terme))
    return base
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [termes, recherche, seulementFavoris, version])

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

      <div className="glossaire-barre">
        <input
          type="text"
          className="glossaire-recherche"
          placeholder="Rechercher un terme (ex : token, RAG, loss...)"
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
        />
        <button
          className={seulementFavoris ? 'chip actif' : 'chip'}
          onClick={() => setSeulementFavoris((v) => !v)}
        >
          ★ Mes favoris
        </button>
      </div>

      {Object.keys(parCategorie).length === 0 && (
        <p className="texte-muted">
          {seulementFavoris ? "Aucun terme épinglé pour l'instant." : `Aucun terme ne correspond à « ${recherche} ».`}
        </p>
      )}

      {Object.entries(parCategorie).map(([categorie, liste]) => (
        <div key={categorie} className="glossaire-categorie">
          <h3>{categorie}</h3>
          <div className="glossaire-grille">
            {liste.map((t) => (
              <div key={t.terme} className="glossaire-carte">
                <div className="glossaire-carte-tete">
                  <h4>{t.terme}</h4>
                  <span
                    className={estFavori('terme', t.terme) ? 'favori-etoile actif' : 'favori-etoile'}
                    role="button"
                    aria-label="Ajouter aux favoris"
                    onClick={() => basculer(t.terme)}
                  >
                    {estFavori('terme', t.terme) ? '★' : '☆'}
                  </span>
                </div>
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
