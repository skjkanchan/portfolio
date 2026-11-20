import { formatMonth, ONGOING } from '../utils/formatDate'

interface DateRangeProps {
  start: string
  end?: string
}

export default function DateRange({ start, end }: DateRangeProps) {
  return (
    <>
      <time dateTime={start}>{formatMonth(start)}</time>
      {end && (
        <>
          {' – '}
          {end === ONGOING ? 'Present' : <time dateTime={end}>{formatMonth(end)}</time>}
        </>
      )}
    </>
  )
}
