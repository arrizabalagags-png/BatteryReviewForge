"""Execute downloaded gallery source packages in detached Chinese paths.

No network, models, generation, or original-repository imports are used. Run
after the canonical scientific demos have been generated/rendered/published.
"""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("demo_packager", ROOT / "scripts/package_demo_bundles.py")
PACKAGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGER)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DemoSourceDeliveryTests(unittest.TestCase):
    evidence = []
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="VoltPeer 示例 独立 中文路径 ")
        cls.folder = Path(cls.temp.name)
        cls.out = cls.folder / "仅下载的压缩包"
        env = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"}
        env.pop("PYTHONPATH", None)
        cls.env = env
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/package_demo_bundles.py"),
                                 "--out", str(cls.out)], cwd=cls.folder, env=env, capture_output=True,
                                encoding="utf-8", timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        cls.packages = json.loads(result.stdout)["packages"]
        cls.packs = {}
        for row in cls.packages:
            identity = row["file"].removeprefix("BRF-demo-").removesuffix(".zip")
            extract = cls.folder / "下载后解压" / identity
            with ZipFile(cls.out / row["file"]) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError("Corrupt archive")
                archive.extractall(extract)
            cls.packs[identity] = extract / f"BRF-demo-{identity}" if identity in PACKAGER.LEGACY else extract

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def copy_pack(self, identity, suffix):
        destination = self.folder / f"体验 {suffix}" / "源码与数据"
        shutil.copytree(self.packs[identity], destination)
        return destination

    def command(self, pack, *args):
        return subprocess.run([sys.executable, "-I", str(pack / "render_existing.py"), *map(str, args)],
                              cwd=self.folder, env=self.env, capture_output=True, encoding="utf-8", timeout=120)

    def test_all_thirty_sources_and_archive_input_closure(self):
        actual = {path.parent.name for path in (ROOT / "examples/showcase").glob("*/metadata.json")}
        self.assertEqual(actual, set(PACKAGER.NAMES))
        self.assertEqual(len(actual), 30)
        self.assertEqual(len(self.packages), 32)
        for row in self.packages:
            identity = row["file"].removeprefix("BRF-demo-").removesuffix(".zip")
            pack = self.packs[identity]
            manifest = json.loads((pack / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(sha(self.out / row["file"]), row["sha256"])
            prefix = f"BRF-demo-{identity}/" if identity in PACKAGER.LEGACY else ""
            with ZipFile(self.out / row["file"]) as archive:
                names = {name.removeprefix(prefix) for name in archive.namelist()}
                self.assertEqual(len(names), len(archive.namelist()))
                self.assertEqual(names - {"SOURCE_MANIFEST.json"}, {record["path"] for record in manifest["files"]})
            for file in manifest["files"]:
                self.assertEqual(sha(pack / file["path"]), file["sha256"])
            for code in manifest["code"]:
                self.assertEqual((pack / code["archive_path"]).read_bytes(), (ROOT / code["repository_path"]).read_bytes())
            for source in manifest["inputs"]:
                self.assertEqual(sha(ROOT / "examples/showcase" / source["render_path"]), source["original_sha256"])
                self.assertEqual(sha(pack / source["archive_path"]), source["sha256"])
            self.assertTrue((pack / "reference/figure.png").stat().st_size > 100)
            self.assertTrue((pack / "reference/figure.svg").stat().st_size > 100)
            ready = self.command(pack, "--check")
            self.assertEqual(ready.returncode, 0, ready.stderr)
            self.assertEqual(json.loads(ready.stdout)["native_host_discovery"], "NOT_TESTED")
            self.evidence.append({"check": "archive_code_input_closure", "sample": row["sample"],
                                  "file": row["file"], "sha256": row["sha256"], "bytes": row["bytes"],
                                  "input_files": len(manifest["inputs"]), "code_files": len(manifest["code"]),
                                  "result": "PASS"})
        capability = json.loads((self.packs["capability_spread"] / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
        members = {row["render_path"].split("/")[0] for row in capability["inputs"]}
        self.assertTrue({"operando_xrd", "li_cu_ce", "li_li", "eis", "rate_capability", "gcd_profiles",
                         "literature_benchmark", "pouch_thermal", "reporting_matrix", "full_cell"} <= members)

    def test_detached_render_all_families_and_both_composites(self):
        for identity in ("eis", "cyclic_voltammetry", "ftir", "aurbach_protocol", "integrated_study", "capability_spread"):
            with self.subTest(sample=identity):
                pack = self.copy_pack(identity, "重画 " + identity)
                originals = {path.relative_to(pack).as_posix(): sha(path) for path in pack.rglob("*") if path.is_file()}
                output = pack.parent / "第一次绘图 新目录"
                result = self.command(pack, "--output", output)
                self.assertEqual(result.returncode, 0, result.stderr)
                for suffix in ("png", "svg", "pdf"):
                    self.assertGreater((output / f"figure.{suffix}").stat().st_size, 100)
                record = json.loads((output / "RUN_RECORD.json").read_text(encoding="utf-8"))
                self.assertFalse(record["regenerated_inputs"])
                self.assertFalse(record["original_inputs_written"])
                self.assertFalse(record["changed_from_demo"])
                self.assertEqual(record["model_calls"], 0)
                self.assertEqual(originals, {path.relative_to(pack).as_posix(): sha(path) for path in pack.rglob("*") if path.is_file()})
                for source in record["inputs"]:
                    self.assertEqual(sha(output / "inputs" / source["render_path"]), source["sha256"])
                self.evidence.append({"check": "detached_real_cli_redraw", "sample": identity, "result": "PASS",
                                      "original_inputs_unchanged": True, "code_closure_detached": True,
                                      "regenerated_inputs": record["regenerated_inputs"], "model_calls": record["model_calls"],
                                      "outputs": [{**file, "bytes": (output / file["path"]).stat().st_size} for file in record["outputs"]],
                                      "renderer_source": record["renderer_source"], "inputs": record["inputs"]})

    def test_existing_output_refused_and_original_results_preserved(self):
        pack = self.copy_pack("eis", "保护旧输出")
        output = pack.parent / "旧成果"
        output.mkdir()
        sentinel = output / "作者原结果.txt"
        sentinel.write_text("必须保持", encoding="utf-8")
        before = sha(sentinel)
        result = self.command(pack, "--output", output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("旧结果不会被覆盖", result.stderr)
        self.assertEqual(sha(sentinel), before)
        self.assertEqual(len(list(output.iterdir())), 1)

    def test_missing_input_stops_without_creating_output(self):
        pack = self.copy_pack("eis", "输入缺失")
        (pack / "eis/data.csv").unlink()
        output = pack.parent / "不应生成"
        result = self.command(pack, "--output", output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Missing input", result.stderr)
        self.assertFalse(output.exists())

    def test_changed_author_data_retained_without_scientific_certification(self):
        pack = self.copy_pack("eis", "更换数据")
        path = pack / "eis/data.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            row["Zreal_ohm"] = str(float(row["Zreal_ohm"]) + .7)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        before = path.read_bytes()
        output = pack.parent / "作者数据结果"
        result = self.command(pack, "--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual((output / "inputs/eis/data.csv").read_bytes(), before)
        metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["data_status"], "author_supplied_unverified")
        self.assertNotIn("scientific_basis", metadata)
        self.assertIn("demo_model_reference", metadata)
        self.assertIsNone(metadata["not_experimental_data"])
        self.assertTrue(json.loads((output / "RUN_RECORD.json").read_text(encoding="utf-8"))["changed_from_demo"])

    def test_nonfinite_author_data_stops_before_plotting(self):
        pack = self.copy_pack("eis", "非有限值")
        path = pack / "eis/data.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["Zreal_ohm"] = "NaN"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        output = pack.parent / "非有限值不出图"
        result = self.command(pack, "--output", output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("non-finite", result.stderr)
        self.assertFalse(output.exists())

    def test_source_edits_require_opt_in_and_generate_is_never_called(self):
        pack = self.copy_pack("eis", "源码修改与禁止造数")
        path = pack / "code/examples/showcase/build.py"
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\ndef _forbidden_generate(*args, **kwargs):\n    raise RuntimeError('GENERATION MUST NOT RUN')\n")
            handle.write("GENERATORS = {key: _forbidden_generate for key in GENERATORS}\n")
        rejected = self.command(pack, "--check")
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("Renderer source is missing or changed", rejected.stderr)
        output = pack.parent / "主动修改源码结果"
        result = self.command(pack, "--output", output, "--allow-code-changes")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((output / "RUN_RECORD.json").read_text(encoding="utf-8"))
        self.assertTrue(record["source_code_modified"])
        self.assertFalse(record["regenerated_inputs"])

    def test_input_path_escape_rejected_by_packager(self):
        root = self.folder / "非法引用 fixture"
        source = root / "showcase"
        folder = source / "eis"
        folder.mkdir(parents=True)
        (root / "private.csv").write_text("this is not a public input", encoding="utf-8")
        (folder / "metadata.json").write_text(json.dumps({"scientific_basis": {"scope": "test only"},
                                                        "source_files": ["../../private.csv"]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing or unsafe"):
            PACKAGER.input_closure("eis", source)


if __name__ == "__main__":
    unittest.main()
