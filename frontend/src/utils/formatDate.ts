const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]

export const ONGOING = 'present'

/** Formats "2025-06" as "Jun 2025". Avoids Date, which can shift months across time zones. */
export function formatMonth(yearMonth: string): string {
  const [year, month] = yearMonth.split('-')
  return `${MONTHS[Number(month) - 1]} ${year}`
}
