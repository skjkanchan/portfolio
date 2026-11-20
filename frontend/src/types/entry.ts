export type EntryType = 'experience' | 'project' | 'leadership' | 'other'

export interface EntryLink {
  label: string
  url: string
}

export interface Entry {
  id: string
  title: string
  type: EntryType
  /** Year and month, e.g. "2025-06". Absent for projects. */
  start?: string
  /** Year and month, or "present" if ongoing. Absent for projects. */
  end?: string
  scale: 1 | 2 | 3 | 4 | 5
  skills: string[]
  summary: string
  links: EntryLink[]
  /** Optional Markdown details. */
  body?: string
}
