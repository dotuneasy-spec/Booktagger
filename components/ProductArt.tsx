type ProductArtProps = {
  title: string;
  brand: string;
  hue: number;
  className?: string;
};

export function ProductArt({ title, brand, hue, className = "" }: ProductArtProps) {
  const initials = brand.slice(0, 2).toUpperCase();
  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={{
        background: `linear-gradient(145deg, hsl(${hue} 42% 28%), hsl(${hue + 28} 48% 46%))`,
      }}
    >
      <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "radial-gradient(circle at 20% 20%, white, transparent 40%)" }} />
      <div className="relative flex h-full flex-col justify-between p-4 text-white">
        <span className="text-xs tracking-[0.18em] uppercase opacity-80">{brand}</span>
        <div>
          <div className="display text-4xl leading-none">{initials}</div>
          <p className="mt-2 line-clamp-2 text-sm text-white/85">{title}</p>
        </div>
      </div>
    </div>
  );
}
