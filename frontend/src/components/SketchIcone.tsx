import { useId } from 'react'

export type SketchCle =
  | 'cerveau'
  | 'llm'
  | 'vision'
  | 'prevision'
  | 'anomalie'
  | 'sante'
  | 'btp'
  | 'industrie'
  | 'commerce'
  | 'agriculture'
  | 'education'
  | 'immobilier'
  | 'transport'
  | 'secteur_public'
  | 'services_pro'
  | 'associations'
  | 'balance'

// Traits en primitives simples (lignes, cercles, chemins) — le filtre de turbulence appliqué
// plus bas leur donne un rendu "carnet de croquis" (léger tremblé de trait), plutôt que de
// dessiner à la main des chemins irréguliers pour chacune des 15 icônes.
const TRACES: Record<SketchCle, JSX.Element> = {
  cerveau: (
    <>
      <rect x="16" y="16" width="32" height="32" rx="8" />
      {[22, 32, 42].flatMap((x) =>
        [22, 32, 42].map((y) => <circle key={`${x}-${y}`} cx={x} cy={y} r="1.6" fill="currentColor" stroke="none" />),
      )}
      <line x1="32" y1="32" x2="22" y2="22" />
      <line x1="32" y1="32" x2="42" y2="22" />
      <line x1="32" y1="32" x2="22" y2="42" />
      <line x1="32" y1="32" x2="42" y2="42" />
      <line x1="24" y1="16" x2="24" y2="8" />
      <line x1="40" y1="16" x2="40" y2="8" />
      <line x1="24" y1="48" x2="24" y2="56" />
      <line x1="40" y1="48" x2="40" y2="56" />
      <line x1="16" y1="24" x2="8" y2="24" />
      <line x1="16" y1="40" x2="8" y2="40" />
      <line x1="48" y1="24" x2="56" y2="24" />
      <line x1="48" y1="40" x2="56" y2="40" />
    </>
  ),
  llm: (
    <>
      <path d="M12 14 h40 a4 4 0 0 1 4 4 v22 a4 4 0 0 1 -4 4 h-26 l-9 9 v-9 h-5 a4 4 0 0 1 -4 -4 v-22 a4 4 0 0 1 4 -4 z" />
      <line x1="20" y1="25" x2="44" y2="25" />
      <line x1="20" y1="33" x2="40" y2="33" />
      <line x1="20" y1="41" x2="34" y2="41" />
    </>
  ),
  vision: (
    <>
      <path d="M8 32 C 16 18, 48 18, 56 32 C 48 46, 16 46, 8 32 Z" />
      <circle cx="32" cy="32" r="7" />
      <circle cx="32" cy="32" r="2" fill="currentColor" stroke="none" />
      <path d="M6 16 v8 M6 16 h8" />
      <path d="M58 16 v8 M58 16 h-8" />
      <path d="M6 48 v-8 M6 48 h8" />
      <path d="M58 48 v-8 M58 48 h-8" />
    </>
  ),
  prevision: (
    <>
      <line x1="10" y1="52" x2="10" y2="10" />
      <line x1="10" y1="52" x2="54" y2="52" />
      <path d="M14 42 L24 34 L32 38 L44 22" fill="none" />
      <path d="M44 22 L52 14 M44 22 h8 v8" strokeDasharray="0" />
    </>
  ),
  anomalie: (
    <>
      {[[16, 40], [22, 46], [26, 36], [34, 44], [30, 30], [40, 38]].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2.2" fill="currentColor" stroke="none" />
      ))}
      <circle cx="48" cy="16" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="48" cy="16" r="8" />
    </>
  ),
  sante: (
    <>
      <circle cx="32" cy="32" r="22" />
      <path d="M12 32 h12 l4 -10 l6 20 l4 -10 h14" fill="none" />
    </>
  ),
  btp: (
    <>
      <path d="M14 40 C14 24, 50 24, 50 40 Z" />
      <line x1="10" y1="40" x2="54" y2="40" />
      <line x1="30" y1="14" x2="30" y2="24" />
      <path d="M22 48 l10 -6 l10 6" fill="none" />
    </>
  ),
  industrie: (
    <>
      <circle cx="32" cy="32" r="16" />
      <circle cx="32" cy="32" r="6" />
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
        const rad = (deg * Math.PI) / 180
        const x1 = 32 + 17 * Math.cos(rad)
        const y1 = 32 + 17 * Math.sin(rad)
        const x2 = 32 + 23 * Math.cos(rad)
        const y2 = 32 + 23 * Math.sin(rad)
        return <line key={deg} x1={x1} y1={y1} x2={x2} y2={y2} />
      })}
    </>
  ),
  commerce: (
    <>
      <path d="M10 14 h6 l4 30 h28 l6 -20 h-34" />
      <circle cx="24" cy="50" r="3.4" />
      <circle cx="42" cy="50" r="3.4" />
    </>
  ),
  agriculture: (
    <>
      <line x1="32" y1="10" x2="32" y2="54" />
      {[16, 24, 32, 40].map((y) => (
        <g key={y}>
          <path d={`M32 ${y} C 24 ${y - 4}, 20 ${y - 2}, 18 ${y - 8}`} fill="none" />
          <path d={`M32 ${y + 4} C 40 ${y}, 44 ${y + 2}, 46 ${y - 4}`} fill="none" />
        </g>
      ))}
      <ellipse cx="32" cy="12" rx="4" ry="6" />
    </>
  ),
  education: (
    <>
      <path d="M32 16 C 24 12, 14 12, 8 16 v28 C 14 40, 24 40, 32 44 Z" />
      <path d="M32 16 C 40 12, 50 12, 56 16 v28 C 50 40, 40 40, 32 44 Z" />
      <line x1="14" y1="22" x2="24" y2="20" />
      <line x1="14" y1="28" x2="24" y2="26" />
      <line x1="40" y1="20" x2="50" y2="22" />
      <line x1="40" y1="26" x2="50" y2="28" />
    </>
  ),
  immobilier: (
    <>
      <path d="M10 30 L32 12 L54 30" fill="none" />
      <path d="M16 28 v24 h32 v-24" />
      <rect x="28" y="38" width="8" height="14" />
    </>
  ),
  transport: (
    <>
      <rect x="6" y="26" width="28" height="18" />
      <path d="M34 32 h10 l8 8 v4 h-18 z" />
      <circle cx="16" cy="46" r="4" />
      <circle cx="42" cy="46" r="4" />
      <line x1="0" y1="24" x2="6" y2="24" />
      <line x1="0" y1="30" x2="4" y2="30" />
    </>
  ),
  secteur_public: (
    <>
      <path d="M10 22 L32 10 L54 22 Z" />
      <line x1="8" y1="22" x2="56" y2="22" />
      <line x1="8" y1="50" x2="56" y2="50" />
      <line x1="16" y1="26" x2="16" y2="46" />
      <line x1="26" y1="26" x2="26" y2="46" />
      <line x1="38" y1="26" x2="38" y2="46" />
      <line x1="48" y1="26" x2="48" y2="46" />
    </>
  ),
  services_pro: (
    <>
      <rect x="10" y="24" width="44" height="26" rx="3" />
      <path d="M24 24 v-6 a4 4 0 0 1 4 -4 h8 a4 4 0 0 1 4 4 v6" fill="none" />
      <line x1="10" y1="36" x2="54" y2="36" />
    </>
  ),
  associations: (
    <>
      <path d="M32 24 C 26 14, 12 18, 12 30 C 12 40, 24 46, 32 52 C 40 46, 52 40, 52 30 C 52 18, 38 14, 32 24 Z" />
      <path d="M14 44 C 18 50, 26 54, 32 54 C 38 54, 46 50, 50 44" fill="none" />
    </>
  ),
  balance: (
    <>
      <line x1="32" y1="10" x2="32" y2="50" />
      <line x1="12" y1="18" x2="52" y2="18" />
      <circle cx="32" cy="18" r="2" fill="currentColor" stroke="none" />
      <line x1="12" y1="18" x2="6" y2="32" />
      <line x1="12" y1="18" x2="18" y2="32" />
      <path d="M6 32 Q12 39 18 32" fill="none" />
      <line x1="52" y1="18" x2="46" y2="32" />
      <line x1="52" y1="18" x2="58" y2="32" />
      <path d="M46 32 Q52 39 58 32" fill="none" />
      <path d="M32 50 L23 58 h18 Z" />
    </>
  ),
}

type Props = {
  cle: SketchCle
  className?: string
}

// Icônes "carnet de croquis" : traits simples passés dans un filtre de déplacement (turbulence)
// pour un léger tremblé de main plutôt que des chemins parfaitement géométriques — cohérent
// avec le motif du grain de café déjà utilisé sur l'Accueil (encre simple + un peu d'imperfection).
export default function SketchIcone({ cle, className }: Props) {
  const id = useId()
  const filtreId = `sketch-rough-${id}`
  return (
    <svg viewBox="0 0 64 64" className={`sketch-icone ${className ?? ''}`} aria-hidden="true">
      <defs>
        <filter id={filtreId} x="-25%" y="-25%" width="150%" height="150%">
          <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="4" result="bruit" />
          <feDisplacementMap in="SourceGraphic" in2="bruit" scale="2" />
        </filter>
      </defs>
      <g
        filter={`url(#${filtreId})`}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.3"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {TRACES[cle]}
      </g>
    </svg>
  )
}
