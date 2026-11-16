import { Link, useParams } from 'react-router-dom'
import { getEntryById } from '../services/entries'
import NotFoundPage from './NotFoundPage'

export default function ExperienceDetailPage() {
  const { id } = useParams()
  const entry = id ? getEntryById(id) : undefined

  if (!entry) {
    return <NotFoundPage />
  }

  return (
    <article className="detail">
      <h1>{entry.title}</h1>
      <p className="meta">
        {entry.type} · <time dateTime={entry.date}>{entry.date}</time> · Scale{' '}
        {entry.scale} of 5
      </p>
      <p className="lead">{entry.summary}</p>

      <section className="detail__section">
        <h2>Skills</h2>
        <ul className="pill-list">
          {entry.skills.map((skill) => (
            <li key={skill} className="pill">
              {skill}
            </li>
          ))}
        </ul>
      </section>

      {entry.links.length > 0 && (
        <section className="detail__section">
          <h2>Links</h2>
          <ul className="link-list">
            {entry.links.map((link) => (
              <li key={link}>
                <a href={link}>{link}</a>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section
        className="detail__similar"
        aria-labelledby="similar-experiences-heading"
      >
        <h2 id="similar-experiences-heading">Similar experiences</h2>
      </section>

      <p className="detail__back">
        <Link to="/experiences">Back to all experiences</Link>
      </p>
    </article>
  )
}
