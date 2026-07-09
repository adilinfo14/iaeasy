import { forwardRef, useCallback, useEffect, useImperativeHandle, useState } from 'react'
import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  Background,
  Controls,
  MarkerType,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  type Edge,
  type Node,
  type OnConnect,
  type OnEdgesChange,
  type OnNodesChange,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

const OPTIONS_ARETE = {
  type: 'smoothstep' as const,
  animated: true,
  markerEnd: { type: MarkerType.ArrowClosed, color: '#4f7cff' },
}

type Condition = 'autorise' | 'bloque' | undefined

// Un lien conditionnel n'est proposé qu'en sortie d'un filtre de modération : c'est le seul
// nœud du moteur qui produit une décision binaire (bloqué/autorisé) exploitable par le graphe.
const BRIQUE_AVEC_CONDITION = 'moderation'

function styleArete(condition: Condition) {
  if (condition === 'autorise') {
    return {
      type: 'smoothstep' as const,
      animated: true,
      label: '✅ Si autorisé',
      labelStyle: { fill: '#4ade80', fontWeight: 600, fontSize: 11 },
      style: { stroke: '#4ade80' },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#4ade80' },
      data: { condition },
    }
  }
  if (condition === 'bloque') {
    return {
      type: 'smoothstep' as const,
      animated: false,
      label: '🚫 Si bloqué',
      labelStyle: { fill: '#f87171', fontWeight: 600, fontSize: 11 },
      style: { stroke: '#f87171', strokeDasharray: '5 4' },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#f87171' },
      data: { condition },
    }
  }
  return { ...OPTIONS_ARETE, data: { condition: undefined } }
}

const CLE_APERCU = ['prompt', 'texte', 'expression']

function apercuConfig(config: Record<string, unknown>): string {
  for (const cle of CLE_APERCU) {
    const valeur = config?.[cle]
    if (typeof valeur === 'string' && valeur.trim()) {
      return valeur.length > 60 ? `${valeur.slice(0, 60)}…` : valeur
    }
  }
  return ''
}

function completerConfig(composant: any, configExistant: Record<string, unknown>) {
  const config = { ...(configExistant || {}) }
  for (const champ of composant?.champs_config || []) {
    if (config[champ.cle] === undefined) {
      config[champ.cle] = champ.defaut !== undefined ? champ.defaut : champ.type === 'select' ? champ.options?.[0] : ''
    }
  }
  return config
}

function construireLabel(titre: string, icone: string, config: Record<string, unknown>) {
  const apercu = apercuConfig(config)
  return (
    <div className="noeud-contenu">
      <strong>{icone} {titre}</strong>
      {apercu ? <div className="noeud-apercu">« {apercu} »</div> : <div className="noeud-apercu noeud-apercu-vide">(aucune entrée définie — cliquez pour en ajouter une)</div>}
    </div>
  )
}

type BriqueNode = Node & { brique: string; config: Record<string, unknown> }

type Props = {
  composants: any[]
  templateACharger: any | null
  resultatsParNoeud: Record<string, any> | null
  enCours: boolean
  onExecuter: (
    nodes: { id: string; type: string; config: Record<string, unknown> }[],
    edges: { source: string; target: string; condition?: 'autorise' | 'bloque' }[],
  ) => void
  onComposantInfo: (brique: string, noeudId: string | undefined, config: Record<string, unknown>) => void
}

export type BrickCanvasHandle = {
  modifierConfigNoeud: (noeudId: string, cle: string, valeur: unknown) => void
}

let compteurId = 1

const COULEURS_CATEGORIE: Record<string, string> = {
  source: '#38bdf8',
  traitement: '#a78bfa',
  stockage: '#facc15',
  modele: '#4ade80',
  outil: '#fb923c',
}

const LABEL_CATEGORIE: Record<string, string> = {
  source: 'Source',
  traitement: 'Traitement',
  stockage: 'Stockage',
  modele: 'Modèle',
  outil: 'Outil',
}

function grouperParCategorie(composants: any[]) {
  const groupes: { categorie: string; items: any[] }[] = []
  for (const c of composants) {
    let groupe = groupes.find((g) => g.categorie === c.categorie)
    if (!groupe) {
      groupe = { categorie: c.categorie, items: [] }
      groupes.push(groupe)
    }
    groupe.items.push(c)
  }
  return groupes
}

