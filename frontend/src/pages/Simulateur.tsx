import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import {
  comparerClassification,
  comparerEmbeddings,
  comparerVision,
  demarrerComparaisonModeles,
  listerModelesClassification,
  listerModelesEmbeddings,
  listerModelesSimulateur,
  listerModelesVision,
  suivreComparaisonModeles,
} from '../api/client'

const CATEGORIES = [
  {
    categorie: 'Raisonnement / logique',
    exemples: [
      "J'ai 3 boîtes. La rouge contient 2 fois plus de billes que la bleue. La verte en contient 5 de moins que la rouge. Il y a 45 billes au total. Combien y en a-t-il dans chaque boîte ?",
      'Trois amis, Alice, Bruno et Chloé, ont chacun un âge différent. Alice est plus âgée que Bruno. Chloé est la plus jeune. Bruno a 28 ans. Qui est le plus âgé ?',
      "Un train part de Paris à 14h à 90 km/h. Un autre part de Lyon (450 km) à 14h30 à 110 km/h, en sens inverse. À quelle heure se croisent-ils ?",
      "Si tous les artisans du bâtiment utilisent un marteau, et que Paul est artisan du bâtiment, que peut-on en conclure sur Paul ?",
      'Compare en 4 points les avantages et inconvénients du télétravail pour une PME de 10 salariés.',
    ],
  },
  {
    categorie: 'Calcul',
    exemples: [
      'Combien font 17 fois 23 ?',
      "Un artisan facture 45€/heure. Il a travaillé 3h30 lundi et 2h15 mardi. Calcule le total facturé, étape par étape.",
      "Un client a acheté 3 articles à 12,50€ et 2 articles à 7,90€, avec une remise de 10% sur le total. Calcule le montant final.",
      'Un prêt de 15 000€ sur 4 ans à un taux fixe de 3% par an : quelle est approximativement la mensualité ?',
      'Convertis 2,5 heures et 45 minutes en minutes, puis en secondes.',
    ],
  },
  {
    categorie: 'Rédaction professionnelle',
    exemples: [
      "Rédige un message pour prévenir un client d'un retard de chantier.",
      'Rédige un email pour relancer un fournisseur dont la livraison a 2 semaines de retard.',
      "Rédige une annonce d'offre d'emploi pour un poste de plombier, 3 ans d'expérience minimum.",
      "Rédige un compte-rendu de réunion de 5 lignes à partir de : validation du planning, retard de 3 semaines sur le gros œuvre, renfort d'équipe prévu.",
      'Rédige un message de remerciement à envoyer à un client après la fin des travaux.',
    ],
  },
  {
    categorie: 'Reformulation / ton',
    exemples: [
      "Reformule cette phrase de façon plus polie : 'vous devez payer maintenant sinon on arrête tout'.",
      "Réponds poliment à cet avis Google 2 étoiles : 'Livraison en retard et produit abîmé, très déçu.'",
      'Reformule ce message en version plus formelle pour un email professionnel : \'salut, on peut pas venir demain, on décale à jeudi\'.',
      "Réécris cette phrase pour qu'elle soit plus rassurante : 'il y a un problème sur votre dossier, on ne sait pas encore combien de temps ça va prendre'.",
      "Simplifie ce texte administratif pour un client non spécialiste : 'la garantie décennale couvre les dommages compromettant la solidité de l'ouvrage ou le rendant impropre à sa destination'.",
    ],
  },
  {
    categorie: 'Traduction',
    exemples: [
      'Traduis en anglais : « Veuillez trouver ci-joint le devis signé pour la rénovation de la toiture. »',
      'Traduis en anglais : « Nous vous rappelons que votre facture est en attente de règlement depuis 15 jours. »',
      'Traduis en espagnol : « Bonjour, votre commande sera livrée sous 48 heures ouvrées. »',
      "Traduis en français cette phrase : « We would be delighted to present our new product range during a meeting. »",
      'Traduis en allemand : « Merci de nous contacter pour toute question concernant votre garantie. »',
    ],
  },
  {
    categorie: 'Code / développement',
    exemples: [
      'Écris une fonction Python qui vérifie si un nombre est premier.',
      "Écris une fonction Python qui prend une liste de prix TTC et renvoie la liste des prix HT (TVA 20%).",
      "Corrige ce code Python qui plante : def moyenne(l): return sum(l)/len(l) -- appelé avec une liste vide.",
      'Écris une fonction Python qui renomme tous les fichiers PDF d\'un dossier au format "facture_AAAA-MM-JJ.pdf".',
      "Explique en une phrase la différence entre une liste et un dictionnaire en Python, pour un débutant.",
    ],
  },
  {
    categorie: 'Résumé',
    exemples: [
      "Résume en une phrase : 'Le télétravail permet de réduire les temps de trajet mais complique parfois la coordination d'équipe et l'accès à certains outils internes.'",
      "Résume en 3 lignes maximum les causes principales de la Révolution française.",
      'Résume ce texte en une phrase : "Le comité de direction a validé le lancement du nouveau produit en octobre, malgré quelques bugs mineurs restants et un budget marketing revu à la hausse de 8%."',
      "Résume les points clés d'un contrat en 3 puces : garantie 2 ans sur les matériaux, pas de couverture en cas de mauvaise utilisation, service client joignable du lundi au vendredi.",
      'Résume ce compte-rendu en 2 phrases : retard de 3 semaines sur le chantier, renfort d\'équipe prévu le 20 juin, client informé et délai accepté.',
    ],
  },
  {
    categorie: 'Créativité',
    exemples: [
      'Propose 3 noms originaux pour une nouvelle marque de café bio.',
      "Propose 3 titres accrocheurs pour un exposé sur le recyclage du plastique, destiné à des collégiens.",
      'Invente un court slogan pour une entreprise de rénovation de toiture, en une phrase.',
      'Propose 3 idées de contenu pour les réseaux sociaux d\'un artisan plombier.',
      "Écris une courte histoire de 4 phrases sur un robot qui apprend à cuisiner.",
    ],
  },
  {
    categorie: 'Explication pédagogique',
    exemples: [
      "Explique en 3 phrases ce qu'est la garantie décennale.",
      'Explique en 3 phrases ce qu\'est la photosynthèse, pour un collégien.',
      "Explique la différence entre un modèle génératif et un modèle de classification, en une phrase simple.",
      "Explique ce qu'est un taux d'intérêt composé, avec un exemple chiffré simple.",
      "Explique à un enfant de 8 ans pourquoi le ciel est bleu.",
    ],
  },
  {
    categorie: 'Limites et robustesse',
    exemples: [
      "Quelle est la capitale de la France en 1600 avant J.-C. ?",
      "Combien pèse un kilo de plumes comparé à un kilo de plomb ?",
      "Si demain il pleut, et qu'aujourd'hui il fait beau, quel jour sommes-nous ?",
      'Peux-tu me donner un avis médical sur une douleur au dos que je ressens depuis 2 jours ?',
      "Réponds seulement par oui ou par non : est-ce que 0,1 + 0,2 fait exactement 0,3 ?",
    ],
  },
]

