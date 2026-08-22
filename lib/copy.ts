export function conditionLabel(condition: string): string {
  if (condition === "uk-used") return "UK used";
  if (condition === "fairly-used") return "Fairly used";
  return "Brand new";
}

export function confidenceLabel(score: number): string {
  if (score >= 0.75) return "Strong match";
  if (score >= 0.55) return "Likely same product";
  if (score >= 0.4) return "Possible match";
  return "Loose match";
}
