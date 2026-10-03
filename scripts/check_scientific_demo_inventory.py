"""Record the scientific model and delivered bytes for every public demo.

This is a provenance/schema gate. Independent equation checks live in the
scientific-core and scientific-domains tests; neither constitutes validation
of an experimental material, a mechanism, or a host/model agent.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import csv
from check_demo_metadata import validate_metadata

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'full_cell','li_cu_ce','li_li','eis','operando_xrd','tof_sims','integrated_study',
    'rate_capability','gcd_profiles','pouch_thermal','literature_benchmark','reporting_matrix',
    'capability_spread','style_presets','cyclic_voltammetry','differential_capacity','gitt_pulse','ionic_conductivity','xps_components','raman_series',
    'ftir','nmr','rdf_coordination','msd','lsv','transference','aurbach_protocol','eis_frequency',
    'chronoamperometry','ocv_rest','na_metal_ce','k_ion_rate','zn_plating_ce','zn_symmetric',
    'zn_air_power','zn_i2_cycle','flow_efficiency','pv_jv','pv_stability','pv_trpl'
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    rows = []
    for namespace in ('showcase','domain_showcase'):
        base = ROOT/'examples'/namespace
        for path in sorted(base.glob('*/metadata.json')):
            meta = validate_metadata(json.loads(path.read_text(encoding='utf-8-sig')))
            inputs = {}
            for name in meta['source_files']:
                source = (path.parent/name).resolve()
                if not source.is_relative_to(base.resolve()) or not source.is_file():
                    raise ValueError(f'Invalid scientific source: {path.parent.name}/{name}')
                if source.suffix == '.csv':
                    with source.open(encoding='utf-8-sig',newline='') as stream:
                        reader=csv.DictReader(stream)
                        for record in reader:
                            for value in record.values():
                                try: number=float(value)
                                except (ValueError,TypeError): continue
                                if not math.isfinite(number):
                                    raise ValueError(f'Nonfinite public synthetic number: {source.name}')
                inputs[source.relative_to(ROOT).as_posix()] = digest(source)
            figures = {f'figure.{extension}':digest(path.parent/f'figure.{extension}')
                       for extension in ('png','svg','pdf')}
            rows.append({'id':path.parent.name,'metadata':path.relative_to(ROOT).as_posix(),
                         'metadata_sha256':digest(path),'input_sha256':inputs,'figure_sha256':figures,
                         'scientific_basis':meta['scientific_basis'],
                         'check_scope':'Schema, finite numeric input, source containment and delivered byte provenance; equation tests are separate.'})
    actual=[row['id'] for row in rows]
    if len(actual)!=len(set(actual)) or set(actual)!=EXPECTED:
        raise ValueError(f'Demo inventory differs: missing={sorted(EXPECTED-set(actual))}, extra={sorted(set(actual)-EXPECTED)}')
    return {'schema_version':1,'checked_at':'2026-10-01','examples':rows,
            'example_count':len(rows),'numeric_data_origin':'Original synthetic parameters; no paper measurements copied.',
            'provenance_gate':'PASS','experimental_material_validation':'NOT_PERFORMED',
            'real_model_and_host_behavior':'NOT_TESTED_BY_THIS_GATE'}


if __name__ == '__main__':
    record = inventory()
    output=ROOT/'docs/validation/2026-10-01-scientific-inventory.json'
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'examples':record['example_count'],'provenance_gate':'PASS','record':output.relative_to(ROOT).as_posix()}))
