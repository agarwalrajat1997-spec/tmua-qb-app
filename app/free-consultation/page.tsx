import { redirect } from "next/navigation";

export const metadata = {
  title: "Find Your University Pathway | Thriving Scholars",
  description: "A personalised academic and university pathway for students and parents.",
};

const PATHWAY_APP =
  "https://thriving-scholars-pathway.raj1291241.chatgpt.site/free-consultation";

export default function FreeConsultationPage() {
  redirect(PATHWAY_APP);
}
