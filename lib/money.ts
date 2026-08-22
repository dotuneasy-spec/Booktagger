export function formatNaira(amount: number): string {
  return new Intl.NumberFormat("en-NG", {
    style: "currency",
    currency: "NGN",
    maximumFractionDigits: 0,
  }).format(Math.round(amount));
}

export function formatCompactNaira(amount: number): string {
  if (amount >= 1_000_000) {
    return `₦${(amount / 1_000_000).toFixed(amount >= 10_000_000 ? 0 : 1)}m`;
  }
  if (amount >= 1_000) {
    return `₦${Math.round(amount / 1_000)}k`;
  }
  return formatNaira(amount);
}

export function savingsPercent(low: number, high: number): number {
  if (high <= 0 || low >= high) return 0;
  return Math.round(((high - low) / high) * 100);
}
