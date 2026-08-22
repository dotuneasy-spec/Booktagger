import { notFound } from "next/navigation";
import { CATEGORIES } from "../../../data/catalog";
import { ProductCard } from "../../../components/ProductCard";
import { searchProducts } from "../../../lib/search";
import type { CategoryId } from "../../../lib/types";

export function generateStaticParams() {
  return CATEGORIES.map((category) => ({ slug: category.id }));
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const category = CATEGORIES.find((item) => item.id === slug);
  if (!category) notFound();
  const result = searchProducts("", { category: slug as CategoryId });

  return (
    <div className="py-8">
      <p className="text-xs uppercase tracking-[0.16em] text-muted">Category</p>
      <h1 className="display mt-2 text-4xl">{category.name}</h1>
      <p className="mt-2 text-muted">{category.blurb}</p>
      <div className="mt-8 space-y-4">
        {result.hits.map((hit) => (
          <ProductCard hit={hit} key={hit.product.id} source="category" />
        ))}
      </div>
    </div>
  );
}
