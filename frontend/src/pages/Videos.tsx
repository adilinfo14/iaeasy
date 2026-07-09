import { Fragment, useEffect, useState } from 'react'
import { listerVideos } from '../api/client'

export default function Videos() {
  const [videos, setVideos] = useState<any[]>([])
  const [schemaOuvert, setSchemaOuvert] = useState<string | null>(null)

  useEffect(() => {
    listerVideos().then(setVideos)
  }, [])

  return (
    <div className="page page-videos">
      <h1>🎬 Vidéos</h1>
      <p className="page-intro">
        Cette rubrique réunit des extraits de conférences consacrées à l'intelligence artificielle,
        chacun accompagné d'une explication en français simple de ce qu'il donne à voir — un schéma
        conçu en anglais pouvant se révéler parfaitement limpide pour son auteur et tout à fait
        opaque pour qui le découvre.
      </p>

      {videos.map((v) => (
        <div key={v.id} className="video-bloc">
          <h2>{v.titre}</h2>
          <p>{v.description}</p>

          <div className="video-embed-wrap">
            <iframe
              className="video-embed"
              src={`https://www.youtube-nocookie.com/embed/${v.youtube_id}`}
              title={v.titre}
              allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>

          {v.source && <p className="texte-muted video-source">{v.source}</p>}

          <div className="templates-liste">
            {v.schemas.map((s: any, i: number) => {
              const id = `${v.id}-${i}`
              const ouvert = schemaOuvert === id
              return (
                <div key={id} className={ouvert ? 'template-carte ouverte' : 'template-carte'}>
                  <button className="template-entete" onClick={() => setSchemaOuvert(ouvert ? null : id)}>
                    <strong>{s.titre}</strong>
                    <span>Cliquez pour voir le schéma et l'explication</span>
                  </button>
                  {ouvert && (
                    <div className="template-details">
                      {s.schema?.length > 0 && (
                        <div className="schema-flow">
                          {s.schema.map((etape: any, j: number) => (
                            <Fragment key={j}>
                              <div className="schema-etape">
                                <div className="schema-icone">{etape.icone}</div>
                                <div className="schema-label">{etape.label}</div>
                              </div>
                              {j < s.schema.length - 1 && <div className="schema-fleche">→</div>}
                            </Fragment>
                          ))}
                        </div>
                      )}
                      <p>{s.explication}</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
