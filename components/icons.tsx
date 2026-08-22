import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

export function SearchIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.2-3.2" />
    </svg>
  );
}

export function ArrowRightIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function TagIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M3 12V5a2 2 0 0 1 2-2h7l9 9-9 9-9-9Z" />
      <circle cx="8.5" cy="8.5" r="1.2" fill="currentColor" />
    </svg>
  );
}

export function BoltIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M13 2 4 14h7l-1 8 10-14h-7l0-6Z" />
    </svg>
  );
}

export function ShieldIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M12 3 5 6v6c0 5 3.2 8.4 7 9 3.8-.6 7-4 7-9V6l-7-3Z" />
    </svg>
  );
}

export function WhatsAppIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M12.04 3C7.15 3 3.2 6.9 3.2 11.74c0 1.54.4 3.03 1.16 4.35L3 21l5.06-1.32a9 9 0 0 0 3.98.92h.01c4.89 0 8.84-3.9 8.84-8.74S16.93 3 12.04 3Zm5.13 12.36c-.22.61-1.28 1.16-1.78 1.23-.46.07-1.03.1-1.66-.1-.38-.13-.86-.27-1.49-.53-2.62-1.13-4.33-3.76-4.46-3.94-.13-.17-1.07-1.42-1.07-2.71 0-1.29.68-1.92.92-2.18.22-.25.49-.32.65-.32h.47c.15 0 .35-.05.55.42.22.51.73 1.78.8 1.91.06.13.1.28.02.46-.08.17-.12.28-.24.43l-.36.42c-.12.13-.24.27-.1.52.13.25.6 1 .1 1.73.87 1.25 1.8 1.73 2.08 1.92.27.18.43.16.6-.08.16-.25.7-.81.88-1.09.18-.28.37-.23.62-.13.25.1 1.57.74 1.84.88.27.13.45.2.52.31.06.12.06.68-.16 1.29Z" />
    </svg>
  );
}
