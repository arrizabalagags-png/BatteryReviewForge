"""Package one Starter launcher, one canonical Skill and explicit synthetic input."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples/plot_starter"
SKILL = ROOT / "skills/battery-review-figure"
LAUNCHER_FILES = ("start.py", "README.md", "AGENT_GUIDE.md", "INPUT_GUIDE.md")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def demo_inputs(root):
    """Invented engineering fixtures only; never called by the author's plot route."""
    target = root / "demo"
    target.mkdir()
    common = dict(source_id="SYNTHETIC-DEMO", evidence_state="verified", chemistry="Synthetic battery",
                  temperature_c="25", electrolyte_ul_mg="10", rate="1 C", loading_mg_cm2="2",
                  voltage_window_v="2.5-4.2", cell_configuration="full cell", pressure_mpa="0.1",
                  cell_format="synthetic coin cell", formation_protocol="invented three cycles")
    cases = {}
    pairs = ("Reference", "Example")
    cases["coulombic_efficiency"] = (
        [dict(series=s, cycle=c, ce_pct=100.5 if s == "Example" and c == 7 else round(98.4 + i*.3 + c*.03, 3))
         for i, s in enumerate(pairs) for c in range(1, 13)],
        dict(cell_configuration="half cell", ce_definition="discharge capacity / charge capacity",
             current_density_ma_cm2="1", areal_capacity_mah_cm2="1", cutoff_rule="synthetic fixed cutoff",
             ce_protocol="invented cycling protocol"))
    for kind, configuration in (("full_cell_cycling", "full cell"), ("half_cell_cycling", "half cell")):
        cases[kind] = ([dict(series=s, cycle=c, discharge_capacity=round(160-(.15+.08*i)*c, 3))
                        for i,s in enumerate(pairs) for c in range(0, 101, 10)],
                       dict(cell_configuration=configuration, capacity_basis="cathode active mass" if kind.startswith("full") else "working-electrode active mass",
                            capacity_unit="mAh g-1", np_ratio="1.1" if kind.startswith("full") else "NA"))
    cases["symmetric_cell_voltage"] = (
        [dict(series=s, time_h=i*.5, voltage_mv=(1 if i%4<2 else -1)*(25+10*j))
         for j,s in enumerate(pairs) for i in range(41)],
        dict(cell_configuration="Li|Li symmetric cell", current_density_ma_cm2="1", areal_capacity_mah_cm2="1",
             separator="synthetic separator", failure_rule="invented cutoff"))
    cases["voltage_capacity"] = (
        [dict(series="Example", cycle=cycle, direction=direction, capacity=c,
              voltage_v=round(3+c*.007+cycle*.0006 if direction=="charge" else 4.15-c*.006-cycle*.0005, 3))
         for cycle in (1, 50) for direction in ("charge", "discharge") for c in range(0, 151, 15)],
        dict(capacity_basis="cathode active mass", capacity_unit="mAh g-1"))
    cases["nyquist"] = (
        [dict(series=s, z_real_ohm=round(5+radius*(1-math.cos(math.pi*i/20)), 6),
              minus_z_imag_ohm=round(radius*math.sin(math.pi*i/20), 6))
         for s,radius in (("Reference",36), ("Example",24)) for i in range(21)],
        dict(cell_state="synthetic before cycling", frequency_range_hz="1e5-0.1", perturbation_mv="10"))
    cases["cycle_retention"] = (
        [dict(series=s, cycle=c, retention_pct=100-(.12+.04*i)*(c-1))
         for i,s in enumerate(pairs) for c in range(1, 101, 10)],
        dict(retention_basis="capacity divided by explicit cycle 1 capacity", reference_cycle="1"))
    cases["rate_capability"] = (
        [dict(series=s, step=i, rate_label=rate, capacity=capacity-j*5)
         for j,s in enumerate(pairs) for i,(rate,capacity) in enumerate((("0.2 C",150),("0.5 C",142),("1 C",132),("2 C",119),("0.2 C",148)),1)],
        dict(capacity_basis="cathode active mass", capacity_unit="mAh g-1"))
    tof = dict(signal_unit="counts", normalization="none; invented raw counts", ion_polarity="negative",
               measurement_state="synthetic pristine sample")
    cases["tofsims_map"] = (
        [dict(sample_id="Example", fragment="F-", x_um=x, y_um=y, signal=10+x*3+y*4)
         for y in range(5) for x in range(6)], tof)
    cases["tofsims_depth"] = (
        [dict(sample_id="Example", fragment=f, sputter_time_s=t, signal=round(200+i*100-t*(.8+i*.3),3))
         for i,f in enumerate(("F-","O-")) for t in range(0, 101, 10)], tof)
    index = {}
    for kind,(rows,context) in cases.items():
        data, mapping = target / (kind + ".csv"), target / (kind + ".json")
        with data.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        metadata = dict(kind=kind, style="forge", columns={}, common={**common, **context}, mode="direct",
                        claim="合成示例，不作实验或文献结论", caption_notes="程序验收用虚构数据；CE 100.5%异常原值保留，不得引用为实验。")
        if kind.startswith("tofsims"):
            metadata["sample_id"] = "Example"
            if kind == "tofsims_map":
                metadata["fragment"] = "F-"
        dump(mapping, metadata)
        index[kind] = dict(data=data.relative_to(root).as_posix(), metadata=mapping.relative_to(root).as_posix(),
                           data_status="synthetic_demo", author_data_fallback=False)
    dump(root / "DEMO_INDEX.json", index)


