"use client";

/** Only validated image sources reach this component through authenticated server pages. */
export default function DiagramImage({ src, fallback, caption }: { src: string; fallback?: string; caption: string }) {
  // Embedded SVG or a byte-identical local raster remains available if the CDN fails.
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={src} alt={caption} loading="lazy" decoding="async" referrerPolicy="no-referrer" onError={event => {
    const image = event.currentTarget;
    if (fallback && image.src !== new URL(fallback, image.baseURI).href) image.src = fallback;
  }} />;
}
