import {
  januaryCheckout,
  JANUARY_OFFER_LIMIT,
  JANUARY_OFFER_PRICE,
  JANUARY_OFFER_SITTING,
  JANUARY_USUAL_PRICE,
} from "@/lib/january-offer";
import styles from "./JanuaryAccessOffer.module.css";

type Props = { programme: "tmua" | "esat"; existingStudent?: boolean };

export default function JanuaryAccessOffer({ programme, existingStudent = false }: Props) {
  const name = programme.toUpperCase();

  return (
    <section className={styles.offer} aria-label={`${name} ${JANUARY_OFFER_SITTING} access offer`}>
      <div className={styles.copy}>
        <span className={styles.eyebrow}>{JANUARY_OFFER_SITTING} preparation</span>
        <div className={styles.title}>
          Full {name} access <strong>£{JANUARY_OFFER_PRICE}</strong>
          <span className={styles.usual}><span className={styles.srOnly}>Standard price </span><s>£{JANUARY_USUAL_PRICE}</s></span>
        </div>
        <p>{name} Question Bank + Practice Test Series.</p>
        <p className={styles.terms}>First {JANUARY_OFFER_LIMIT} purchases across TMUA and ESAT combined. £30 discount at checkout while available.</p>
        {existingStudent ? <p className={styles.existing}>Offer shown for reference. Your existing access is unchanged.</p> : null}
      </div>
      <a className={styles.cta} href={januaryCheckout(programme)} target="_blank" rel="noopener noreferrer">
        View {name} offer <span aria-hidden="true">↗</span>
      </a>
    </section>
  );
}
