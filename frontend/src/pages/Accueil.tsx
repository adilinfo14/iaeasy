import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  lireBadges,
  lireProgression,
  lireStatsAvis,
  lireVisiteurs,
  listerBriques,
  listerMetiers,
  listerModeles,
  StatsAvis,
} from '../api/client'
import SketchIcone, { SketchCle } from '../components/SketchIcone'

const FAMILLES: { cle: SketchCle; titre: string; pitch: string }[] = [
  { cle: 'llm', titre: 'Génératif (LLM)', pitch: 'Prédit le mot suivant le plus probable — texte, code, résumé.' },
  { cle: 'vision', titre: 'Vision', pitch: 'Reconnaît des formes ou des objets dans une image.' },
  { cle: 'prevision', titre: 'Prévision', pitch: 'Extrapole une tendance à partir de mesures passées.' },
  { cle: 'anomalie', titre: "Détection d'anomalie", pitch: "Repère ce qui s'écarte du comportement habituel." },
]

// Associe chaque intitulé réel de secteur (backend /metiers) à une icône — tenu à jour
// manuellement plutôt que dérivé automatiquement, pour garder un contrôle éditorial sur l'icône
// choisie par secteur.
const SECTEUR_ICONE: Record<string, SketchCle> = {
  'BTP / Artisanat': 'btp',
  Industrie: 'industrie',
  'Commerce / Distribution': 'commerce',
  'Agriculture / Agroalimentaire': 'agriculture',
  'Services professionnels': 'services_pro',
  'Santé / Social': 'sante',
  'Éducation / Formation': 'education',
  Immobilier: 'immobilier',
  'Transport / Logistique': 'transport',
  'Secteur public / Collectivité': 'secteur_public',
  'Associations / ONG': 'associations',
}

const MODULES = [
  {
    to: '/catalogue',
    icone: '🗂️',
    titre: 'Catalogue',
    groupe: 'pratiquer',
    duree: '~20 min',
    // Complété dynamiquement (nombre de modèles/familles réel) une fois le catalogue chargé.
    pitch: "Des dizaines de modèles, des familles d'IA différentes — pas seulement des chatbots.",
  },
  {
    to: '/parcours',
    icone: '🧭',
    titre: 'Parcours',
    groupe: 'pratiquer',
    duree: '~30 min',
    pitch: 'Construis ton assistant brique par brique, avec une vraie mise en situation.',
    recommande: true,
  },
  {
    to: '/entrainement',
    icone: '📉',
    titre: 'Entraînement',
    groupe: 'pratiquer',
    duree: '~10 min',
    pitch: 'Regarde une vraie courbe de loss descendre, sur 3 cas d\'usage concrets.',
  },
  {
    to: '/constructeur',
    icone: '🏗️',
    titre: 'Constructeur',
    groupe: 'pratiquer',
    duree: '~20 min',
    pitch: "Mode architecte : assemble un vrai RAG, un agent, un pipeline multi-agent.",
  },
  {
    to: '/simulateur',
    icone: '⚖️',
    titre: 'Simulateur',
    groupe: 'pratiquer',
    duree: '~10 min',
    pitch: 'Comparez en direct la vitesse et le coût réel de plusieurs modèles.',
  },
  {
    to: '/brief-ia',
    icone: '🗞️',
    titre: 'Brief IA',
    groupe: 'pratiquer',
    duree: '~10 min',
    pitch: 'Un vrai système agentique (LangGraph) qui croise plusieurs sources avant de te demander ta validation.',
  },
  {
    to: '/strategie-test',
    icone: '🧪',
    titre: 'Stratégie de tests',
    groupe: 'ressources',
    duree: '~15 min',
    pitch: "Comment vérifier sérieusement chaque famille de modèle — cahiers de test à réutiliser.",
  },
  {
    to: '/securite',
    icone: '🛡️',
    titre: 'Sécurité',
    groupe: 'ressources',
    duree: '~10 min',
    pitch: "10 risques concrets d'un agent IA (OWASP) et les bonnes pratiques pour s'en protéger.",
  },
  {
    to: '/glossaire',
    icone: '📖',
    titre: 'Glossaire',
    groupe: 'ressources',
    duree: '~5 min',
    pitch: "Le jargon de l'IA expliqué simplement, un terme à la fois.",
  },
  {
    to: '/metiers',
    icone: '🧭',
    titre: 'Mon métier',
    groupe: 'ressources',
    duree: '~5 min',
    pitch: "L'IA dans votre métier : des cas d'usage concrets, pas des promesses abstraites.",
  },
  {
    to: '/videos',
    icone: '🎬',
    titre: 'Vidéos',
    groupe: 'ressources',
    duree: '~15 min',
    pitch: "Des schémas de conférences IA expliqués en français simple.",
  },
  {
    to: '/theatre',
    icone: '🎭',
    titre: 'Théâtre',
    groupe: 'ressources',
    duree: '~10 min',
    pitch: "Deux personnages générés et animés par une IA se racontent des histoires vraies.",
  },
  {
    to: '/voyage',
    icone: '🧭',
    titre: "Voyage de l'IA",
    groupe: 'ressources',
    duree: '~15 min',
    pitch: 'Un récit continu qui traverse toutes les familles de modèles du site, schémas à l\'appui.',
  },
  {
    to: '/quiz-eclair',
    icone: '⚡',
    titre: 'Quiz éclair',
    groupe: 'ressources',
    duree: '~2 min',
    pitch: 'Cinq questions piochées au hasard parmi les briques déjà débloquées, pour réviser vite.',
  },
  {
    to: '/mon-parcours',
    icone: '🕓',
    titre: 'Mon parcours',
    groupe: 'ressources',
    duree: '~1 min',
    pitch: "L'historique personnel de tout ce que vous avez déjà essayé sur cet appareil.",
  },
  {
    to: '/avis',
    icone: '⭐',
    titre: 'Avis',
    groupe: 'avis',
    duree: '~1 min',
    pitch: 'Notez le site en 2 secondes et lisez les avis des autres visiteurs.',
  },
]

