import type { Entry } from '../types/entry'

// Fake data for the scaffold only. Replaced by real entries from content/entries.
export const placeholderEntries: Entry[] = [
  {
    id: 'placeholder-project',
    title: 'Placeholder Project',
    type: 'project',
    date: '2000-01',
    scale: 1,
    skills: ['Placeholder skill A', 'Placeholder skill B'],
    summary: 'Placeholder summary for a project entry.',
    links: ['https://example.com'],
  },
  {
    id: 'placeholder-internship',
    title: 'Placeholder Internship',
    type: 'internship',
    date: '2000-02',
    scale: 3,
    skills: ['Placeholder skill B', 'Placeholder skill C'],
    summary: 'Placeholder summary for an internship entry.',
    links: [],
  },
  {
    id: 'placeholder-leadership',
    title: 'Placeholder Leadership Role',
    type: 'leadership',
    date: '2000-03',
    scale: 2,
    skills: ['Placeholder skill D'],
    summary: 'Placeholder summary for a leadership entry.',
    links: [],
  },
]
