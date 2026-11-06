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
    <article>
      <h1>{entry.title}</h1>
      <p>
        {entry.type} · <time dateTime={entry.date}>{entry.date}</time> · Scale{' '}
        {entry.scale} of 5
      </p>
      <p>{entry.summary}</p>

      <h2>Skills</h2>
      <ul>
        {entry.skills.map((skill) => (
          <li key={skill}>{skill}</li>
        ))}
      </ul>

      {entry.links.length > 0 && (
        <>
          <h2>Links</h2>
          <ul>
            {entry.links.map((link) => (
              <li key={link}>
                <a href={link}>{link}</a>
              </li>
            ))}
          </ul>
        </>
      )}

      <section aria-labelledby="similar-experiences-heading">
        <h2 id="similar-experiences-heading">Similar experiences</h2>
      </section>

      <p>
        <Link to="/experiences">Back to all experiences</Link>
      </p>
    </article>
  )
}