export default function Accueil() {
  const [debloquees, setDebloquees] = useState(0)
  const [total, setTotal] = useState(5)
  const [visiteurs, setVisiteurs] = useState<number | null>(null)
  const [badges, setBadges] = useState(0)
  const [statsAvis, setStatsAvis] = useState<StatsAvis | null>(null)
  const [catalogue, setCatalogue] = useState<{ nbModeles: number; nbFamilles: number } | null>(null)
  const [metiers, setMetiers] = useState<any[]>([])
  const [secteurOuvert, setSecteurOuvert] = useState<string | null>(null)

  useEffect(() => {
    listerBriques().then((b) => setTotal(b.length))
    lireProgression().then((p) => setDebloquees(p.debloquees.length))
    lireVisiteurs().then((v) => setVisiteurs(v.total_visiteurs_uniques))
    lireBadges().then((b) => setBadges(b.badges.length))
    lireStatsAvis().then(setStatsAvis)
    listerModeles().then((modeles) =>
      setCatalogue({ nbModeles: modeles.length, nbFamilles: new Set(modeles.map((m: any) => m.famille)).size }),
    )
    listerMetiers().then(setMetiers)
  }, [])

  // Regroupe les fiches métier réelles par secteur (une même secteur peut réunir plusieurs
  // métiers) plutôt que d'inventer un texte de teaser par secteur — les exemples affichés sont
  // les vrais titres de cas d'usage déjà démontrables ailleurs sur le site.
  const secteurs = useMemo(() => {
    const groupes = new Map<string, { nbCas: number; exemples: string[] }>()
    for (const m of metiers) {
      const g = groupes.get(m.secteur) ?? { nbCas: 0, exemples: [] }
      g.nbCas += m.cas_usage.length
      for (const c of m.cas_usage) {
        if (g.exemples.length < 2) g.exemples.push(c.titre)
      }
      groupes.set(m.secteur, g)
    }
    return Array.from(groupes.entries()).map(([secteur, infos]) => ({ secteur, ...infos }))
  }, [metiers])

  // Fiches complètes (description du métier + cas d'usage détaillés) groupées par secteur, pour
  // le récit déplié — distinct de `secteurs` ci-dessus qui ne garde que les titres courts pour
  // la ligne repliée.
  const fichesParSecteur = useMemo(() => {
    const groupes = new Map<string, any[]>()
    for (const m of metiers) {
      if (!groupes.has(m.secteur)) groupes.set(m.secteur, [])
      groupes.get(m.secteur)!.push(m)
    }
    return groupes
  }, [metiers])

  return (
    <div className="page page-accueil">
      <div className="accueil-hero">
        <div className="accueil-hero-grain" aria-hidden="true">
          {[-18, 8, -8, 14].map((angle, i) => (
            <svg key={i} viewBox="0 0 60 90" style={{ transform: `rotate(${angle}deg)` }}>
              <ellipse cx="30" cy="45" rx="26" ry="43" fill="#8a5a34" />
              <path
                d="M30 8 C16 22,16 40,30 45 C44 50,44 68,30 82"
                fill="none"
                stroke="#3c2415"
                strokeWidth="6"
                strokeLinecap="round"
              />
            </svg>
          ))}
        </div>
        <p className="accueil-eyebrow">☕ Plateforme pédagogique IA souveraine</p>
        <h1 className="accueil-titre">Apprendre l'IA en la construisant</h1>
        <p className="page-intro accueil-intro">
          Née de la conviction qu'on ne comprend véritablement l'intelligence artificielle qu'en la
          manipulant soi-même, iaeasy s'attache à porter une pédagogie à la fois exigeante et
          accessible, ouverte à toute personne curieuse — étudiante, artisan, salariée, ou
          simplement désireuse de savoir ce qui se cache derrière un chatbot. La plateforme
          conjugue rigueur technique et souveraineté numérique : hébergée sur un serveur personnel
          et fondée exclusivement sur des modèles ouverts, elle ne transmet jamais la moindre
          donnée à un service tiers.
        </p>
      </div>

      <section className="accueil-conviction">
        <SketchIcone cle="balance" className="conviction-icone" />
        <div className="conviction-corps">
          <p className="accueil-eyebrow">🧭 Notre conviction</p>
          <h2 className="section-titre">L'IA doit muscler votre jugement, pas le remplacer</h2>
          <p>
            Une étude du MIT Media Lab menée sur quatre mois a mesuré une activité cérébrale
            affaiblie — mémoire, créativité, esprit critique — chez les personnes qui rédigeaient
            avec l'aide de ChatGPT, comparées à celles qui écrivaient seules : les chercheurs
            parlent de « dette cognitive ». Une étude de Microsoft Research présentée à la
            conférence CHI 2025, menée auprès de 319 professionnels, établit un lien direct entre
            la confiance accordée à l'IA et la baisse d'effort de pensée critique.
          </p>
          <p>
            Le facteur déterminant n'est pas l'IA elle-même, mais l'usage qu'on en fait : une IA
            qui répond à votre place vous décharge de l'effort qui, justement, construit la
            compétence ; une IA que vous manipulez, dont vous observez le fonctionnement et les
            limites, vous oblige à rester actif. C'est le parti pris de ce site — jamais un
            chatbot qui pense à votre place, toujours un outil que vous actionnez vous-même —
            pour garder la maîtrise de la connaissance, et faire de l'IA un levier de votre
            réflexion et de vos décisions, pas un substitut.
          </p>
          <p className="conviction-sources">
            Sources :{' '}
            <a href="https://www.media.mit.edu/publications/your-brain-on-chatgpt/" target="_blank" rel="noreferrer">
              MIT Media Lab, « Your Brain on ChatGPT » (2025)
            </a>{' '}
            ·{' '}
            <a
              href="https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/"
              target="_blank"
              rel="noreferrer"
            >
              Lee et al., Microsoft Research, CHI 2025
            </a>
          </p>
        </div>
      </section>

      <section className="accueil-pedagogie">
        <p className="accueil-eyebrow">🧠 Comprendre avant de pratiquer</p>
        <h2 className="section-titre">Qu'est-ce que l'intelligence artificielle, concrètement ?</h2>
        <div className="pedagogie-definition">
          <SketchIcone cle="cerveau" className="pedagogie-icone-principale" />
          <p>
            L'intelligence artificielle n'est pas un objet unique : c'est un ensemble de familles de
            modèles mathématiques, entraînés à reconnaître des régularités dans des données (texte,
            image, mesures) pour ensuite les reproduire, les classer ou les prédire sur de nouvelles
            données. Un modèle de langage prédit le mot suivant le plus probable ; un modèle de
            vision reconnaît des formes dans une image ; un modèle de prévision extrapole une
            tendance à partir de mesures passées. Aucun de ces modèles ne « comprend » au sens
            humain — chacun excelle sur la tâche pour laquelle il a été entraîné, et échoue
            silencieusement en dehors. C'est cette diversité de familles, pas une IA générale
            unique, que ce site donne à manipuler concrètement.
          </p>
        </div>
        <div className="familles-legende">
          {FAMILLES.map((f) => (
            <div key={f.cle} className="famille-item">
              <SketchIcone cle={f.cle} />
              <div>
                <h4>{f.titre}</h4>
                <p>{f.pitch}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="accueil-secteurs">
        <p className="accueil-eyebrow">🌍 Déjà déployée aujourd'hui</p>
        <h2 className="section-titre">Des cas d'usage réels, secteur par secteur</h2>
        <p className="page-intro accueil-intro">
          Le même schéma se répète, secteur après secteur : une tâche précise, répétitive ou
          risquée — jamais « tout » — est confiée à un modèle entraîné spécifiquement pour elle.
          {' '}{metiers.reduce((n, m) => n + m.cas_usage.length, 0) || 51} cas d'usage concrets sont
          déjà démontrables sur ce site, associations et collectivités comprises. Cliquez sur un
          secteur pour lire le mécanisme en détail.
        </p>
        <div className="secteurs-liste">
          {secteurs.map((s) => {
            const estOuvert = secteurOuvert === s.secteur
            const fiches = fichesParSecteur.get(s.secteur) ?? []
            return (
              <div key={s.secteur} className={estOuvert ? 'secteur-bloc ouvert' : 'secteur-bloc'}>
                <button
                  className="secteur-ligne"
                  onClick={() => setSecteurOuvert(estOuvert ? null : s.secteur)}
                  aria-expanded={estOuvert}
                >
                  <SketchIcone cle={SECTEUR_ICONE[s.secteur] ?? 'services_pro'} className="secteur-ligne-icone" />
                  <div className="secteur-ligne-corps">
                    <h4>{s.secteur}</h4>
                    <p>{s.exemples.join(' · ')}</p>
                  </div>
                  <span className="secteur-ligne-compteur">
                    {s.nbCas} cas d'usage {estOuvert ? '▲' : '▼'}
                  </span>
                </button>
                {estOuvert && (
                  <div className="secteur-recit">
                    {fiches.map((f) => (
                      <div key={f.id} className="secteur-recit-metier">
                        <p className="secteur-recit-chapo">
                          <strong>{f.titre}.</strong> {f.description}
                        </p>
                        {f.cas_usage.map((c: any, i: number) => (
                          <div key={i} className="metier-cas">
                            <h5>{c.titre}</h5>
                            <p>{c.description}</p>
                            <Link to={c.page} className="metier-lien">
                              {c.texte_lien}
                            </Link>
                          </div>
                        ))}
                      </div>
                    ))}
                    <Link to={`/metiers?secteur=${encodeURIComponent(s.secteur)}`} className="secteur-recit-plus">
                      Voir la fiche complète « {s.secteur} » →
                    </Link>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      <section className="accueil-pratique">
        <p className="accueil-eyebrow">🚀 Passer à la pratique</p>
        <h2 className="section-titre">Seize modules, du plus court au plus complet</h2>
        <p className="page-intro accueil-intro">
          De 1 minute (Quiz éclair) à 30 minutes (Parcours) — pas besoin de tout faire dans
          l'ordre, chaque module se suffit à lui-même.
        </p>
        <div className="stats-legende">
          <div className="stat-item">
            <span className="stat-item-chiffre">🔓 {debloquees}/{total}</span>
            <span className="stat-item-label">briques débloquées</span>
          </div>
          <div className="stat-item">
            <span className="stat-item-chiffre">🏅 {badges}/{total}</span>
            <span className="stat-item-label">quiz réussis</span>
          </div>
          {visiteurs != null && (
            <div className="stat-item">
              <span className="stat-item-chiffre">👀 {visiteurs}</span>
              <span className="stat-item-label">visiteur{visiteurs > 1 ? 's' : ''} unique{visiteurs > 1 ? 's' : ''}</span>
            </div>
          )}
          {statsAvis?.moyenne != null && (
            <div className="stat-item">
              <span className="stat-item-chiffre">⭐ {statsAvis.moyenne.toFixed(2)}/5</span>
              <span className="stat-item-label">
                <Link to="/avis">{statsAvis.total} avis →</Link>
              </span>
            </div>
          )}
        </div>
      </section>

      <div className="modules-grille">
        {MODULES.map((m) => (
          <Link
            key={m.to}
            to={m.to}
            className={`module-carte module-carte-${m.groupe}${m.recommande ? ' module-carte-recommande' : ''}`}
          >
            {m.recommande && <span className="module-badge">Commence ici</span>}
            <div className="module-carte-tete">
              <div className="module-icone-badge">
                <span className="module-icone">{m.icone}</span>
              </div>
              <span className="module-duree">{m.duree}</span>
            </div>
            <h3>{m.titre}</h3>
            <p>
              {m.to === '/catalogue' && catalogue
                ? `${catalogue.nbModeles} modèles, ${catalogue.nbFamilles} familles d'IA différentes — pas seulement des chatbots.`
                : m.pitch}
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}
