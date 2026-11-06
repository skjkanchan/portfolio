import { placeholderEntries } from '../data/placeholderEntries'
import type { Entry } from '../types/entry'

export function getEntries(): Entry[] {
  return placeholderEntries
}

export function getEntryById(id: string): Entry | undefined {
  return placeholderEntries.find((entry) => entry.id === id)
}
