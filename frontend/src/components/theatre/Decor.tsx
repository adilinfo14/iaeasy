import { useMemo } from 'react'

const SILHOUETTES: Record<string, JSX.Element> = {
  plaine_venteuse: (
    // Les personnages occupent environ 8%-46% et 54%-92% de la largeur (soit ~64-368 et
    // 432-736 sur 800) : tout accent décoratif doit rester dans la bande centrale étroite
    // (368-432) ou tout en haut du ciel, jamais à hauteur de visage dans ces deux zones —
    // un premier essai y plaçait des nuages qui créaient des halos derrière les têtes.
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <circle cx="650" cy="45" r="40" fill="#fff6da" opacity="0.85" />
      <path d="M0 220 Q200 190 400 215 T800 205 V300 H0 Z" fill="#c9a86a" />
      <path d="M0 250 Q200 230 400 248 T800 240 V300 H0 Z" fill="#a9863f" />
      <g className="decor-avion" transform="translate(400,90)">
        <ellipse cx="0" cy="0" rx="55" ry="7" fill="#c9c0a0" />
        <ellipse cx="0" cy="-14" rx="38" ry="6" fill="#b8ac86" />
        <rect x="-6" y="-4" width="12" height="16" fill="#6b6248" />
      </g>
      <ellipse cx="60" cy="30" rx="40" ry="13" fill="#fff" opacity="0.5" />
    </svg>
  ),
  chantier_urbain: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <rect x="0" y="180" width="120" height="120" fill="#5a4636" />
      <rect x="130" y="150" width="100" height="150" fill="#4a3a2c" />
      <rect x="620" y="160" width="110" height="140" fill="#4a3a2c" />
      <rect x="700" y="190" width="100" height="110" fill="#5a4636" />
      {/* Tour en construction */}
      <g stroke="#caa15a" strokeWidth="4" fill="none">
        <path d="M340 300 L400 60 L460 300" />
        <path d="M355 260 L445 260 M362 210 L438 210 M370 160 L430 160 M380 110 L420 110" />
        <path d="M340 300 L460 60 M460 300 L340 60" opacity="0.6" />
      </g>
      <rect x="392" y="40" width="16" height="24" fill="#caa15a" />
      <line x1="400" y1="40" x2="460" y2="20" stroke="#caa15a" strokeWidth="3" />
    </svg>
  ),
  siege_medieval: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <rect x="0" y="190" width="800" height="20" fill="#3a2420" />
      {Array.from({ length: 10 }).map((_, i) => (
        <rect key={i} x={i * 82} y="150" width="60" height="60" fill="#3a2420" />
      ))}
      {Array.from({ length: 11 }).map((_, i) => (
        <rect key={`c${i}`} x={i * 82 - 12} y="135" width="24" height="18" fill="#3a2420" />
      ))}
      <rect x="360" y="70" width="70" height="130" fill="#2c1a18" />
      <path className="decor-flamme" d="M30 150 Q40 120 30 100 Q20 120 30 150 Z" fill="#ff8a3d" />
      <path className="decor-flamme" d="M400 150 Q412 115 400 90 Q388 115 400 150 Z" fill="#ff6a2d" style={{ animationDelay: '0.6s' }} />
      <path className="decor-flamme" d="M770 150 Q780 122 770 105 Q760 122 770 150 Z" fill="#ffab3d" style={{ animationDelay: '1.1s' }} />
    </svg>
  ),
  espace_etoiles: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <circle cx="130" cy="70" r="34" fill="#e8e8ec" />
      <circle cx="118" cy="60" r="6" fill="#c9c9d4" opacity="0.6" />
      <circle cx="142" cy="82" r="4" fill="#c9c9d4" opacity="0.6" />
      <path d="M0 260 Q200 230 400 250 T800 245 V300 H0 Z" fill="#8f97ad" />
      <path d="M0 280 Q200 260 400 275 T800 270 V300 H0 Z" fill="#6b7390" />
      <g className="decor-module" transform="translate(400,220)">
        <rect x="-20" y="-20" width="40" height="30" fill="#d8d8d8" />
        <line x1="-25" y1="10" x2="-30" y2="30" stroke="#aaa" strokeWidth="4" />
        <line x1="25" y1="10" x2="30" y2="30" stroke="#aaa" strokeWidth="4" />
        <rect x="-8" y="-32" width="16" height="14" fill="#ffd873" />
      </g>
    </svg>
  ),
  ville_medievale_sombre: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      {Array.from({ length: 9 }).map((_, i) => (
        <g key={i}>
          <rect x={i * 92} y={210 - (i % 3) * 20} width="80" height={90 + (i % 3) * 20} fill="#232a24" />
          <polygon
            points={`${i * 92 - 4},${210 - (i % 3) * 20} ${i * 92 + 40},${170 - (i % 3) * 20} ${i * 92 + 84},${210 - (i % 3) * 20}`}
            fill="#1a201b"
          />
        </g>
      ))}
      <ellipse cx="400" cy="205" rx="16" ry="10" fill="#ffd873" opacity="0.5" className="decor-lueur" />
    </svg>
  ),
  temple_antique: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <circle cx="680" cy="60" r="40" fill="#ffe3a3" opacity="0.8" />
      <polygon points="120,300 220,120 320,300" fill="#8a6a3a" />
      <polygon points="330,300 400,180 470,300" fill="#7a5c30" />
      <polygon points="480,300 560,150 640,300" fill="#8a6a3a" />
      <rect x="0" y="290" width="800" height="10" fill="#c9a86a" />
    </svg>
  ),
  ocean_exploration: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <g transform="translate(420,140)">
        <path d="M-70 40 Q0 60 70 40 L55 70 Q0 85 -55 70 Z" fill="#3a2c1e" />
        <line x1="0" y1="-70" x2="0" y2="40" stroke="#3a2c1e" strokeWidth="5" />
        <polygon points="0,-70 45,20 0,20" fill="#e8e2d0" />
        <polygon points="0,-50 -30,20 0,20" fill="#d8d0ba" />
      </g>
      <path d="M0 220 Q100 200 200 220 T400 218 T600 222 T800 218 V300 H0 Z" fill="#1f5a6b" />
      <path d="M0 250 Q100 235 200 250 T400 246 T600 252 T800 248 V300 H0 Z" fill="#164654" />
    </svg>
  ),
  revolution_industrielle: (
    <svg viewBox="0 0 800 300" className="decor-silhouette" preserveAspectRatio="xMidYMax slice">
      <rect x="60" y="160" width="140" height="140" fill="#3a3230" />
      <rect x="220" y="190" width="180" height="110" fill="#2c2624" />
      <rect x="420" y="150" width="150" height="150" fill="#3a3230" />
      <rect x="30" y="90" width="24" height="80" fill="#2c2624" />
      <rect x="390" y="80" width="24" height="80" fill="#2c2624" />
      <ellipse className="decor-fumee" cx="42" cy="80" rx="20" ry="14" fill="#6b6560" opacity="0.6" />
      <ellipse className="decor-fumee" cx="402" cy="70" rx="24" ry="16" fill="#6b6560" opacity="0.55" style={{ animationDelay: '1s' }} />
    </svg>
  ),
}

