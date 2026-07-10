type Props = {
  type: 'clio' | 'marco'
  parle: boolean
  actif: boolean
  decor?: string
  variante?: boolean
}

// Une couleur de robe par décor (donc par époque/ambiance) plutôt qu'une couleur fixe : Clio et
// Marco changent d'allure d'une histoire à l'autre — et même de scène à scène — au lieu de
// toujours porter exactement les mêmes teintes.
const COULEURS_PAR_DECOR: Record<string, { clio: string; marco: string }> = {
  plaine_venteuse: { clio: '#c17a4a', marco: '#3a5f7a' },
  chantier_urbain: { clio: '#a8522e', marco: '#2c4a5e' },
  siege_medieval: { clio: '#8f2d20', marco: '#4a2318' },
  espace_etoiles: { clio: '#6a5a9a', marco: '#233a6b' },
  ville_medievale_sombre: { clio: '#5a6b4a', marco: '#2c3a2c' },
  temple_antique: { clio: '#b5872f', marco: '#5c4522' },
  ocean_exploration: { clio: '#2f7a6b', marco: '#1a4a5c' },
  revolution_industrielle: { clio: '#8a4a2e', marco: '#3a3230' },
}
const COULEURS_DEFAUT = { clio: '#b45f3a', marco: '#2c3e6b' }

function assombrir(hex: string, facteur = 0.72): string {
  const n = parseInt(hex.slice(1), 16)
  const r = Math.round(((n >> 16) & 255) * facteur)
  const g = Math.round(((n >> 8) & 255) * facteur)
  const b = Math.round((n & 255) * facteur)
  return `rgb(${r}, ${g}, ${b})`
}

// Deux personnages simples et distincts (silhouette illustrée, pas photoréaliste) : Clio la
// curieuse (chignon, tient un livre) et Marco le conteur (capuche, tient une lanterne). La
// bouche s'anime en boucle pendant la réplique de ce personnage (classe .parle).
export default function Personnage({ type, parle, actif, decor, variante }: Props) {
  const estClio = type === 'clio'
  const palette = (decor && COULEURS_PAR_DECOR[decor]) || COULEURS_DEFAUT
  const couleurRobe = estClio ? palette.clio : palette.marco
  const couleurRobeOmbre = assombrir(couleurRobe)
  const couleurCapuche = estClio ? '#4a2e1a' : couleurRobe
  const couleurPeau = '#e8b98a'

  return (
    <div
      className={`personnage personnage-${type} ${actif ? 'personnage-actif' : 'personnage-inactif'} ${
        variante ? 'personnage-variante-a' : 'personnage-variante-b'
      }`}
    >
      <svg viewBox="0 0 200 300" className={parle ? 'personnage-svg personnage-parle' : 'personnage-svg'}>
        {/* Robe */}
        <path
          d="M 60 300 L 55 160 Q 55 130 100 130 Q 145 130 145 160 L 140 300 Z"
          fill={couleurRobe}
        />
        <path d="M 60 300 L 55 160 Q 55 145 65 135 L 70 300 Z" fill={couleurRobeOmbre} opacity="0.5" />

        {/* Bras */}
        <path d="M 55 170 Q 35 190 40 230" stroke={couleurRobe} strokeWidth="16" fill="none" strokeLinecap="round" />
        <path d="M 145 170 Q 165 190 160 230" stroke={couleurRobe} strokeWidth="16" fill="none" strokeLinecap="round" />

        {estClio ? (
          <>
            {/* Livre tenu par Clio */}
            <rect x="26" y="220" width="28" height="22" rx="2" fill="#f2e4c8" stroke="#8f4a2c" strokeWidth="2" />
            <line x1="40" y1="220" x2="40" y2="242" stroke="#8f4a2c" strokeWidth="1.5" />
          </>
        ) : (
          <>
            {/* Lanterne tenue par Marco */}
            <rect x="146" y="220" width="18" height="22" rx="2" fill="#3a3a3a" />
            <circle cx="155" cy="229" r="7" fill="#ffd873" className="lanterne-lueur" />
          </>
        )}

        {/* Cou */}
        <rect x="90" y="118" width="20" height="18" fill={couleurPeau} />

        {/* Capuche / coiffe (cercle plus large DERRIÈRE la tête — silhouette simple et fiable) */}
        <circle cx="100" cy="88" r="52" fill={couleurCapuche} />
        {estClio && <circle cx="100" cy="46" r="13" fill={couleurCapuche} />}

        {/* Tête */}
        <circle cx="100" cy="92" r="40" fill={couleurPeau} />

        {!estClio && (
          <>
            {/* Barbe de Marco */}
            <path d="M 74 108 Q 100 138 126 108 Q 100 122 74 108 Z" fill="#6b6b6b" />
          </>
        )}

        {/* Yeux */}
        <ellipse cx="84" cy="90" rx="4.5" ry="6" fill="#2a2018" className="personnage-oeil" />
        <ellipse cx="116" cy="90" rx="4.5" ry="6" fill="#2a2018" className="personnage-oeil" />

        {/* Sourcils */}
        <path d="M 77 80 Q 84 76 91 80" stroke="#4a2e1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d="M 109 80 Q 116 76 123 80" stroke="#4a2e1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />

        {/* Bouche (anime pendant la réplique) */}
        <ellipse cx="100" cy="110" rx="9" ry="4" fill="#8f4a3a" className="personnage-bouche" />
      </svg>
    </div>
  )
}
