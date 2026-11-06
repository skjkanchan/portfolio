export type EntryType = 'project' | 'internship' | 'leadership' | 'other'

export interface Entry {
  id: string
  title: string
  type: EntryType
  date: string
  scale: 1 | 2 | 3 | 4 | 5
  skills: string[]
  summary: string
  links: string[]
}
