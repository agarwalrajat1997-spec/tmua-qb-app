import assert from "node:assert/strict";
import {
  decodeLoginDestination,
  safeLoginDestination,
} from "../lib/auth/login-destination.ts";

const accepted = [
  "/dashboard",
  "/dashboard?view=tmua",
  "/esat",
  "/ib",
  "/ib?subject=physics-hl&view=mocks",
  "/ib/question-bank/functions?difficulty=hard&calculator=no&page=2",
  "/ib/questions/ib-aa-fn-001",
  "/ib/mark-scheme/ib-aa-fn-001",
  "/esat-practice-tests/tests/esat-mock-01/index.html",
  "/tmua-question-bank?page=2",
];

for (const destination of accepted) {
  assert.equal(safeLoginDestination(destination), destination);
  assert.equal(decodeLoginDestination(destination), destination);
  assert.equal(decodeLoginDestination(encodeURIComponent(destination)), destination);
}

const rejected = [
  "https://evil.example/esat",
  "//evil.example/esat",
  "/auth/callback",
  "/login?next=/esat",
  "/unknown",
  "/ib-login",
  "/ib-evil",
  "/ib/../auth/callback",
  "/esat\\..\\dashboard",
];

for (const destination of rejected) {
  assert.equal(safeLoginDestination(destination), "/dashboard");
}

assert.equal(safeLoginDestination(null), "/dashboard");
assert.equal(decodeLoginDestination(undefined), null);

console.log("Login destination routing verification passed.");
