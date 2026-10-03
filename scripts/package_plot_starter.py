"""Package one Starter launcher, one canonical Skill and explicit synthetic input."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/starter"
SKILL = ROOT / "skills/voltpeer-plot"
LAUNCHER_FILES = ("start.py", "README.md", "AGENT_GUIDE.md", "INPUT_GUIDE.md")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def demo_inputs(root):
    """Adapt checked teaching sources; never called by the author's plot route.

    The Starter uses the same data/models as the gallery and recipe packs. It
    must not introduce another collection of unrelated, hand-drawn numbers.
    """
    target = root / "demo"
    target.mkdir()
    showcase = ROOT / "examples/showcase"
    recipe = ROOT / "examples/recipe_packs/full_cell"
    used = {}
    def read(path):
        used[path.relative_to(ROOT).as_posix()] = digest(path)
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    def settings(slug):
        path = showcase / slug / "metadata.json"
        used[path.relative_to(ROOT).as_posix()] = digest(path)
        meta = json.loads(path.read_text(encoding="utf-8"))
        return {"source": path.relative_to(ROOT).as_posix(), "scientific_basis": meta["scientific_basis"],
                "source_conditions": meta["test_conditions"]}
    common = dict(evidence_state="verified", chemistry="Generic analytic teaching model",
                  temperature_c="25", electrolyte_ul_mg="NA", rate="declared in source model",
                  loading_mg_cm2="NA", voltage_window_v="2.8-4.3", cell_configuration="half cell",
                  pressure_mpa="NA", cell_format="no experimental package simulated",
                  formation_protocol="no experimental formation simulated")
    cases = {}
    science = {}
    ce = read(showcase / "li_cu_ce/data.csv")
    cases["coulombic_efficiency"] = (
        [dict(series=sample, cycle=row["cycle"], ce_pct=row[f"{sample}_ce_pct"],
              q_plated_mAh_cm2=row["plated_mAh_cm2"],
              q_stripped_mAh_cm2=float(row["plated_mAh_cm2"])*float(row[f"{sample}_ce_pct"])/100)
         for sample in ("A", "B") for row in ce],
        dict(chemistry="Li||Cu teaching model", cell_configuration="half cell",
             ce_definition="stripped charge / plated charge * 100%", rate="1 mA cm^-2",
             current_density_ma_cm2="1", areal_capacity_mah_cm2="1", cutoff_rule="1 V vs Li/Li+",
             ce_protocol="cycle-by-cycle plating/stripping"))
    science["coulombic_efficiency"] = settings("li_cu_ce")
    full = read(recipe / "demo/cycling.csv")
    cfg = json.loads((recipe / "config.demo.json").read_text(encoding="utf-8"))["conditions"]["common"]
    cases["full_cell_cycling"] = (
        [dict(series=r["sample"], cycle=r["cycle"], discharge_capacity=r["capacity"],
              charge_capacity=r['charge_capacity'],ce_pct=r['ce'],reference_cycle='1',
              reference_capacity=next(q['capacity'] for q in full if q['sample']==r['sample'] and int(q['cycle'])==1)) for r in full],
        dict(cell_configuration="full cell", chemistry="Generic positive||negative electrode inventory model",
             capacity_basis="cathode active mass", capacity_unit="mAh g-1", rate=cfg["rate_or_current"],
             voltage_window_v="2.9-4.2", np_ratio="NA (not modelled)",
             ce_definition="discharge capacity / charge capacity",
             retention_basis="100 * same-model discharge capacity / declared cycle 1 discharge capacity"))
    path = recipe / "sources.json"
    used[path.relative_to(ROOT).as_posix()] = digest(path)
    science["full_cell_cycling"] = {"source": path.relative_to(ROOT).as_posix(),
                                    "model_record": json.loads(path.read_text(encoding="utf-8")),
                                    "retention_calculation":"100*Qdis(n)/Qdis(1), explicitly selected teaching reference, same declared 0.5 C context; no experimental validation"}
    half = read(showcase / "full_cell/data.csv")
    cases["half_cell_cycling"] = (
        [dict(series=s, cycle=r["cycle"], discharge_capacity=r[f"{s}_mAh_g"]) for s in ("A", "B") for r in half],
        dict(cell_configuration="half cell", chemistry="NMC811||Li illustrative half cell",
             capacity_basis="working-electrode active mass", capacity_unit="mAh g-1", rate="0.5 C",
             voltage_window_v="2.8-4.3", np_ratio="NA"))
    science["half_cell_cycling"] = settings("full_cell")
    trace = read(showcase / "li_li/data.csv")
    cases["symmetric_cell_voltage"] = (
        [dict(series=r["sample"], time_h=r["time_h"], voltage_mv=r["voltage_mV"]) for r in trace],
        dict(chemistry="Li||Li teaching model", cell_configuration="Li|Li symmetric cell",
             current_density_ma_cm2="1", areal_capacity_mah_cm2="1", rate="1 mA cm^-2",
             separator="NA (not modelled)", failure_rule="no experimental failure assignment"))
    science["symmetric_cell_voltage"] = settings("li_li")
    profiles = read(showcase / "gcd_profiles/data.csv")
    selected = [r for r in profiles if int(r["cycle"]) in (1, 500)]
    cases["voltage_capacity"] = (
        [dict(series="A", cycle=r["cycle"], direction=r["direction"], capacity=r["capacity_mAh_g"],
              voltage_v=r["voltage_V"]) for r in selected],
        dict(chemistry="NMC811||Li illustrative half cell", cell_configuration="half cell", rate="0.5 C",
             capacity_basis="working-electrode active mass", capacity_unit="mAh g-1", voltage_window_v="2.8-4.3"))
    science["voltage_capacity"] = {**settings("gcd_profiles"), "selection": "Complete charge/discharge records at cycles 1 and 500; no within-trace thinning."}
    eis = read(showcase / "eis/data.csv")
    cases["nyquist"] = (
        [dict(series=r["sample"], z_real_ohm=r["Zreal_ohm"], minus_z_imag_ohm=-float(r["Zimag_ohm"]),
              frequency_hz=r["frequency_Hz"]) for r in eis],
        dict(chemistry="Randles/CPE equivalent circuit", cell_state="stationary linear analytic model",
             frequency_range_hz="1e5-0.01", perturbation_mv="NA (linear model)", cell_configuration="two-terminal circuit"))
    science["nyquist"] = settings("eis")
    first = {s: float(half[0][f"{s}_mAh_g"]) for s in ("A", "B")}
    cases["cycle_retention"] = (
        [dict(series=s, cycle=r["cycle"], retention_pct=float(r[f"{s}_mAh_g"])/first[s]*100) for s in ("A", "B") for r in half],
        dict(chemistry="NMC811||Li illustrative half cell", cell_configuration="half cell", rate="0.5 C",
             retention_basis="discharge capacity divided by recorded cycle 1 discharge capacity", reference_cycle="1"))
    science["cycle_retention"] = {**settings("full_cell"), "calculation": "100*Q_dis(n)/Q_dis(1); activation may exceed 100% without clipping."}
    rates = read(showcase / "rate_capability/data.csv")
    cases["rate_capability"] = (
        [dict(series=r["sample"], step=r["cycle"], rate_label=r["discharge_rate_C"]+" C", capacity=r["capacity_mAh_g"]) for r in rates],
        dict(chemistry="NMC811||Li illustrative half cell", cell_configuration="half cell",
             capacity_basis="working-electrode active mass", capacity_unit="mAh g-1", rate="declared per recorded stage"))
    science["rate_capability"] = settings("rate_capability")
    tof = dict(chemistry="Generic ion-intensity fields", cell_configuration="surface-intensity model",
               signal_unit="a.u.", normalization="model normalized intensity; not concentration", ion_polarity="negative",
               measurement_state="original analytic teaching field at 30 s sputter time")
    maps = read(showcase / "tof_sims/data.csv")
    cases["tofsims_map"] = (
        [dict(sample_id="Example", fragment="F-", x_um=r["x_um"], y_um=r["y_um"], signal=r["normalized_intensity"])
         for r in maps if r["species"] == "F-"], tof)
    science["tofsims_map"] = {**settings("tof_sims"), "selection": "Complete F- map at the source's recorded 30 s time; no concentration inference."}
    depth = read(showcase / "tof_sims/depth.csv")
    cases["tofsims_depth"] = (
        [dict(sample_id="Example", fragment=r["species"], sputter_time_s=r["sputter_time_s"], signal=r["mean_normalized_intensity"])
         for r in depth if r["species"] in ("F-", "S-")], tof)
    science["tofsims_depth"] = {**settings("tof_sims"), "selection": "Complete F-/S- time profiles; sputter time is not calibrated depth."}
    index = {}
    for kind,(rows,context) in cases.items():
        data, mapping = target / (kind + ".csv"), target / (kind + ".json")
        with data.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        metadata = dict(kind=kind, style="forge", columns={}, common={**common, **context, "source_id":"SYNTHETIC-DEMO:"+kind}, mode="direct",
                        claim="合成示例，不作实验或文献结论", caption_notes="模型假设和科学依据见 DEMO_MODELS.json；数值为自设，不是论文实测。")
        if kind.startswith("tofsims"):
            metadata["sample_id"] = "Example"
            if kind == "tofsims_map":
                metadata["fragment"] = "F-"
        dump(mapping, metadata)
        index[kind] = dict(data=data.relative_to(root).as_posix(), metadata=mapping.relative_to(root).as_posix(),
                           data_status="synthetic_demo", author_data_fallback=False)
    dump(root / "DEMO_INDEX.json", index)
    dump(root / "DEMO_MODELS.json", {"schema_version": 1, "data_origin": "original_synthetic",
                                    "adapted_sources": used, "models": science,
                                    "scope": "Teaching source selection and field mapping; not measured cells or a scientific certification."})


def package(destination):
    version = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8-sig"))["version"]
    if json.loads((SKILL / "assets/SKILL_RELEASE.json").read_text(encoding="utf-8-sig"))["version"] != version:
        raise ValueError("Synchronize SKILL_RELEASE before packaging Starter.")
    destination = Path(destination)
    archive = destination / f"VoltPeer-Plot-Starter-v{version}.zip"
    if archive.exists():
        raise FileExistsError("Choose a new Starter directory; existing versioned archive bytes are immutable")
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
                target = stage / "skills/voltpeer-plot" / file.relative_to(SKILL)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, target)
        demo_inputs(stage)
        dump(stage / "HOSTS.json", dict(schema_version=1, hosts={
            "dsh":dict(install_path=".dsh/skills/voltpeer-plot", frontmatter="agent-skills-name-description", native_discovery="NOT_TESTED"),
            "codex":dict(install_path=".agents/skills/voltpeer-plot", frontmatter="agent-skills-name-description", native_discovery="NOT_TESTED")}, scientific_runtime="batteryplot", runtime_forks=0))
        files = sorted(p for p in stage.rglob("*") if p.is_file())
        dump(stage / "PACKAGE_MANIFEST.json", dict(schema_version=1, resource_id="plot_starter", version=version, channel="beta",
            scientific_runtime="batteryplot", skill_id="voltpeer-plot", hosts=["dsh","codex"],
            api_key_for_install=False, files=[dict(path=p.relative_to(stage).as_posix(), sha256=digest(p)) for p in files]))
        archive = destination / f"VoltPeer-Plot-Starter-v{version}.zip"
        with ZipFile(archive, "x", ZIP_DEFLATED) as output:
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
    version = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))["version"]
    parser.add_argument("--out", type=Path, default=ROOT / f"docs/downloads/v{version}/starter")
    package(parser.parse_args().out)
