import ExamMagicLinkLogin from "@/app/_components/ExamMagicLinkLogin";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "SAT Portal Login | Thriving Scholars",
};

export default function SATLoginPage() {
  return (
    <ExamMagicLinkLogin
      exam="SAT"
      destination="/sat"
      uiMark="TS_SAT_LOGIN_V1"
    />
  );
}
