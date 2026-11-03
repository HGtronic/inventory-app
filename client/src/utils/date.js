// `new Date('2025-09-01')` parses a date-only string as UTC midnight, so in time zones
// west of UTC the local getters (getDate, toLocaleDateString, ...) report the previous day.
// Plain YYYY-MM-DD strings are calendar dates with no time zone, so build them as local
// midnight instead. Anything else (full ISO datetimes, Date objects, timestamps) is
// passed to the Date constructor unchanged.
export function parseLocalDate(value) {
  if (typeof value === 'string') {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
    if (match) {
      return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
    }
  }
  return new Date(value)
}
