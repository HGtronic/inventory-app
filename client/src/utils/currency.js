// Currency conversion utility
// USD to JPY exchange rate (approximate)
const USD_TO_JPY = 150

export function formatCurrency(amount, currency = 'USD') {
  if (currency === 'JPY') {
    const yenAmount = Math.round(amount * USD_TO_JPY)
    return `¥${yenAmount.toLocaleString('ja-JP')}`
  }
  // Default USD
  return `$${amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export function formatCurrencyWithDecimals(amount, currency = 'USD', decimals = 0) {
  if (currency === 'JPY') {
    // Callers pass decimals > 0 for exact amounts (unit prices, line totals). Converted
    // cent prices can land on fractional yen (14.25 USD -> 2137.5 JPY); rounding each one
    // on its own would make "100 x ¥2,138" sit next to a ¥213,750 line total. So keep up to
    // `decimals` fraction digits, but show none when the yen amount is whole.
    return `¥${(amount * USD_TO_JPY).toLocaleString('ja-JP', { minimumFractionDigits: 0, maximumFractionDigits: decimals })}`
  }
  // Default USD
  return `$${amount.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
}

// Short form for chart axis ticks: $25K / $1.2M in USD, ¥375万 / ¥5.6億 in JPY.
// Input is always USD. Uses decimal compact notation (not style: 'currency') and prepends the
// same symbols as the formatters above, because Intl's ja-JP currency style emits the
// full-width ￥ (U+FFE5) while the rest of the app uses ¥ (U+00A5).
export function formatCurrencyCompact(amountUsd, currency = 'USD') {
  const isJpy = currency === 'JPY'
  const value = isJpy ? Math.round(amountUsd * USD_TO_JPY) : amountUsd
  const compact = new Intl.NumberFormat(isJpy ? 'ja-JP' : 'en-US', {
    notation: 'compact',
    maximumFractionDigits: 1
  }).format(Math.abs(value))
  // Sign goes before the symbol ("-$5K"), matching how a negative amount reads
  return `${value < 0 ? '-' : ''}${isJpy ? '¥' : '$'}${compact}`
}

export function convertAmount(amount, currency = 'USD') {
  if (currency === 'JPY') {
    return Math.round(amount * USD_TO_JPY)
  }
  return amount
}

// Inverse of convertAmount, for amounts the user typed in the display currency
// (JPY -> USD is / 150). Deliberately NOT rounded: rounding to cents would turn
// 1,000 yen into $6.67, which displays back as 1,000.5 yen. Callers that need a
// tidy number for an input field round it themselves.
export function convertToUsd(amount, currency = 'USD') {
  if (currency === 'JPY') {
    return amount / USD_TO_JPY
  }
  return amount
}

// Unrounded counterpart of convertAmount (which rounds to whole yen): USD -> display
// currency without losing the fractional yen (14.25 USD -> 2137.5 JPY). Used to carry
// a typed amount across a currency switch, so it can come back to the same USD value.
export function convertFromUsd(amount, currency = 'USD') {
  if (currency === 'JPY') {
    return amount * USD_TO_JPY
  }
  return amount
}
