import { useEffect, useMemo, useRef, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import {
  lancerRechercheMissions,
  listerMissions,
  statsMissions,
  statutRechercheMissions,
  type Mission,
  type StatsMissions,
} from '../api/client'

// Réutilise les 5 teintes catégorielles déjà définies pour le Constructeur (--cat-source,
// --cat-traitement...) plutôt que d'introduire une nouvelle palette concurrente — cohérence
// visuelle avec le reste du site, et ces teintes couvrent déjà exactement les 5 sources
// actuelles (DroneConnect, Indeed, LinkedIn, Comet, Rekrute).
const TEINTES = ['var(--cat-source)', 'var(--cat-traitement)', 'var(--cat-stockage)', 'var(--cat-modele)', 'var(--cat-outil)']

const LABELS_PAYS: Record<string, string> = { France: '🇫🇷 France', Maroc: '🇲🇦 Maroc' }
const LABELS_FAMILLE: Record<string, string> = { conseil_it: 'Conseil / IT', drone: 'Pilote de drone' }
const LABELS_CONTRAT: Record<string, string> = { freelance: 'Freelance', cdi: 'CDI' }

function versBarres(dict: Record<string, number>, labels?: Record<string, string>) {
  return Object.entries(dict)
    .map(([nom, valeur]) => ({ nom: labels?.[nom] ?? nom, valeur }))
    .sort((a, b) => b.valeur - a.valeur)
}

function RepartitionBarChart({ titre, donnees }: { titre: string; donnees: { nom: string; valeur: number }[] }) {
  const hauteur = Math.max(90, donnees.length * 44)
  return (
    <div className="mission-graphique">
      <h4>{titre}</h4>
      <ResponsiveContainer width="100%" height={hauteur}>
        <BarChart data={donnees} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
          <CartesianGrid horizontal={false} stroke="var(--border)" />
          <XAxis type="number" allowDecimals={false} tick={{ fill: 'var(--fg-muted)', fontSize: 12 }} axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
          <YAxis
            type="category"
            dataKey="nom"
            width={140}
            tick={{ fill: 'var(--fg)', fontSize: 13 }}
            axisLine={{ stroke: 'var(--border)' }}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{ background: 'var(--bg-alt)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--fg)' }}
            cursor={{ fill: 'var(--accent-soft)' }}
          />
          <Bar dataKey="valeur" radius={[0, 4, 4, 0]} maxBarSize={22}>
            {donnees.map((_, i) => (
              <Cell key={i} fill={TEINTES[i % TEINTES.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function ChasseurMission() {
  const [connecte, setConnecte] = useState(false)
  const [motDePasse, setMotDePasse] = useState('')
  const [enCoursConnexion, setEnCoursConnexion] = useState(false)
  const [erreurConnexion, setErreurConnexion] = useState<string | null>(null)

  const [missions, setMissions] = useState<Mission[]>([])
  const [stats, setStats] = useState<StatsMissions | null>(null)
  const [filtrePays, setFiltrePays] = useState('tous')
  const [filtreFamille, setFiltreFamille] = useState('tous')

  const [motsCles, setMotsCles] = useState('')
  const [paysRecherche, setPaysRecherche] = useState<('France' | 'Maroc')[]>(['France', 'Maroc'])
  const [jobId, setJobId] = useState<string | null>(null)
  const [statutJob, setStatutJob] = useState<'idle' | 'en_cours' | 'termine' | 'erreur'>('idle')
  const [messageRecherche, setMessageRecherche] = useState<string | null>(null)
  const intervalleRef = useRef<number | null>(null)

  function rafraichirDonnees() {
    listerMissions(motDePasse).then(setMissions)
    statsMissions(motDePasse).then(setStats)
  }

  async function connexion() {
    setEnCoursConnexion(true)
    setErreurConnexion(null)
    try {
      const [m, s] = await Promise.all([listerMissions(motDePasse), statsMissions(motDePasse)])
      setMissions(m)
      setStats(s)
      setConnecte(true)
    } catch (e: any) {
      setErreurConnexion(e.message)
    } finally {
      setEnCoursConnexion(false)
    }
  }

  useEffect(() => {
    if (!jobId) return
    intervalleRef.current = window.setInterval(async () => {
      try {
        const r = await statutRechercheMissions(jobId, motDePasse)
        if (r.statut === 'termine' && r.resultat) {
          setStatutJob('termine')
          setJobId(null)
          setMessageRecherche(
            `${r.resultat.ajoutees} nouvelle(s) mission(s) ajoutée(s)` +
              (r.resultat.ignorees_doublons ? `, ${r.resultat.ignorees_doublons} doublon(s) ignoré(s)` : '') +
              (r.resultat.rejetees ? `, ${r.resultat.rejetees} résultat(s) rejeté(s) (format invalide)` : '') +
              `. ${r.resultat.recherches_effectuees} recherche(s) web effectuée(s). ${r.resultat.notes}`,
          )
          rafraichirDonnees()
        } else if (r.statut === 'erreur') {
          setStatutJob('erreur')
          setJobId(null)
          setMessageRecherche(r.erreur ?? 'Erreur inconnue pendant la recherche.')
        }
      } catch (e: any) {
        setStatutJob('erreur')
        setJobId(null)
        setMessageRecherche(e.message)
      }
    }, 4000)
    return () => {
      if (intervalleRef.current) window.clearInterval(intervalleRef.current)
    }
  }, [jobId])

  async function lancer() {
    setMessageRecherche(null)
    try {
      const r = await lancerRechercheMissions(motDePasse, motsCles, paysRecherche)
      setJobId(r.job_id)
      setStatutJob('en_cours')
    } catch (e: any) {
      setStatutJob('erreur')
      setMessageRecherche(e.message)
    }
  }

  function togglePaysRecherche(p: 'France' | 'Maroc') {
    setPaysRecherche((prev) => (prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]))
  }

  const visibles = useMemo(
    () =>
      missions.filter(
        (m) => (filtrePays === 'tous' || m.pays === filtrePays) && (filtreFamille === 'tous' || m.famille === filtreFamille),
      ),
    [missions, filtrePays, filtreFamille],
  )

  const nbMoisHistorique = stats ? Object.keys(stats.par_mois).length : 0
  const pctFreelance = stats && stats.total > 0 ? Math.round(((stats.par_type_contrat.freelance ?? 0) / stats.total) * 100) : 0

  if (!connecte) {
    return (
      <div className="page page-agents">
        <p className="accueil-eyebrow">🤖 Agents</p>
        <h1>Chasseur de mission</h1>
        <p className="page-intro">Accès réservé — saisissez le mot de passe pour continuer.</p>
        <div className="admin-connexion">
          <input
            type="password"
            value={motDePasse}
            onChange={(e) => setMotDePasse(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && connexion()}
            placeholder="Mot de passe"
          />
          <button onClick={connexion} disabled={enCoursConnexion || !motDePasse}>
            {enCoursConnexion ? 'Vérification…' : 'Se connecter'}
          </button>
        </div>
        {erreurConnexion && <p className="erreur">{erreurConnexion}</p>}
      </div>
    )
  }

  return (
    <div className="page page-agents">
      <p className="accueil-eyebrow">🤖 Agents</p>
      <h1>Chasseur de mission</h1>
      <p className="page-intro">
        Un agent de recherche qui repère de vraies missions et offres d'emploi (conseil/IT et
        pilote de drone, France/Maroc), en respectant strictement les CGU de chaque plateforme —
        jamais de scraping LinkedIn, jamais de collecte automatisée en boucle. Relancé
        ponctuellement, pas un crawler permanent : les résultats ci-dessous datent de sa dernière
        passe de recherche.
      </p>

      <div className="mission-recherche-panneau">
        <h3>🔎 Rechercher maintenant</h3>
        <p className="texte-muted">
          Déclenche une vraie recherche web (Claude + web_search), en respectant les mêmes règles
          CGU. Prend en général 30 à 90 secondes.
        </p>
        <div className="mission-recherche-champs">
          <input
            type="text"
            value={motsCles}
            onChange={(e) => setMotsCles(e.target.value)}
            placeholder="Mots-clés (optionnel, ex. « développeur React freelance »)"
            disabled={statutJob === 'en_cours'}
          />
          {(['France', 'Maroc'] as const).map((p) => (
            <label key={p} className="mission-recherche-checkbox">
              <input
                type="checkbox"
                checked={paysRecherche.includes(p)}
                onChange={() => togglePaysRecherche(p)}
                disabled={statutJob === 'en_cours'}
              />
              {LABELS_PAYS[p]}
            </label>
          ))}
          <button onClick={lancer} disabled={statutJob === 'en_cours' || paysRecherche.length === 0}>
            {statutJob === 'en_cours' ? 'Recherche en cours…' : 'Lancer la recherche'}
          </button>
        </div>
        {messageRecherche && (
          <p className={statutJob === 'erreur' ? 'erreur' : 'texte-muted'}>{messageRecherche}</p>
        )}
      </div>

      {stats && stats.total > 0 && (
        <>
          <div className="stats-legende">
            <div className="stat-item">
              <span className="stat-item-chiffre">{stats.total}</span>
              <span className="stat-item-label">missions collectées</span>
            </div>
            <div className="stat-item">
              <span className="stat-item-chiffre">{pctFreelance}%</span>
              <span className="stat-item-label">en freelance</span>
            </div>
            <div className="stat-item">
              <span className="stat-item-chiffre">{Object.keys(stats.par_pays).length}</span>
              <span className="stat-item-label">pays couverts</span>
            </div>
            <div className="stat-item">
              <span className="stat-item-chiffre">{stats.derniere_collecte ?? '—'}</span>
              <span className="stat-item-label">dernière collecte</span>
            </div>
          </div>

          <div className="mission-graphiques-grille">
            <RepartitionBarChart titre="Par pays" donnees={versBarres(stats.par_pays, LABELS_PAYS)} />
            <RepartitionBarChart titre="Par famille" donnees={versBarres(stats.par_famille, LABELS_FAMILLE)} />
            <RepartitionBarChart titre="Freelance vs CDI" donnees={versBarres(stats.par_type_contrat, LABELS_CONTRAT)} />
            <RepartitionBarChart titre="Par source" donnees={versBarres(stats.par_source)} />
          </div>

          {nbMoisHistorique < 2 && (
            <p className="texte-muted note mission-note-historique">
              Historique en cours de constitution : une seule passe de recherche a eu lieu pour
              l'instant ({stats.derniere_collecte}). Une évolution mensuelle apparaîtra ici après
              plusieurs relances.
            </p>
          )}
        </>
      )}

      {stats && stats.total === 0 && <p className="texte-muted">Aucune mission collectée pour l'instant.</p>}

      <div className="exemples-categories">
        {['tous', 'France', 'Maroc'].map((p) => (
          <button key={p} className={p === filtrePays ? 'chip actif' : 'chip'} onClick={() => setFiltrePays(p)}>
            {p === 'tous' ? 'Tous pays' : LABELS_PAYS[p] ?? p}
          </button>
        ))}
        {['tous', 'conseil_it', 'drone'].map((f) => (
          <button key={f} className={f === filtreFamille ? 'chip actif' : 'chip'} onClick={() => setFiltreFamille(f)}>
            {f === 'tous' ? 'Toutes familles' : LABELS_FAMILLE[f] ?? f}
          </button>
        ))}
      </div>

      <div className="mission-table-wrap">
        <table className="mission-table">
          <thead>
            <tr>
              <th>Intitulé</th>
              <th>Entreprise</th>
              <th>Ville</th>
              <th>Contrat</th>
              <th>Rémunération</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((m) => (
              <tr key={m.id}>
                <td>
                  <a href={m.lien} target="_blank" rel="noopener noreferrer">
                    {m.intitule}
                  </a>
                </td>
                <td>{m.entreprise}</td>
                <td>
                  {m.ville} <span className="texte-muted">({LABELS_PAYS[m.pays] ?? m.pays})</span>
                </td>
                <td>{LABELS_CONTRAT[m.type_contrat] ?? m.type_contrat}</td>
                <td>{m.remuneration}</td>
                <td>{m.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
