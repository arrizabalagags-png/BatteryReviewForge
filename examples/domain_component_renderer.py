"""Replay original domain-demo inputs without generating or changing any CSV.

This renderer is deliberately limited to the declared synthetic examples. Real
instrument records need a checked input contract and adapted scientific model.
"""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def render(name):
    folder=ROOT/name
    closure=json.loads(Path(__file__).with_name('domain_inputs.json').read_text(encoding='utf-8'))
    record=closure[name]
    for relative,digest in record['inputs'].items():
        if hashlib.sha256((folder/relative).read_bytes()).hexdigest()!=digest:
            raise ValueError('This domain renderer replays the original synthetic inputs only. Author data need an adapted input contract/model; do not inherit demo conditions: '+relative)
    script=Path(__file__).with_name('domain_model.py')
    spec=importlib.util.spec_from_file_location('voltpeer_domain_model',script);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    with (folder/'data.csv').open(encoding='utf-8-sig',newline='') as handle:
        rows=list(csv.reader(handle));fields=rows[0];values=np.array(rows[1:],dtype=float)
    if values.ndim!=2 or not np.all(np.isfinite(values)):raise ValueError('Incomplete/nonfinite data')
    metadata=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    # draw() plots only supplied arrays; data() and main() are never called.
    checks=model.draw(record['kind'],fields,values,folder)
    metadata['data_frame_checks']=checks
    metadata['component_redraw_scope']='Unchanged original synthetic inputs only; no experimental-data adaptation claimed.'
    (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
