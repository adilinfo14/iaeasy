import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts'

type Props = { resultat: any }

function Meter({ valeur, etiquette }: { valeur: number; etiquette: string }) {
  const pct = Math.max(0, Math.min(1, valeur)) * 100
  const couleur = valeur > 0.66 ? '#4ade80' : valeur > 0.33 ? '#facc15' : '#ff6b6b'
  return (
    <div className="meter">
      <div className="meter-label">
        {etiquette} — <strong>{(valeur * 100).toFixed(0)}%</strong>
      </div>
      <div className="meter-track">
        <div className="meter-fill" style={{ width: `${pct}%`, background: couleur }} />
      </div>
    </div>
  )
}

function EntitesSurlignees({ texte, entites }: { texte: string; entites: any[] }) {
  if (entites.length === 0) return <p>{texte}</p>
  const trie = [...entites]
  const segments: { texte: string; categorie?: string }[] = []
  let curseur = 0
  for (const e of trie) {
    const idx = texte.indexOf(e.texte, curseur)
    if (idx === -1) continue
    if (idx > curseur) segments.push({ texte: texte.slice(curseur, idx) })
    segments.push({ texte: e.texte, categorie: e.categorie })
    curseur = idx + e.texte.length
  }
  if (curseur < texte.length) segments.push({ texte: texte.slice(curseur) })

  return (
    <p className="entites-texte">
      {segments.map((s, i) =>
        s.categorie ? (
          <span key={i} className={`entite entite-${s.categorie.toLowerCase()}`}>
            {s.texte}
            <sup>{s.categorie}</sup>
          </span>
        ) : (
          <span key={i}>{s.texte}</span>
        ),
      )}
    </p>
  )
}

