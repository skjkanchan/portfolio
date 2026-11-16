import { Link } from 'react-router-dom'
import type { Entry } from '../types/entry'

interface ExperienceCardProps {
  entry: Entry
}

export default function ExperienceCard({ entry }: ExperienceCardProps) {
  return (
    <article className="card">
      <h2 className="card__title">
        <Link to={`/experiences/${entry.id}`} className="card__link">
          {entry.title}
        </Link>
      </h2>
      <p className="meta">
        {entry.type} · <time dateTime={entry.date}>{entry.date}</time>
      </p>
      <p className="card__summary">{entry.summary}</p>
    </article>
  )
}
