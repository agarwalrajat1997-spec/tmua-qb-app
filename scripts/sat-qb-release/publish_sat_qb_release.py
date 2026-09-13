#!/usr/bin/env python3
"""Safely stage and publish the reviewed 595-question SAT Question Bank release."""

from __future__ import annotations

import argparse
import base64
import copy
import datetime as dt
import hashlib
import json
import mimetypes
import os
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

EXPECTED_EXISTING = 495
EXPECTED_AUTO_PASS = 230
EXPECTED_CORRECTED = 265
EXPECTED_NEW = 100
EXPECTED_FINAL = 595
EXPECTED_BATCH_COUNTS = [50, 50, 50, 50, 50, 15]
EXPECTED_EMBEDDED_IMAGES = 24
CONFIRMATION = "PUBLISH-595-SAT-QUESTIONS"
QUESTION_COLUMNS = {
    "qid",
    "display_order",
    "paper_question_number",
    "kind",
    "paper",
    "topic",
    "subtopic",
    "difficulty",
    "tags",
    "prompt_html",
    "options",
    "answer",
    "solution_html",
    "page_assets",
    "answer_verified",
    "shortcut_available",
    "nice_tip_html",
    "checker_flags",
    "source_json",
    "is_active",
    "updated_at",
}


class ReleaseError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ReleaseError(message)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Required file is missing: {path}")
    except json.JSONDecodeError as error:
        fail(f"Invalid JSON in {path.name}: {error}")


def atomic_write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def ordered_qid_md5(qids: set[str] | list[str]) -> str:
    return hashlib.md5("\n".join(sorted(qids)).encode("utf-8")).hexdigest()


def require_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        fail(f"Missing {label}")
    return text


def require_question_shape(question: dict[str, Any], label: str) -> None:
    qid = require_text(question.get("qid"), f"{label}.qid")
    require_text(question.get("paper"), f"{qid}.paper")
    require_text(question.get("prompt_html"), f"{qid}.prompt_html")
    answer = require_text(question.get("answer"), f"{qid}.answer")
    if answer not in {"A", "B", "C", "D"}:
        fail(f"{qid} has unsupported answer {answer!r}")
    options = question.get("options")
    if not isinstance(options, list) or len(options) != 4:
        fail(f"{qid} must have exactly four options")
    if {str(option.get("key") or "").strip() for option in options} != {"A", "B", "C", "D"}:
        fail(f"{qid} option keys must be A, B, C, D")
    if not isinstance(question.get("tags", []), list):
        fail(f"{qid}.tags must be an array")
    if not isinstance(question.get("page_assets", []), list):
        fail(f"{qid}.page_assets must be an array")
    if not isinstance(question.get("checker_flags", {}), dict):
        fail(f"{qid}.checker_flags must be an object")
    if not isinstance(question.get("source_json", {}), dict):
        fail(f"{qid}.source_json must be an object")


