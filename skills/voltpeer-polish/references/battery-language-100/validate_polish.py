"""Conservative risk checks for supplied polishing responses and corpus metadata.

Uses only Python's standard library. Self-tests check synthetic fixtures, not a
language model. Protected-span checks can flag sound paraphrases for human
review and cannot prove complete scientific equivalence.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import decimal
import json
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
CITATION = re.compile(r"\\(?:cite|citep|citet|parencite|textcite)\*?(?:\[[^\]]*\]){0,2}\{[^}]+\}|\[\s*\d+(?:\s*[,;–-]\s*\d+)*\s*\]")
NUMBER = re.compile(r"(?<![A-Za-z0-9_.])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")
PRIMARY_HOSTS = {"www.nature.com", "nature.com", "pubs.rsc.org", "www.science.org", "science.org",
                 "pubs.acs.org", "link.springer.com", "www.mdpi.com", "mdpi.com",
                 "advanced.onlinelibrary.wiley.com", "chemistry-europe.onlinelibrary.wiley.com", "onlinelibrary.wiley.com"}


def normalized(text):
    text = str(text).translate(SUPER).replace("−", "-").replace("‖", "||").replace("∥", "||")
    text = text.replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ")
    text = text.replace("mA h", "mAh").replace("W h", "Wh")
    return re.sub(r"\s+", " ", text).strip()


def numbers(text):
    text = CITATION.sub("", normalized(text))
    result = set()
    for value in NUMBER.findall(text):
        try:
            result.add(str(decimal.Decimal(value).normalize()))
        except decimal.InvalidOperation:
            result.add(value)
    return result


def citations(text):
    return collections.Counter(re.sub(r"\s+", "", x) for x in CITATION.findall(str(text)))


def evaluate(case, response):
    errors = []
    if not isinstance(response, dict):
        return {"case_id": case["id"], "pass": False, "issues": ["response is not a JSON object"]}
    value = response.get("text")
    if not isinstance(value, str) or not value.strip():
        return {"case_id": case["id"], "pass": False, "issues": ["polished text is missing or empty"]}
    text = normalized(value)
    for field in ("section", "paper_type"):
        expected = case["expected_" + field]
        if str(response.get(field, "")).strip().casefold() != expected.casefold():
            errors.append(field + " route differs from expected " + expected)
    original_numbers = numbers(case["source"])
    revised_numbers = numbers(value)
    missing = sorted(original_numbers - revised_numbers)
    invented = sorted(revised_numbers - original_numbers)
    if missing:
        errors.append("source numeric values missing: " + ", ".join(missing))
    if invented:
        errors.append("new numeric values require verification: " + ", ".join(invented))
    if citations(case["source"]) != citations(value):
        errors.append("citation markers or keys changed")
    for fact in case.get("protected_facts", []):
        allowed = [normalized(option) for option in fact["allowed"]]
        if not any(option in text for option in allowed):
            errors.append("protected fact " + fact["label"] + " missing or changed: " + " / ".join(fact["allowed"]))
    for pattern in case.get("required_patterns", []):
        if not re.search(pattern, value, re.I):
            errors.append("required scientific relation not found: " + pattern)
    for pattern in case.get("forbidden_patterns", []):
        if re.search(pattern, value, re.I):
            errors.append("unsupported or altered claim: " + pattern)
    required_note = case.get("required_note_pattern")
    notes = response.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        errors.append("notes must be a list of strings")
        notes = []
    if required_note and not re.search(required_note, " ".join(notes), re.I):
        errors.append("factual ambiguity needs a verification note")
    order = case.get("required_section_order", [])
    if order:
        heading_positions = []
        for heading in order:
            match = re.search(r"(?m)^\s*" + re.escape(heading) + r"\s*$", value)
            heading_positions.append(match.start() if match else -1)
        if -1 in heading_positions or heading_positions != sorted(heading_positions):
            errors.append("supplied section boundary or order changed")
    return {"case_id": case["id"], "pass": not errors, "issues": errors,
            "human_review_required": True}


def load_cases(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    cases = document["cases"]
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("evaluation IDs must be unique")
    return document, cases


def run_self_test(cases):
    positives = []
    negatives = []
    for case in cases:
        positives.append(evaluate(case, case["acceptable_response"]))
        for mutation in case["corrupted_responses"]:
            result = evaluate(case, mutation["response"])
            result["mutation"] = mutation["label"]
            result["expected_rejection"] = True
            negatives.append(result)
    failures = [{"type": "acceptable fixture rejected", **row} for row in positives if not row["pass"]]
    failures += [{"type": "corrupt fixture accepted", **row} for row in negatives if row["pass"]]
    # Concrete response-format and uncertainty risks in addition to the 48
    # scientific mutations. These are not additional model evaluations.
    case15 = next(case for case in cases if case["id"] == "BP15")
    missing_note = evaluate(case15, {**case15["acceptable_response"], "notes": []})
    missing_text = evaluate(cases[0], {"section": cases[0]["expected_section"], "paper_type": cases[0]["expected_paper_type"], "text": "", "notes": []})
    typography = evaluate(cases[0], {**cases[0]["acceptable_response"], "text": cases[0]["acceptable_response"]["text"].replace("mAh", "mA h").replace("cm−2", "cm⁻²")})
    guards = {"missing_factual_note_rejected": not missing_note["pass"],
              "empty_output_rejected": not missing_text["pass"],
              "equivalent_capacity_typography_accepted": typography["pass"]}
    failures += [{"type": "response safeguard failed", "guard": name} for name, passed in guards.items() if not passed]
    return {"mode": "engineering-fixture-self-test", "case_count": len(cases),
            "acceptable_fixture_count": len(positives), "acceptable_fixtures_accepted": sum(row["pass"] for row in positives),
            "deliberate_corruption_count": len(negatives), "deliberate_corruptions_rejected": sum(not row["pass"] for row in negatives),
            "failures": failures, "pass": not failures, "positive_results": positives, "negative_results": negatives,
            "response_safeguards": guards,
            "model_requests": 0, "model_behavior_certified": False,
            "limitation": "Checks named scientific risks on synthetic outputs; they are conservative and do not prove full semantic equivalence."}


def check_corpus(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["records"]
    issues = []
    if len(rows) != 100:
        issues.append("record count is not 100")
    if len({row["doi"].lower() for row in rows}) != 100:
        issues.append("DOI list is not 100 unique entries")
    buckets = collections.Counter(row["domain"] for row in rows)
    if len(buckets) != 10 or set(buckets.values()) != {10}:
        issues.append("topic buckets are not 10 by 10")
    passage_count = 0
    sampled_count = 0
    for row in rows:
        prefix = row["id"] + ": "
        if row["crossref_type"] != "journal-article":
            issues.append(prefix + "Crossref type is not journal-article")
        if not re.fullmatch(r"10\.\d{4,9}/\S+", row["doi"], re.I):
            issues.append(prefix + "invalid DOI syntax")
        url = urllib.parse.urlparse(row["primary_url"])
        if url.scheme not in {"http", "https"} or url.hostname not in PRIMARY_HOSTS:
            issues.append(prefix + "primary URL is outside recorded publisher hosts")
        if "entire indexed author abstract" not in row["abstract_read_scope"]:
            issues.append(prefix + "abstract inspection scope absent")
        evidence = row["abstract_evidence"]
        if row["abstract_source_url"] != evidence["source_query_url"]:
            issues.append(prefix + "abstract source URL differs from the batch query actually fetched")
        if evidence["source_query_response_http_status"] != 200:
            issues.append(prefix + "abstract query did not return 200")
        for digest in (evidence["sha256"], evidence["source_query_response_sha256"], row["metadata_verification"]["crossref_response_sha256"]):
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                issues.append(prefix + "invalid retrieval digest")
        if not row["metadata_verification"]["crossref_doi_exact_match"] or row["metadata_verification"]["normalized_title_similarity"] < 0.95:
            issues.append(prefix + "DOI/title corroboration failed")
        first_date = row["first_publication_date_europe_pmc"]
        if not "2016-01-01" <= first_date <= "2025-12-31":
            issues.append(prefix + "first publication falls outside recorded query window")
        if not row["independent_language_observation"].strip():
            issues.append(prefix + "reading observation missing")
        sample = row["fulltext_selected_reading"]
        if sample:
            sampled_count += 1
            if sample["http_status"] != 200 or "not the complete article" not in sample["scope"]:
                issues.append(prefix + "fulltext access or selective-reading scope invalid")
            identifiers = set()
            for passage in sample["inspected_passages"]:
                passage_count += 1
                if passage["paragraph_id"] in identifiers:
                    issues.append(prefix + "duplicate inspected paragraph")
                identifiers.add(passage["paragraph_id"])
                if not passage["xml_locator"].startswith("article/body/"):
                    issues.append(prefix + "body paragraph locator absent")
                if not re.fullmatch(r"[0-9a-f]{64}", passage["text_sha256"]):
                    issues.append(prefix + "inspected paragraph digest invalid")
    count = data["counts"]
    if count["abstracts_fully_read"] != 100 or count["articles_with_selected_body_reading"] != sampled_count or count["selected_body_paragraphs_read"] != passage_count:
        issues.append("reading summary differs from individual records")
    if count["complete_fulltext_articles_read"] != 0 or count["supplements_read"] != 0:
        issues.append("unsupported complete-article or supplement reading claim")
    forbidden_fields = {"abstractText", "abstract_text", "fulltext_xml", "pdf_bytes", "article_paragraph_text"}
    def scan(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_fields:
                    issues.append("raw author-text field present: " + key)
                scan(child)
        elif isinstance(value, list):
            for child in value:
                scan(child)
    scan(data)
    return {"mode": "corpus-structure-and-provenance-check", "records_checked": len(rows),
            "unique_dois": len({row["doi"].lower() for row in rows}), "domains": dict(buckets),
            "sampled_fulltext_articles": sampled_count, "body_paragraphs": passage_count,
            "issues": issues, "pass": not issues,
            "limitation": "Validates recorded metadata/scopes and payload structure; it is not a fresh network readback or an independent confirmation of reader inspection."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=HERE / "evaluation_cases.json")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check-corpus", action="store_true")
    parser.add_argument("--corpus", type=Path, default=HERE / "corpus.json")
    parser.add_argument("--responses", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not any((args.self_test, args.check_corpus, args.responses)):
        parser.error("choose --self-test, --check-corpus or --responses")
    results = []
    if args.self_test or args.responses:
        _, cases = load_cases(args.cases)
    if args.self_test:
        results.append(run_self_test(cases))
    if args.check_corpus:
        results.append(check_corpus(args.corpus))
    if args.responses:
        responses = json.loads(args.responses.read_text(encoding="utf-8"))
        rows = [evaluate(case, responses.get(case["id"])) for case in cases]
        results.append({"mode": "supplied-response-risk-screen", "case_count": len(rows),
                        "passed_screen": sum(row["pass"] for row in rows), "pass": all(row["pass"] for row in rows),
                        "results": rows, "human_review_required": True, "model_behavior_certified": False})
    report = {"created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "pass": all(result["pass"] for result in results), "results": results}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # The compact console output excludes detailed fixture bodies and paths.
    brief = {"pass": report["pass"], "results": [{key: value for key, value in row.items() if key not in {"positive_results", "negative_results", "results"}} for row in results]}
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