def package(destination):
    version = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8-sig"))["version"]
    if json.loads((SKILL / "assets/SKILL_RELEASE.json").read_text(encoding="utf-8-sig"))["version"] != version:
        raise ValueError("Synchronize SKILL_RELEASE before packaging Starter.")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="voltpeer-starter-build-") as directory:
        stage = Path(directory) / "plot_starter"
        stage.mkdir()
        for name in LAUNCHER_FILES:
            shutil.copyfile(SOURCE / name, stage / name)
        shutil.copyfile(ROOT / "LICENSE", stage / "LICENSE")
        # A single canonical Skill tree. Host metadata and scientific body are not forked.
        for file in sorted(SKILL.rglob("*")):
            if file.is_symlink() or (hasattr(file,"is_junction") and file.is_junction()):
                raise ValueError("Canonical Skill links are not distributable: " + str(file))
            if file.is_file() and "__pycache__" not in file.parts and file.suffix not in {".pyc", ".pyo"}:
                target = stage / "skills/battery-review-figure" / file.relative_to(SKILL)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, target)
        demo_inputs(stage)
        dump(stage / "HOSTS.json", dict(schema_version=1, hosts={
            "dsh":dict(install_path=".dsh/skills/battery-review-figure", frontmatter="agent-skills-name-description", native_discovery="NOT_TESTED"),
            "codex":dict(install_path=".agents/skills/battery-review-figure", frontmatter="agent-skills-name-description", native_discovery="NOT_TESTED")}, scientific_runtime="batteryplot", runtime_forks=0))
        files = sorted(p for p in stage.rglob("*") if p.is_file())
        dump(stage / "PACKAGE_MANIFEST.json", dict(schema_version=1, resource_id="plot_starter", version=version, channel="beta",
            scientific_runtime="batteryplot", skill_id="battery-review-figure", hosts=["dsh","codex"],
            api_key_for_install=False, files=[dict(path=p.relative_to(stage).as_posix(), sha256=digest(p)) for p in files]))
        archive = destination / f"VoltPeer-Plot-Starter-v{version}.zip"
        with ZipFile(archive, "w", ZIP_DEFLATED) as output:
            for file in sorted(p for p in stage.rglob("*") if p.is_file()):
                output.write(file, "plot_starter/" + file.relative_to(stage).as_posix())
    row = dict(resource_id="plot_starter", version=version, channel="beta", file=archive.name,
               bytes=archive.stat().st_size, sha256=digest(archive), hosts=["dsh","codex"],
               scientific_runtime="batteryplot", plot_kinds=[
               "coulombic_efficiency","full_cell_cycling","half_cell_cycling","symmetric_cell_voltage","voltage_capacity",
               "nyquist","cycle_retention","rate_capability","tofsims_map","tofsims_depth"],
               validation="structure_checked; actual extracted execution recorded separately; native/model NOT_TESTED")
    dump(destination / "plot-starter.json", dict(schema_version=1, packs=[row]))
    print(json.dumps(row, ensure_ascii=False))
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/downloads/starter")
    package(parser.parse_args().out)
