import ExperienceCard from '../components/ExperienceCard'
import { getEntries } from '../services/entries'

export default function ExperienceListPage() {
  return (
    <>
      <h1>Experiences</h1>
      <ul className="card-grid">
        {getEntries().map((entry) => (
          <li key={entry.id}>
            <ExperienceCard entry={entry} />
          </li>
        ))}
      </ul>
    </>
  )
}