const TOUS_LES_EXEMPLES = CATEGORIES.flatMap((c) => c.exemples)

const PAIRES_EXEMPLES = [
  {
    categorie: 'Synonymes',
    phraseA: 'Le chat dort sur le canapé.',
    phraseB: 'Un félin fait la sieste sur le sofa.',
  },
  {
    categorie: 'Sens opposé',
    phraseA: 'Le client est très satisfait du service.',
    phraseB: 'Le client est furieux et veut être remboursé.',
  },
  {
    categorie: 'Sans rapport',
    phraseA: 'La réunion est reportée à demain.',
    phraseB: 'Il pleut fort sur la côte bretonne.',
  },
  {
    categorie: 'Paraphrase professionnelle',
    phraseA: "Comment poser mes congés payés ?",
    phraseB: 'Quelle est la procédure pour demander des vacances ?',
  },
  {
    categorie: 'Nuance subtile',
    phraseA: "L'appartement était impeccable, exactement conforme aux photos.",
    phraseB: 'Le colis est arrivé avec deux jours de retard et l\'emballage était abîmé.',
  },
]

const EXEMPLES_CLASSIFICATION = [
  'Cliquez ici pour gagner un iPhone gratuitement maintenant.',
  'Bonjour, voici le compte-rendu de la réunion de ce matin.',
  'Urgent : votre compte sera fermé, confirmez vos données ici.',
  'Merci de valider le devis ci-joint avant vendredi.',
  'Vous avez gagné 10000€, réclamez votre prix immédiatement.',
  'Le rendez-vous chantier est confirmé pour lundi 9h.',
]

const FAMILLES = [
  {
    id: 'llm_generatif',
    label: 'LLM génératif',
    disponible: true,
    note: 'Ces modèles répondent à un prompt en texte libre : on compare durée et réponse.',
  },
  {
    id: 'embeddings',
    label: 'Embeddings',
    disponible: true,
    note: 'Ces modèles transforment 2 phrases en vecteurs : on compare durée et score de similarité.',
  },
  {
    id: 'vision',
    label: 'Vision',
    disponible: true,
    note: "Ces modèles analysent la même image d'exemple fournie par l'outil : on compare durée et objets détectés.",
  },
  {
    id: 'classification_classique',
    label: 'Classification classique',
    disponible: true,
    note: 'Ces algorithmes s\'entraînent en direct sur le même jeu de données (spam) : on compare durée d\'entraînement et précision.',
  },
]

