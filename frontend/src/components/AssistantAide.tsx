import { useState, type KeyboardEvent } from 'react'
import { demarrerChat, suivreChat } from '../api/client'

type Message = { role: 'user' | 'assistant'; content: string }

const MESSAGE_ACCUEIL: Message = {
  role: 'assistant',
  content:
    "Bonjour ! Je peux vous aider à comprendre un terme ou une notion d'IA rencontrée sur ce site (voir aussi le Glossaire). Que voulez-vous savoir ?",
}

export default function AssistantAide() {
  const [ouvert, setOuvert] = useState(false)
  const [messages, setMessages] = useState<Message[]>([MESSAGE_ACCUEIL])
  const [saisie, setSaisie] = useState('')
  const [enCours, setEnCours] = useState(false)
  const [reponseEnCours, setReponseEnCours] = useState('')

  async function envoyer() {
    const texte = saisie.trim()
    if (!texte || enCours) return
    const historique = messages.slice(-8).map((m) => ({ role: m.role, content: m.content }))
    setMessages((m) => [...m, { role: 'user', content: texte }])
    setSaisie('')
    setEnCours(true)
    setReponseEnCours('')
    try {
      const { job_id } = await demarrerChat(texte, historique)
      // Le flux SSE rejoue tous les morceaux depuis le début à chaque reconnexion — remettre le
      // texte accumulé à zéro sur onOuverture évite un effet de frappe dupliqué si le visiteur
      // change d'onglet/d'application sur mobile pendant la réponse.
      let accumulateur = ''
      suivreChat(
        job_id,
        (delta) => {
          accumulateur += delta
          setReponseEnCours(accumulateur)
        },
        (fin) => {
          if (fin.status === 'erreur') {
            setMessages((m) => [
              ...m,
              { role: 'assistant', content: `Désolé, une erreur est survenue : ${fin.erreur}` },
            ])
          } else {
            setMessages((m) => [...m, { role: 'assistant', content: fin.reponse || accumulateur }])
          }
          setReponseEnCours('')
          setEnCours(false)
        },
        () => {
          accumulateur = ''
          setReponseEnCours('')
        },
      )
    } catch (e: any) {
      setMessages((m) => [...m, { role: 'assistant', content: `Désolé, une erreur est survenue : ${e.message}` }])
      setEnCours(false)
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      envoyer()
    }
  }

  return (
    <div className="assistant-aide">
      {ouvert && (
        <div className="assistant-panneau">
          <div className="assistant-entete">
            <strong>💬 Besoin d'aide ?</strong>
            <button className="assistant-fermer" onClick={() => setOuvert(false)} aria-label="Fermer l'assistant">
              ✕
            </button>
          </div>
          <div className="assistant-messages">
            {messages.map((m, i) => (
              <div
                key={i}
                className={m.role === 'user' ? 'assistant-msg assistant-msg-user' : 'assistant-msg assistant-msg-bot'}
              >
                {m.content}
              </div>
            ))}
            {enCours && reponseEnCours && (
              <div className="assistant-msg assistant-msg-bot">{reponseEnCours}</div>
            )}
            {enCours && !reponseEnCours && (
              <div className="assistant-msg assistant-msg-bot assistant-msg-attente">
                <span className="assistant-typing-dot" />
                <span className="assistant-typing-dot" />
                <span className="assistant-typing-dot" />
              </div>
            )}
          </div>
          <div className="assistant-saisie">
            <textarea
              value={saisie}
              onChange={(e) => setSaisie(e.target.value)}
              onKeyDown={onKeyDown}
              rows={2}
              maxLength={500}
              placeholder="Posez votre question… (Entrée pour envoyer)"
              disabled={enCours}
            />
            <button onClick={envoyer} disabled={enCours || !saisie.trim()}>
              Envoyer
            </button>
          </div>
        </div>
      )}
      <button
        className="assistant-bouton"
        onClick={() => setOuvert(!ouvert)}
        aria-label={ouvert ? "Fermer l'assistant" : "Ouvrir l'assistant d'aide"}
      >
        {ouvert ? '✕' : '💬'}
      </button>
    </div>
  )
}
