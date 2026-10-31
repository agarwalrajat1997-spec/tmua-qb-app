import StudioEmbed from "@/src/tmua-studio/StudioEmbed";
import "@/src/tmua-studio/studio.css";

export const metadata = {
  title: "TMUA Study Studio | Thriving Scholars",
  robots: { index: false, follow: false },
};

export default function StudioPage() {
  return <StudioEmbed />;
}
