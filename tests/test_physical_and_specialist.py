"""Regressions for observed colorbar drift and reproducible optional recipes."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/voltpeer-plot/scripts'))
from batteryplot.layout import axes_mm, measure_layout
from batteryplot.specialist import RECIPES, render_recipe


class PhysicalAndSpecialistTests(unittest.TestCase):
    def tearDown(self): plt.close('all')

    def test_colorbar_stealing_space_is_detected_after_draw(self):
        fig=plt.figure(figsize=(180/25.4,100/25.4))
        a=axes_mm(fig,left=15,top=10,width=60,height=45.6)
        b=axes_mm(fig,left=110,top=10,width=60,height=45.6)
        image=a.imshow(np.ones((76,100)),extent=(0,100,0,76),aspect='equal')
        fig.colorbar(image,ax=a)
        report=measure_layout(fig,{'a':a,'b':b},[('a','b','top'),('a','b','bottom')])
        self.assertTrue(report['failures'])
        with self.assertRaises(ValueError): measure_layout(fig,{'a':a},[])

    def test_pouch_actual_renderer_has_eight_real_edge_checks(self):
        spec=importlib.util.spec_from_file_location('showcase_build',ROOT/'examples/showcase/build.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        fig=module.figure('pouch_thermal')
        report=module.ruler_audit('pouch_thermal',fig)
        self.assertEqual(len(report['checks']),8)
        self.assertFalse(report['failures'])
        self.assertLessEqual(max(row['delta_mm'] for row in report['checks']),.3)
        letters={t.get_text():t.get_position() for t in fig.texts}
        self.assertAlmostEqual(letters['a'][0],letters['c'][0],places=8)

    def test_specialist_data_relationships_and_input_preservation(self):
        for recipe in RECIPES:
            folder=ROOT/'examples/showcase'/recipe
            before=hashlib.sha256((folder/'data.csv').read_bytes()).digest()
            with self.subTest(recipe=recipe):
                fig, report=render_recipe(recipe,folder)
                self.assertFalse(report['alignment']['failures'])
                self.assertTrue(report['alignment']['checks'])
                self.assertEqual(report['data_status'],'synthetic_demo')
                with (folder/'data.csv').open() as f: rows=list(csv.DictReader(f))
                a,b=fig.axes
                if recipe=='differential_capacity':
                    r=[row for row in rows if row['cycle']=='1']
                    q=np.array([float(row['capacity_mAh_g']) for row in r])
                    v=np.array([float(row['voltage_V']) for row in r])
                    np.testing.assert_allclose(b.lines[0].get_ydata(),np.gradient(q,v,edge_order=2))
                elif recipe=='xps_components':
                    expected=[float(r['intensity_counts'])-sum(float(r[k]) for k in ('background_counts','component_1','component_2','component_3')) for r in rows]
                    np.testing.assert_allclose(b.lines[0].get_ydata(),expected,atol=1e-9)
                    self.assertGreater(a.get_xlim()[0],a.get_xlim()[1])
                elif recipe=='gitt_pulse':
                    np.testing.assert_array_equal(a.lines[0].get_xdata(),b.lines[0].get_xdata())
                elif recipe=='ionic_conductivity':
                    # Arrhenius observations remain scatter; compare the actual
                    # PathCollection values rather than assuming a fitted line.
                    self.assertFalse(b.lines)
                    observed = b.collections[0].get_offsets()
                    np.testing.assert_allclose(observed[:,0],1000/(a.lines[0].get_xdata()+273.15))
                    np.testing.assert_allclose(observed[:,1],np.log(a.lines[0].get_ydata()/1000))
                elif recipe=='raman_series':
                    np.testing.assert_array_equal(a.lines[1].get_ydata(),b.lines[1].get_ydata())
                elif recipe=='cyclic_voltammetry':
                    self.assertTrue((np.diff(a.lines[0].get_xdata())<0).any())
                self.assertEqual(before,hashlib.sha256((folder/'data.csv').read_bytes()).digest())
                plt.close(fig)

    def test_real_cli_from_unpacked_new_demo(self):
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp)
            with zipfile.ZipFile(ROOT/'docs/assets/showcase/BRF-demo-xps_components.zip') as z:
                z.extractall(temp)
            command=[sys.executable,str(ROOT/'skills/voltpeer-plot/scripts/render_specialist.py'),
                     '--recipe','xps_components','--input-folder',str(temp/'xps_components'),
                     '--output-dir',str(temp/'result')]
            result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            for ext in ('svg','pdf','png'): self.assertGreater((temp/'result'/f'figure.{ext}').stat().st_size,1000)
            self.assertIn('<text', (temp/'result/figure.svg').read_text(encoding='utf-8'))
            import fitz
            with fitz.open(temp/'result/figure.pdf') as pdf:
                self.assertTrue(pdf.get_page_fonts(0))
                for xref, *_ in pdf.get_page_fonts(0): self.assertTrue(pdf.extract_font(xref)[3])
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,2)


if __name__=='__main__': unittest.main()
