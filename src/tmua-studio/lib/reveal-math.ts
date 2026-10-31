// Reveal fully validated, fully typeset text. Maths is atomic: never show half-LaTeX.
// This changes presentation latency only; it does not claim to speed reasoning.
export function revealMath(node: HTMLElement, startAt = 0) {
  if (
    node.ownerDocument.defaultView?.matchMedia?.(
      "(prefers-reduced-motion: reduce)",
    ).matches
  )
    return;
  const doc = node.ownerDocument;
  const walker = doc.createTreeWalker(node, 4),
    texts: Text[] = [];
  while (walker.nextNode()) {
    const text = walker.currentNode as Text;
    if (
      text.textContent?.trim() &&
      !text.parentElement?.closest("mjx-container, .reveal-word")
    )
      texts.push(text);
  }
  for (const text of texts) {
    const fragment = doc.createDocumentFragment();
    for (const part of text.data.split(/(\s+)/)) {
      if (!part.trim()) {
        fragment.appendChild(doc.createTextNode(part));
        continue;
      }
      const span = doc.createElement("span");
      span.className = "reveal-word";
      span.textContent = part;
      fragment.appendChild(span);
    }
    text.replaceWith(fragment);
  }
  scheduleMathReveal(node, startAt);
}

export function scheduleMathReveal(node: HTMLElement, startAt = 0) {
  const pieces = node.querySelectorAll<HTMLElement>(
    ".reveal-word,mjx-container",
  );
  const wait = Math.max(
    0,
    startAt - (node.ownerDocument.defaultView?.performance.now() ?? 0),
  );
  pieces.forEach((part, i) => {
    part.classList.add("reveal-word");
    part.style.animationDelay = `${wait + Math.min(850, i * 24)}ms`;
  });
}
