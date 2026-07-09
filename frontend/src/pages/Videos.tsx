import { useEffect, useState } from 'react'
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
        Des extraits de conférences ou de formations sur l'IA, avec une explication de ce qu'on y
        voit en français simple — un schéma en anglais peut être parfaitement clair pour son auteur
        et complètement opaque pour vous.
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
                    <span>Cliquez pour voir l'explication</span>
                  </button>
                  {ouvert && (
                    <div className="template-details">
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
