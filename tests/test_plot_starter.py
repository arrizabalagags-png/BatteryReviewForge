"""Execute a downloaded Starter, including failure boundaries; no model/API calls."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PlotStarterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="VoltPeer 新手包 中文 空格 ")
        cls.folder = Path(cls.temp.name)
        output = cls.folder / "downloads"
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/package_plot_starter.py"), "--out", str(output)],
                                   capture_output=True, text=True, encoding="utf-8")
        if completed.returncode:
            raise RuntimeError(completed.stdout + completed.stderr)
        cls.row = json.loads(completed.stdout)
        cls.archive = output / cls.row["file"]
        with ZipFile(cls.archive) as archive:
            assert archive.testzip() is None
            archive.extractall(cls.folder / "解压独立运行")
        cls.pack = cls.folder / "解压独立运行/plot_starter"
        cls.env = {**os.environ, "PYTHONUTF8":"1", "MPLBACKEND":"Agg"}
        cls.demos = json.loads((cls.pack / "DEMO_INDEX.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def command(self, *args):
        return subprocess.run([sys.executable, str(self.pack / "start.py"), *map(str,args)], cwd=self.folder,
                              env=self.env, capture_output=True, text=True, encoding="utf-8")

    def author_fixture(self, name):
        folder = self.folder / name
        folder.mkdir()
        row = self.demos["coulombic_efficiency"]
        data = folder / "原数据 中文.csv"
        data.write_bytes((self.pack / row["data"]).read_bytes())
        config = json.loads((self.pack / row["metadata"]).read_text(encoding="utf-8"))
        config["common"]["source_id"] = "ENGINEERING-UPLOAD-FIXTURE-NOT-EXPERIMENT"
        config["claim"] = "作者输入格式的工程试验，非实验结论"
        metadata = folder / "已确认映射.json"
        metadata.write_text(json.dumps(config,ensure_ascii=False),encoding="utf-8-sig")
        return data,metadata,config

    def test_archive_self_contained_one_runtime(self):
        manifest = json.loads((self.pack / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
        # Compare downloaded file closure, not __pycache__ created by later execution.
        with ZipFile(self.archive) as archive:
            files = {name.removeprefix('plot_starter/') for name in archive.namelist()
                     if name != 'plot_starter/PACKAGE_MANIFEST.json'}
        self.assertEqual(files,{row["path"] for row in manifest["files"]})
        for row in manifest["files"]:
            self.assertEqual(digest(self.pack / row["path"]),row["sha256"])
        self.assertEqual(digest(self.archive),self.row["sha256"])
        self.assertEqual(len(list(self.pack.rglob("batteryplot/__init__.py"))),1)
        self.assertEqual(set(self.demos),set(self.row["plot_kinds"]))
        result = self.command("check")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["native_host_discovery"],"NOT_TESTED")

    def test_new_starter_refuses_legacy_plot_and_preserves_customisations(self):
        workspace=self.folder/'旧技能项目';workspace.mkdir()
        old=workspace/'.dsh/skills/battery-review-figure';old.mkdir(parents=True)
        (old/'SKILL.md').write_text('author customised old plotting skill',encoding='utf-8')
        (old/'custom.json').write_text('{"keep":"old author configuration"}',encoding='utf-8')
        before={p.name:digest(p) for p in old.iterdir()}
        result=self.command('install','--host','dsh','--workspace',workspace)
        self.assertEqual(result.returncode,2,result.stdout)
        self.assertIn('explicit migration',result.stderr)
        self.assertEqual({p.name:digest(p) for p in old.iterdir()},before)
        self.assertFalse((workspace/'.dsh/skills/voltpeer-plot').exists())

    def test_inspect_styles_and_confirmed_nonstandard_mapping(self):
        data,metadata,config=self.author_fixture("非标准真实表头")
        content=data.read_text(encoding='utf-8').replace('series,cycle,ce_pct','batch_id,my_cycle,my_percent')
        data.write_text(content,encoding='utf-8')
        inspect=self.command('inspect','--data',data)
        self.assertEqual(inspect.returncode,0,inspect.stderr)
        self.assertEqual(json.loads(inspect.stdout)['matching_plot_types'],{})
        config['columns']={'series':'batch_id','cycle':'my_cycle','ce_pct':'my_percent'}
        metadata.write_text(json.dumps(config),encoding='utf-8')
        actual=self.command('plot','--data',data,'--metadata',metadata,'--out',self.folder/'confirmed-fields')
        self.assertEqual(actual.returncode,0,actual.stderr)
        styles=self.command('styles')
        self.assertEqual(styles.returncode,0,styles.stderr)
        self.assertIn('forge',styles.stdout)

    def test_changed_package_is_rejected_before_install(self):
        path=self.pack/'INPUT_GUIDE.md';saved=path.read_bytes()
        try:
            path.write_bytes(saved+b'changed')
            failed=self.command('check')
            self.assertEqual(failed.returncode,2)
            self.assertIn('missing or changed',failed.stderr)
        finally:
            path.write_bytes(saved)

    def test_style_inheritance_explicit_change_and_unknown_style(self):
        data,metadata,config=self.author_fixture('明确配色')
        config['style']='rose_blue'
        metadata.write_text(json.dumps(config),encoding='utf-8')
        before=[digest(data),digest(metadata)]
        for cli,expected,explicit in (([], 'rose_blue',False),(['--style','peach_ice'],'peach_ice',True)):
            result=self.command('plot','--data',data,'--metadata',metadata,'--out',self.folder/('palette-'+expected),*cli)
            self.assertEqual(result.returncode,0,result.stderr)
            bundle=Path(json.loads(result.stdout)['preview']).parent
            record=json.loads((bundle/'.voltpeer/records/figure.provenance.json').read_text(encoding='utf-8'))
            self.assertEqual(record['style'],expected)
            self.assertEqual(record['style_selection']['metadata_style'],'rose_blue')
            self.assertEqual(record['style_selection']['explicit_change'],explicit)
            self.assertEqual([digest(data),digest(metadata)],before)
        demo=self.command('demo','--style','thermal_balance','--out',self.folder/'selected-demo')
        self.assertEqual(demo.returncode,0,demo.stderr)
        bundle=Path(json.loads(demo.stdout)['preview']).parent
        record=json.loads((bundle/'.voltpeer/records/figure.provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(record['style'],'thermal_balance')
        failed=self.command('plot','--data',data,'--metadata',metadata,'--out',self.folder/'bad-palette','--style','made-up')
        self.assertEqual(failed.returncode,2)
        self.assertIn('Unknown style',failed.stderr)
        self.assertEqual([digest(data),digest(metadata)],before)

    def test_packager_does_not_replace_output_directory_file(self):
        target=self.folder/'existing-user-file';target.write_text('preserve me',encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/package_plot_starter.py'),'--out',str(target)],
                              capture_output=True,text=True,encoding='utf-8',env=self.env)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(target.read_text(encoding='utf-8'),'preserve me')

    def test_all_ten_extracted_demo_exports(self):
        for kind,row in self.demos.items():
            with self.subTest(kind=kind):
                data,metadata = self.pack / row["data"],self.pack / row["metadata"]
                before = [digest(data),digest(metadata)]
                result = self.command("demo","--kind",kind,"--out",self.folder / ("demo-"+kind))
                self.assertEqual(result.returncode,0,result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(record["data_status"],"synthetic_demo")
                bundle = Path(record["preview"]).parent
                self.assertTrue(Path(record["preview"]).is_file())
                for suffix in ("pdf","svg","png"):
                    self.assertTrue((bundle / "results" / ("figure."+suffix)).is_file())
                provenance = json.loads((bundle / ".voltpeer/records/figure.provenance.json").read_text(encoding="utf-8"))
                self.assertEqual(provenance["source_sha256"],before[0])
                self.assertEqual(provenance["raster_dpi"],300)
                for panel in provenance["actual_artist_checks"]:
                    self.assertTrue(all(panel["spines"].values()))
                    for curve in panel["continuous_curves"]:
                        self.assertEqual(curve["linestyle"],"-")
                        self.assertIn(curve["marker"],(None,"None",""," "))
                check = self.command("check","--working",bundle)
                self.assertEqual(check.returncode,0,check.stderr)
                self.assertEqual([digest(data),digest(metadata)],before)

    def test_actual_artists_raw_values_and_distinct_colors(self):
        code = '''
import csv,json,sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'skills/voltpeer-plot/scripts'))
from plot_uploaded import render_from_metadata
demos=json.loads((root/'DEMO_INDEX.json').read_text(encoding='utf-8'))
for kind,row in demos.items():
    data=root/row['data'];mapping=root/row['metadata'];fig,config=render_from_metadata(data,mapping)
    records=list(csv.DictReader(data.open(encoding='utf-8')))
    ax=fig.axes[0];lines=ax.lines
    colors=[to_hex(line.get_color()) for line in lines]
    assert len(colors)==len(set(colors)), (kind,colors)
    assert all(line.get_linestyle()=='-' and line.get_marker() in (None,'None','', ' ') for line in lines)
    assert all(ax.spines[side].get_visible() for side in ('left','right','top','bottom'))
    if kind=='coulombic_efficiency':
        for line in lines:
            original=[r for r in records if r['series']==line.get_label()]
            assert np.array_equal(line.get_xdata(),[float(r['cycle']) for r in original])
            assert np.array_equal(line.get_ydata(),[float(r['ce_pct']) for r in original])
    plt.close(fig)
print('10 raw-artist routes; original values unchanged; distinct solid markerless curves and data frames')
'''
        result = subprocess.run([sys.executable,"-c",code,str(self.pack)],env=self.env,cwd=self.folder,
                                capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("original values unchanged",result.stdout)

    def test_author_anomaly_is_preserved_outside_public_demo(self):
        # A measured anomaly must survive plotting. It is an engineering fixture,
        # not a scientifically plausible synthetic cell offered to learners.
        data, metadata, _ = self.author_fixture("作者异常保留")
        data.write_text("series,cycle,ce_pct\nAuthor,1,99.2\nAuthor,2,100.5\nAuthor,3,98.8\n", encoding="utf-8")
        before = digest(data)
        code = '''
import sys,json
from pathlib import Path
import numpy as np
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'skills/voltpeer-plot/scripts'))
from plot_uploaded import render_from_metadata
fig,config=render_from_metadata(Path(sys.argv[2]),Path(sys.argv[3]))
assert np.array_equal(fig.axes[0].lines[0].get_ydata(),[99.2,100.5,98.8])
assert fig.axes[0].get_ylim()[1]>100.5
print('author anomaly preserved')
'''
        result = subprocess.run([sys.executable,"-c",code,str(self.pack),str(data),str(metadata)],
                                env=self.env,capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("author anomaly preserved",result.stdout)
        self.assertEqual(digest(data),before)

    def test_public_demo_charge_and_source_relationships(self):
        models = json.loads((self.pack/"DEMO_MODELS.json").read_text(encoding="utf-8"))
        self.assertEqual(set(models["models"]),set(self.demos))
        self.assertEqual(models["data_origin"],"original_synthetic")
        for relative, expected in models["adapted_sources"].items():
            self.assertEqual(digest(ROOT/relative),expected,relative)
        ce_row=self.demos["coulombic_efficiency"]
        with (self.pack/ce_row["data"]).open(encoding="utf-8") as stream:
            records=list(csv.DictReader(stream))
        for row in records:
            plated=float(row["q_plated_mAh_cm2"]); stripped=float(row["q_stripped_mAh_cm2"])
            self.assertGreater(plated,0)
            self.assertGreaterEqual(stripped,0)
            self.assertLessEqual(stripped,plated)
            self.assertAlmostEqual(float(row["ce_pct"]),100*stripped/plated,places=8)
        # Derived retention must agree with the delivered capacity, including
        # activation above 100%; this check must never clip author uploads.
        with (self.pack/self.demos["half_cell_cycling"]["data"]).open(encoding="utf-8") as stream:
            capacities={(r["series"],r["cycle"]):float(r["discharge_capacity"]) for r in csv.DictReader(stream)}
        with (self.pack/self.demos["cycle_retention"]["data"]).open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                q=capacities[row["series"],row["cycle"]]
                q0=capacities[row["series"],"1"]
                self.assertAlmostEqual(float(row["retention_pct"]),100*q/q0,places=8)

    def test_missing_scientific_fields_stop_without_modifying_input(self):
        data,metadata,config = self.author_fixture("缺信息")
        del config["common"]["ce_definition"]
        metadata.write_text(json.dumps(config),encoding="utf-8")
        before = [digest(data),digest(metadata)]
        out = self.folder / "must-not-create"
        result = self.command("plot","--data",data,"--metadata",metadata,"--out",out)
        self.assertEqual(result.returncode,2)
        self.assertIn("ce_definition",result.stderr)
        self.assertFalse(out.exists())
        self.assertEqual([digest(data),digest(metadata)],before)

    def test_unknown_metadata_and_nr_nv_stop(self):
        data,metadata,config = self.author_fixture("错误键")
        for mutation,expected in (({"figure_size_mm":[89,65]},"Unknown metadata keys"),
                                  ({"common":{**config["common"],"rate":"NR"}},"NR"),
                                  ({"common":{**config["common"],"rate":"NV"}},"NV")):
            with self.subTest(mutation=expected):
                metadata.write_text(json.dumps({**config,**mutation}),encoding="utf-8")
                result=self.command("plot","--data",data,"--metadata",metadata,"--out",self.folder / ("blocked-"+expected))
                self.assertEqual(result.returncode,2)
                self.assertIn(expected,result.stderr)

    def test_bundled_demo_is_not_author_fallback(self):
        row=self.demos["coulombic_efficiency"]
        result=self.command("plot","--data",self.pack / row["data"],"--metadata",self.pack / row["metadata"],"--out",self.folder / "not-author")
        self.assertEqual(result.returncode,2)
        self.assertIn("synthetic input",result.stderr)

    def test_author_delivery_versions_and_integrity_failure(self):
        data,metadata,_=self.author_fixture("独立原数据")
        before=[digest(data),digest(metadata)]
        out=self.folder / "原图保存"
        first=self.command("plot","--data",data,"--metadata",metadata,"--out",out)
        self.assertEqual(first.returncode,0,first.stderr)
        first_files={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}
        second=self.command("plot","--data",data,"--metadata",metadata,"--out",out)
        self.assertEqual(second.returncode,0,second.stderr)
        actual=Path(json.loads(second.stdout)["preview"]).parent
        self.assertNotEqual(actual,out)
        self.assertTrue(actual.name.endswith("_v002"),actual)
        self.assertEqual(first_files,{p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
        self.assertEqual([digest(data),digest(metadata)],before)
        (actual / "results/figure.png").write_bytes(b"changed")
        failed=self.command("check","--working",actual)
        self.assertEqual(failed.returncode,2)

    def test_dsh_and_codex_install_same_source_no_overwrite(self):
        canonical=(self.pack / "skills/voltpeer-plot/SKILL.md").read_bytes()
        for host,path in (("dsh",".dsh/skills"),("codex",".agents/skills")):
            with self.subTest(host=host):
                workspace=self.folder / ("新项目 "+host);workspace.mkdir()
                copied=self.command("install","--host",host,"--workspace",workspace)
                self.assertEqual(copied.returncode,0,copied.stderr)
                self.assertEqual(json.loads(copied.stdout)["status"],"copied")
                self.assertEqual((workspace/path/"voltpeer-plot/SKILL.md").read_bytes(),canonical)
                conflict=self.command("install","--host",host,"--workspace",workspace)
                self.assertEqual(conflict.returncode,2)
                alternate=self.command("install","--host","codex" if host=="dsh" else "dsh","--workspace",workspace)
                self.assertEqual(alternate.returncode,2)
        parent=self.folder / "git项目";parent.mkdir();(parent/".git").mkdir()
        child=parent/"子目录";child.mkdir()
        refused=self.command("install","--workspace",child)
        self.assertEqual(refused.returncode,2)
        self.assertIn("nearest Git project root",refused.stderr)
        missing=self.command("install","--workspace",self.folder/"不存在")
        self.assertEqual(missing.returncode,2)

    def test_setup_owned_isolated_environment_without_key(self):
        # This test actually creates a venv, downloads/installs the shipped requirements
        # and executes Demo with that interpreter. It is not a mocked pip assertion.
        self.assertFalse((self.pack/".venv").exists())
        result=self.command("setup")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"],"runtime_ready")
        py=self.pack/".venv"/("Scripts/python.exe" if os.name=='nt' else 'bin/python')
        isolation=subprocess.run([str(py),"-c","import sys,json; print(json.dumps([sys.prefix,sys.base_prefix]))"],capture_output=True,text=True)
        prefix,base=json.loads(isolation.stdout)
        self.assertNotEqual(prefix,base)
        demo=self.command("demo","--out",self.folder/"隔离环境demo")
        self.assertEqual(demo.returncode,0,demo.stderr)
        # Reject a foreign pre-existing venv instead of mutating it.
        marker=self.pack/".venv/voltpeer-starter.json";saved=marker.read_bytes()
        marker.write_text('{"resource_id":"foreign"}',encoding="utf-8")
        refused=self.command("setup","--create-only")
        self.assertEqual(refused.returncode,2)
        marker.write_bytes(saved)


if __name__ == "__main__":
    unittest.main()
