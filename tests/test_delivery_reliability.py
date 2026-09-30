"""Exercise actual outputs and failure boundaries, including Windows path fixtures."""
from __future__ import annotations
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
FIGURE = ROOT / 'skills/battery-review-figure'
ASSEMBLY = ROOT / 'skills/battery-figure-assemble'
sys.path.insert(0, str(FIGURE / 'scripts'))
sys.path.insert(0, str(ASSEMBLY / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts'))

from batteryplot import DataContractError, cycling_capacity, save_bundle
from batteryplot.specification import resolve_specification
from batterycompose.assets import _svg_pdf
from batterycompose.layout import ComposeError
from delivery_contract import collect_working_bundle, check_working_bundle, digest
from output_safety import reserve_stem
from share_bundle import create_share_bundle
from check_skill_distribution import check_skill
from workflow_eval import prepare, record, suite, validate_cases
from runtime_contract.check_task_state import validate


def inputs(folder):
    data = folder / '中文 原始数据.csv'
    data.write_text('series,cycle,discharge_capacity\nSYNTHETIC,1,150\nSYNTHETIC,2,149\nSYNTHETIC,3,148\n', encoding='utf-8-sig')
    context = {'source_id':'synthetic:qa','evidence_state':'verified','chemistry':'DEMO only','cell_configuration':'full cell',
        'temperature_c':'25','rate':'1 C','voltage_window_v':'2.5-4.2','capacity_basis':'cathode active mass','capacity_unit':'mAh g-1',
        'loading_mg_cm2':'2','electrolyte_ul_mg':'10','np_ratio':'1.1','cell_format':'synthetic coin','formation_protocol':'synthetic test','pressure_mpa':'0.1'}
    config = {'kind':'full_cell_cycling','style':'forge','columns':{},'common':context,'claim':'SYNTHETIC QA only','caption_notes':'Not experimental data.'}
    metadata = folder / '中文 映射.json'
    metadata.write_text(json.dumps(config,ensure_ascii=False),encoding='utf-8-sig')
    return data, metadata


def run(command, cwd=None):
    return subprocess.run([sys.executable, '-X', 'utf8'] + list(map(str,command)), cwd=cwd, capture_output=True, encoding='utf-8', timeout=90)


class ReliabilityTests(unittest.TestCase):
    def test_result_first_bundle_exports_real_lzw_and_preserves_versions(self):
        with tempfile.TemporaryDirectory(prefix='科研 输入 空格 ') as temp:
            root = Path(temp); data, metadata = inputs(root)
            command = [FIGURE/'scripts/deliver.py','--data',data,'--metadata',metadata,'--out',root/'图件 结果',
                       '--png-dpi','300','--tiff-dpi','600']
            first=run(command); self.assertEqual(first.returncode,0,first.stderr)
            working=root/'图件 结果'; self.assertTrue((working/'index.html').is_file())
            self.assertTrue((working/'results/figure.pdf').is_file())
            old_hash = digest(working/'results/figure.pdf')
            # Feed a real Matplotlib SVG (including its standard header) back into composition.
            vector_pdf = _svg_pdf(working/'results/figure.svg')
            self.assertEqual(len(PdfReader(io.BytesIO(vector_pdf)).pages),1)
            with Image.open(working/'results/figure.tiff') as image:
                self.assertEqual(image.tag_v2[259],5)  # TIFF LZW, not a filename assertion.
                self.assertAlmostEqual(image.info['dpi'][0],600,delta=1)
                dimensions=image.size
            with Image.open(working/'results/figure.png') as image:
                self.assertAlmostEqual(image.info['dpi'][0],300,delta=1)
                self.assertGreater(dimensions[0],image.width*1.9)
            info=json.loads((working/'.voltpeer/records/figure.provenance.json').read_text(encoding='utf-8'))
            self.assertEqual(info['specification']['status'],'journal_neutral_preview')
            self.assertIsNone(info['dpi_by_format']['pdf']);self.assertEqual(info['dpi_by_format']['tiff'],600)
            state=json.loads((working/'.voltpeer/TASK_STATE.json').read_text(encoding='utf-8'))
            self.assertEqual(validate(state,working/'.voltpeer'),[])
            self.assertEqual(check_working_bundle(working),[])
            second=run(command);self.assertEqual(second.returncode,0,second.stderr)
            self.assertTrue((root/'图件 结果_v002/results/figure.pdf').is_file())
            self.assertEqual(digest(working/'results/figure.pdf'),old_hash)
            self.assertNotIn('source_sha256',first.stdout)

    def test_dpi_content_range_and_missing_profile_are_not_guessed(self):
        profile={'profile_id':'wiley_general','line_art_raster_dpi':[600,1000],'image_raster_dpi':300}
        with self.assertRaises(DataContractError): resolve_specification(profile,content_class='line_art')
        self.assertEqual(resolve_specification(profile,content_class='image')['dpi'],300)
        choice=resolve_specification(profile,requested_dpi=800)
        self.assertEqual(choice['status'],'author_requested');self.assertEqual(choice['dpi'],800)
        with self.assertRaises(DataContractError):resolve_specification({'profile_id':'nature'})
        with self.assertRaises(DataContractError):resolve_specification(profile,dpi_by_format={'pdf':600})
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);data,meta=inputs(root)
            result=run([FIGURE/'scripts/deliver.py','--data',data,'--metadata',meta,'--out',root/'unused','--journal','nature'])
            self.assertNotEqual(result.returncode,0);self.assertFalse((root/'unused').exists())

    def test_exclusive_export_reservation_keeps_concurrent_names_distinct(self):
        with tempfile.TemporaryDirectory() as temp:
            stem=Path(temp)/'Fig.3'
            with reserve_stem(stem,('.pdf',)) as (first,_):
                with reserve_stem(stem,('.pdf',)) as (second,version):
                    self.assertNotEqual(first,second);self.assertEqual(version,2)
                    Path(str(second)+'.pdf').write_bytes(b'new')
            self.assertFalse(list(Path(temp).glob('*.lock')))
            self.assertEqual(Path(str(second)+'.pdf').read_bytes(),b'new')

    def test_pdf_audit_help_is_lazy_without_importing_optional_library(self):
        code='import runpy,sys;sys.modules["pymupdf"]=None;sys.argv=["audit_pdf_fonts.py","--help"];runpy.run_path(sys.argv[0],run_name="__main__")'
        result=run(['-c',code],cwd=FIGURE/'scripts')
        self.assertEqual(result.returncode,0,result.stderr);self.assertIn('usage:',result.stdout)

    def test_missing_native_cairo_reports_fallback_after_svg_safety(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'panel.svg';path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20"/></svg>')
            original=__import__('builtins').__import__
            def without_cairo(name,*args,**kwargs):
                if name=='cairosvg':raise OSError('native Cairo missing')
                return original(name,*args,**kwargs)
            with patch('builtins.__import__',side_effect=without_cairo):
                with self.assertRaisesRegex(ComposeError,'vector PDF'):_svg_pdf(path)
                path.write_text('<!DOCTYPE svg SYSTEM "https://example.com/private"><svg/>')
                with self.assertRaisesRegex(ComposeError,'external or entity'):_svg_pdf(path)

    def test_assembly_cli_help_does_not_create_help_directory_and_pdf_fallback_runs(self):
        with tempfile.TemporaryDirectory(prefix='科研 拼版 ') as temp:
            root=Path(temp)
            result=run([ASSEMBLY/'examples/demo_assemble.py','--help'],cwd=root)
            self.assertEqual(result.returncode,0,result.stderr);self.assertFalse(list(root.iterdir()))
            demo=run([ASSEMBLY/'examples/demo_assemble.py','--output',root/'演示 来源','--without-svg'])
            self.assertEqual(demo.returncode,0,demo.stderr)
            manifest=root/'演示 来源/demo_manifest.json'
            manifest.write_text(manifest.read_text(encoding='utf-8'),encoding='utf-8-sig')
            result=run([ASSEMBLY/'scripts/compose_figure.py','deliver','--manifest',manifest,'--out',root/'拼版 结果'])
            self.assertEqual(result.returncode,0,result.stderr)
            working=root/'拼版 结果'
            self.assertTrue((working/'results/figure.pdf').is_file())
            self.assertEqual(len(PdfReader(working/'results/figure.pdf').pages),1)
            self.assertFalse((working/'results/alignment-check.record.png').exists())
            self.assertTrue((working/'.voltpeer/records/alignment-check.record.png').is_file())
            self.assertEqual(check_working_bundle(working),[])

    def test_share_bundle_requires_rights_and_excludes_recovery_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);data,meta=inputs(root)
            result=run([FIGURE/'scripts/deliver.py','--data',data,'--metadata',meta,'--out',root/'working'])
            self.assertEqual(result.returncode,0,result.stderr)
            working=root/'working'
            with self.assertRaises(ValueError):create_share_bundle(working,root/'share',rights_confirmed=False,license_name='CC BY 4.0')
            self.assertFalse((root/'share').exists())
            share=create_share_bundle(working,root/'share',rights_confirmed=True,license_name='CC BY 4.0')
            self.assertFalse((share/'.voltpeer').exists())
            self.assertFalse(list(share.rglob('*.csv')));self.assertFalse(list(share.rglob('*provenance*')))
            self.assertNotIn(str(root),''.join(path.read_text(encoding='utf-8') for path in share.glob('*.json')))
            pdf=next(share.glob('*.pdf'));self.assertNotIn('/Author',PdfReader(pdf).metadata)
            source=working/'results/figure.png';source.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'变化'):create_share_bundle(working,root/'share2',rights_confirmed=True,license_name='CC BY 4.0')
            self.assertFalse((root/'share2').exists())

    def test_share_svg_blocks_scripts_and_local_paths_without_silent_removal(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source.svg'
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Safe</text><script>alert(1)</script></svg>')
            working=collect_working_bundle([source],root/'working',skill_id='battery-review-figure',objective='QA')
            with self.assertRaises(ValueError):create_share_bundle(working,root/'share',rights_confirmed=True,license_name='CC BY 4.0')
            self.assertFalse((root/'share').exists())

    def test_standalone_reference_check_catches_removed_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            copy=Path(temp)/'assembly';shutil.copytree(ASSEMBLY,copy,ignore=shutil.ignore_patterns('__pycache__'))
            self.assertEqual(check_skill(copy),[])
            (copy/'references/shared/battery-review-figure/references/STYLE_PRESETS.md').unlink()
            self.assertTrue(check_skill(copy))

    def test_eval_preparation_is_not_model_execution_and_resume_has_real_hash_drift(self):
        self.assertEqual(validate_cases(suite()),[])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);workspace=prepare('battery-claim-check-resume',root/'run')
            self.assertTrue((workspace/'.git/HEAD').is_file())
            self.assertNotIn('expected',(workspace/'TASK.md').read_text(encoding='utf-8'))
            state=json.loads((workspace/'old-working/.voltpeer/TASK_STATE.json').read_text(encoding='utf-8'))
            self.assertTrue(any('hash mismatch' in message for message in validate(state,workspace/'old-working/.voltpeer')))
            self.assertEqual(json.loads((workspace/'EVAL_RUN.json').read_text())['execution_status'],'NOT_RUN')
            review=root/'review.json';review.write_text(json.dumps({'case_id':'battery-claim-check-resume','host':'DSH','host_version':'test','model_id':'deepseek-flash','reviewer':'test','observations':[]}))
            with self.assertRaises(ValueError):record(workspace,review,root/'invalid-evidence')

    @unittest.skipUnless(shutil.which('pwsh') or shutil.which('powershell'),'PowerShell unavailable')
    def test_desktop_installer_uses_chinese_workspace_and_keeps_other_skills(self):
        shell=shutil.which('pwsh') or shutil.which('powershell')
        with tempfile.TemporaryDirectory(prefix='研究 项目 ') as temp:
            root=Path(temp);package=root/'package';source=package/'skills/battery-test';source.mkdir(parents=True)
            (source/'SKILL.md').write_text('test');shutil.copyfile(ROOT/'install.ps1',package/'install.ps1')
            workspace=root/'课题 工作区';workspace.mkdir()
            other=workspace/'.dsh/skills/other';other.mkdir(parents=True);(other/'SKILL.md').write_text('keep')
            result=subprocess.run([shell,'-NoProfile','-File',str(package/'install.ps1'),'-Workspace',str(workspace)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((workspace/'.dsh/skills/battery-test/SKILL.md').exists())
            self.assertEqual((other/'SKILL.md').read_text(),'keep')


if __name__ == '__main__':
    unittest.main()
