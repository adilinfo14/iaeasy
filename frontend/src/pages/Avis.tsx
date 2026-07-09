import { useEffect, useState } from 'react'
import { Avis as AvisType, StatsAvis, envoyerAvis, lireStatsAvis, listerAvis } from '../api/client'

const TAILLE_PAGE = 10

export default function Avis() {
  const [note, setNote] = useState(0)
  const [survol, setSurvol] = useState(0)
  const [commentaire, setCommentaire] = useState('')
  const [envoi, setEnvoi] = useState(false)
  const [confirme, setConfirme] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)
  const [stats, setStats] = useState<StatsAvis | null>(null)
  const [avis, setAvis] = useState<AvisType[]>([])
  const [page, setPage] = useState(0)

  function rafraichir() {
    lireStatsAvis().then(setStats)
    listerAvis().then(setAvis)
  }

  useEffect(() => {
    rafraichir()
  }, [])

  async function soumettre() {
    if (note < 1) return
    setEnvoi(true)
    setErreur(null)
    try {
      const s = await envoyerAvis(note, commentaire)
      setStats(s)
      setConfirme(true)
      setCommentaire('')
      listerAvis().then(setAvis)
    } catch (e) {
      setErreur(e instanceof Error ? e.message : 'Erreur inconnue')
    } finally {
      setEnvoi(false)
    }
  }

  const totalAvis = stats?.total || 0
  const nbPages = Math.max(1, Math.ceil(avis.length / TAILLE_PAGE))
  const pageCourante = Math.min(page, nbPages - 1)
  const debut = pageCourante * TAILLE_PAGE
  const avisPage = avis.slice(debut, debut + TAILLE_PAGE)

  return (
    <div className="page page-avis">
      <h1>⭐ Votre avis sur iaeasy</h1>
      <p className="page-intro">
        Ce site s'enrichit des retours de ceux qui le parcourent : une note suffit, en quelques
        secondes, et un commentaire, lorsque le temps le permet, vient utilement la compléter —
        l'ensemble demeurant visible ci-dessous, sans qu'aucun compte ne soit nécessaire.
      </p>

      <div className="avis-formulaire">
        <div className="avis-etoiles" role="radiogroup" aria-label="Note de 1 à 5 étoiles">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              className="avis-etoile"
              aria-label={`${n} étoile${n > 1 ? 's' : ''}`}
              onMouseEnter={() => setSurvol(n)}
              onMouseLeave={() => setSurvol(0)}
              onClick={() => {
                setNote(n)
                setConfirme(false)
              }}
            >
              {(survol || note) >= n ? '★' : '☆'}
            </button>
          ))}
        </div>

        <textarea
          className="avis-commentaire"
          placeholder="Un commentaire ? (facultatif)"
          maxLength={500}
          value={commentaire}
          onChange={(e) => {
            setCommentaire(e.target.value)
            setConfirme(false)
          }}
        />

        <div className="avis-actions">
          <button disabled={note < 1 || envoi} onClick={soumettre}>
            {envoi ? 'Envoi…' : 'Envoyer mon avis'}
          </button>
          {confirme && <span className="avis-confirmation">✅ Merci pour votre avis !</span>}
          {erreur && <span className="avis-erreur">⚠️ {erreur}</span>}
        </div>
      </div>

      {stats && (
        <div className="avis-recap">
          <div className="avis-moyenne">
            {stats.moyenne != null ? (
              <>
                <span className="avis-moyenne-chiffre">{stats.moyenne.toFixed(2)} / 5</span>
                <span className="texte-muted">sur {totalAvis} avis</span>
              </>
            ) : (
              <span className="texte-muted">Aucun avis pour l'instant — soyez le premier !</span>
            )}
          </div>
          {totalAvis > 0 && (
            <div className="avis-distribution">
              {[5, 4, 3, 2, 1].map((n) => {
                const compte = stats.distribution[String(n)] || 0
                const pourcentage = totalAvis ? Math.round((compte / totalAvis) * 100) : 0
                return (
                  <div key={n} className="avis-barre-ligne">
                    <span>{n} ★</span>
                    <div className="avis-barre-fond">
                      <div className="avis-barre-remplie" style={{ width: `${pourcentage}%` }} />
                    </div>
                    <span className="texte-muted">{compte}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {avis.length > 0 && (
        <div className="avis-liste">
          <h5>💬 Avis des visiteurs</h5>
          {avisPage.map((a, i) => (
            <div key={debut + i} className="avis-item">
              <span className="avis-item-note">{'★'.repeat(a.note)}{'☆'.repeat(5 - a.note)}</span>
              {a.commentaire && <p>{a.commentaire}</p>}
              <span className="texte-muted">{new Date(a.horodatage).toLocaleDateString('fr-FR')}</span>
            </div>
          ))}
          {nbPages > 1 && (
            <div className="cahier-pagination">
              <button className="chip" disabled={pageCourante === 0} onClick={() => setPage(pageCourante - 1)}>
                ← Précédent
              </button>
              <span className="texte-muted">
                Page {pageCourante + 1} / {nbPages} — {avis.length} avis au total
              </span>
              <button
                className="chip"
                disabled={pageCourante >= nbPages - 1}
                onClick={() => setPage(pageCourante + 1)}
              >
                Suivant →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
