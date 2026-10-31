import type { ReactNode } from "react";
import NoRightClick from "./NoRightClick";
export const dynamic = "force-dynamic";
export const revalidate = 0;
export default function Layout({ children }: { children: ReactNode }) {
  return <><NoRightClick />{children}</>;
}
