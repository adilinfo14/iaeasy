type Etape = { icone: string; label: string }

type Props = {
  etapes: Etape[]
  // Change à chaque chapitre : force le remontage (via key côté appelant) pour rejouer
  // l'apparition étape par étape plutôt que de figer un schéma statique d'un bloc.
}

// Réutilise les classes schema-flow/schema-etape déjà existantes (Parcours, Vidéos) pour rester
// visuellement cohérent avec le reste du site, avec en plus une apparition échelonnée
// (schema-anime) propre au Voyage — demandé explicitement : "il faut que ce soit animé".
export default function SchemaDiagram({ etapes }: Props) {
  return (
    <div className="schema-flow schema-anime">
      {etapes.map((s, i) => (
        <div key={i} className="schema-etape-groupe">
          <div className="schema-etape schema-etape-anime" style={{ animationDelay: `${i * 0.35}s` }}>
            <div className="schema-icone">{s.icone}</div>
            <div className="schema-label">{s.label}</div>
          </div>
          {i < etapes.length - 1 && (
            <div className="schema-fleche schema-fleche-anime" style={{ animationDelay: `${i * 0.35 + 0.2}s` }}>
              →
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
