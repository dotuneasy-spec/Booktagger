import type { Metadata } from "next";
import { Fraunces, Manrope } from "next/font/google";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import "./globals.css";

const sans = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
});

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
});

export const metadata: Metadata = {
  title: {
    default: "Oja — Compare prices across Jumia, Konga, Jiji and more",
    template: "%s · Oja",
  },
  description:
    "A Nigerian price comparison engine that matches the same product across Jumia, Konga, Jiji, Slot, Kara and Pointek, then monetizes through affiliates, sponsored slots, and merchant intel.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html className={`${sans.variable} ${display.variable} h-full`} lang="en">
      <body className="min-h-full font-sans text-ink antialiased">
        <SiteHeader compact />
        <div className="flex min-h-full flex-col">
          <main className="mx-auto w-full max-w-6xl flex-1 px-4">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
