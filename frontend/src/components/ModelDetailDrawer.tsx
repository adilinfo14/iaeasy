import { useState } from 'react'
import { essayerModele } from '../api/client'
import { ajouterEntreeParcours, basculerFavori, estFavori } from '../stockageLocal'
import ResultRenderer from './ResultRenderer'

type Props = {
  modele: any
  onFermer: () => void
}

const IDX_LIBRE = -1

export default function ModelDetailDrawer({ modele, onFermer }: Props) {
  const exemples: { label: string; input: string }[] = modele.cas_usage.exemples || []
  const [exempleIdx, setExempleIdx] = useState(0)
  const [input, setInput] = useState(exemples[0]?.input || '')
  const [resultat, setResultat] = useState<any>(null)
  const [enCours, setEnCours] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)
  const [favori, setFavori] = useState(() => estFavori('modele', modele.id))

  function choisirExemple(idx: number) {
    setExempleIdx(idx)
    setInput(idx === IDX_LIBRE ? '' : exemples[idx]?.input || '')
    setResultat(null)
  }

  async function essayer() {
    setEnCours(true)
    setErreur(null)
    setResultat(null)
    try {
      const r = await essayerModele(modele.id, input)
      setResultat(r)
      ajouterEntreeParcours({
        type: 'modele',
        id: modele.id,
        titre: modele.nom,
        detail: exempleIdx === IDX_LIBRE ? 'Bac à sable' : exemples[exempleIdx]?.label,
      })
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
        <div className="drawer-titre-ligne">
          <h2>{modele.nom}</h2>
          <span
            className={favori ? 'favori-etoile actif' : 'favori-etoile'}
            role="button"
            aria-label={favori ? 'Retirer des favoris' : 'Ajouter aux favoris'}
            onClick={() => setFavori(basculerFavori('modele', modele.id))}
          >
            {favori ? '★' : '☆'}
          </span>
        </div>
        <p className="drawer-meta">
          {modele.famille.replace(/_/g, ' ')} · {modele.secteur} · {modele.taille}
        </p>
        <p className="drawer-description">{modele.description_pedagogique}</p>

        <h4>Cas d'usage</h4>
        <p>{modele.cas_usage.enonce}</p>

        {modele.cas_usage.idees_usage?.length > 0 && (
          <>
            <h4>Idées pour s'en inspirer</h4>
            <ul className="liste-simple">
              {modele.cas_usage.idees_usage.map((idee: string, i: number) => (
                <li key={i}>{idee}</li>
              ))}
            </ul>
          </>
        )}

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
              <button
                className={exempleIdx === IDX_LIBRE ? 'chip actif' : 'chip'}
                onClick={() => choisirExemple(IDX_LIBRE)}
              >
                ✏️ Mon propre texte
              </button>
            </div>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              rows={8}
              placeholder={exempleIdx === IDX_LIBRE ? 'Écris ton propre texte à tester ici…' : undefined}
            />
          </>
        )}

        <button onClick={essayer} disabled={enCours}>
          {enCours ? 'Exécution en cours…' : 'Essayer ce modèle'}
        </button>

        {erreur && <div className="erreur">{erreur}</div>}
        {resultat && <ResultRenderer resultat={resultat} />}

        {(modele.lien_telechargement || modele.mode_emploi) && (
          <div className="drawer-installation">
            <h4>Installer / utiliser ce modèle chez soi</h4>
            <p className="texte-muted">
              Référence technique : <code>{modele.moteur_ref}</code>
            </p>
            {modele.mode_emploi && <p>{modele.mode_emploi}</p>}
            {modele.lien_telechargement && (
              <a href={modele.lien_telechargement} target="_blank" rel="noopener noreferrer">
                📥 Page du modèle / téléchargement
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
