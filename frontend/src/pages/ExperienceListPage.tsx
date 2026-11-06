import ExperienceCard from '../components/ExperienceCard'
import { getEntries } from '../services/entries'

export default function ExperienceListPage() {
  return (
    <>
      <h1>Experiences</h1>
      <ul>
        {getEntries().map((entry) => (
          <li key={entry.id}>
            <ExperienceCard entry={entry} />
          </li>
        ))}
      </ul>
    </>
  )
}
