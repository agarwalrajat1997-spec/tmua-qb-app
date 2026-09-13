"use client";

import { useEffect } from "react";

function isValidImageSrc(srcAttr: string | null) {
  const src = String(srcAttr || "").trim();

  if (!src) return false;

  const fakeValues = /^(diagram|null|undefined|none|n\/a|question image)$/i;
  if (fakeValues.test(src)) return false;

  if (/^data:image\//i.test(src)) return true;
  if (/^https?:\/\/.+\.(png|jpg|jpeg|webp|gif|svg)(\?.*)?$/i.test(src)) return true;
  if (/^\/.+\.(png|jpg|jpeg|webp|gif|svg)(\?.*)?$/i.test(src)) return true;

  return false;
}

function hideImageAndEmptyWrapper(img: HTMLImageElement) {
  img.style.display = "none";

  const wrapper = img.closest(
    ".question-image-wrap, .question-image-container, .question-assets, figure, p, div"
  );

  if (wrapper instanceof HTMLElement) {
    const text = (wrapper.textContent || "").trim();
    const imageCount = wrapper.querySelectorAll("img").length;

    // Hide wrapper only when it is just the broken/empty question-image block.
    if (imageCount <= 1 && (!text || /^question image$/i.test(text))) {
      wrapper.style.display = "none";
    }
  }
}

function scanQuestionImages() {
  const imgs = document.querySelectorAll<HTMLImageElement>(
    'img[alt="Question image"], img[alt="question image"]'
  );

  imgs.forEach((img) => {
    const srcAttr = img.getAttribute("src");

    if (!isValidImageSrc(srcAttr)) {
      hideImageAndEmptyWrapper(img);
      return;
    }

    img.addEventListener(
      "error",
      () => {
        hideImageAndEmptyWrapper(img);
      },
      { once: true }
    );
  });
}

export default function QuestionImageGuard() {
  useEffect(() => {
    scanQuestionImages();

    const observer = new MutationObserver(() => {
      scanQuestionImages();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => observer.disconnect();
  }, []);

  return null;
}