const CanvasInterne = forwardRef<BrickCanvasHandle, Props>(function CanvasInterne(
  { composants, templateACharger, resultatsParNoeud, enCours, onExecuter, onComposantInfo },
  ref,
) {
  const [nodes, setNodes] = useState<BriqueNode[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const { fitView } = useReactFlow()

  useImperativeHandle(ref, () => ({
    modifierConfigNoeud(noeudId, cle, valeur) {
      setNodes((nds) =>
        nds.map((n) => {
          if (n.id !== noeudId) return n
          const composant = composants.find((c) => c.id === n.brique)
          const nouvelleConfig = { ...n.config, [cle]: valeur }
          return { ...n, config: nouvelleConfig, data: { label: construireLabel(composant?.titre || n.brique, composant?.icone || '', nouvelleConfig) } }
        }),
      )
    },
  }))

  useEffect(() => {
    if (!templateACharger) return
    const composantParType = new Map(composants.map((c) => [c.id, c]))
    const nouveauxNoeuds: BriqueNode[] = templateACharger.nodes.map((n: any) => {
      const composant = composantParType.get(n.type)
      const config = completerConfig(composant, n.config || {})
      return {
        id: n.id,
        position: n.position || { x: 100, y: 100 },
        data: { label: construireLabel(composant?.titre || n.type, composant?.icone || '', config) },
        brique: n.type,
        config,
        style: {
          background: COULEURS_CATEGORIE[composant?.categorie] ? `${COULEURS_CATEGORIE[composant.categorie]}22` : undefined,
          borderColor: COULEURS_CATEGORIE[composant?.categorie],
          width: 220,
        },
      }
    })
    const nouvellesAretes: Edge[] = templateACharger.edges.map((e: any, i: number) => ({
      id: `tpl-${i}`,
      source: e.source,
      target: e.target,
      ...styleArete(e.condition),
    }))
    setNodes(nouveauxNoeuds)
    setEdges(nouvellesAretes)
    compteurId = nouveauxNoeuds.length + 1
    // Laisse react-flow calculer les positions avant de recentrer la vue.
    requestAnimationFrame(() => fitView({ padding: 0.25, duration: 300 }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [templateACharger])

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds) as BriqueNode[]),
    [],
  )
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [],
  )
  const onConnect: OnConnect = useCallback(
    (connexion) => {
      const noeudSource = nodes.find((n) => n.id === connexion.source)
      // Un lien sortant d'un filtre de modération est conditionnel par défaut ("si autorisé") :
      // c'est la seule brique qui produit une décision binaire exploitable par le graphe.
      const condition: Condition = noeudSource?.brique === BRIQUE_AVEC_CONDITION ? 'autorise' : undefined
      setEdges((eds) => addEdge({ ...connexion, ...styleArete(condition) }, eds))
    },
    [nodes],
  )

  function onEdgeClick(_: unknown, edge: Edge) {
    const noeudSource = nodes.find((n) => n.id === edge.source)
    if (noeudSource?.brique !== BRIQUE_AVEC_CONDITION) return
    const conditionActuelle = (edge.data as { condition?: Condition } | undefined)?.condition
    const suivante: Condition = conditionActuelle === 'autorise' ? 'bloque' : 'autorise'
    setEdges((eds) => eds.map((e) => (e.id === edge.id ? { ...e, ...styleArete(suivante) } : e)))
  }

  function ajouterNoeud(composant: any) {
    const id = String(compteurId++)
    const config = completerConfig(composant, {})
    setNodes((nds) => {
      const nouveaux = [
        ...nds,
        {
          id,
          position: { x: 80 + (nds.length % 3) * 220, y: 60 + Math.floor(nds.length / 3) * 140 },
          data: { label: construireLabel(composant.titre, composant.icone, config) },
          brique: composant.id,
          config,
          style: {
            background: COULEURS_CATEGORIE[composant.categorie] ? `${COULEURS_CATEGORIE[composant.categorie]}22` : undefined,
            borderColor: COULEURS_CATEGORIE[composant.categorie],
            width: 220,
          },
        },
      ]
      requestAnimationFrame(() => fitView({ padding: 0.25, duration: 300 }))
      return nouveaux
    })
    onComposantInfo(composant.id, id, config)
  }

  function executer() {
    onExecuter(
      nodes.map((n) => ({ id: n.id, type: n.brique, config: n.config || {} })),
      edges.map((e) => ({
        source: e.source,
        target: e.target,
        condition: (e.data as { condition?: Condition } | undefined)?.condition,
      })),
    )
  }

  return (
    <div className="canvas-layout">
      <aside className="palette">
        <h4>Briques d'architecture</h4>
        <p className="texte-muted">Cliquez une brique pour l'ajouter au canvas et voir sa définition.</p>
        {grouperParCategorie(composants).map((groupe) => (
          <div key={groupe.categorie} className="palette-groupe">
            <span className={`palette-groupe-titre cat-${groupe.categorie}`}>
              {LABEL_CATEGORIE[groupe.categorie] || groupe.categorie}
            </span>
            {groupe.items.map((c) => (
              <button
                key={c.id}
                className={`palette-brique cat-${groupe.categorie}-bordure`}
                onClick={() => ajouterNoeud(c)}
              >
                {c.icone} {c.titre}
              </button>
            ))}
          </div>
        ))}
      </aside>
      <div className="canvas">
        {enCours && <div className="canvas-chargement" />}
        <button className="executer-flottant" onClick={executer} disabled={nodes.length === 0 || enCours}>
          {enCours ? '⏳ Exécution en cours…' : '▶ Exécuter le graphe'}
        </button>
        {nodes.length === 0 && (
          <div className="canvas-vide">
            <p>👈 Choisissez un modèle d'architecture à gauche</p>
            <p className="texte-muted">ou cliquez une brique ci-contre pour construire votre propre graphe.</p>
          </div>
        )}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={(_, node) => {
            const n = node as BriqueNode
            onComposantInfo(n.brique, n.id, n.config || {})
          }}
          onEdgeClick={onEdgeClick}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
      {nodes.length > 0 && (
        <div className="canvas-hint">
          💡 Cliquez un nœud pour voir sa définition et <strong>remplir ou modifier son entrée</strong> avant d'exécuter.
          {resultatsParNoeud && ' Un second clic après exécution montre aussi ce que le nœud a produit.'}
          {nodes.some((n) => n.brique === BRIQUE_AVEC_CONDITION) &&
            ' Un lien tracé depuis un filtre de modération est conditionnel (✅ Si autorisé par défaut) — cliquez ce lien pour basculer vers 🚫 Si bloqué.'}
        </div>
      )}
    </div>
  )
})

const BrickCanvas = forwardRef<BrickCanvasHandle, Props>(function BrickCanvas(props, ref) {
  return (
    <ReactFlowProvider>
      <CanvasInterne {...props} ref={ref} />
    </ReactFlowProvider>
  )
})

export default BrickCanvas
