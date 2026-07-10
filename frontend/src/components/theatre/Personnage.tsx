type Props = {
  type: 'clio' | 'marco'
  parle: boolean
  actif: boolean
}

// Deux personnages simples et distincts (silhouette illustrée, pas photoréaliste) : Clio la
// curieuse (robe terracotta, chignon, tient un livre) et Marco le conteur (robe bleu nuit,
// capuche, tient une lanterne). La bouche s'anime en boucle pendant la réplique de ce
// personnage (classe .parle), l'autre s'assombrit légèrement pour indiquer qui a la parole.
export default function Personnage({ type, parle, actif }: Props) {
  const estClio = type === 'clio'
  const couleurRobe = estClio ? '#b45f3a' : '#2c3e6b'
  const couleurRobeOmbre = estClio ? '#8f4a2c' : '#1e2b4f'
  const couleurPeau = '#e8b98a'

  return (
    <div className={`personnage personnage-${type} ${actif ? 'personnage-actif' : 'personnage-inactif'}`}>
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
            <rect x="28" y="222" width="26" height="20" rx="2" fill="#f2e4c8" stroke="#8f4a2c" strokeWidth="2" />
            <line x1="41" y1="222" x2="41" y2="242" stroke="#8f4a2c" strokeWidth="1.5" />
          </>
        ) : (
          <>
            {/* Lanterne tenue par Marco */}
            <rect x="148" y="222" width="16" height="20" rx="2" fill="#3a3a3a" />
            <circle cx="156" cy="230" r="7" fill="#ffd873" className="lanterne-lueur" />
          </>
        )}

        {/* Cou */}
        <rect x="90" y="118" width="20" height="18" fill={couleurPeau} />

        {/* Tête */}
        <circle cx="100" cy="90" r="42" fill={couleurPeau} />

        {estClio ? (
          <>
            {/* Chignon + cheveux */}
            <circle cx="100" cy="60" r="30" fill="#4a2e1a" />
            <circle cx="100" cy="52" r="10" fill="#4a2e1a" />
            <path d="M 60 90 Q 58 65 75 55" stroke="#4a2e1a" strokeWidth="10" fill="none" strokeLinecap="round" />
            <path d="M 140 90 Q 142 65 125 55" stroke="#4a2e1a" strokeWidth="10" fill="none" strokeLinecap="round" />
          </>
        ) : (
          <>
            {/* Capuche */}
            <path d="M 55 95 Q 50 30 100 25 Q 150 30 145 95 Q 148 60 100 55 Q 52 60 55 95 Z" fill={couleurRobe} />
            {/* Barbe */}
            <path d="M 75 105 Q 100 135 125 105 Q 100 120 75 105 Z" fill="#6b6b6b" />
          </>
        )}

        {/* Yeux */}
        <ellipse cx="84" cy="88" rx="4.5" ry="6" fill="#2a2018" className="personnage-oeil" />
        <ellipse cx="116" cy="88" rx="4.5" ry="6" fill="#2a2018" className="personnage-oeil" />

        {/* Sourcils */}
        <path d="M 77 78 Q 84 74 91 78" stroke="#4a2e1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d="M 109 78 Q 116 74 123 78" stroke="#4a2e1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />

        {/* Bouche (anime pendant la réplique) */}
        <ellipse cx="100" cy="108" rx="9" ry="4" fill="#8f4a3a" className="personnage-bouche" />
      </svg>
    </div>
  )
}
