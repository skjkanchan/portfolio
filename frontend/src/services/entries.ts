import entriesData from '../data/entries.json'
import type { Entry, EntryType } from '../types/entry'

// Generated and validated by pipeline/build_entries.py, so the shape is
// checked there; TypeScript only sees plain strings and numbers in JSON.
const entries = entriesData as Entry[]

export interface EntryGroup {
  type: EntryType
  heading: string
  entries: Entry[]
}

// Display order of the groups on the experience list.
const GROUPS: { type: EntryType; heading: string }[] = [
  { type: 'experience', heading: 'Experience' },
  { type: 'project', heading: 'Projects' },
  { type: 'leadership', heading: 'Leadership' },
  { type: 'other', heading: 'Other' },
]

export function getEntries(): Entry[] {
  return entries
}

export function getEntryById(id: string): Entry | undefined {
  return entries.find((entry) => entry.id === id)
}

/** Entries grouped by type in display order, skipping empty groups. */
export function getEntryGroups(): EntryGroup[] {
  return GROUPS.map((group) => ({
    ...group,
    entries: entries.filter((entry) => entry.type === group.type),
  })).filter((group) => group.entries.length > 0)
}