export default function Simulateur() {
  const [categorieActive, setCategorieActive] = useState(CATEGORIES[0].categorie)
  const [prompt, setPrompt] = useState(TOUS_LES_EXEMPLES[0])
  const [enCours, setEnCours] = useState(false)
  const [resultat, setResultat] = useState<any>(null)
  const [erreur, setErreur] = useState<string | null>(null)
  const [modeles, setModeles] = useState<any[]>([])
  const [selectionnes, setSelectionnes] = useState<Set<string>>(new Set())
  const [familleActive, setFamilleActive] = useState('llm_generatif')

  // Famille Embeddings : état séparé, mécanique différente (2 phrases à comparer, pas un
  // prompt qui produit une réponse).
  const [modelesEmbeddings, setModelesEmbeddings] = useState<any[]>([])
  const [selectionnesEmbeddings, setSelectionnesEmbeddings] = useState<Set<string>>(new Set())
  const [phraseA, setPhraseA] = useState(PAIRES_EXEMPLES[0].phraseA)
  const [phraseB, setPhraseB] = useState(PAIRES_EXEMPLES[0].phraseB)
  const [enCoursEmbeddings, setEnCoursEmbeddings] = useState(false)
  const [resultatEmbeddings, setResultatEmbeddings] = useState<any>(null)
  const [erreurEmbeddings, setErreurEmbeddings] = useState<string | null>(null)

  // Famille Classification classique : entraînement en direct sur le même jeu de données, un
  // message à classer plutôt qu'un prompt libre.
  const [modelesClassification, setModelesClassification] = useState<any[]>([])
  const [selectionnesClassification, setSelectionnesClassification] = useState<Set<string>>(new Set())
  const [messageClassification, setMessageClassification] = useState(
    'Cliquez ici pour gagner un iPhone gratuitement maintenant.',
  )
  const [enCoursClassification, setEnCoursClassification] = useState(false)
  const [resultatClassification, setResultatClassification] = useState<any>(null)
  const [erreurClassification, setErreurClassification] = useState<string | null>(null)

  // Famille Vision : aucune saisie, l'outil fournit lui-même l'image d'exemple.
  const [modelesVision, setModelesVision] = useState<any[]>([])
  const [selectionnesVision, setSelectionnesVision] = useState<Set<string>>(new Set())
  const [enCoursVision, setEnCoursVision] = useState(false)
  const [resultatVision, setResultatVision] = useState<any>(null)
  const [erreurVision, setErreurVision] = useState<string | null>(null)

  useEffect(() => {
    listerModelesSimulateur().then((liste) => {
      setModeles(liste)
      setSelectionnes(new Set(liste.map((m: any) => m.id)))
    })
    listerModelesEmbeddings().then((liste) => {
      setModelesEmbeddings(liste)
      setSelectionnesEmbeddings(new Set(liste.map((m: any) => m.id)))
    })
    listerModelesClassification().then((liste) => {
      setModelesClassification(liste)
      setSelectionnesClassification(new Set(liste.map((m: any) => m.id)))
    })
    listerModelesVision().then((liste) => {
      setModelesVision(liste)
      setSelectionnesVision(new Set(liste.map((m: any) => m.id)))
    })
  }, [])

  function basculerModele(id: string) {
    setSelectionnes((s) => {
      const copie = new Set(s)
      if (copie.has(id)) copie.delete(id)
      else copie.add(id)
      return copie
    })
  }

  function basculerModeleEmbeddings(id: string) {
    setSelectionnesEmbeddings((s) => {
      const copie = new Set(s)
      if (copie.has(id)) copie.delete(id)
      else copie.add(id)
      return copie
    })
  }

  function basculerModeleClassification(id: string) {
    setSelectionnesClassification((s) => {
      const copie = new Set(s)
      if (copie.has(id)) copie.delete(id)
      else copie.add(id)
      return copie
    })
  }

  function basculerModeleVision(id: string) {
    setSelectionnesVision((s) => {
      const copie = new Set(s)
      if (copie.has(id)) copie.delete(id)
      else copie.add(id)
      return copie
    })
  }

  async function lancer() {
    setEnCours(true)
    setErreur(null)
    setResultat({ prompt, resultats: [] })
    try {
      const { job_id } = await demarrerComparaisonModeles(prompt, Array.from(selectionnes))
      suivreComparaisonModeles(
        job_id,
        (r) => setResultat((prev: any) => ({ ...prev, resultats: [...(prev?.resultats ?? []), r] })),
        (fin) => {
          setEnCours(false)
          if (fin.status === 'erreur') setErreur(fin.erreur || 'Erreur pendant la comparaison')
        },
        // Le flux SSE rejoue tout depuis le début à chaque reconnexion (utile si l'onglet a été mis
        // en arrière-plan sur mobile) — repartir de zéro ici évite des résultats dupliqués.
        () => setResultat((prev: any) => ({ ...prev, resultats: [] })),
      )
    } catch (e: any) {
      setErreur(e.message)
      setEnCours(false)
    }
  }

  async function lancerEmbeddings() {
    setEnCoursEmbeddings(true)
    setErreurEmbeddings(null)
    setResultatEmbeddings(null)
    try {
      const r = await comparerEmbeddings(phraseA, phraseB, Array.from(selectionnesEmbeddings))
      setResultatEmbeddings(r)
    } catch (e: any) {
      setErreurEmbeddings(e.message)
    } finally {
      setEnCoursEmbeddings(false)
    }
  }

  async function lancerClassification() {
    setEnCoursClassification(true)
    setErreurClassification(null)
    setResultatClassification(null)
    try {
      const r = await comparerClassification(messageClassification, Array.from(selectionnesClassification))
      setResultatClassification(r)
    } catch (e: any) {
      setErreurClassification(e.message)
    } finally {
      setEnCoursClassification(false)
    }
  }

  async function lancerVision() {
    setEnCoursVision(true)
    setErreurVision(null)
    setResultatVision(null)
    try {
      const r = await comparerVision(Array.from(selectionnesVision))
      setResultatVision(r)
    } catch (e: any) {
      setErreurVision(e.message)
    } finally {
      setEnCoursVision(false)
    }
  }

  return (
    <div className="page page-simulateur">
      <h1>⚖️ Simulateur coût / latence des modèles</h1>
      <p className="page-intro">
        Le Simulateur soumet une même entrée, successivement, à l'ensemble des modèles sélectionnés
        au sein d'une même famille — un prompt en texte libre pour les LLM génératifs, deux phrases
        à comparer pour les embeddings, un message à classer pour les algorithmes de classification
        classique (entraînés en direct sous vos yeux), ou une image d'exemple fournie par l'outil
        pour les modèles de vision. La{' '}
        <strong>durée affichée constitue une mesure réelle</strong>, effectuée en direct sur cette
        machine, quand l'énergie relative (LLM uniquement) demeure une{' '}
        <strong>approximation illustrative</strong>, proportionnelle au nombre de paramètres de
        chaque modèle plutôt qu'une consommation véritablement observée.
      </p>

      <div className="simulateur-modeles-annonce">
        <p className="texte-muted">1. Choisissez la famille de modèle à comparer :</p>
        <div className="exemples-chips">
          {FAMILLES.map((f) => (
            <button
              key={f.id}
              className={f.id === familleActive ? 'chip actif' : 'chip'}
              disabled={!f.disponible}
              title={f.note}
              onClick={() => f.disponible && setFamilleActive(f.id)}
            >
              {f.label} {!f.disponible && '(bientôt)'}
            </button>
          ))}
        </div>
        <p className="texte-muted simulateur-famille-note">
          {FAMILLES.find((f) => f.id === familleActive)?.note}
        </p>

        {familleActive === 'llm_generatif' && modeles.length > 0 && (
          <>
            <p className="texte-muted">
              2. Choisissez les modèles de cette famille à comparer sur le même prompt (
              {selectionnes.size}/{modeles.length} sélectionnés) :
            </p>
            <div className="exemples-chips">
              <button className="chip" onClick={() => setSelectionnes(new Set(modeles.map((m) => m.id)))}>
                Tout sélectionner
              </button>
              <button className="chip" onClick={() => setSelectionnes(new Set())}>
                Tout désélectionner
              </button>
            </div>
            <div className="simulateur-modeles-liste">
              {modeles.map((m) => (
                <label key={m.id} className="simulateur-modele-case">
                  <input
                    type="checkbox"
                    checked={selectionnes.has(m.id)}
                    onChange={() => basculerModele(m.id)}
                  />
                  {m.nom} <span className="texte-muted">({m.parametres_milliards} Md)</span>
                </label>
              ))}
            </div>
          </>
        )}

        {familleActive === 'embeddings' && modelesEmbeddings.length > 0 && (
          <>
            <p className="texte-muted">
              2. Choisissez les modèles de cette famille à comparer sur les 2 mêmes phrases (
              {selectionnesEmbeddings.size}/{modelesEmbeddings.length} sélectionnés) :
            </p>
            <div className="exemples-chips">
              <button
                className="chip"
                onClick={() => setSelectionnesEmbeddings(new Set(modelesEmbeddings.map((m) => m.id)))}
              >
                Tout sélectionner
              </button>
              <button className="chip" onClick={() => setSelectionnesEmbeddings(new Set())}>
                Tout désélectionner
              </button>
            </div>
            <div className="simulateur-modeles-liste">
              {modelesEmbeddings.map((m) => (
                <label key={m.id} className="simulateur-modele-case">
                  <input
                    type="checkbox"
                    checked={selectionnesEmbeddings.has(m.id)}
                    onChange={() => basculerModeleEmbeddings(m.id)}
                  />
                  {m.nom} <span className="texte-muted">({m.parametres_millions} M)</span>
                </label>
              ))}
            </div>
          </>
        )}

        {familleActive === 'classification_classique' && modelesClassification.length > 0 && (
          <>
            <p className="texte-muted">
              2. Choisissez les algorithmes à entraîner sur le même jeu de données (
              {selectionnesClassification.size}/{modelesClassification.length} sélectionnés) :
            </p>
            <div className="exemples-chips">
              <button
                className="chip"
                onClick={() => setSelectionnesClassification(new Set(modelesClassification.map((m) => m.id)))}
              >
                Tout sélectionner
              </button>
              <button className="chip" onClick={() => setSelectionnesClassification(new Set())}>
                Tout désélectionner
              </button>
            </div>
            <div className="simulateur-modeles-liste">
              {modelesClassification.map((m) => (
                <label key={m.id} className="simulateur-modele-case">
                  <input
                    type="checkbox"
                    checked={selectionnesClassification.has(m.id)}
                    onChange={() => basculerModeleClassification(m.id)}
                  />
                  {m.nom}
                </label>
              ))}
            </div>
          </>
        )}

        {familleActive === 'vision' && modelesVision.length > 0 && (
          <>
            <p className="texte-muted">
              2. Choisissez les modèles de détection à comparer sur la même image (
              {selectionnesVision.size}/{modelesVision.length} sélectionnés) :
            </p>
            <div className="exemples-chips">
              <button className="chip" onClick={() => setSelectionnesVision(new Set(modelesVision.map((m) => m.id)))}>
                Tout sélectionner
              </button>
              <button className="chip" onClick={() => setSelectionnesVision(new Set())}>
                Tout désélectionner
              </button>
            </div>
            <div className="simulateur-modeles-liste">
              {modelesVision.map((m) => (
                <label key={m.id} className="simulateur-modele-case">
                  <input
                    type="checkbox"
                    checked={selectionnesVision.has(m.id)}
                    onChange={() => basculerModeleVision(m.id)}
                  />
                  {m.nom} <span className="texte-muted">({m.parametres_millions} M)</span>
                </label>
              ))}
            </div>
          </>
        )}
      </div>

      {familleActive === 'llm_generatif' && (
        <>
          <p className="texte-muted">
            3. Choisissez un prompt parmi {TOUS_LES_EXEMPLES.length} exemples classés par type de
            tâche (ce ne sont pas des familles de modèle différentes, juste des catégories de tâche
            à tester) :
          </p>
          <div className="exemples-categories">
            {CATEGORIES.map((c) => (
              <button
                key={c.categorie}
                className={c.categorie === categorieActive ? 'chip actif' : 'chip'}
                onClick={() => setCategorieActive(c.categorie)}
              >
                {c.categorie}
              </button>
            ))}
          </div>
          <div className="exemples-chips">
            {CATEGORIES.find((c) => c.categorie === categorieActive)?.exemples.map((ex, i) => (
              <button key={i} className={ex === prompt ? 'chip actif' : 'chip'} onClick={() => setPrompt(ex)}>
                {ex.length > 50 ? `${ex.slice(0, 50)}…` : ex}
              </button>
            ))}
          </div>

          <textarea
            className="simulateur-prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            maxLength={300}
          />

          <button onClick={lancer} disabled={enCours || !prompt.trim() || selectionnes.size === 0}>
            {enCours
              ? `${resultat?.resultats?.length ?? 0}/${selectionnes.size} modèle${selectionnes.size > 1 ? 's' : ''} comparé${(resultat?.resultats?.length ?? 0) > 1 ? 's' : ''}…`
              : selectionnes.size === 0
                ? 'Sélectionnez au moins un modèle'
                : 'Lancer la comparaison'}
          </button>

          {erreur && <p className="erreur">{erreur}</p>}

          {resultat && (
            <>
              <div className="simulateur-graphique">
                <h4>Durée de réponse mesurée (secondes)</h4>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={resultat.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis label={{ value: 'secondes', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey={(d: any) => d.performance?.duree_secondes} name="Durée (s)" fill="#4f7cff" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="simulateur-graphique">
                <h4>Estimation d'énergie relative (illustrative, % du plus gros modèle)</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultat.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis label={{ value: '%', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey={(d: any) => d.performance?.estimation_energie_relative_pourcent}
                      name="Énergie estimée (%)"
                      fill="#fb923c"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="explication-bloc">
                <h4>Fiche comparative détaillée (~46 critères, classés par catégorie)</h4>
                <p className="texte-muted">
                  Chaque modèle est noté selon 5 angles : performance mesurée, fiche technique réelle
                  (Ollama), analyse automatique de la réponse, avis d'un modèle arbitre, et une
                  synthèse pour vous aider à choisir. Dépliez une catégorie pour le détail.
                </p>
                {resultat.resultats.map((r: any) => (
                  <div key={r.id} className="simulateur-fiche-modele">
                    <div className="simulateur-fiche-entete">
                      <h5>{r.nom} — ~{r.parametres_milliards} milliards de paramètres</h5>
                      {r.synthese && (
                        <div className="simulateur-fiche-badges">
                          <span className="chip">{r.synthese.niveau_materiel_requis}</span>
                          {r.synthese.cas_usage_recommandes?.map((c: string) => (
                            <span key={c} className="chip">{c}</span>
                          ))}
                        </div>
                      )}
                    </div>

                    {r.synthese && <p className="simulateur-verdict">💡 {r.synthese.verdict_global}</p>}

                    {r.performance && (
                      <details className="simulateur-categorie">
                        <summary>Performance mesurée</summary>
                        <ul className="simulateur-criteres">
                          <li>Durée de réponse : {r.performance.duree_secondes}s</li>
                          <li>Débit : {r.performance.debit_caracteres_par_seconde} caractères/s</li>
                          <li>Longueur de la réponse : {r.performance.longueur_reponse_caracteres} caractères</li>
                          <li>Nombre de mots : {r.performance.nb_mots}</li>
                          <li>Nombre de phrases : {r.performance.nb_phrases}</li>
                          <li>Longueur moyenne de phrase : {r.performance.longueur_moyenne_phrase_mots} mots</li>
                          <li>Énergie relative estimée : {r.performance.estimation_energie_relative_pourcent}%</li>
                        </ul>
                      </details>
                    )}

                    {r.fiche_technique && (
                      <details className="simulateur-categorie">
                        <summary>Fiche technique du modèle</summary>
                        <ul className="simulateur-criteres">
                          <li>Éditeur : {r.fiche_technique.editeur}</li>
                          <li>Licence : {r.fiche_technique.licence}</li>
                          <li>Paramètres réels : {r.fiche_technique.parametres_reels_milliards ?? '—'} milliards</li>
                          <li>Quantization utilisée ici : {r.fiche_technique.quantization ?? '—'}</li>
                          <li>Format de fichier : {r.fiche_technique.format_fichier ?? '—'}</li>
                          <li>Nombre de couches : {r.fiche_technique.nb_couches ?? '—'}</li>
                          <li>Fenêtre de contexte : {r.fiche_technique.fenetre_contexte_tokens ?? '—'} tokens</li>
                          <li>Poids du fichier : {r.fiche_technique.poids_fichier_go ?? '—'} Go</li>
                          <li>RAM estimée nécessaire : {r.fiche_technique.estimation_ram_go ?? '—'} Go</li>
                          <li>Année de sortie : {r.fiche_technique.annee_sortie ?? '—'}</li>
                          <li>Spécialisation : {r.fiche_technique.specialisation}</li>
                          <li>Support multilingue : {r.fiche_technique.multilingue}</li>
                          <li>Function calling / outils : {r.fiche_technique.function_calling ? 'Oui' : 'Non'}</li>
                        </ul>
                      </details>
                    )}

                    {r.analyse_reponse && (
                      <details className="simulateur-categorie">
                        <summary>Analyse automatique de la réponse</summary>
                        <ul className="simulateur-criteres">
                          <li>Diversité lexicale : {r.analyse_reponse.diversite_lexicale_pourcent}%</li>
                          <li>Réponse bien en français : {r.analyse_reponse.langue_correcte ? 'Oui' : 'À vérifier'}</li>
                          <li>Contient des données chiffrées : {r.analyse_reponse.contient_donnees_chiffrees ? 'Oui' : 'Non'}</li>
                          <li>Contient une liste structurée : {r.analyse_reponse.contient_liste_structuree ? 'Oui' : 'Non'}</li>
                          <li>Marqueurs d'incertitude détectés : {r.analyse_reponse.nb_marqueurs_incertitude}</li>
                          <li>Réponse semble tronquée : {r.analyse_reponse.reponse_semble_tronquee ? 'Oui' : 'Non'}</li>
                          <li>
                            Respect de la longueur demandée :{' '}
                            {r.analyse_reponse.respect_longueur_demandee == null
                              ? 'Non applicable'
                              : r.analyse_reponse.respect_longueur_demandee
                                ? 'Oui'
                                : 'Non'}
                          </li>
                          <li>
                            Cohérence lexicale avec la question :{' '}
                            {r.analyse_reponse.coherence_avec_prompt_pourcent ?? '—'}%
                          </li>
                          <li>Mentionne être une IA : {r.analyse_reponse.presence_disclaimer_ia ? 'Oui' : 'Non'}</li>
                        </ul>
                      </details>
                    )}

                    {r.evaluation_qualitative ? (
                      <details className="simulateur-categorie">
                        <summary>Évaluation qualitative (avis d'un modèle arbitre)</summary>
                        <ul className="simulateur-criteres">
                          <li>Pertinence : {r.evaluation_qualitative.score_pertinence}/5</li>
                          <li>Clarté : {r.evaluation_qualitative.score_clarte}/5</li>
                          <li>Concision : {r.evaluation_qualitative.score_concision}/5</li>
                          <li>Exactitude perçue : {r.evaluation_qualitative.score_exactitude_percue}/5</li>
                          <li>Ton professionnel : {r.evaluation_qualitative.score_ton_professionnel}/5</li>
                          <li>Recommandé par le juge : {r.evaluation_qualitative.recommande_par_le_juge ? 'Oui' : 'Non'}</li>
                          <li>Justification : {r.evaluation_qualitative.justification_juge}</li>
                        </ul>
                      </details>
                    ) : (
                      <p className="texte-muted">Évaluation qualitative indisponible pour ce modèle.</p>
                    )}

                    <p className="traduction-cible">{r.reponse}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}

      {familleActive === 'embeddings' && (
        <>
          <p className="texte-muted">
            3. Choisissez 2 phrases à comparer — un exemple type, ou les vôtres :
          </p>
          <div className="exemples-chips">
            {PAIRES_EXEMPLES.map((p, i) => (
              <button
                key={i}
                className={p.phraseA === phraseA && p.phraseB === phraseB ? 'chip actif' : 'chip'}
                onClick={() => {
                  setPhraseA(p.phraseA)
                  setPhraseB(p.phraseB)
                }}
              >
                {p.categorie}
              </button>
            ))}
          </div>

          <label className="texte-muted" htmlFor="phrase-a">
            Phrase A
          </label>
          <textarea
            id="phrase-a"
            className="simulateur-prompt"
            value={phraseA}
            onChange={(e) => setPhraseA(e.target.value)}
            rows={2}
            maxLength={300}
          />
          <label className="texte-muted" htmlFor="phrase-b">
            Phrase B
          </label>
          <textarea
            id="phrase-b"
            className="simulateur-prompt"
            value={phraseB}
            onChange={(e) => setPhraseB(e.target.value)}
            rows={2}
            maxLength={300}
          />

          <button
            onClick={lancerEmbeddings}
            disabled={enCoursEmbeddings || !phraseA.trim() || !phraseB.trim() || selectionnesEmbeddings.size === 0}
          >
            {enCoursEmbeddings
              ? `${selectionnesEmbeddings.size} modèle${selectionnesEmbeddings.size > 1 ? 's' : ''} à comparer…`
              : selectionnesEmbeddings.size === 0
                ? 'Sélectionnez au moins un modèle'
                : 'Lancer la comparaison'}
          </button>

          {erreurEmbeddings && <p className="erreur">{erreurEmbeddings}</p>}

          {resultatEmbeddings && (
            <>
              <div className="simulateur-graphique">
                <h4>Durée de calcul mesurée (secondes, 2 phrases confondues)</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultatEmbeddings.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis label={{ value: 'secondes', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey="duree_secondes" name="Durée (s)" fill="#4f7cff" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="simulateur-graphique">
                <h4>Score de similarité cosinus entre les 2 phrases (0 = aucun rapport, 1 = identique)</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultatEmbeddings.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Bar dataKey="similarite_cosinus" name="Similarité cosinus" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="explication-bloc">
                <h4>Détail par modèle</h4>
                {resultatEmbeddings.resultats.map((r: any) => (
                  <div key={r.id} className="simulateur-detail">
                    <h5>{r.nom} — ~{r.parametres_millions} millions de paramètres</h5>
                    <p className="texte-muted">
                      {r.duree_secondes}s · vecteur de {r.dimension_vecteur} dimensions · similarité
                      cosinus : {r.similarite_cosinus}
                    </p>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}

      {familleActive === 'classification_classique' && (
        <>
          <p className="texte-muted">
            3. Choisissez un message à classer (spam ou légitime) — un exemple type, ou le vôtre :
          </p>
          <div className="exemples-chips">
            {EXEMPLES_CLASSIFICATION.map((ex, i) => (
              <button
                key={i}
                className={ex === messageClassification ? 'chip actif' : 'chip'}
                onClick={() => setMessageClassification(ex)}
              >
                {ex.length > 50 ? `${ex.slice(0, 50)}…` : ex}
              </button>
            ))}
          </div>

          <textarea
            className="simulateur-prompt"
            value={messageClassification}
            onChange={(e) => setMessageClassification(e.target.value)}
            rows={3}
            maxLength={300}
          />

          <button
            onClick={lancerClassification}
            disabled={
              enCoursClassification || !messageClassification.trim() || selectionnesClassification.size === 0
            }
          >
            {enCoursClassification
              ? `Entraînement de ${selectionnesClassification.size} algorithme${selectionnesClassification.size > 1 ? 's' : ''} en cours…`
              : selectionnesClassification.size === 0
                ? 'Sélectionnez au moins un algorithme'
                : 'Lancer la comparaison'}
          </button>

          {erreurClassification && <p className="erreur">{erreurClassification}</p>}

          {resultatClassification && (
            <>
              <div className="simulateur-graphique">
                <h4>Durée d'entraînement mesurée (secondes, sur ~34 exemples)</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultatClassification.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis label={{ value: 'secondes', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey="duree_secondes" name="Durée (s)" fill="#4f7cff" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="simulateur-graphique">
                <h4>Précision en validation croisée (5 blocs, %)</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultatClassification.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="precision_validation_croisee_pourcent" name="Précision (%)" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="explication-bloc">
                <h4>Détail par algorithme</h4>
                {resultatClassification.resultats.map((r: any) => (
                  <div key={r.id} className="simulateur-detail">
                    <h5>{r.nom}</h5>
                    <p className="texte-muted">
                      {r.duree_secondes}s d'entraînement · précision validation croisée :{' '}
                      {r.precision_validation_croisee_pourcent}% · prédiction sur ce message :{' '}
                      <strong>{r.prediction}</strong> ({Math.round(r.confiance * 100)}% de confiance)
                    </p>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}

      {familleActive === 'vision' && (
        <>
          <p className="texte-muted">
            3. Aucune saisie nécessaire : l'outil fournit lui-même une image d'exemple, identique
            pour chaque modèle comparé.
          </p>

          <button onClick={lancerVision} disabled={enCoursVision || selectionnesVision.size === 0}>
            {enCoursVision
              ? `${selectionnesVision.size} modèle${selectionnesVision.size > 1 ? 's' : ''} à comparer…`
              : selectionnesVision.size === 0
                ? 'Sélectionnez au moins un modèle'
                : 'Lancer la comparaison'}
          </button>

          {erreurVision && <p className="erreur">{erreurVision}</p>}

          {resultatVision && (
            <>
              {resultatVision.image_note && <p className="texte-muted">{resultatVision.image_note}</p>}

              <div className="simulateur-graphique">
                <h4>Durée d'analyse mesurée (secondes)</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultatVision.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <YAxis label={{ value: 'secondes', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey="duree_secondes" name="Durée (s)" fill="#4f7cff" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="simulateur-graphique">
                <h4>Nombre d'objets détectés</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resultatVision.resultats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nom" />
                    <Tooltip />
                    <Bar dataKey="nb_objets" name="Objets détectés" fill="#fb923c" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="explication-bloc">
                <h4>Détail par modèle</h4>
                {resultatVision.resultats.map((r: any) => (
                  <div key={r.id} className="simulateur-detail">
                    <h5>{r.nom} — ~{r.parametres_millions} millions de paramètres</h5>
                    <p className="texte-muted">
                      {r.duree_secondes}s · {r.nb_objets} objet{r.nb_objets > 1 ? 's' : ''} détecté
                      {r.nb_objets > 1 ? 's' : ''} :{' '}
                      {r.objets_detectes.map((o: any) => `${o.etiquette} (${Math.round(o.confiance * 100)}%)`).join(', ')}
                    </p>
                    <img
                      src={`data:image/jpeg;base64,${r.image_annotee_base64}`}
                      alt={`Détection annotée par ${r.nom}`}
                      className="simulateur-image-vision"
                    />
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
