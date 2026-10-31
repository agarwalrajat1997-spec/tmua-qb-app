import { useEffect, useRef, useState } from "react";
export function ThinkingBrand({ active = false }: { active?: boolean }) {
  const video = useRef<HTMLVideoElement>(null);
  const [motion, setMotion] = useState(false),
    [ready, setReady] = useState(false);
  useEffect(() => {
    const query = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    const update = () => setMotion(!query?.matches);
    update();
    query?.addEventListener("change", update);
    return () => query?.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    const v = video.current;
    if (!v) return;
    if (active && motion) {
      v.currentTime = 0;
      void v.play().catch(() => setReady(false));
    } else {
      v.pause();
      v.currentTime = 0;
    }
  }, [active, motion]);
  return (
    <div className="thinking-brand">
      <span
        className={`thinking-mascot ${active && motion && ready ? "is-thinking" : ""}`}
        aria-hidden="true"
      >
        <img src="/tmua-studio/brand/thinking.png" width="64" height="64" alt="" />
        {motion && (
          <video
            ref={video}
            width="64"
            height="64"
            muted
            loop
            playsInline
            preload="auto"
            onCanPlay={() => {
              setReady(true);
              if (active)
                void video.current?.play().catch(() => setReady(false));
            }}
            onError={() => setReady(false)}
          >
            <source src="/tmua-studio/brand/thinking.webm" type="video/webm" />
            <source src="/tmua-studio/brand/thinking.mp4" type="video/mp4" />
          </video>
        )}
      </span>
    </div>
  );
}
