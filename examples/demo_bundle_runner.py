"""Redraw existing CSVs from one downloaded VoltPeer example.

Only render() is called. Code and inputs are copied into an isolated temporary
tree; original data stay intact and results require a fresh output directory.
"""
from __future__ import annotations
import argparse
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile

BUNDLE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root, relative):
    part = PurePosixPath(relative)
    if not relative or part.is_absolute() or ".." in part.parts or "\\" in relative or ":" in relative:
        raise ValueError("Unsafe relative path in package")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Package path leaves its own folder")
    return path


def load_manifest(allow_code_changes=False):
    value = json.loads((BUNDLE / "SOURCE_MANIFEST.json").read_text(encoding="utf-8-sig"))
    if value.get("schema_version") != 1 or value.get("operation") != "render_existing_inputs_only":
        raise ValueError("Unsupported package manifest")
    if not value.get("code") or not value.get("inputs"):
        raise ValueError("Incomplete code or input records")
    current_code = []
    for record in value["code"]:
        path = safe_path(BUNDLE, record["archive_path"])
        if not path.is_file():
            raise ValueError(f"Renderer source missing: {record['archive_path']}")
        actual = sha(path)
        if actual != record["sha256"] and not allow_code_changes:
            raise ValueError(f"Renderer source is missing or changed: {record['archive_path']}")
        current_code.append({**record, "original_sha256": record["sha256"], "sha256": actual,
                             "changed_from_demo": actual != record["sha256"]})
    value["current_code"] = current_code
    return value


def check_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"{path.name}: missing or duplicate CSV columns")
        count = 0
        for row in reader:
            count += 1
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"{path.name}: row {count} does not match its column count")
            for key, value in row.items():
                try:
                    number = float(value)
                except ValueError:
                    continue
                if not math.isfinite(number):
                    raise ValueError(f"{path.name}: {key} has a non-finite value; ask the author before plotting")
        if count == 0:
            raise ValueError(f"{path.name}: no data rows")


