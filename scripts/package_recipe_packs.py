"""Prepare three independent, adaptable figure packs; version-safe ZIPs, no publication."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / 'examples/recipe_packs'
sys.path.insert(0, str(ROOT / 'scripts/runtime_contract'))
from output_safety import new_directory
from cli_runtime import configure_utf8

IDS = ('full_cell', 'li_li', 'operando_xrd')


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_config(kind):
    config = {'schema_version': 1, 'resource_id': kind, 'data_status': 'synthetic_demo', 'title': {'full_cell': 'Full-cell cycling and voltage profiles', 'li_li': 'Li symmetric cell', 'operando_xrd': 'Diffraction and measured-coordinate linkage'}[kind],
              'provenance': {'input_origin': 'original_synthetic_demo', 'demo_conditions_cleared': False},
              'labels': {}, 'style': {'width_mm': 180, 'font_pt': 8}, 'export': {'formats': ['pdf', 'svg', 'png', 'tiff'], 'png_dpi': 300, 'tiff_dpi': 300}, 'limits': {}}
    def table(name, fields):
        return {'path': 'demo/' + name + '.csv', 'columns': {field: field for field in fields}}
    if kind == 'full_cell':
        config.update({'data': {'cycling': table('cycling', ['sample', 'cycle', 'capacity', 'ce']), 'profiles': table('profiles', ['sample', 'cycle', 'capacity', 'voltage'])},
                       'units': {'cycle': '1', 'capacity': 'mAh g^-1', 'voltage': 'V', 'ce': '%'},
                       'conditions': {'common': {'cathode': 'Illustrative layered cathode', 'anode': 'Illustrative graphite', 'capacity_basis': 'Illustrative cathode active material mass', 'rate_or_current': 'Illustrative 0.5 C', 'formation': 'Illustrative two formation cycles; not experimental', 'loading_or_areal_capacity': 'Illustrative 3 mAh cm^-2', 'temperature_C': 25, 'voltage_window_V': [2.9, 4.2], 'N_P': 'not inferred', 'E_C': 'not inferred'}, 'by_sample': {}}})
    elif kind == 'li_li':
        config.update({'data': {'trace': table('trace', ['sample', 'time', 'voltage'])}, 'units': {'time': 'h', 'voltage': 'mV'}, 'view': {'zoom': [10, 14]},
                       'conditions': {'common': {'metal': 'Li', 'cell_configuration': 'Li||Li', 'area_basis': 'Illustrative projected electrode overlap area', 'current_density_mA_cm2': 1, 'half_cycle_areal_capacity_mAh_cm2': 1, 'temperature_C': 25, 'rest_protocol': 'Illustrative no rest', 'failure_rule': 'Illustrative input contains no experimental failure assignment'}, 'by_sample': {}}})
    else:
        config.update({'data': {'diffraction': table('diffraction', ['sample', 'two_theta', 'progress', 'intensity']), 'voltage': table('voltage', ['sample', 'progress', 'voltage'])},
                       'units': {'two_theta': 'deg', 'progress': 'fraction', 'intensity': 'a.u.', 'voltage': 'V'},
                       'conditions': {'common': {'radiation': 'Illustrative Cu K-alpha; not acquired', 'wavelength_A': 1.5406, 'cell_configuration': 'Illustrative operando cell', 'progress_definition': 'Illustrative fractional charging progress; not measured SOC', 'synchronization': 'Illustrative equal coordinate endpoints; no measured timestamps', 'intensity_normalization': 'Invented model values; no experimental normalization'}, 'by_sample': {}}})
    return config


GUIDE = '''# 给助手的接手说明

此包的resource_id与网站样图一致，独立源码、依赖和演示输入均已包含。先读input_contract.json和用户真实输入，不需要加载其他整套图库。只使用能读本地文件、运行Python并保存结果的Agent。

1. 在用户研究项目中解压或复制整个包。保留原文件，不修改全局安装Skill。
2. 在项目独立venv安装requirements.txt。先用config.demo.json验证运行环境；这是原创合成演示。
3. 复制config.real.example.json到新文件，核对列映射、每个样品、单位、归一化分母及测试条件。所有null需由作者资料确认，不把演示温度、体系、倍率、辐射、测试面积或SOC定义复制给真实数据。
4. 优先只改配置和显示名；格式不同再增加小CSV适配器，另存规范化数据与映射记录；确实超出契约才改项目副本src/renderer.py，记录差异并重检。
5. `python src/plot.py --config <已确认配置> --out <Working结果>`。真实缺文件、单位、面积/质量基准、工况或XRD同步时先停；不得随机生成或调用demo/generate_data.py作为真实输入后备。
6. `python checks.py --working <Working结果>`核对文件哈希和实际绘图数组记录。技术通过不等于科学审查完成。先看index.html预览，再核对原值、标签、测试条件、图例、PDF和期刊最新要求。

只交给用户结果链接和影响使用的缺口。QA/来源/状态保存在Working/.voltpeer，不能省掉或冒充已完成科学审查。Flash可读图片时做最终视觉核对；当前Pro无视觉时保留人工/具备视觉工具的检查项，不谎称看过图。

样式可继承；数据、条件与结论不能继承。既有坐标/色标范围会裁掉新值时程序停止，请用auto或经作者确认扩大范围。signed voltage不能取绝对值；XRD不得按CSV行顺序reshape，不拟合物相、不插值、不补测量点。可选CE只能读实际记录，不凭容量列猜。

本项目连续曲线默认无点实线，以不同颜色区分。所有数据坐标轴同时保留上、右、下、左四条框线，线宽和颜色一致；刻度可只放下侧和左侧。包括热图数据坐标和每个组合panel；独立色标、插图与关闭的布局轴不作为额外数据框。容量循环和可选CE都要检查，不能只改CE后遗漏容量。保留每条原始数值记录；去掉显示符号不代表删数据。检查实际图件和每个组合panel，内部记录会保存Line2D线型/marker、四边框可见性及原数组核对结果。这是项目显示规则，不是所有期刊的统一要求。

颜色按真实曲线身份分配：全电池每个样品的capacity、CE和每个cycle剖面分别计数；对称电池同一signed_voltage轨迹在全图和放大图同色；XRD色标表示强度，同步电压按样品身份区分。默认只有10种曲线色，超过时先停。可提供足够长的style.colors数组，或完整的style.curve_colors身份→颜色对象；两者不能同时给。身份见data_checks记录，不能按旧Demo样品盲套。重复/别名同色、透明色、白底对比不足2:1或sRGB距离小于0.10的颜色先停，请作者选互异颜色后复核。这是显示启发式，不宣称色盲无障碍认证；不得循环复用或自动改数据来减少曲线。

重复运行会新建带版本的Working目录。对外分享需作者确认权利、许可、姓名/课题/未公开图像；不要上传整个Working。包内src/share_bundle.py可按现有交付契约创建脱敏Share包，自动检查不代替人工审查。
'''


def prepare_sources(version):
    for kind in IDS:
        pack = PACKS / kind
        (pack / 'src').mkdir(parents=True, exist_ok=True)
        (pack / 'demo').mkdir(exist_ok=True)
        (pack / 'reference').mkdir(exist_ok=True)
        for name in ('recipe_runtime.py',):
            shutil.copy2(PACKS / '_runtime' / name, pack / 'src' / name)
        shutil.copy2(PACKS / '_runtime' / f'render_{kind}.py', pack / 'src/renderer.py')
        for name in ('output_safety.py', 'delivery_contract.py', 'share_bundle.py', 'cli_runtime.py'):
            shutil.copy2(ROOT / 'scripts/runtime_contract' / name, pack / 'src' / name)
        shutil.copy2(PACKS / '_runtime/generate_demo.py', pack / 'demo/generate_data.py')
        (pack / 'src/plot.py').write_text(f'"""Real/local data rendering; demo generation is a separate executable."""\nfrom recipe_runtime import run\n\ndef render(config, tables):\n    from renderer import render as render_figure\n    return render_figure(config, tables)\n\nif __name__ == "__main__":\n    raise SystemExit(run("{kind}", render))\n', encoding='utf-8')
        (pack / 'checks.py').write_text('"""Inspect existing outputs without publishing or calling a model."""\nimport argparse\nfrom pathlib import Path\nimport sys\nsys.path.insert(0, str(Path(__file__).resolve().parent / "src"))\nfrom recipe_runtime import verify\nfrom cli_runtime import configure_utf8\n\nif __name__ == "__main__":\n    configure_utf8()\n    parser = argparse.ArgumentParser(description="核对图件文件/输入哈希；不声称完成科学审查")\n    parser.add_argument("--working", type=Path, required=True)\n    args = parser.parse_args()\n    errors = verify(args.working)\n    print("\\n".join(errors) if errors else "Technical file/data-record checks PASS; author scientific/visual review remains pending.")\n    raise SystemExit(1 if errors else 0)\n', encoding='utf-8')
        cfg = base_config(kind)
        dump(pack / 'config.demo.json', cfg)
        real = json.loads(json.dumps(cfg))
        real['data_status'] = 'author_data'
        real['provenance'] = {'input_origin': 'author_supplied', 'demo_conditions_cleared': False}
        real['title'] = {'full_cell': 'Full-cell cycling', 'li_li': 'Symmetric-cell cycling', 'operando_xrd': 'Operando diffraction'}[kind]
        real['units'] = {k: None for k in cfg['units']}
        real['conditions']['common'] = {k: None for k in cfg['conditions']['common']}
        for table in real['data'].values():
            table['path'] = 'input/your_' + Path(table['path']).name
        if 'view' in real:
            real['view']['zoom'] = None
        dump(pack / 'config.real.example.json', real)
        required = {'full_cell': {'cycling': ['sample', 'cycle', 'capacity'], 'profiles_optional': ['sample', 'cycle', 'capacity', 'voltage'], 'ce_optional': ['ce']},
                    'li_li': {'trace': ['sample', 'time', 'voltage']},
                    'operando_xrd': {'diffraction': ['sample', 'two_theta', 'progress', 'intensity'], 'voltage_optional': ['sample', 'progress', 'voltage']}}[kind]
        units_supported = {'full_cell': {'cycle': ['1'], 'capacity': ['mAh g^-1', 'mAh cm^-2', 'mAh'], 'voltage': ['V'], 'ce': ['%']},
                           'li_li': {'time': ['h', 's'], 'voltage': ['V', 'mV']},
                           'operando_xrd': {'two_theta': ['deg'], 'progress': ['%', 'fraction', 'h', 's', 'cycle'], 'intensity': ['counts', 'a.u.'], 'voltage': ['V']}}[kind]
        required_conditions = [name for name in cfg['conditions']['common'] if name not in {'N_P', 'E_C'}]
        condition_policy = {'full_cell': 'Every required field must be confirmed per actual sample. N_P/E_C are optional reporting fields: if present they must be confirmed text (explicit not reported only after checking); omitted fields remain unknown and are never guessed. Capacity basis must match the selected mass/area/absolute unit.',
                            'li_li': 'Every required field must be confirmed per actual sample. metal is Li or Na and cell_configuration must be exactly Li||Li or Na||Na. Current density and half-cycle areal capacity must be positive; signed voltage and overlap-area basis are retained. No full-cell N/P or E/C condition is inherited.',
                            'operando_xrd': 'Every required field must be confirmed per actual sample. Wavelength must be positive; progress_definition and intensity_normalization must describe the actual coordinates/units. Optional voltage requires V, matching samples and confirmed synchronization over the same endpoints. No full-cell N/P or E/C condition is inherited.'}[kind]
        geometry = {'full_cell': 'One or more samples; uneven strictly increasing cycle records allowed. Cycles are positive integers, capacity nonnegative. Optional voltage profiles must match recorded sample/cycle and each capacity coordinate must strictly increase. Auto ranges include all values; layouts must be reviewed.',
                    'li_li': 'One or more Li/Na symmetric-cell samples; uneven strictly increasing nonnegative time records allowed, at least two points per sample. Zoom must lie within every sample trace and contain at least two points. Auto ranges retain signed voltage; layouts must be reviewed.',
                    'operando_xrd': 'One or more samples, each with its own complete unique rectangular two_theta/progress grid of at least 2x2 coordinates. CSV order may vary; coordinate-keyed lookup never fills missing cells. %/fraction progress must stay within 0..100/0..1. Auto ranges include all values; layouts must be reviewed.'}[kind]
        dump(pack / 'input_contract.json', {'schema_version': 2, 'config_schema_version': 1, 'resource_id': kind, 'format': 'UTF-8/BOM CSV long table; explicit JSON mapping; preserve raw file', 'required_columns': required,
                   'units_supported': units_supported, 'units_optional': {'full_cell': ['ce'], 'li_li': [], 'operando_xrd': ['voltage']}[kind],
                   'units_note': {'full_cell': 'capacity mAh g^-1/mAh cm^-2/mAh; explicit mass/area/absolute basis; cycle=1; voltage=V; CE=% only when recorded', 'li_li': 'time h/s; signed voltage mV/V; explicit Li||Li or Na||Na and current/half-cycle areal-capacity/overlap area basis', 'operando_xrd': '2theta deg; progress %/fraction/h/s/cycle; intensity counts/a.u.; optional voltage V; no phase inference'}[kind],
                   'required_conditions': required_conditions, 'optional_conditions': ['N_P', 'E_C'] if kind == 'full_cell' else [], 'condition_policy': condition_policy,
                   'geometry': geometry,
                   'curve_colors': {'default_palette_size': 10, 'identity_rule': {'full_cell': '<sample>:capacity / <sample>:CE / <sample>:profile:<cycle>', 'li_li': '<sample>:signed_voltage; full and zoom views share identity', 'operando_xrd': '<sample>:measured_synchronized_voltage; heatmap colormap describes intensity, not sample identity'}[kind],
                                    'custom': 'Use style.colors with enough unique opaque colours, or exact style.curve_colors mapping for all actual identities; do not provide both.',
                                    'stop_on': ['insufficient colours', 'duplicate or alias-equivalent colours', 'transparent colour', 'white-background contrast below 2:1', 'pairwise sRGB distance below 0.10'],
                                    'scope': 'Project display heuristic and actual Line2D checks; not a universal journal or colour-vision certification.'},
                   'disallowed': ['missing-data demo fallback', 'silent dropped rows', 'silent smoothing/fitting', 'duplicate coordinates overwritten', 'unknown units guessed', 'demo condition reuse in author output', 'truncated data from old limits', 'silent palette cycling or curve-identity reuse'],
                   'validation_status': 'local_engineering_checked; model_behavior_NOT_RUN; author_scientific_review_pending'})
        (pack / 'AGENT_GUIDE.md').write_text(GUIDE, encoding='utf-8')
        (pack / 'requirements.txt').write_text('# Python 3.10+; install in this project venv, never globally.\nmatplotlib>=3.8,<4\nnumpy>=1.26,<3\nPillow>=10,<13\npypdf>=4,<7\n', encoding='utf-8')
        shutil.copy2(ROOT / 'LICENSE', pack / 'LICENSE')
        dump(pack / 'VERSION.json', {'schema_version': 1, 'resource_id': kind, 'version': version, 'updated': '2026-09-30', 'status': 'Beta', 'original_code_license': 'MIT', 'generated_demo': True, 'reference_image': 'reference/figure.png', 'author_data_supported': True,
                    'derived_from_resource_id': kind, 'source_repository': 'https://github.com/arrizabalagags-png/BatteryReviewForge', 'baseline_commit': '79b4238a5a7dfc963bafc0aefacd2337f9795ba8', 'model_evals': {'deepseek-flash': 'NOT_RUN', 'deepseek-v4-pro': 'NOT_RUN'}, 'native_desktop_discovery': 'NOT_RUN'})
        dump(pack / 'sources.json', {'resource_id': kind, 'source_kind': 'VoltPeer original reproducible tutorial', 'reference': f'https://github.com/arrizabalagags-png/BatteryReviewForge/tree/79b4238a5a7dfc963bafc0aefacd2337f9795ba8/examples/showcase/{kind}', 'reference_scope': 'Original synthetic example; visual expression only, no experimental values/conditions/claims inherited by author data.', 'third_party_paper_data_included': False, 'DOI': None, 'license': 'MIT; original code and generated tutorial assets only; does not license third-party papers'})
        for name in ('figure.png', 'figure.svg', 'metadata.json'):
            shutil.copy2(ROOT / 'examples/showcase' / kind / name, pack / 'reference' / name)
        with tempfile.TemporaryDirectory(prefix='voltpeer-recipe-data-') as temp:
            demo = Path(temp) / 'invented'
            result = subprocess.run([sys.executable, str(pack / 'demo/generate_data.py'), '--out', str(demo)], capture_output=True, text=True, encoding='utf-8')
            if result.returncode:
                raise RuntimeError(result.stderr or result.stdout)
            for file in demo.glob('*.csv'):
                shutil.copy2(file, pack / 'demo' / file.name)
        metadata = json.loads((pack / 'VERSION.json').read_text(encoding='utf-8'))
        metadata['demo_sha256'] = {p.relative_to(pack).as_posix(): digest(p) for p in sorted((pack / 'demo').glob('*.csv'))}
        dump(pack / 'VERSION.json', metadata)
        (pack / 'README.md').write_text(f'# VoltPeer 可复现绘图包：{kind}\n\nresource_id=`{kind}`，候选版本{version} / Beta。源码、演示、依赖、输入契约和接手说明均在本包，不要求完整仓库或全局Skill。\n\n## 先验证环境\n\n在包目录创建项目venv，使用其Python：\n\n```text\npython -m pip install -r requirements.txt\npython src/plot.py --config config.demo.json --out Working-demo\npython checks.py --working Working-demo\n```\n\n演示为原创合成数据，仅供理解布局。参考图来自同resource_id原始合成样图；新源码接收长表、动态分组和范围，不要求数值/条件与参考图相同。\n\n## 换作者数据\n\n先读AGENT_GUIDE.md、input_contract.json。复制config.real.example.json为新配置；按真实资料填全列映射、单位、归一化基准和工况，确认demo_conditions_cleared。命令同上，将--config换成新文件；没有缺数据后备。\n\n输出打开index.html，实际图件在results，内部检查/原文件/恢复状态在.voltpeer。重复运行新建版本目录。原CSV不改，原始数值不平滑/拟合；坐标会裁值时停止。PNG/TIFF是作者请求预览DPI，尚未核对具体期刊要求。\n\n## 公开分享\n\n```text\npython src/share_bundle.py --working Working-demo --out Share --rights-confirmed --license MIT\n```\n\n上例许可只适用于本包原创演示。真实结果需确认公开权利/许可及可见姓名、课题、未发表图像；不得默认沿用MIT。技术检查不能证明科学结论、授权或真实模型适配。Flash/Pro行为和原生桌面完整流程本轮NOT_RUN。\n', encoding='utf-8')


def package(output):
    version = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8-sig'))['version']
    prepare_sources(version)
    destination, _ = new_directory(output.resolve())
    archive_rows = []
    for kind in IDS:
        pack = PACKS / kind
        files = [p for p in sorted(pack.rglob('*')) if p.is_file() and p.name != 'PACKAGE_MANIFEST.json' and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.pyo'}]
        required = {'AGENT_GUIDE.md', 'input_contract.json', 'config.demo.json', 'config.real.example.json', 'src/plot.py', 'src/renderer.py', 'src/recipe_runtime.py', 'src/delivery_contract.py', 'src/output_safety.py', 'checks.py', 'requirements.txt', 'VERSION.json', 'reference/figure.png'}
        names = {p.relative_to(pack).as_posix() for p in files}
        if not required <= names:
            raise RuntimeError(f'{kind} missing {required - names}')
        manifest = {'resource_id': kind, 'version': version, 'files': [{'path': p.relative_to(pack).as_posix(), 'sha256': digest(p)} for p in files]}
        dump(pack / 'PACKAGE_MANIFEST.json', manifest)
        if pack / 'PACKAGE_MANIFEST.json' not in files:
            files.append(pack / 'PACKAGE_MANIFEST.json')
        zip_path = destination / f'VoltPeer-{kind}-{version}.zip'
        with ZipFile(zip_path, 'w', ZIP_DEFLATED) as archive:
            for file in files:
                archive.write(file, f'{kind}/{file.relative_to(pack).as_posix()}')
        with ZipFile(zip_path) as archive:
            if {kind + '/' + r for r in required} - set(archive.namelist()):
                raise RuntimeError('实际ZIP缺少运行文件')
        archive_rows.append({'resource_id': kind, 'version': version, 'file': zip_path.name, 'sha256': digest(zip_path), 'bytes': zip_path.stat().st_size, 'validation': 'package_structure_checked; see local QA for extracted execution; model NOT_RUN'})
    dump(destination / 'recipe-packs.json', {'schema_version': 1, 'packs': archive_rows})
    print(destination)
    return destination


def main():
    configure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'outputs/recipe-packs')
    args = parser.parse_args()
    package(args.out)


if __name__ == '__main__':
    main()
