export function formatCurrency(amount: number | string): string {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'ZAR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numAmount);
}

export function formatCurrencyCompact(amount: number | string): string {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (numAmount >= 1000000) {
    return `R${(numAmount / 1000000).toFixed(1)}M`;
  } else if (numAmount >= 1000) {
    return `R${(numAmount / 1000).toFixed(0)}K`;
  }
  return `R${numAmount.toLocaleString('en-ZA')}`;
}

export function formatCurrencyShort(amount: number | string): string {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  return `R${numAmount.toLocaleString('en-ZA')}`;
}
