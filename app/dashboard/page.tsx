import DashboardAccessRouterClient from "./DashboardAccessRouterClient";
import NoProductsLogoutButton from "./NoProductsLogoutButton";

export const dynamic = "force-dynamic";

export default function Page() {
  return (
    <>
      <DashboardAccessRouterClient />
      <NoProductsLogoutButton />
    </>
  );
}
