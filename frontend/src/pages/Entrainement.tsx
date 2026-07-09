import { useEffect, useState } from 'react'
import {
  apercuDonnees,
  demarrerEntrainement,
  listerScenariosEntrainement,
  obtenirJobEntrainement,
  suivreEntrainement,
  testerModeleEntraine,
} from '../api/client'
import LossChart from '../components/LossChart'

type Statut = 'inactif' | 'en_cours' | 'termine' | 'erreur'

export default function Entrainement() {
  const [scenarios, setScenarios] = useState<any[]>([])
  const [scenarioId, setScenarioId] = useState<string | null>(null)
  const [apercu, setApercu] = useState<any>(null)
  const [historique, setHistorique] = useState<any[]>([])
  const [statut, setStatut] = useState<Statut>('inactif')
  const [erreur, setErreur] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [avant, setAvant] = useState<any[] | null>(null)
  const [apres, setApres] = useState<any[] | null>(null)
  const [testEntree, setTestEntree] = useState('')
  const [testResultat, setTestResultat] = useState<any>(null)

  useEffect(() => {
    listerScenariosEntrainement().then((s) => {
      setScenarios(s)
      if (s.length > 0) choisirScenario(s[0].id)
    })
  }, [])

  async function choisirScenario(id: string) {
    setScenarioId(id)
    setHistorique([])
    setStatut('inactif')
    setErreur(null)
    setJobId(null)
    setAvant(null)
    setApres(null)
    setTestResultat(null)
    setApercu(await apercuDonnees(id))
  }

  async function lancer() {
    if (!scenarioId) return
    setHistorique([])
    setErreur(null)
    setTestResultat(null)
    setApres(null)
    setStatut('en_cours')
    const { job_id } = await demarrerEntrainement(scenarioId)
    setJobId(job_id)
    const job = await obtenirJobEntrainement(job_id)
    setAvant(job.avant)

    suivreEntrainement(
      job_id,
      (point) => setHistorique((h) => [...h, point]),
      async (fin) => {
        setStatut(fin.status === 'termine' ? 'termine' : 'erreur')
        if (fin.erreur) setErreur(fin.erreur)
        if (fin.status === 'termine') {
          const jobFinal = await obtenirJobEntrainement(job_id)
          setApres(jobFinal.apres)
        }
      },
    )
  }

  async function tester() {
    if (!jobId) return
    try {
      const r = await testerModeleEntraine(jobId, testEntree)
      setTestResultat(r)
    } catch (e: any) {
      setTestResultat({ erreur: e.message })
    }
  }

  const scenario = scenarios.find((s) => s.id === scenarioId)

  return (
    <div className="page">
      <h1>Entraînement — comprendre la perte (loss)</h1>
      <p className="page-intro">
        Le module Entraînement s'attache à rendre visible ce qui demeure, la plupart du temps,
        invisible : la manière dont un modèle apprend. Trois scénarios réels, relevant chacun d'une
        famille d'algorithme différente, permettent d'observer précisément les données mobilisées,
        avant de comparer, sur une dizaine d'exemples, le comportement du modèle avant et après son
        entraînement.
      </p>

      <div className="filtres">
        {scenarios.map((s) => (
          <button
            key={s.id}
            className={s.id === scenarioId ? 'filtre actif' : 'filtre'}
            onClick={() => choisirScenario(s.id)}
          >
            {s.titre}
          </button>
        ))}
      </div>

      {scenario && (
        <div className="explication-bloc">
          <h4>Cas d'usage</h4>
          <p>{scenario.cas_usage}</p>
          <p className="texte-muted">
            <strong>Type d'algorithme :</strong> {scenario.famille_algo} — {scenario.modele_base}
          </p>
        </div>
      )}

      {apercu && (
        <div className="explication-bloc">
          <h4>
            Les données d'entraînement ({apercu.total} exemples, {apercu.lignes.length} affichés)
          </h4>
          <div className="table-scroll">
            <table className="table-donnees">
              <thead>
                <tr>
                  {apercu.colonnes.map((c: string) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {apercu.lignes.map((ligne: any, i: number) => (
                  <tr key={i}>
                    {apercu.colonnes.map((c: string) => (
                      <td key={c}>{String(ligne[c])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <button onClick={lancer} disabled={statut === 'en_cours' || !scenarioId}>
        {statut === 'en_cours' ? 'Entraînement en cours…' : 'Lancer cet entraînement'}
      </button>

      {historique.length > 0 && <LossChart data={historique} />}
      {statut === 'termine' && <p className="succes">Entraînement terminé — regarde l'avant/après ci-dessous.</p>}
      {erreur && <p className="erreur">{erreur}</p>}

      {avant && (
        <div className="explication-bloc">
          <h4>Avant / après — {avant.length} exemples jamais vus par le modèle pendant l'entraînement</h4>
          <div className="table-scroll">
            <table className="table-donnees">
              <thead>
                <tr>
                  <th>Entrée</th>
                  <th>Avant entraînement</th>
                  <th>Après entraînement</th>
                </tr>
              </thead>
              <tbody>
                {avant.map((a, i) => {
                  const ap = apres?.[i]
                  return (
                    <tr key={i}>
                      <td>{a.entree}</td>
                      <td className="cellule-avant">{a.prediction}</td>
                      <td className="cellule-apres">{ap ? ap.prediction : '…'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          {!apres && statut === 'en_cours' && (
            <p className="texte-muted">La colonne « après » se remplit une fois l'entraînement terminé.</p>
          )}
        </div>
      )}

      {statut === 'termine' && jobId && (
        <div className="explication-bloc">
          <h4>Teste le modèle avec ta propre entrée</h4>
          <input
            className="input-texte"
            value={testEntree}
            onChange={(e) => setTestEntree(e.target.value)}
            placeholder={
              scenarioId === 'prevision_ca'
                ? 'Numéro du mois à prévoir (ex: 20)'
                : 'Tapez votre propre exemple…'
            }
          />
          <button onClick={tester}>Tester</button>
          {testResultat && !testResultat.erreur && (
            <p className="traduction-cible">
              → {testResultat.prediction}
              {testResultat.confiance != null && ` (confiance ${(testResultat.confiance * 100).toFixed(0)}%)`}
            </p>
          )}
          {testResultat?.erreur && <p className="erreur">{testResultat.erreur}</p>}
        </div>
      )}

      <div className="explication-bloc">
        <h4>Pourquoi la courbe descend (ou pas)</h4>
        <ul>
          <li>
            <strong>Loss</strong> : un nombre qui mesure l'écart entre la prédiction du modèle et
            la bonne réponse. Plus il est petit, mieux c'est — et c'est le même principe, qu'il
            s'agisse d'un réseau de neurones ou d'un algorithme classique comme la régression
            logistique ou linéaire.
          </li>
          <li>
            <strong>Epoch</strong> : un passage complet sur tout le jeu de données.
          </li>
          <li>
            <strong>Surapprentissage (overfitting)</strong> : si on entraînait beaucoup plus
            longtemps sur un aussi petit jeu de données, le modèle finirait par « apprendre par
            cœur » ces exemples précis plutôt que la notion générale recherchée.
          </li>
        </ul>
      </div>
    </div>
  )
}
