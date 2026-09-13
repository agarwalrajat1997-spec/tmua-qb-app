import AmcQuestionBankClient from "../../components/amc/AmcQuestionBankClient";

function getExamFromPaper(paper?: string) {
  const p = decodeURIComponent(paper || "")
    .toLowerCase()
    .replace(/\s+/g, "");

  if (p.includes("12")) {
    return {
      exam: "AMC12" as const,
      title: "AMC 12 Question Bank",
    };
  }

  if (p.includes("10")) {
    return {
      exam: "AMC10" as const,
      title: "AMC 10 Question Bank",
    };
  }

  return {
    exam: "AMC8" as const,
    title: "AMC 8 Question Bank",
  };
}

export default async function Page({
  searchParams,
}: {
  searchParams?: Promise<{ paper?: string }>;
}) {
  const params = searchParams ? await searchParams : {};
  const config = getExamFromPaper(params?.paper);

  return <AmcQuestionBankClient exam={config.exam} title={config.title} />;
}