def redraw(output, allow_code_changes=False):
    output = output.resolve()
    if output.exists():
        raise ValueError("输出目录已存在，请换一个名称；旧结果不会被覆盖。")
    if output == BUNDLE or (BUNDLE / "code").resolve() in output.parents:
        raise ValueError("Choose output outside the renderer source folder")
    manifest = load_manifest(allow_code_changes)
    sample = manifest["sample"]
    if not isinstance(sample, str) or not sample.replace("_", "").isalnum():
        raise ValueError("Invalid sample identity")
    records, logs = [], io.StringIO()
    with tempfile.TemporaryDirectory(prefix="voltpeer-redraw-") as temporary:
        work = Path(temporary)
        repo = work / "code"
        for record in manifest["current_code"]:
            if record["archive_path"].startswith("code/"):
                source = safe_path(BUNDLE, record["archive_path"])
                target = safe_path(work, record["archive_path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
        showcase = repo / "examples/showcase"
        for record in manifest["inputs"]:
            source = safe_path(BUNDLE, record["archive_path"])
            if not source.is_file():
                raise ValueError(f"Missing input: {record['archive_path']}")
            target = safe_path(showcase, record["render_path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            content = source.read_bytes()
            target.write_bytes(content)
            if target.suffix.lower() == ".csv":
                check_csv(target)
            current = hashlib.sha256(content).hexdigest()
            records.append({"path": record["archive_path"], "render_path": record["render_path"],
                            "sha256": current, "changed_from_demo": current != record["sha256"]})
        changed_code = any(record["changed_from_demo"] for record in manifest["current_code"])
        changed = any(record["changed_from_demo"] for record in records) or changed_code
        submitted_metadata = json.loads((showcase / sample / "metadata.json").read_text(encoding="utf-8-sig"))
        submitted_conditions = next((row["changed_from_demo"] for row in records
                                     if row["render_path"] == sample + "/metadata.json"), False)
        os.environ["MPLBACKEND"] = "Agg"
        os.environ["MPLCONFIGDIR"] = str(work / "matplotlib-cache")
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(repo / "skills/battery-review-figure/scripts"))
        sys.path.insert(0, str(repo / "skills/voltpeer-plot/scripts"))
        sys.path.insert(0, str(repo / "examples/recipe_packs/_runtime"))
        script = safe_path(repo, manifest["renderer"])
        if script.suffix != ".py" or not script.is_file():
            raise ValueError("Renderer missing")
        spec = importlib.util.spec_from_file_location("voltpeer_example_redraw", script)
        if spec is None or spec.loader is None:
            raise ValueError("Cannot load renderer")
        module = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(logs), contextlib.redirect_stderr(logs):
            spec.loader.exec_module(module)
            module.ROOT = showcase
            if hasattr(module, "REPO"):
                module.REPO = repo
            module.render(sample)
        generated = safe_path(showcase, sample)
        if any(not (generated / f"figure.{suffix}").is_file() for suffix in ("png", "svg", "pdf")):
            raise ValueError("Renderer did not produce PNG, SVG and PDF")
        metadata_path = generated / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        if changed:
            # Core render() reconstructs teaching metadata. Remove its claim for
            # substituted author data instead of calling those data synthetic.
            metadata["demo_model_reference"] = {key: metadata.pop(key) for key in (
                "scientific_basis", "test_conditions", "sample_identity", "random_seed",
                "generator_version", "reference") if key in metadata}
            metadata["data_status"] = "author_supplied_unverified"
            metadata["not_experimental_data"] = None
            metadata["test_conditions"] = submitted_metadata.get("test_conditions", "NOT_CONFIRMED") if submitted_conditions else (
                "NOT_CONFIRMED: recheck the original demonstration conditions for the substituted author input")
            metadata["conditions_review"] = "NOT_REVIEWED: submitted conditions are not experimental verification"
            metadata["creator"] = "Author-input redraw using packaged VoltPeer code; see RUN_RECORD.json"
            metadata["review"] = {"science": "NOT_REVIEWED: changed author inputs; no model or experimental certification"}
        metadata["bundle_redraw"] = {"changed_from_demo": changed,
            "operation": "render_existing_inputs_only", "original_inputs_written": False,
            "scope": "Redraw only; check conditions and axis limits before using author data"}
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for record in records:
            if sha(safe_path(BUNDLE, record["path"])) != record["sha256"]:
                raise ValueError("An input changed during rendering; save it and rerun")
        # An exclusive mkdir prevents concurrent output replacement too.
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir(exist_ok=False)
        artifacts = [path for path in generated.iterdir() if path.is_file() and
                     (path.suffix in {".png", ".svg", ".pdf"} or path.name in {
                        "metadata.json", "alignment.json", "render-report.json"})]
        for path in sorted(artifacts):
            with (output / path.name).open("xb") as handle:
                handle.write(path.read_bytes())
        snapshot = output / "inputs"
        for record in records:
            target = safe_path(snapshot, record["render_path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            # render() may update staging metadata: snapshot original bytes.
            with target.open("xb") as handle:
                handle.write(safe_path(BUNDLE, record["path"]).read_bytes())
        result = {"schema_version": 1, "sample": sample, "operation": "render_existing_inputs_only",
          "regenerated_inputs": False, "original_inputs_written": False, "changed_from_demo": changed,
          "model_calls": "NOT_MEASURED_FOR_MODIFIED_CODE" if changed_code else 0,
          "network_required_for_redraw": "NOT_VERIFIED_FOR_MODIFIED_CODE" if changed_code else False,
          "renderer_source": manifest["current_code"],
          "source_code_modified": changed_code,
          "inputs": records, "outputs": [{"path": path.name, "sha256": sha(output / path.name)} for path in sorted(artifacts)],
          "data_scope": "author_supplied_unverified" if changed else "original_synthetic_teaching_model",
          "validation_scope": "Closure and redraw only; not scientific certification of author data"}
        (output / "RUN_RECORD.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if logs.getvalue().strip():
            (output / "render-log.txt").write_text(logs.getvalue(), encoding="utf-8")
    return {"status": "redrawn", "sample": sample, "output": str(output),
            "formats": ["png", "svg", "pdf"], "changed_from_demo": changed,
            "note": "待核对作者数据的条件和坐标范围。" if changed else "示例重画完成。"}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=BUNDLE / "brf-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--allow-code-changes", action="store_true", help="Record deliberate source edits instead of rejecting changed source")
    args = parser.parse_args()
    try:
        if args.check:
            manifest = load_manifest(args.allow_code_changes)
            for record in manifest["inputs"]:
                path = safe_path(BUNDLE, record["archive_path"])
                if not path.is_file():
                    raise ValueError(f"Missing input: {record['archive_path']}")
                if path.suffix.lower() == ".csv":
                    check_csv(path)
            result = {"status": "source_and_inputs_checked", "sample": manifest["sample"],
                      "dependencies": "NOT_IMPORTED", "render": "NOT_RUN",
                      "operation": "render_existing_inputs_only", "native_host_discovery": "NOT_TESTED",
                      "source_code_modified": any(row["changed_from_demo"] for row in manifest["current_code"])}
        else:
            result = redraw(args.output, args.allow_code_changes)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, ImportError, KeyError, TypeError) as error:
        print(f"无法重画：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
