"""Build 50 separate, paper-informed, scientifically declared teaching packages."""
from __future__ import annotations
import csv
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'examples'))
from paper_models import TASKS,generate,scientific_basis
import paper_renderer

def sha(data):return hashlib.sha256(data).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def build():
    results=[];paper_renderer.ROOT=ROOT/'examples/showcase'
    for task in TASKS:
        model=generate(task);slug='paper_'+model.ident
        folder=paper_renderer.ROOT/slug;folder.mkdir(parents=True,exist_ok=True)
        fields=['panel','series','x','y']+(['z'] if any('z'in row for row in model.rows) else [])
        with (folder/'data.csv').open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(model.rows)
        config=dict(schema_version=1,title=model.en,panels=model.panels,colours=paper_renderer.COLOURS,
            input_contract='Panel indices are zero based. x/y meanings and units come from each panel. z is the row coordinate of rectangular heatmaps. Keep each series in its original row order. Changed author data need an adapted scientific contract.')
        dump(folder/'model.json',config)
        basis=scientific_basis(model);ref=basis['references'][0]
        meta=dict(id=slug,title=model.zh,domain='photovoltaic' if model.ident.startswith('pv_') else 'storage' if model.ident.startswith('flow_') else 'general',
            type='demo',license='MIT',scope='Paper-informed original analytic teaching model; no copied points or figure.',
            data_status='synthetic_demo',not_experimental_data=True,source_files=['data.csv','model.json'],
            test_conditions='Declared analytic parameters in scientific_basis.parameters; no experimental cell or material is assigned.',
            variables_and_units={str(i+1):[p['xlabel'],p['ylabel']] for i,p in enumerate(model.panels)},creator='VoltPeer',generator_version='1.0.0',
            reproduce='python render_existing.py --output new-result-folder',scientific_basis=basis,
            reference=dict(doi=ref['doi'],figure_panel=ref['figure_panel'],observation=ref['supports'],
                review_scope=ref['scope'],default_template=False),
            review=dict(science='Analytic consistency and units checked; no material validation.',display='Actual artist, frame and text-bound checks; inspect exported figure at final size.'))
        dump(folder/'metadata.json',meta)
        report=paper_renderer.render(slug)
        from check_demo_metadata import validate_metadata
        validate_metadata(json.loads((folder/'metadata.json').read_text(encoding='utf-8')))
        if not report['axis_count'] or report['text_bbox_outside']:raise ValueError('Render gate failed: '+slug)
        destination=ROOT/'docs/assets/showcase'/slug;destination.mkdir(parents=True,exist_ok=True)
        for file in folder.iterdir():shutil.copyfile(file,destination/file.name)
        code={'code/examples/showcase/paper.py':(ROOT/'examples/paper_renderer.py').read_bytes(),
            'code/examples/showcase/paper_models.py':(ROOT/'examples/paper_models.py').read_bytes(),
            'code/examples/showcase/paper_references.py':(ROOT/'examples/paper_references.py').read_bytes(),
            'render_existing.py':(ROOT/'examples/demo_bundle_runner.py').read_bytes(),
            'code/examples/showcase/series_policy.py':(ROOT/'skills/voltpeer-plot/scripts/batteryplot/series_policy.py').read_bytes()}
        inputs={slug+'/'+name:(folder/name).read_bytes() for name in ('data.csv','model.json','metadata.json')}
        readme=f'''# {model.en} / {model.zh}

Original analytic teaching data, NOT experimental measurements.
Paper reference: {ref['title']} — {ref['url']}
Checked form / equation: {ref['figure_panel']}. Parameters are our declared teaching inputs.
No publisher points, images, material assignment or experimental fit are copied.

1. Extract Python source and CSV components into the SAME new folder.
2. In a project virtual environment: pip install -r requirements.txt
3. python render_existing.py --output result-01
Expected: result-01/figure.png, figure.svg, figure.pdf and metadata.json.
The output folder must be new; input files are never overwritten.
The default entry ONLY redraws existing CSVs; it never generates new rows.

CSV: panel,series,x,y{',z' if 'z' in fields else ''}. Read model.json for every axis/unit.
Before replacing inputs, verify units, conditions, normalisation and model applicability.
Use your assistant to adapt a copy. A different CSV is not automatically covered by
the teaching reference or model. Keep experimental data, assumptions and provenance.

Cycle capacity/CE/retention: points without connecting lines. Continuous voltage/spectra: solid, unmarked. All four data borders are visible.
Nyquist scales are equal; declared zoom windows do not discard the complete CSV.
Read metadata.json / scientific_basis for equations, assumptions and limitations.
The optional paper_models.py documents how the teaching inputs were calculated;
it is not invoked by the default entry.

把源码与 CSV 解压到同一新文件夹，用独立 Python 环境运行上面的命令。
输出是 PNG、SVG、PDF 和说明文件。换成自己的数据前，先让助手核对列名、单位、
条件和模型是否适用。示例数据是教学合成数据，不能充当论文实验结果。
'''
        payload={**code,**inputs,'README.md':readme.encode('utf-8'),
            'LICENSE':(ROOT/'LICENSE').read_bytes(),'requirements.txt':b'numpy>=2,<3\nmatplotlib>=3.8,<4\n'}
        for ext in ('png','svg','pdf'):payload['reference/figure.'+ext]=(folder/('figure.'+ext)).read_bytes()
        payload['reference/metadata.json']=(folder/'metadata.json').read_bytes()
        manifest=dict(schema_version=1,sample=slug,renderer='examples/showcase/paper.py',entry_point='render_existing.py',operation='render_existing_inputs_only',
            code=[dict(archive_path=p,sha256=sha(v)) for p,v in code.items()],
            inputs=[dict(archive_path=p,render_path=p,sha256=sha(v)) for p,v in inputs.items()],
            files=[dict(path=p,sha256=sha(v)) for p,v in payload.items()])
        payload['SOURCE_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
        archive=ROOT/'docs/assets/showcase'/('BRF-demo-'+slug+'.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as output:
            for name,data in payload.items():
                info=zipfile.ZipInfo(name,(2026,10,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;output.writestr(info,data)
        results.append(dict(id=slug,title=model.zh,title_en=model.en,family=model.family,rows=len(model.rows),panels=len(model.panels),
            reference=ref,archive=archive.name,sha256=sha(archive.read_bytes()),render=report))
    report=dict(count=len(results),data_status='original_analytic_teaching_not_experimental',examples=results)
    dump(ROOT/'docs/assets/showcase/paper-collection.json',report)
    print('Built',len(results),'paper-informed teaching models; source / CSV / figures remain separate.')
    return results

if __name__=='__main__':build()
