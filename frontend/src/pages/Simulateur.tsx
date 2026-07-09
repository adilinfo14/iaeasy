import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { comparerModeles, listerModelesSimulateur } from '../api/client'

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

export default function Simulateur() {
  const [categorieActive, setCategorieActive] = useState(CATEGORIES[0].categorie)
  const [prompt, setPrompt] = useState(TOUS_LES_EXEMPLES[0])
  const [enCours, setEnCours] = useState(false)
  const [resultat, setResultat] = useState<any>(null)
  const [erreur, setErreur] = useState<string | null>(null)
  const [modeles, setModeles] = useState<any[]>([])
  const [selectionnes, setSelectionnes] = useState<Set<string>>(new Set())

  useEffect(() => {
    listerModelesSimulateur().then((liste) => {
      setModeles(liste)
      setSelectionnes(new Set(liste.map((m: any) => m.id)))
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

  async function lancer() {
    setEnCours(true)
    setErreur(null)
    setResultat(null)
    try {
      const r = await comparerModeles(prompt, Array.from(selectionnes))
      setResultat(r)
    } catch (e: any) {
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="page page-simulateur">
      <h1>⚖️ Simulateur coût / latence des modèles</h1>
      <p className="page-intro">
        Le Simulateur soumet un même prompt, successivement, à l'ensemble des modèles génératifs
        sélectionnés — les modèles d'embeddings, de vision ou de classification classique échappant
        par nature à cette comparaison, puisqu'ils ne répondent pas à un texte libre. La{' '}
        <strong>durée affichée constitue une mesure réelle</strong>, effectuée en direct sur cette
        machine, quand l'énergie demeure une <strong>approximation illustrative</strong>,
        proportionnelle au nombre de paramètres de chaque modèle plutôt qu'une consommation
        véritablement observée.
      </p>

      {modeles.length > 0 && (
        <div className="simulateur-modeles-annonce">
          <p className="texte-muted">
            Famille de modèle : <strong>LLM génératif</strong> — choisissez lesquels comparer sur le même
            prompt ({selectionnes.size}/{modeles.length} sélectionnés) :
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
        </div>
      )}

      <p className="texte-muted">
        {TOUS_LES_EXEMPLES.length} exemples prêts à l'emploi, classés par type de tâche (ce ne sont pas
        des familles de modèle différentes — tous les modèles ci-dessus appartiennent à la même famille) :
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
          ? `${selectionnes.size} modèle${selectionnes.size > 1 ? 's' : ''} à comparer, cela peut prendre quelques minutes…`
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
                <Bar dataKey="duree_secondes" name="Durée (s)" fill="#4f7cff" />
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
                <Bar dataKey="estimation_energie_relative_pourcent" name="Énergie estimée (%)" fill="#fb923c" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="explication-bloc">
            <h4>Détail par modèle</h4>
            {resultat.resultats.map((r: any) => (
              <div key={r.id} className="simulateur-detail">
                <h5>{r.nom} — ~{r.parametres_milliards} milliards de paramètres</h5>
                <p className="texte-muted">
                  {r.duree_secondes}s pour {r.longueur_reponse} caractères de réponse
                </p>
                <p className="traduction-cible">{r.reponse}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
