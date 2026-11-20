import { Link } from 'react-router-dom'
import type { Entry } from '../types/entry'
import DateRange from './DateRange'

interface ExperienceCardProps {
  entry: Entry
}

export default function ExperienceCard({ entry }: ExperienceCardProps) {
  return (
    <article className="card">
      <h3 className="card__title">
        <Link to={`/experiences/${entry.id}`} className="card__link">
          {entry.title}
        </Link>
      </h3>
      {entry.start && (
        <p className="meta">
          <DateRange start={entry.start} end={entry.end} />
        </p>
      )}
      <p className="card__summary">{entry.summary}</p>
    </article>
  )
}
