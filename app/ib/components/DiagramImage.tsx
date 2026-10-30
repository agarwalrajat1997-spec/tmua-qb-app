"use client";

/** Only validated image sources reach this component through authenticated server pages. */
export default function DiagramImage({ src, fallback, caption }: { src: string; fallback?: string; caption: string }) {
  // The embedded SVG remains available if an optional CDN image fails to load.
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={src} alt={caption} loading="lazy" decoding="async" referrerPolicy="no-referrer" onError={event => {
    if (fallback && event.currentTarget.src !== fallback) event.currentTarget.src = fallback;
  }} />;
}
