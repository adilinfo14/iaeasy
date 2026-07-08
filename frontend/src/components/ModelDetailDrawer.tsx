import { useState } from 'react'
import { essayerModele } from '../api/client'
import ResultRenderer from './ResultRenderer'

type Props = {
  modele: any
  onFermer: () => void
}

export default function ModelDetailDrawer({ modele, onFermer }: Props) {
  const exemples: { label: string; input: string }[] = modele.cas_usage.exemples || []
  const [exempleIdx, setExempleIdx] = useState(0)
  const [input, setInput] = useState(exemples[0]?.input || '')
  const [resultat, setResultat] = useState<any>(null)
  const [enCours, setEnCours] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  function choisirExemple(idx: number) {
    setExempleIdx(idx)
    setInput(exemples[idx]?.input || '')
  }

  async function essayer() {
    setEnCours(true)
    setErreur(null)
    setResultat(null)
    try {
      const r = await essayerModele(modele.id, input)
      setResultat(r)
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  const necessiteTexte = exemples.length > 0

  return (
    <div className="drawer-overlay" onClick={onFermer}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <button className="drawer-close" onClick={onFermer} aria-label="Fermer">×</button>
        <h2>{modele.nom}</h2>
        <p className="drawer-meta">
          {modele.famille.replace(/_/g, ' ')} · {modele.secteur} · {modele.taille}
        </p>
        <p className="drawer-description">{modele.description_pedagogique}</p>

        <h4>Cas d'usage</h4>
        <p>{modele.cas_usage.enonce}</p>

        {necessiteTexte && (
          <>
            <div className="exemples-chips">
              {exemples.map((ex, i) => (
                <button
                  key={i}
                  className={i === exempleIdx ? 'chip actif' : 'chip'}
                  onClick={() => choisirExemple(i)}
                >
                  {ex.label}
                </button>
              ))}
            </div>
            <textarea value={input} onChange={(e) => setInput(e.target.value)} rows={8} />
          </>
        )}

        <button onClick={essayer} disabled={enCours}>
          {enCours ? 'Exécution en cours…' : 'Essayer ce modèle'}
        </button>

        {erreur && <div className="erreur">{erreur}</div>}
        {resultat && <ResultRenderer resultat={resultat} />}
      </div>
    </div>
  )
}
