import chunk01 from "@/lib/erasable-notepad-image/chunk-01";
import chunk02 from "@/lib/erasable-notepad-image/chunk-02";
import chunk03 from "@/lib/erasable-notepad-image/chunk-03";
import chunk04 from "@/lib/erasable-notepad-image/chunk-04";
import chunk05 from "@/lib/erasable-notepad-image/chunk-05";
import chunk06 from "@/lib/erasable-notepad-image/chunk-06";
import chunk07 from "@/lib/erasable-notepad-image/chunk-07";
import chunk08 from "@/lib/erasable-notepad-image/chunk-08";
import chunk09 from "@/lib/erasable-notepad-image/chunk-09";

const imageBase64 = [
  chunk01,
  chunk02,
  chunk03,
  chunk04,
  chunk05,
  chunk06,
  chunk07,
  chunk08,
  chunk09,
].join("");

export const ERASABLE_NOTEPAD_IMAGE_DATA_URL =
  `data:image/webp;base64,${imageBase64}`;

export const ERASABLE_NOTEPAD_IMAGE_WIDTH = 300;
export const ERASABLE_NOTEPAD_IMAGE_HEIGHT = 300;
