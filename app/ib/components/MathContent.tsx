import Markdown from "react-markdown";
import remarkMath from "remark-math";
import remarkGfm from "remark-gfm";
import rehypeKatex from "rehype-katex";
import styles from "../questions.module.css";

export default function MathContent({ children }: { children: string }) {
  return <div className={styles.math}><Markdown remarkPlugins={[remarkGfm, remarkMath]}
    rehypePlugins={[[rehypeKatex, { trust: false, strict: false }]]} skipHtml
    components={{ table: ({ children }) => <div className={styles.tableScroll}><table>{children}</table></div> }}>
    {children}
  </Markdown></div>;
}
