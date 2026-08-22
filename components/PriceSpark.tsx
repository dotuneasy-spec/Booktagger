import { formatNaira } from "../lib/money";
import type { PricePoint } from "../lib/types";

export function PriceSpark({ points }: { points: PricePoint[] }) {
  if (points.length === 0) return null;
  const prices = points.map((point) => point.priceNgn);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const width = 560;
  const height = 140;
  const path = points
    .map((point, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - ((point.priceNgn - min) / Math.max(max - min, 1)) * (height - 16) - 8;
      return `${index === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <div className="card rounded-3xl p-5">
      <div className="flex items-end justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Lowest price, 6 weeks</p>
          <p className="mt-1 text-2xl font-semibold">{formatNaira(prices[prices.length - 1])}</p>
        </div>
        <p className="text-sm text-muted">
          Range {formatNaira(min)} – {formatNaira(max)}
        </p>
      </div>
      <svg className="mt-4 w-full" viewBox={`0 0 ${width} ${height}`}>
        <path d={path} fill="none" stroke="#0b7a43" strokeWidth="3" />
      </svg>
    </div>
  );
}
