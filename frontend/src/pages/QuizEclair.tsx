import { useEffect, useState } from 'react'
import { lireProgression, listerBriques } from '../api/client'

const NB_QUESTIONS = 5

type QuestionPiochee = { briqueId: string; briqueTitre: string; question: string; options: string[]; bonne_reponse: number }

function melanger<T>(tableau: T[]): T[] {
  const copie = [...tableau]
  for (let i = copie.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copie[i], copie[j]] = [copie[j], copie[i]]
  }
  return copie
}

export default function QuizEclair() {
  const [chargement, setChargement] = useState(true)
  const [questions, setQuestions] = useState<QuestionPiochee[]>([])
  const [reponses, setReponses] = useState<(number | null)[]>([])
  const [valide, setValide] = useState(false)

  function piocher(briques: any[], debloquees: string[]) {
    const pool: QuestionPiochee[] = []
    for (const b of briques) {
      if (!debloquees.includes(b.id)) continue
      for (const q of b.quiz || []) {
        pool.push({ briqueId: b.id, briqueTitre: b.titre, ...q })
      }
    }
    const piochees = melanger(pool).slice(0, NB_QUESTIONS)
    setQuestions(piochees)
    setReponses(piochees.map(() => null))
    setValide(false)
  }

  useEffect(() => {
    Promise.all([listerBriques(), lireProgression()]).then(([briques, p]) => {
      piocher(briques, p.debloquees)
      setChargement(false)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function relancer() {
    Promise.all([listerBriques(), lireProgression()]).then(([briques, p]) => piocher(briques, p.debloquees))
  }

  function choisir(qIdx: number, optIdx: number) {
    if (valide) return
    setReponses((r) => r.map((v, i) => (i === qIdx ? optIdx : v)))
  }

  const toutRepondu = questions.length > 0 && reponses.every((r) => r !== null)
  const score = valide ? questions.filter((q, i) => reponses[i] === q.bonne_reponse).length : 0

  return (
    <div className="page page-quiz-eclair">
      <h1>⚡ Quiz éclair</h1>
      <p className="page-intro">
        {NB_QUESTIONS} questions piochées au hasard parmi toutes les briques déjà débloquées —
        pour réviser en deux minutes plutôt que refaire un module entier.
      </p>

      {chargement && <p className="texte-muted">Préparation du quiz…</p>}

      {!chargement && questions.length === 0 && (
        <p className="texte-muted">
          Débloquez au moins une brique dans le Parcours pour pouvoir générer un quiz éclair.
        </p>
      )}

      {questions.map((q, qi) => (
        <div key={qi} className="quiz-question quiz-eclair-question">
          <p className="texte-muted quiz-eclair-source">{q.briqueTitre}</p>
          <p>{q.question}</p>
          <div className="quiz-options">
            {q.options.map((opt, oi) => {
              const selectionne = reponses[qi] === oi
              let classe = 'quiz-option'
              if (selectionne) classe += ' selectionne'
              if (valide && oi === q.bonne_reponse) classe += ' correcte'
              if (valide && selectionne && oi !== q.bonne_reponse) classe += ' incorrecte'
              return (
                <button key={oi} type="button" className={classe} onClick={() => choisir(qi, oi)} disabled={valide}>
                  {opt}
                </button>
              )
            })}
          </div>
        </div>
      ))}

      {questions.length > 0 && !valide && (
        <button onClick={() => setValide(true)} disabled={!toutRepondu}>
          Valider mes réponses
        </button>
      )}

      {valide && (
        <div className="quiz-resultat">
          <p className={score === questions.length ? 'quiz-resultat-ok' : ''}>
            Score : {score} / {questions.length}
          </p>
          <button onClick={relancer}>🔁 Nouveau quiz éclair</button>
        </div>
      )}
    </div>
  )
}
