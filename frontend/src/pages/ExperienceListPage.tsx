import ExperienceCard from '../components/ExperienceCard'
import { getEntryGroups } from '../services/entries'

export default function ExperienceListPage() {
  return (
    <>
      <h1>Experiences</h1>
      {getEntryGroups().map((group) => (
        <section
          key={group.type}
          className="entry-group"
          aria-labelledby={`group-${group.type}`}
        >
          <h2 id={`group-${group.type}`}>{group.heading}</h2>
          <ul className="card-grid">
            {group.entries.map((entry) => (
              <li key={entry.id}>
                <ExperienceCard entry={entry} />
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  )
}