const PARTICULES: Record<string, { emoji: string; classe: string } | null> = {
  plaine_venteuse: { emoji: '·', classe: 'particule-vent' },
  chantier_urbain: { emoji: '·', classe: 'particule-poussiere' },
  siege_medieval: { emoji: '·', classe: 'particule-braise' },
  espace_etoiles: { emoji: '·', classe: 'particule-etoile' },
  ville_medievale_sombre: { emoji: '·', classe: 'particule-brume' },
  temple_antique: { emoji: '·', classe: 'particule-poussiere' },
  ocean_exploration: { emoji: '·', classe: 'particule-embrun' },
  revolution_industrielle: { emoji: '·', classe: 'particule-suie' },
}

export default function Decor({ decor }: { decor: string }) {
  const particule = PARTICULES[decor]

  // Positions/délais générés une seule fois par décor (pas à chaque re-render du dialogue).
  const particules = useMemo(
    () =>
      Array.from({ length: 16 }).map((_, i) => ({
        left: `${(i * 37) % 100}%`,
        delay: `${(i * 0.6) % 8}s`,
        duree: `${6 + (i % 5)}s`,
      })),
    [decor],
  )

  return (
    <div className={`decor decor-${decor}`}>
      {SILHOUETTES[decor]}
      {particule && (
        <div className="particules">
          {particules.map((p, i) => (
            <span
              key={i}
              className={`particule ${particule.classe}`}
              style={{ left: p.left, animationDelay: p.delay, animationDuration: p.duree }}
            />
          ))}
        </div>
      )}
      <div className="decor-vignette" />
    </div>
  )
}
