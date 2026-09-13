import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default function ESATLoginPage() {
  redirect("/login?next=/esat");
}
