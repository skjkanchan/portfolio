import { Link } from 'react-router-dom'
import type { Entry } from '../types/entry'

interface ExperienceCardProps {
  entry: Entry
}

export default function ExperienceCard({ entry }: ExperienceCardProps) {
  return (
    <article>
      <h2>
        <Link to={`/experiences/${entry.id}`}>{entry.title}</Link>
      </h2>
      <p>
        {entry.type} · <time dateTime={entry.date}>{entry.date}</time>
      </p>
      <p>{entry.summary}</p>
    </article>
  )
}
