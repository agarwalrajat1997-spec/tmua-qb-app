import { json, requireSATAccess } from "../_server";

const DEFAULT_ADMIN_EMAIL = "agarwalrajat1997@gmail.com";

function configuredAdminEmails() {
  return new Set(
    [DEFAULT_ADMIN_EMAIL, ...(process.env.SAT_QB_ADMIN_EMAILS || "").split(",")]
      .map((email) => email.trim().toLowerCase())
      .filter(Boolean)
  );
}

export async function requireSATAdmin() {
  const access = await requireSATAccess();
  if (!access.ok) return access;

  const email = access.email.toLowerCase();
  if (!configuredAdminEmails().has(email)) {
    return {
      ok: false as const,
      response: json({ ok: false, error: "Administrator access required" }, 403),
    };
  }

  return {
    ok: true as const,
    user: access.user,
    email,
  };
}
