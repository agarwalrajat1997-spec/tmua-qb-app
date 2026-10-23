// Keep the public offer and login checkout destinations together. The promotion
// is limited across both programmes, not 50 purchases for each programme.
export const JANUARY_TMUA_CHECKOUT = "https://buy.stripe.com/5kQ14p2A0cJw6cj6fM0oM0e?prefilled_promo_code=JAN2027FIRST50";
export const JANUARY_ESAT_CHECKOUT = "https://buy.stripe.com/4gM28tdeE8tg58f9rY0oM0f?prefilled_promo_code=JAN2027FIRST50";
export const JANUARY_OFFER_PRICE = 119;
export const JANUARY_USUAL_PRICE = 149;
export const JANUARY_OFFER_LIMIT = 50;
export const JANUARY_OFFER_SITTING = "January 2027";

export function januaryCheckout(programme: "tmua" | "esat") {
  return programme === "esat" ? JANUARY_ESAT_CHECKOUT : JANUARY_TMUA_CHECKOUT;
}