class SupabaseRest:
    def __init__(self, project_ref: str, service_role_key: str) -> None:
        self.base = f"https://{project_ref}.supabase.co/rest/v1"
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
        }

    def request(
        self,
        method: str,
        path: str,
        payload: Any | None = None,
        prefer: str | None = None,
    ) -> tuple[Any, dict[str, str]]:
        body = None
        headers = dict(self.headers)
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if prefer:
            headers["Prefer"] = prefer
        request = urllib.request.Request(self.base + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
                value = json.loads(raw) if raw else None
                return value, dict(response.headers.items())
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            fail(f"Supabase {method} {path} failed ({error.code}): {details[:2000]}")
        except urllib.error.URLError as error:
            fail(f"Supabase {method} {path} failed: {error}")

    def fetch_all_questions(self) -> list[dict[str, Any]]:
        value, _ = self.request(
            "GET",
            "/sat_qb_questions?select=*&order=qid.asc&limit=1000",
        )
        if not isinstance(value, list):
            fail("Supabase returned an invalid question list")
        return value

    def upsert_questions(self, questions: list[dict[str, Any]], chunk_size: int = 25) -> None:
        for start in range(0, len(questions), chunk_size):
            chunk = questions[start : start + chunk_size]
            self.request(
                "POST",
                "/sat_qb_questions?on_conflict=qid",
                chunk,
                "resolution=merge-duplicates,return=minimal,missing=default",
            )
            print(f"Staged {min(start + len(chunk), len(questions))}/{len(questions)} records")

    def publish(self, expected_hash: str) -> dict[str, Any]:
        value, _ = self.request(
            "POST",
            "/rpc/publish_sat_qb_release",
            {"p_expected_count": EXPECTED_FINAL, "p_expected_qid_md5": expected_hash},
        )
        if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
            fail(f"Publication RPC returned an invalid result: {value!r}")
        return value[0]


def load_corrected(input_dir: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    corrected: list[dict[str, Any]] = []
    review_by_qid: dict[str, Any] = {}
    batch_receipts: list[dict[str, Any]] = []

    for batch_number, expected_count in enumerate(EXPECTED_BATCH_COUNTS, start=1):
        path = input_dir / f"sat-qb-manual-batch-{batch_number:02d}-of-06-reviewed.json"
        data = read_json(path)
        if not isinstance(data, dict):
            fail(f"{path.name} must contain a JSON object")
        candidates = data.get("import_candidates")
        reviews = data.get("questions")
        if not isinstance(candidates, list) or len(candidates) != expected_count:
            fail(f"{path.name} must contain {expected_count} import_candidates")
        if not isinstance(reviews, list) or len(reviews) != expected_count:
            fail(f"{path.name} must contain {expected_count} reviewed questions")

        for item in reviews:
            qid = require_text(item.get("qid"), f"{path.name} review qid")
            manual = item.get("manual_review")
            if not isinstance(manual, dict) or manual.get("decision") != "correct":
                fail(f"{qid} is not marked as a completed correction")
            review_by_qid[qid] = manual

        for item in candidates:
            if not isinstance(item, dict):
                fail(f"{path.name} has a non-object import candidate")
            require_question_shape(item, path.name)
            corrected.append(copy.deepcopy(item))

        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        batch_receipts.append({"file": path.name, "count": expected_count, "sha256": digest})

    qids = [question["qid"] for question in corrected]
    if len(corrected) != EXPECTED_CORRECTED or len(set(qids)) != EXPECTED_CORRECTED:
        fail("The six corrected batches must contain 265 unique qids")
    if set(qids) != set(review_by_qid):
        fail("Corrected import candidates do not match the completed manual reviews")

    return corrected, {"batches": batch_receipts, "qid_md5": ordered_qid_md5(set(qids))}


def load_new_questions(input_dir: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = input_dir / "sat-hard-original-100-verified.json"
    data = read_json(path)
    if not isinstance(data, dict):
        fail(f"{path.name} must contain a JSON object")
    candidates = data.get("import_candidates")
    if not isinstance(candidates, list) or len(candidates) != EXPECTED_NEW:
        fail(f"{path.name} must contain 100 import_candidates")
    questions = [copy.deepcopy(item) for item in candidates]
    for item in questions:
        if not isinstance(item, dict):
            fail(f"{path.name} has a non-object import candidate")
        require_question_shape(item, path.name)
    qids = [question["qid"] for question in questions]
    if len(set(qids)) != EXPECTED_NEW:
        fail("The hard SAT set must contain 100 unique qids")
    return questions, {
        "file": path.name,
        "count": EXPECTED_NEW,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "qid_md5": ordered_qid_md5(set(qids)),
    }


DATA_URI = re.compile(r"^data:(image/(?:png|jpeg|jpg|webp));base64,(.+)$", re.IGNORECASE | re.DOTALL)


def image_locations(question: dict[str, Any]):
    for asset in question.get("page_assets", []):
        if isinstance(asset, dict) and isinstance(asset.get("url"), str):
            yield asset, "url"
    for option in question.get("options", []):
        if isinstance(option, dict) and isinstance(option.get("image_url"), str):
            yield option, "image_url"


def upload_embedded_images(
    questions: list[dict[str, Any]],
    account_id: str,
    access_key: str,
    secret_key: str,
    bucket: str,
    prefix: str,
    public_base_url: str,
) -> dict[str, Any]:
    import boto3
    from botocore.exceptions import ClientError

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    uploaded: dict[str, dict[str, Any]] = {}
    placements = 0

    for question in questions:
        for container, key_name in image_locations(question):
            source = container.get(key_name)
            if not isinstance(source, str) or not source.startswith("data:image/"):
                continue
            match = DATA_URI.match(source)
            if not match:
                fail(f"{question['qid']} has an unsupported embedded image")
            mime = match.group(1).lower().replace("jpg", "jpeg")
            try:
                body = base64.b64decode(match.group(2), validate=True)
            except ValueError as error:
                fail(f"{question['qid']} has invalid base64 image data: {error}")
            digest = hashlib.sha256(body).hexdigest()
            extension = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}.get(mime)
            if not extension:
                extension = mimetypes.guess_extension(mime, strict=False) or ".bin"
                extension = extension.lstrip(".")
            object_key = f"{prefix.strip('/')}/assets/{digest[:2]}/{digest}.{extension}"
            public_url = f"{public_base_url.rstrip('/')}/{object_key}"

            if digest not in uploaded:
                exists = False
                try:
                    head = client.head_object(Bucket=bucket, Key=object_key)
                    exists = int(head.get("ContentLength", -1)) == len(body)
                except ClientError as error:
                    status = int(error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0))
                    code = str(error.response.get("Error", {}).get("Code", ""))
                    if status not in {403, 404} and code not in {"404", "NoSuchKey", "NotFound"}:
                        raise

                if not exists:
                    client.put_object(
                        Bucket=bucket,
                        Key=object_key,
                        Body=body,
                        ContentType=mime,
                        CacheControl="public, max-age=31536000, immutable",
                        Metadata={"sha256": digest},
                    )
                    action = "uploaded"
                else:
                    action = "exists"

                uploaded[digest] = {
                    "sha256": digest,
                    "bytes": len(body),
                    "content_type": mime,
                    "key": object_key,
                    "url": public_url,
                    "action": action,
                }
                print(f"Image {len(uploaded)}/{EXPECTED_EMBEDDED_IMAGES}: {digest[:12]} {action}")

            container[key_name] = public_url
            container["image_asset_sha256"] = digest
            placements += 1

    if placements != EXPECTED_EMBEDDED_IMAGES or len(uploaded) != EXPECTED_EMBEDDED_IMAGES:
        fail(
            f"Expected 24 unique embedded-image placements, found {placements} placements "
            f"and {len(uploaded)} assets"
        )
    for asset in uploaded.values():
        request = urllib.request.Request(
            asset["url"],
            headers={"Range": "bytes=0-0", "User-Agent": "ThrivingScholars-SAT-QB-Release/1.0"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = str(response.headers.get("Content-Type") or "").lower()
                if response.status not in {200, 206} or not content_type.startswith("image/"):
                    fail(f"Public R2 verification failed for {asset['url']}: {response.status} {content_type}")
                response.read(1)
        except urllib.error.URLError as error:
            fail(f"Public R2 verification failed for {asset['url']}: {error}")

    print(f"Verified {len(uploaded)} public immutable image URLs")
    return {"placements": placements, "assets": list(uploaded.values())}


def prepare_records(
    corrected: list[dict[str, Any]],
    new_questions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    published_at = utc_now()

    for question in corrected:
        flags = question.setdefault("checker_flags", {})
        flags["human_review_status"] = "approved"
        flags["publication"] = {
            "release": "sat-qb-595-v1",
            "approved_for_publication": True,
            "approved_at": published_at,
            "basis": "manual correction batch",
        }
        question["answer_verified"] = True
        question["is_active"] = False
        question["updated_at"] = published_at

    for index, question in enumerate(new_questions, start=1):
        question["display_order"] = EXPECTED_EXISTING + index
        flags = question.setdefault("checker_flags", {})
        flags["human_review_status"] = "publication_approved"
        flags["publication"] = {
            "release": "sat-qb-595-v1",
            "approved_for_publication": True,
            "approved_at": published_at,
            "basis": "verified original hard SAT set",
        }
        question["answer_verified"] = True
        question["is_active"] = False
        question["updated_at"] = published_at

    def database_shape(question: dict[str, Any]) -> dict[str, Any]:
        shaped = {key: value for key, value in question.items() if key in QUESTION_COLUMNS}
        require_question_shape(shaped, question.get("qid", "question"))
        return shaped

    return [database_shape(q) for q in corrected], [database_shape(q) for q in new_questions]


def validate_remote_existing(
    remote: list[dict[str, Any]], corrected: list[dict[str, Any]], new_questions: list[dict[str, Any]]
) -> dict[str, Any]:
    if len(remote) != EXPECTED_EXISTING:
        fail(f"Expected 495 staged questions in Supabase, found {len(remote)}")
    existing_qids = {require_text(row.get("qid"), "remote qid") for row in remote}
    if len(existing_qids) != EXPECTED_EXISTING:
        fail("Supabase does not contain 495 unique existing qids")

    status_qids: dict[str, set[str]] = {"pass": set(), "needs_review": set(), "reject": set()}
    active = 0
    for row in remote:
        active += int(bool(row.get("is_active")))
        flags = row.get("checker_flags") if isinstance(row.get("checker_flags"), dict) else {}
        ai = flags.get("ai") if isinstance(flags.get("ai"), dict) else {}
        status = str(ai.get("status") or "")
        if status in status_qids:
            status_qids[status].add(row["qid"])

    if active != 0:
        fail(f"Preflight expected zero active SAT questions, found {active}")
    if len(status_qids["pass"]) != EXPECTED_AUTO_PASS:
        fail(f"Expected 230 automatically passed questions, found {len(status_qids['pass'])}")
    nonpass = status_qids["needs_review"] | status_qids["reject"]
    corrected_qids = {q["qid"] for q in corrected}
    if nonpass != corrected_qids:
        fail(
            "The 265 corrected qids do not exactly match the Supabase needs_review/reject set "
            f"(local {ordered_qid_md5(corrected_qids)}, remote {ordered_qid_md5(nonpass)})"
        )
    new_qids = {q["qid"] for q in new_questions}
    if existing_qids & new_qids:
        fail("The new 100-question set overlaps an existing Supabase qid")

    return {
        "existing_count": len(remote),
        "existing_qid_md5": ordered_qid_md5(existing_qids),
        "auto_pass_count": len(status_qids["pass"]),
        "corrected_count": len(nonpass),
        "corrected_qid_md5": ordered_qid_md5(nonpass),
        "expected_final_qid_md5": ordered_qid_md5(existing_qids | new_qids),
    }


def validate_no_embedded_images(questions: list[dict[str, Any]]) -> None:
    encoded = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
    if "data:image/" in encoded:
        fail("Embedded image data remains after R2 upload")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=pathlib.Path)
    parser.add_argument("--project-ref", default="pnkzxzigpkvhlmhsmzdd")
    parser.add_argument("--r2-prefix", default="sat/question-bank/v2/original-hard-100")
    parser.add_argument("--r2-public-base-url", default="https://media.thrivingscholars.com")
    parser.add_argument("--receipt", required=True, type=pathlib.Path)
    parser.add_argument("--backup", required=True, type=pathlib.Path)
    return parser.parse_args()


def required_env(name: str) -> str:
    return require_text(os.environ.get(name), f"environment variable {name}")


def run() -> None:
    args = parse_args()
    if os.environ.get("SAT_QB_PUBLISH_CONFIRM") != CONFIRMATION:
        fail(f"Set SAT_QB_PUBLISH_CONFIRM to {CONFIRMATION!r} to authorize publication")

    print("1/8 - Load and verify the six corrected batches")
    corrected, corrected_receipt = load_corrected(args.input_dir)
    print(f"Verified {len(corrected)} corrected questions")

    print("2/8 - Load and verify the original hard 100")
    new_questions, new_receipt = load_new_questions(args.input_dir)
    print(f"Verified {len(new_questions)} new questions")

    supabase = SupabaseRest(args.project_ref, required_env("SUPABASE_SERVICE_ROLE_KEY"))

    print("3/8 - Verify and back up the 495 inactive Supabase records")
    remote_before = supabase.fetch_all_questions()
    remote_receipt = validate_remote_existing(remote_before, corrected, new_questions)
    atomic_write_json(
        args.backup,
        {
            "schema_version": 1,
            "created_at": utc_now(),
            "project_ref": args.project_ref,
            "table": "public.sat_qb_questions",
            "questions": remote_before,
        },
    )
    print(f"Backup written: {args.backup}")

    print("4/8 - Upload and replace 24 embedded images in Cloudflare R2")
    media_receipt = upload_embedded_images(
        new_questions,
        required_env("R2_ACCOUNT_ID"),
        required_env("R2_ACCESS_KEY_ID"),
        required_env("R2_SECRET_ACCESS_KEY"),
        required_env("R2_BUCKET"),
        args.r2_prefix,
        args.r2_public_base_url,
    )
    validate_no_embedded_images(new_questions)

    print("5/8 - Prepare inactive corrected and new records")
    corrected_records, new_records = prepare_records(corrected, new_questions)
    validate_no_embedded_images(corrected_records + new_records)

    print("6/8 - Stage 265 corrections and 100 additions as inactive")
    supabase.upsert_questions(corrected_records)
    supabase.upsert_questions(new_records)

    print("7/8 - Re-read and validate the exact 595-question corpus")
    staged = supabase.fetch_all_questions()
    staged_qids = {row["qid"] for row in staged}
    if len(staged) != EXPECTED_FINAL or len(staged_qids) != EXPECTED_FINAL:
        fail(f"Expected exactly 595 staged unique records, found {len(staged)} / {len(staged_qids)}")
    expected_hash = remote_receipt["expected_final_qid_md5"]
    actual_hash = ordered_qid_md5(staged_qids)
    if actual_hash != expected_hash:
        fail(f"Final qid hash mismatch: expected {expected_hash}, found {actual_hash}")
    validate_no_embedded_images(staged)

    print("8/8 - Atomically verify, mark verified, and publish all 595")
    publish_result = supabase.publish(expected_hash)
    if (
        int(publish_result.get("published_count", 0)) != EXPECTED_FINAL
        or int(publish_result.get("active_count", 0)) != EXPECTED_FINAL
        or int(publish_result.get("answer_verified_count", 0)) != EXPECTED_FINAL
        or publish_result.get("qid_md5") != expected_hash
    ):
        fail(f"Unexpected publication receipt: {publish_result}")

    final_rows = supabase.fetch_all_questions()
    final_active = sum(bool(row.get("is_active")) for row in final_rows)
    final_verified = sum(bool(row.get("answer_verified")) for row in final_rows)
    if len(final_rows) != EXPECTED_FINAL or final_active != EXPECTED_FINAL or final_verified != EXPECTED_FINAL:
        fail("Post-publication verification did not return 595 active and verified records")

    receipt = {
        "schema_version": 1,
        "release": "sat-qb-595-v1",
        "published_at": utc_now(),
        "project_ref": args.project_ref,
        "table": "public.sat_qb_questions",
        "merge": {
            "automatically_passed_preserved": EXPECTED_AUTO_PASS,
            "corrected_overrides": EXPECTED_CORRECTED,
            "existing_corpus": EXPECTED_EXISTING,
            "new_original_hard_questions": EXPECTED_NEW,
            "published_total": EXPECTED_FINAL,
            "qid_md5": expected_hash,
        },
        "corrected_batches": corrected_receipt,
        "new_batch": new_receipt,
        "remote_preflight": remote_receipt,
        "media": media_receipt,
        "publication": publish_result,
        "backup": str(args.backup),
    }
    atomic_write_json(args.receipt, receipt)
    print(json.dumps(receipt["merge"], indent=2))
    print(f"SUCCESS: 595 SAT questions are live. Receipt: {args.receipt}")


if __name__ == "__main__":
    try:
        run()
    except ReleaseError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
