# IB free trials

The public /api/public/ib-free-trial endpoint shares input validation, CORS, distributed email cooldown and delivery status handling with TMUA/ESAT. It grants ib-portal for exactly 48 hours through the two-argument grant_ib_free_trial function. Each normalized email can claim one lifetime free trial across TMUA, ESAT and IB, including historical trials and the legacy TMUA grant path. Existing longer/permanent paid grants are preserved.

The shared database trial history is authoritative. A repeated request for an existing active trial in the same programme returns its original timestamps; it never starts another 48 hours. A used email requesting a new trial, including in a different programme, receives trial_already_used and HTTP 409. That response stops before email delivery or cooldown metadata updates. Existing active trials retain their original expiry, and paid users can continue to sign in normally. Different email accounts remain distinct; names are not used to merge accounts or deny trials.

ib_access_state runs with the caller privileges and RLS. Pages and both Physics mock APIs check access after verified authentication. New accounts without entitlement reach /ib-access; expired trials do too. Database failures fail closed with a retry route.

Before this launch, all authenticated accounts could open IB. ib_legacy_access snapshots those existing account IDs to preserve that access without opening future signups indefinitely. Explicit revoked IB entitlements override the legacy allowance. New students need a trial or approved ib-portal entitlement. Old accounts that request a trial retain their legacy access; the recorded trial still cannot restart.

The existing shared EmailJS template template_whjida8 receives IB names, links, features and an IB screenshot. The template editor needs sign-in to remove/conditionally hide images. No new template is required. Supabase sends the secure login link separately. Provider success means accepted for delivery, not proof of inbox receipt.

Paid checkout was inactive at launch and remains inactive. Upgrade enquiries go to WhatsApp. stripe_grant_student_access accepts ib-portal for future/manual paid fulfilment; no Stripe mapping or charges were created.

Validation: isolated route, mail, repeat/cooldown and guard tests; all three endpoints reject a consumed-trial RPC result without sending email or changing cooldown metadata. Cross-portal rejection fixtures exercise the API contract separately from the database enforcement. Database transactions are rolled back after exact-duration/repeat/expiry/paid-upgrade/RLS tests. No student records are changed by those tests.
