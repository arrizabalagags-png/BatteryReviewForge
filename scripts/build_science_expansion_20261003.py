"""Build only 100 additional science demos; never construct a website.

Default output is an independent evidence tree. --install copies ONLY the new
science_* folders/full ZIPs and catalogue into source/examples and source/docs.
Old assets, community versions and frozen ready packages are not touched.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,shutil,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'examples'))
from science_models_20261003 import catalogue
import science_renderer_20261003 as renderer
sys.path.insert(0,str(ROOT/'scripts'))
from check_demo_metadata import validate_metadata

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(value):return hashlib.sha256(value).hexdigest()
def packed(path,files):
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(2026,10,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)

def install_existing(output):
    """Copy a verified existing collection; never regenerate or redraw inputs."""
    output=output.resolve()
    record=json.loads((output/'science-collection-20261003.json').read_text(encoding='utf-8'))
    qa=json.loads((output/'science-qa-20261003.json').read_text(encoding='utf-8'))
    if record['count']!=100 or qa['status']!='PASS' or qa['examples']!=100 or not qa['all_100_actual_source_csv_replayed']:
        raise ValueError('Require the complete passing 100-example actual-replay report before install')
    expected={'science_'+m.ident for m in catalogue()}
    if {r['id'] for r in record['examples']}!=expected:raise ValueError('Collection identity differs from current source')
    for row in record['examples']:
        slug=row['id'];folder=output/'showcase'/slug;archive=output/row['archive']
        if sha(archive.read_bytes())!=row['sha256']:raise ValueError('Changed archive '+slug)
        with zipfile.ZipFile(archive) as z:
            manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
            for item in manifest['files']:
                if sha(z.read(item['path']))!=item['sha256']:raise ValueError('Changed archive member '+slug)
            for filename in ['data.csv','model.json','metadata.json']:
                if z.read(slug+'/'+filename)!=(folder/filename).read_bytes():raise ValueError('Changed source input '+slug)
        for base in [ROOT/'examples/showcase',ROOT/'docs/assets/showcase']:
            target=(base/slug).resolve()
            if not target.is_relative_to(base.resolve()):raise ValueError('Unsafe install path')
            shutil.copytree(folder,target,dirs_exist_ok=True)
        shutil.copyfile(archive,ROOT/'docs/assets/showcase'/archive.name)
    shutil.copyfile(output/'science-collection-20261003.json',ROOT/'docs/assets/showcase/science-collection-20261003.json')
    print('Installed 100 verified existing examples; no inputs regenerated or site built.')
    return record

def build(output,install=False):
    output=output.resolve();output.mkdir(parents=True,exist_ok=True)
    renderer.ROOT=output/'showcase';results=[]
    for m in catalogue():
        slug='science_'+m.ident;folder=renderer.ROOT/slug;folder.mkdir(parents=True,exist_ok=True)
        with (folder/'data.csv').open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=['panel','series','x','y']);writer.writeheader();writer.writerows(m.rows)
        config=dict(schema_version=1,title=m.en,panels=m.panels,colours=renderer.COLOURS,
            input_contract='Panel is zero-based. x/y meanings and units are declared in panels. Rows are retained in original order. Author data require a reviewed adapted contract; no silent sorting, smoothing or normalisation.')
        dump(folder/'model.json',config)
        ref=m.basis['references'][0]
        meta=dict(id=slug,title=m.zh,domain='general',type='demo',license='MIT',
            scope='Original analytic teaching record. Source references support the declared method/derivation only, never this invented parameter set or measurements.',
            data_status='synthetic_demo',not_experimental_data=True,source_files=['data.csv','model.json'],
            test_conditions='No acquired cell or material. Independently declared analytic parameters, assumptions and units in scientific_basis.',
            variables_and_units={'1':[m.panels[0]['xlabel'],m.panels[0]['ylabel']]},creator='VoltPeer',generator_version='1.0.0',
            reproduce='python render_existing.py --output result-01',scientific_basis=m.basis,
            review=dict(science='Equation/units/numerical constraints and source scope checked. No author-data validation.',display='Actual cycle-marker/continuous-solid artists, four-frame spines, legend/title and text bounds checked.'))
        if ref['doi']:meta['reference']=dict(doi=ref['doi'],figure_panel=ref['figure_panel'],observation=ref['supports'],review_scope=ref['scope'],default_template=False)
        dump(folder/'metadata.json',meta)
        report=renderer.render(slug);validate_metadata(json.loads((folder/'metadata.json').read_text(encoding='utf-8')))
        code={'code/examples/showcase/science.py':(ROOT/'examples/science_renderer_20261003.py').read_bytes(),
              'code/examples/showcase/science_models_20261003.py':(ROOT/'examples/science_models_20261003.py').read_bytes(),
              'code/examples/showcase/science_references_20261003.py':(ROOT/'examples/science_references_20261003.py').read_bytes(),
              'render_existing.py':(ROOT/'examples/demo_bundle_runner.py').read_bytes(),
            'code/examples/showcase/series_policy.py':(ROOT/'skills/voltpeer-plot/scripts/batteryplot/series_policy.py').read_bytes()}
        inputs={slug+'/'+name:(folder/name).read_bytes() for name in ['data.csv','model.json','metadata.json']}
        readme=f'''# {m.en} / {m.zh}

Original analytic teaching data; NOT acquired experimental evidence.
Scientific question: {m.basis['relationship']}
Method/reference: {ref['title']} — {ref['url']}
Reference location: {ref['figure_panel']}
Our equation: {m.basis['equations'][0]}
Applicability: {m.basis['limitations'][0]}
No paper pixels, numerical measurements or material fit are reproduced.

Extract SOURCE and CSV components into the SAME new folder, preserving paths.
Use a project virtual environment: pip install -r requirements.txt
Run: python render_existing.py --output result-01
The output folder must be new. Outputs: PNG, SVG, PDF, metadata, RUN_RECORD.json.
The default entry reads existing CSV only; the generator module is documentary.
To use author data, inspect model.json units and metadata conditions, adapt a copy
and keep provenance. Data substitution produces author_supplied_unverified status.
Do not label replaced data as synthetic or certify mechanisms from this package.
Cycle CE/capacity/retention use points without connecting lines; continuous voltage/spectra use solid traces without markers. All four data-axis borders are shown; this is the user display preference.

这份输入是原创解析教学数据，不能充当实验结果。将源码和CSV组件解压到同一新目录，
按上面命令重画，输出PNG/SVG/PDF。换作者数据前核对字段、单位、条件与适用边界。
不重新生成已有CSV、不平滑原始数据、不静默覆盖旧结果；逐圈CE、容量和保持率使用散点、不加连线；连续电压/光谱使用无点实线。
'''
        payload={**code,**inputs,'README.md':readme.encode('utf-8'),'LICENSE':(ROOT/'LICENSE').read_bytes(),
            'requirements.txt':b'numpy>=1.26,<3\nmatplotlib>=3.8,<4\nscipy>=1.11,<2\n'}
        for ext in ['png','svg','pdf']:payload['reference/figure.'+ext]=(folder/('figure.'+ext)).read_bytes()
        payload['reference/metadata.json']=(folder/'metadata.json').read_bytes()
        manifest=dict(schema_version=1,sample=slug,renderer='examples/showcase/science.py',entry_point='render_existing.py',operation='render_existing_inputs_only',
            code=[dict(archive_path=p,sha256=sha(v)) for p,v in code.items()],
            inputs=[dict(archive_path=p,render_path=p,sha256=sha(v)) for p,v in inputs.items()],
            files=[dict(path=p,sha256=sha(v)) for p,v in payload.items()])
        payload['SOURCE_MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        archive=output/f'BRF-demo-{slug}.zip';packed(archive,payload)
        # Independently split delivery in the evidence tree; the site splitter
        # can produce identical contracts when root builds the website later.
        base=output/'split-demos'/slug
        source={**code,'README.md':payload['README.md'],'requirements.txt':payload['requirements.txt'],'LICENSE':payload['LICENSE'],
            'SOURCE_MANIFEST.json':payload['SOURCE_MANIFEST.json']}
        figures={p:v for p,v in payload.items() if p.startswith('reference/')}
        components={}
        for kind,files in [('source',source),('data',inputs),('figures',figures)]:
            path=base/f'{slug}-{kind}.zip';packed(path,files);components[kind]=dict(file=path.name,sha256=sha(path.read_bytes()),bytes=path.stat().st_size)
        prompt=f'请使用 {m.zh} 的源码和 CSV 包重画已有输入。先读 README、model.json 和 metadata.json 的科学关系、单位、条件与边界。示例是教学合成数据，不能当作实验结果。收到我的真实数据后先核对输入约定并保留原始数据副本；不要补造、静默平滑或重新生成数据。逐圈CE、容量和保持率散点、无连线；连续电压/光谱无点实线，数据图保留四边框。输出到新目录，给出 PNG/SVG/PDF 与来源说明。\n\nUse this source and CSV to redraw existing inputs. Read the declared relation, units, conditions and limits first. Synthetic teaching inputs are not experimental results. Check author inputs and preserve original data before adapting. No fabrication, regeneration, silent smoothing or overwrite. Cycle CE/capacity/retention: marker-only, no connecting lines. Continuous voltage/spectra: solid unmarked traces. Four data-axis borders. New output folder; PNG/SVG/PDF and provenance.\n'
        path=base/f'{slug}-prompt.txt';path.write_text(prompt,encoding='utf-8');components['prompt']=dict(file=path.name,sha256=sha(path.read_bytes()),bytes=path.stat().st_size)
        dump(base/'components.json',components)
        results.append(dict(id=slug,title=m.zh,title_en=m.en,family=m.family,rows=len(m.rows),panels=len(m.panels),reference=ref,
            scientific_basis=m.basis,archive=archive.name,sha256=sha(archive.read_bytes()),render=report,components=components))
        if install:
            source_dest=ROOT/'examples/showcase'/slug;site_dest=ROOT/'docs/assets/showcase'/slug
            shutil.copytree(folder,source_dest,dirs_exist_ok=True);shutil.copytree(folder,site_dest,dirs_exist_ok=True)
            shutil.copyfile(archive,site_dest.parent/archive.name)
        print(f'{len(results):03d}/100 {slug}',flush=True)
    record=dict(count=len(results),data_status='original_analytic_teaching_not_experimental',families={f:sum(r['family']==f for r in results) for f in sorted({r['family'] for r in results})},examples=results)
    dump(output/'science-collection-20261003.json',record)
    if install:shutil.copyfile(output/'science-collection-20261003.json',ROOT/'docs/assets/showcase/science-collection-20261003.json')
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-root',type=Path,default=ROOT.parent/'deployment/evidence/2026-10-03/science-expansion/generated')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--install',action='store_true');mode.add_argument('--install-existing',action='store_true')
    a=p.parse_args()
    if a.install_existing:install_existing(a.output_root)
    else:build(a.output_root,a.install)
