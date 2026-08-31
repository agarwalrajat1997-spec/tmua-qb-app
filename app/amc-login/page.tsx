import ExamMagicLinkLogin from "@/app/_components/ExamMagicLinkLogin";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "AMC Portal Login | Thriving Scholars",
};

export default function AMCLoginPage() {
  return (
    <ExamMagicLinkLogin
      exam="AMC"
      destination="/amc"
      uiMark="TS_AMC_LOGIN_V1"
    />
  );
}
