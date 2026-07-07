import { redirect } from "next/navigation";

export default async function Page({
  searchParams,
}: {
  searchParams?: Promise<{ paper?: string }>;
}) {
  const params = searchParams ? await searchParams : {};
  const rawPaper = decodeURIComponent(params?.paper || "AMC 8");
  const compact = rawPaper.toLowerCase().replace(/\s+/g, "");

  if (compact.includes("12")) {
    redirect("/amc-12-question-bank/index.html");
  }

  if (compact.includes("10")) {
    redirect("/amc-10-question-bank/index.html");
  }

  redirect("/amc-8-question-bank/index.html");
}