export default function ResultRenderer({ resultat }: Props) {
  if (!resultat) return null

  switch (resultat.type) {
    case 'texte':
      return <div className="resultat-carte">{resultat.sortie}</div>

    case 'traduction':
      return (
        <div className="resultat-carte">
          <p className="traduction-cible">→ {resultat.sortie}</p>
        </div>
      )

    case 'resume':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Texte original ({resultat.texte_original?.length ?? 0} caractères) :</p>
          <p className="texte-original">{resultat.texte_original}</p>
          <p className="texte-muted">Résumé généré :</p>
          <p className="traduction-cible">{resultat.sortie}</p>
        </div>
      )

    case 'similarite':
      return (
        <div className="resultat-carte">
          <div className="phrase-chip">A · {resultat.phrase_a}</div>
          <div className="phrase-chip">B · {resultat.phrase_b}</div>
          <Meter valeur={resultat.similarite_cosinus} etiquette="Similarité cosinus" />
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'classification':
      return (
        <div className="resultat-carte">
          <div className="badge-etiquette">{resultat.etiquette}</div>
          <Meter valeur={resultat.confiance} etiquette="Confiance" />
        </div>
      )

    case 'detection_langue':
      return (
        <div className="resultat-carte">
          <div className="badge-etiquette">Langue détectée : {resultat.langue_detectee.toUpperCase()}</div>
          <Meter valeur={resultat.confiance} etiquette="Confiance" />
        </div>
      )

    case 'extraction_entites':
      return (
        <div className="resultat-carte">
          <EntitesSurlignees texte={resultat.texte_analyse} entites={resultat.entites} />
          {resultat.entites.length === 0 && <p className="texte-muted">Aucune entité détectée.</p>}
        </div>
      )

    case 'question_reponse':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Contexte fourni :</p>
          <p className="texte-original">{resultat.contexte}</p>
          <p className="texte-muted">Question : « {resultat.question} »</p>
          <div className="badge-etiquette">Réponse : {resultat.reponse}</div>
          <Meter valeur={resultat.confiance} etiquette="Confiance" />
        </div>
      )

    case 'transcription_audio':
      return (
        <div className="resultat-carte">
          <audio controls src={`data:audio/wav;base64,${resultat.audio_base64}`} style={{ width: '100%' }} />
          <p className="texte-muted">Texte transcrit :</p>
          <p className="traduction-cible">{resultat.texte_transcrit}</p>
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'detection_objets':
      return (
        <div className="resultat-carte">
          <img
            src={`data:image/jpeg;base64,${resultat.image_annotee_base64}`}
            alt="Détection d'objets"
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          <ul className="liste-simple">
            {resultat.objets_detectes.map((o: any, i: number) => (
              <li key={i}>
                {o.etiquette} — {(o.confiance * 100).toFixed(0)}%
              </li>
            ))}
          </ul>
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'classification_image':
      return (
        <div className="resultat-carte">
          <img
            src={`data:image/jpeg;base64,${resultat.image_base64}`}
            alt="Image classifiée"
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          {resultat.predictions.map((p: any, i: number) => (
            <Meter key={i} valeur={p.confiance} etiquette={p.etiquette} />
          ))}
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'prevision_serie_temporelle': {
      const data = [
        ...resultat.historique.map((v: number, i: number) => ({ x: i, historique: v })),
        ...resultat.prevision_mediane.map((v: number, i: number) => ({
          x: resultat.historique.length + i,
          prevision: v,
          bas: resultat.intervalle_bas[i],
          haut: resultat.intervalle_haut[i],
        })),
      ]
      return (
        <div className="resultat-carte">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="x" label={{ value: 'Mois', position: 'insideBottom', offset: -5 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="historique" name="Historique" stroke="#4f7cff" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="prevision" name="Prévision" stroke="#4ade80" strokeDasharray="5 5" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="haut" name="Intervalle haut" stroke="#4ade8055" dot={false} strokeWidth={1} />
              <Line type="monotone" dataKey="bas" name="Intervalle bas" stroke="#4ade8055" dot={false} strokeWidth={1} />
            </LineChart>
          </ResponsiveContainer>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )
    }

    case 'detection_anomalie': {
      const anomIdx = new Set(resultat.anomalies_detectees.map((a: any) => a.indice))
      const normales = resultat.mesures
        .map((v: number, i: number) => ({ x: i, y: v }))
        .filter((p: any) => !anomIdx.has(p.x))
      const anomalies = resultat.anomalies_detectees.map((a: any) => ({ x: a.indice, y: a.valeur ?? a.montant }))
      return (
        <div className="resultat-carte">
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="x" name="Mesure n°" type="number" />
              <YAxis dataKey="y" name="Valeur" type="number" />
              <ZAxis range={[30, 30]} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={normales} fill="#4f7cff" />
              <Scatter data={anomalies} fill="#ff6b6b" />
            </ScatterChart>
          </ResponsiveContainer>
          <p className="texte-muted">
            {resultat.anomalies_detectees.length} anomalie(s) détectée(s) sur {resultat.nb_mesures} mesures (en rouge).
          </p>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )
    }

    case 'scoring_credit':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">
            Entraîné en direct sur {resultat.nb_dossiers_entrainement} dossiers jouets ({resultat.nb_dossiers_a_risque} à risque).
          </p>
          <p className="texte-muted">Dossier testé :</p>
          <ul className="liste-simple">
            <li>Revenu mensuel : {resultat.dossier_teste.revenu_mensuel} €</li>
            <li>Taux d'endettement : {(resultat.dossier_teste.taux_endettement * 100).toFixed(0)}%</li>
            <li>Incidents de paiement : {resultat.dossier_teste.incidents_paiement}</li>
          </ul>
          <Meter valeur={resultat.probabilite_risque} etiquette="Probabilité de risque" />
          <div className="badge-etiquette">{resultat.decision_suggeree}</div>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'scoring_assurance_auto':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">
            Entraîné en direct sur {resultat.nb_profils_entrainement} profils jouets ({resultat.nb_profils_a_risque} à risque).
          </p>
          <p className="texte-muted">Profil testé :</p>
          <ul className="liste-simple">
            <li>Âge du conducteur : {resultat.profil_teste.age_conducteur} ans</li>
            <li>Ancienneté du permis : {resultat.profil_teste.anciennete_permis_annees} ans</li>
            <li>Sinistres responsables (3 ans) : {resultat.profil_teste.nb_sinistres_3ans}</li>
          </ul>
          <Meter valeur={resultat.probabilite_risque} etiquette="Probabilité de risque" />
          <div className="badge-etiquette">{resultat.decision_suggeree}</div>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'scoring_assurance_sante':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">
            Entraîné en direct sur {resultat.nb_profils_entrainement} profils jouets ({resultat.nb_profils_a_risque} à risque).
          </p>
          <p className="texte-muted">Profil testé :</p>
          <ul className="liste-simple">
            <li>Âge : {resultat.profil_teste.age} ans</li>
            <li>Consultations dans l'année : {resultat.profil_teste.nb_consultations_an}</li>
            <li>Hospitalisation récente : {resultat.profil_teste.hospitalisation_recente ? 'Oui' : 'Non'}</li>
          </ul>
          <Meter valeur={resultat.probabilite_risque} etiquette="Probabilité de sur-risque" />
          <div className="badge-etiquette">{resultat.decision_suggeree}</div>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'scoring_pret_immobilier':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">
            Entraîné en direct sur {resultat.nb_dossiers_entrainement} dossiers jouets ({resultat.nb_dossiers_acceptes} acceptés).
          </p>
          <p className="texte-muted">Dossier testé :</p>
          <ul className="liste-simple">
            <li>Apport : {(resultat.dossier_teste.apport_pourcent * 100).toFixed(0)}%</li>
            <li>Durée du prêt : {resultat.dossier_teste.duree_annees} ans</li>
            <li>Revenu mensuel : {resultat.dossier_teste.revenu_mensuel} €</li>
          </ul>
          <Meter valeur={resultat.probabilite_acceptation} etiquette="Probabilité d'acceptation" />
          <div className="badge-etiquette">{resultat.decision_suggeree}</div>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'recommandation':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Notes déjà données par {resultat.utilisateur} :</p>
          <ul className="liste-simple">
            {resultat.films_deja_notes.map((f: any, i: number) => (
              <li key={i}>
                {f.film} — {'⭐'.repeat(f.note)}
              </li>
            ))}
          </ul>
          <div className="badge-etiquette">Recommandation : {resultat.film_recommande}</div>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'segmentation_image':
      return (
        <div className="resultat-carte">
          <img
            src={`data:image/jpeg;base64,${resultat.image_annotee_base64}`}
            alt="Segmentation d'objets"
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          <ul className="liste-simple">
            {resultat.objets_segmentes.map((o: any, i: number) => (
              <li key={i}>
                {o.etiquette} — {(o.confiance * 100).toFixed(0)}% ({o.nb_points_contour} points de contour)
              </li>
            ))}
          </ul>
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'estimation_pose':
      return (
        <div className="resultat-carte">
          <img
            src={`data:image/jpeg;base64,${resultat.image_annotee_base64}`}
            alt="Estimation de pose"
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          <ul className="liste-simple">
            {resultat.personnes_detectees.map((p: any, i: number) => (
              <li key={i}>
                Personne {p.personne} — {p.points_cles_detectes}/{p.points_cles_total} points clés détectés
              </li>
            ))}
          </ul>
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'clustering':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">
            {resultat.nb_clients_total} clients répartis en {resultat.nb_groupes} groupes, découverts sans étiquette fournie :
          </p>
          <ul className="liste-simple">
            {resultat.groupes_decouverts.map((g: any, i: number) => (
              <li key={i}>
                Groupe {g.groupe} — {g.nb_clients} clients, panier moyen {g.montant_moyen_facture}€,{' '}
                {g.frequence_moyenne_par_an}x/an
              </li>
            ))}
          </ul>
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'similarite_image':
      return (
        <div className="resultat-carte">
          <div style={{ display: 'flex', gap: '0.6rem' }}>
            <img
              src={`data:image/jpeg;base64,${resultat.image_a_base64}`}
              alt="Image A"
              style={{ maxWidth: '48%', borderRadius: 8 }}
            />
            <img
              src={`data:image/jpeg;base64,${resultat.image_b_base64}`}
              alt="Image B"
              style={{ maxWidth: '48%', borderRadius: 8 }}
            />
          </div>
          <Meter valeur={resultat.similarite_cosinus} etiquette="Similarité cosinus" />
          <p className="texte-muted">{resultat.explication}</p>
        </div>
      )

    case 'ocr_texte':
      return (
        <div className="resultat-carte">
          <img
            src={`data:image/png;base64,${resultat.image_base64}`}
            alt="Document à lire"
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          <p className="texte-muted">Texte extrait :</p>
          <pre className="traduction-cible">{resultat.texte_extrait}</pre>
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'classification_multi_labels':
      return (
        <div className="resultat-carte">
          {resultat.predictions.map((p: any, i: number) => (
            <Meter key={i} valeur={p.confiance} etiquette={p.etiquette} />
          ))}
        </div>
      )

    case 'classification_zero_shot':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Catégories candidates classées par pertinence :</p>
          {resultat.predictions.map((p: any, i: number) => (
            <Meter key={i} valeur={p.confiance} etiquette={p.etiquette} />
          ))}
        </div>
      )

    case 'question_generee':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Texte source :</p>
          <p className="texte-original">{resultat.texte_source}</p>
          <p className="texte-muted">Question générée :</p>
          <div className="badge-etiquette">{resultat.question_generee}</div>
        </div>
      )

    case 'correction_grammaticale':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Texte original :</p>
          <p className="texte-original">{resultat.texte_original}</p>
          <p className="texte-muted">Texte corrigé :</p>
          <p className="traduction-cible">{resultat.texte_corrige}</p>
        </div>
      )

    case 'legende_image':
      return (
        <div className="resultat-carte">
          <img
            src={`data:image/jpeg;base64,${resultat.image_base64}`}
            alt="Image à légender"
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          <p className="texte-muted">Légende générée :</p>
          <div className="badge-etiquette">{resultat.legende}</div>
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'classification_audio':
      return (
        <div className="resultat-carte">
          <audio controls src={`data:audio/wav;base64,${resultat.audio_base64}`} style={{ width: '100%' }} />
          {resultat.predictions.map((p: any, i: number) => (
            <Meter key={i} valeur={p.confiance} etiquette={p.etiquette} />
          ))}
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'image_generee':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Prompt :</p>
          <p className="texte-original">{resultat.prompt}</p>
          <img
            src={`data:image/png;base64,${resultat.image_base64}`}
            alt={resultat.prompt}
            style={{ maxWidth: '100%', borderRadius: 8 }}
          />
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    case 'synthese_vocale':
      return (
        <div className="resultat-carte">
          <p className="texte-muted">Texte source :</p>
          <p className="texte-original">{resultat.texte_source}</p>
          <audio controls src={`data:audio/wav;base64,${resultat.audio_base64}`} style={{ width: '100%' }} />
          <p className="texte-muted note">{resultat.note}</p>
        </div>
      )

    default:
      return <pre className="resultat">{JSON.stringify(resultat, null, 2)}</pre>
  }
}
