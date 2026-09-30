"""Freeze matching A/B/C workspaces for a real host/model experiment; never run or score models."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/runtime_contract'))
from cli_runtime import configure_utf8
from eval_provenance import freeze


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def source_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(resource, scenario, output, host, host_version, model):
    pack = ROOT / 'examples/recipe_packs' / resource
    if not (pack / 'PACKAGE_MANIFEST.json').is_file():
        raise ValueError('先运行package_recipe_packs.py，冻结独立绘图包版本。')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixture = output / '_frozen_input'
    fixture.mkdir()
    # Deliberately new shape and values, not the pack's two-group demo. All numbers
    # remain synthetic engineering fixtures, never claimed as experimental evidence.
    config = json.loads((pack / 'config.demo.json').read_text(encoding='utf-8'))
    config['title'] = 'Synthetic adaptation comparison — new inputs'
    config['provenance']['input_origin'] = 'original_synthetic_comparison_fixture'
    config['labels'] = {}
    samples = ['Input group ' + x + ' with a long distinct label' for x in 'XYZ']
    if resource == 'full_cell':
        headers = ['specimen', 'cycle_index', 'measured_capacity', 'reported_ce']
        rows = [(s, c, 250 - i * 10 - c * .9, 99.6 - c * .015) for i, s in enumerate(samples) for c in range(1, 5 + i * 3)]
        config['data'] = {'cycling': {'path': 'new_input.csv', 'columns': dict(zip(('sample', 'cycle', 'capacity', 'ce'), headers))}}
        config['conditions']['common'].update(cathode='Comparison fixture cathode F', anode='Comparison fixture anode G', capacity_basis='Comparison fixture cathode active material mass', rate_or_current='Comparison fixture 0.3 C', formation='Comparison fixture three declared formation cycles', loading_or_areal_capacity='Comparison fixture 2.4 mAh cm^-2', temperature_C=29, voltage_window_V=[2.4, 4.5], N_P='not reported', E_C='not reported')
        if scenario == 'conflict_range':
            config['limits'] = {'cycling': {'y': [145, 188]}}
    elif resource == 'li_li':
        headers = ['specimen', 'elapsed', 'signed_cell_voltage']
        rows = [(s, j * 2.5, (-1 if j % 2 else 1) * (80 + 4 * i + j)) for i, s in enumerate(samples) for j in range(5 + i * 3)]
        config['data'] = {'trace': {'path': 'new_input.csv', 'columns': dict(zip(('sample', 'time', 'voltage'), headers))}}
        config['view']['zoom'] = None
        config['conditions']['common'].update(metal='Na', cell_configuration='Na||Na', area_basis='Comparison fixture projected electrode overlap area', current_density_mA_cm2=.4, half_cycle_areal_capacity_mAh_cm2=.8, temperature_C=30, rest_protocol='Comparison fixture ten-minute rest each half-cycle', failure_rule='Comparison fixture declared 1 V threshold; no lifetime inference')
        if scenario == 'conflict_range':
            config['limits'] = {'trace': {'y': [-70, 70]}}
    else:
        headers = ['specimen', 'angle_deg', 'elapsed_h', 'detector_count']
        rows = [(s, 23 + k * 1.7, t, 1200 + 40 * i + k * 10 + t * 2) for i, s in enumerate(samples) for t in (0, 2, 6, 11) for k in range(2 + i)]
        rows.reverse()
        config['data'] = {'diffraction': {'path': 'new_input.csv', 'columns': dict(zip(('sample', 'two_theta', 'progress', 'intensity'), headers))}}
        config['units'].update(progress='h', intensity='counts')
        config['conditions']['common'].update(radiation='Synthetic comparison synchrotron radiation', wavelength_A=.61992, cell_configuration='Synthetic comparison operando cell F', progress_definition='Synthetic new elapsed-time axis in hours', intensity_normalization='Synthetic detector counts; no normalization', synchronization='Synthetic single diffraction time axis; no external electrochemical trace')
        if scenario == 'conflict_range':
            config['limits'] = {'intensity': [0, 1]}
    config['conditions']['common']['comparison_note'] = 'Author-specified synthetic test conditions for this comparison; do not copy original gallery conditions.'
    if scenario == 'missing_units':
        config['units'] = {}
    if scenario == 'missing_conditions':
        config['conditions'] = {'common': {}, 'by_sample': {}}
    with (fixture / 'new_input.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
    write_json(fixture / 'input_information.json', config)
    frozen = [{'path': p.name, 'sha256': source_digest(p)} for p in sorted(fixture.iterdir())]
    common_prompt = f'''这是VoltPeer样图{resource}、新的CSV和输入说明。所有对照输入为原创合成工程验证，不是实验结果。请用新CSV及其已声明条件复现参考图的表达方法；不能沿用参考图原有样品、数值或条件。先核对列名、单位、归一化依据和测试条件；缺信息先提最少的必要问题。优先改配置、再做数据适配、最后才改当前项目副本源码。保持原文件和新数据全部点、符号与分组，不平滑、不补随机曲线、不截掉超范围数据。生成预览及PDF/SVG/PNG，并告诉我保存位置和影响使用的缺口。必要的科学与视觉检查不能编造通过。资料在input/和reference/；可用Skill在项目.dsh/skills。
'''
    if scenario == 'conflict_range':
        common_prompt += '\n作者已明确最新优先级：旧范围会截掉新值时应扩展auto显示全部点；不要为了保持参考图范围删点。\n'
    for arm in ('A', 'B', 'C'):
        workspace = output / arm
        shutil.copytree(fixture, workspace / 'input')
        init = subprocess.run(['git', 'init', '--quiet', str(workspace)], capture_output=True, text=True, encoding='utf-8')
        if init.returncode:
            raise ValueError('Cannot anchor isolated A/B/C project root: ' + init.stderr.strip())
        shutil.copytree(pack / 'reference', workspace / 'reference')
        shutil.copytree(ROOT / 'skills/battery-review-figure', workspace / '.dsh/skills/battery-review-figure', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if arm == 'B':
            legacy = workspace / 'existing_source'
            (legacy / 'examples/showcase').mkdir(parents=True)
            shutil.copy2(ROOT / 'examples/showcase/build.py', legacy / 'examples/showcase/build.py')
            shutil.copytree(ROOT / 'examples/showcase' / resource, legacy / 'examples/showcase' / resource, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            shutil.copytree(ROOT / 'skills/battery-review-figure', legacy / 'skills/battery-review-figure', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if arm == 'C':
            shutil.copytree(pack, workspace / 'figure_pack', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        prompt = common_prompt + ('\n还提供existing_source原有完整入口与依赖源码，需适配新的CSV，不能直接把原Demo当新数据输出。\n' if arm == 'B' else '\n还提供figure_pack完整绘图包，请先读取AGENT_GUIDE.md和input_contract.json。\n' if arm == 'C' else '')
        (workspace / 'TASK.md').write_text(prompt, encoding='utf-8')
        write_json(workspace / 'RUN_RECORD.json', {'schema_version': 2, 'resource_id': resource, 'scenario': scenario, 'arm': arm, 'run_state': 'NOT_RUN', 'host': host, 'host_version': host_version, 'model': model, 'actual_model_version': None, 'skill_version': json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8-sig'))['version'],
                    **freeze(ROOT, workspace / '.dsh/skills'), 'execution_environment': {'os': None, 'architecture': None},
                    'input_files': frozen, 'started_at': None, 'finished_at': None, 'duration_s': None, 'request_count': None, 'actual_cost': None, 'cost_evidence': None, 'rework_count': None, 'human_rescue': None, 'reviewer': None, 'final_artifact_evidence': [], 'checks': {'new_data_used': 'NOT_RUN', 'units_groups_conditions': 'NOT_RUN', 'no_demo_residue': 'NOT_RUN', 'all_points_and_signed_values_preserved': 'NOT_RUN', 'proper_stop_or_resolution': 'NOT_RUN', 'visual_review': 'NOT_RUN'}})
    write_json(output / 'COMPARISON.json', {'schema_version': 1, 'resource_id': resource, 'scenario': scenario, 'host': host, 'host_version': host_version, 'model': model, 'input_files': frozen, 'arms': ['A', 'B', 'C'], 'model_runs': 'NOT_RUN', 'policy': 'Same actual host/model/settings and new independent conversations; repeat each arm >=3 times; preparation is not execution or a PASS.'})
    return output


def main():
    configure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resource', choices=('full_cell', 'li_li', 'operando_xrd'), required=True)
    parser.add_argument('--scenario', choices=('new_shape', 'missing_units', 'missing_conditions', 'conflict_range'), required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--host-version', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(prepare(args.resource, args.scenario, args.out, args.host, args.host_version, args.model))


if __name__ == '__main__':
    main()
