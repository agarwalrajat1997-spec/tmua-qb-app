import { MathText } from "./MathHtml";
import type { StudentMethod } from "../lib/student-content";

export function UsefulMethods({ methods }: { methods: StudentMethod[] }) {
  if (!methods.length) return null;
  return <section className="student-methods" aria-label="Useful methods">
    {methods.map((method) => <details className="guide-trick" key={method.id}>
      <summary>{method.title}{method.title !== method.label ? ` · ${method.label}` : ""}</summary>
      <MathText text={method.explanation} inline={false} />
      {method.conditions.length > 0 && <details>
        <summary>When this works</summary>
        {method.conditions.map((condition, index) => <MathText key={index} text={condition} inline={false} />)}
      </details>}
      {method.limitations.length > 0 && <details>
        <summary>Take care</summary>
        {method.limitations.map((limitation, index) => <MathText key={index} text={limitation} inline={false} />)}
      </details>}
    </details>)}
  </section>;
}
