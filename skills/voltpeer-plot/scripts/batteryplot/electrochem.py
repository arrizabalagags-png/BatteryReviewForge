"""Four optional electrochemistry displays with declared experimental identity.

These render supplied curves only. No CE, resistance, capacity loss, nucleation
rate, or mechanism is inferred from a visual trace.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from .corpus import _groups, _ordered, _range, _read, _required_text
from .layout import axes_mm, measure_layout
from .style import colors_for


ELECTROCHEM_RECIPES = ('aurbach_protocol', 'eis_frequency', 'chronoamperometry', 'ocv_rest')


def _metadata(folder: Path, recipe: str):
    meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8-sig'))
    if meta.get('figure_grammar_id') != f'optional:{recipe}' or meta.get('reference', {}).get('default_template') is not False:
        raise ValueError('Electrochemistry recipes are explicit optional variants')
    if not isinstance(meta.get('render_options'), dict) or not meta.get('test_conditions'):
        raise ValueError('metadata needs render_options and test_conditions')
    sources = meta.get('source_files')
    allowed = {'data.csv', 'protocol.json'} if recipe == 'aurbach_protocol' else {'data.csv'}
    if (not isinstance(sources, list) or not sources
            or not all(isinstance(name, str) for name in sources)
            or len(set(sources)) != len(sources)
            or 'data.csv' not in sources or not set(sources) <= allowed):
        raise ValueError('source_files must explicitly list data.csv; only the Aurbach protocol.json sidecar is optional')
    root = folder.resolve()
    for name in sources:
        source = (folder / name).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f'Declared electrochemistry source is missing or outside input folder: {name}')
    return meta, meta['render_options']


def render_electrochem(recipe, folder, *, style='forge'):
    if recipe not in ELECTROCHEM_RECIPES:
        raise ValueError('Unknown electrochemistry recipe')
    folder = Path(folder)
    meta, opt = _metadata(folder, recipe)
    from .specialist import font
    family, font_path = font()
    colors = colors_for(style)
    rc = {'font.family': family, 'mathtext.fontset': 'custom', 'mathtext.rm': family,
          'mathtext.it': family + ':italic', 'mathtext.bf': family + ':bold',
          'mathtext.fallback': None, 'font.size': 6.5, 'axes.labelsize': 6.5,
          'xtick.labelsize': 6, 'ytick.labelsize': 6, 'legend.fontsize': 6,
          'text.color': '#202124', 'axes.labelcolor': '#202124',
          'axes.edgecolor': '#202124', 'axes.linewidth': .6,
          'lines.linewidth': .9, 'svg.fonttype': 'none', 'pdf.fonttype': 42}
    transformations = []
    with mpl.rc_context(rc):
        fig = plt.figure(figsize=(180/25.4, 88/25.4))
        axes = {'a': axes_mm(fig, left=19, top=10, width=62, height=60),
                'b': axes_mm(fig, left=107, top=10, width=62, height=60)}
        a, b = axes.values()
        relations = [('a', 'b', edge) for edge in ('top', 'bottom', 'height')]

        if recipe == 'aurbach_protocol':
            rows = _read(folder, 'data.csv', ('time_h', 'voltage_V', 'current_density_mA_cm2'), ('stage',))
            for key in ('protocol_name', 'cell_configuration', 'current_sign_convention',
                        'capacity_schedule_mAh_cm2', 'cutoff_description'):
                _required_text(opt, key)
            declared = opt.get('stage_sequence')
            if not isinstance(declared, list) or len(declared) < 3 or len(set(declared)) != len(declared):
                raise ValueError('stage_sequence needs >=3 unique declared stages')
            time = np.array([r['time_h'] for r in rows])
            _ordered(time, 'Aurbach protocol time')
            if time[0] < 0: raise ValueError('Protocol time must be nonnegative')
            stages = [rows[0]['stage']]
            for row in rows[1:]:
                if row['stage'] != stages[-1] and row['stage'] not in stages:
                    stages.append(row['stage'])
                elif row['stage'] != stages[-1] and row['stage'] in stages:
                    raise ValueError('Aurbach stages must be contiguous; split repeated stages explicitly')
            if stages != declared or len(stages) > len(colors):
                raise ValueError('Observed stage order must match declared stage_sequence and palette')
            groups = _groups(rows, ('stage',))
            if any(len(groups[(stage,)]) < 3 for stage in stages):
                raise ValueError('Each protocol stage needs >=3 samples')
            for idx, stage in enumerate(stages):
                group = groups[(stage,)]
                x = [r['time_h'] for r in group]
                a.plot(x, [r['voltage_V'] for r in group], color=colors[idx], label=stage)
                b.plot(x, [r['current_density_mA_cm2'] for r in group], color=colors[idx])
            a.set(xlabel='Time (h)', ylabel='Cell voltage (V)')
            b.set(xlabel='Time (h)', ylabel='Current density (mA/cm$^2$)')
            for ax in (a, b): ax.set_xlim(time[0], time[-1])
            fig.legend(*a.get_legend_handles_labels(), frameon=False, loc='lower center',
                       bbox_to_anchor=(.5, .006), ncol=len(stages), fontsize=5.4,
                       handlelength=1.4, columnspacing=.75)
            transformations.append('Supplied stage-resolved voltage/current only; capacity schedule is declared, no CE formula or value inferred')

        elif recipe == 'eis_frequency':
            rows = _read(folder, 'data.csv', ('frequency_Hz', 'z_real_ohm', 'z_imag_ohm'), ('sample',))
            for key in ('cell_configuration', 'measurement_state', 'temperature_C',
                        'perturbation_mV', 'frequency_direction'):
                if key in ('temperature_C', 'perturbation_mV'):
                    value = float(opt.get(key, np.nan))
                    if not np.isfinite(value) or (key == 'perturbation_mV' and value <= 0):
                        raise ValueError(f'{key} must be declared and finite')
                else: _required_text(opt, key)
            if opt['frequency_direction'] not in ('ascending', 'descending'):
                raise ValueError('frequency_direction must be ascending or descending')
            groups = _groups(rows, ('sample',))
            if len(groups) > len(colors): raise ValueError('Too many EIS series for palette')
            for idx, ((sample,), group) in enumerate(groups.items()):
                x = np.array([r['frequency_Hz'] for r in group])
                if np.any(x <= 0): raise ValueError('EIS frequencies must be positive')
                ordered = x if opt['frequency_direction'] == 'ascending' else -x
                _ordered(ordered, f'EIS {sample} frequency')
                a.plot(x, [r['z_real_ohm'] for r in group], color=colors[idx], label=sample)
                b.plot(x, [-r['z_imag_ohm'] for r in group], color=colors[idx])
            a.set(xscale='log', xlabel='Frequency (Hz)', ylabel="Z' (Ω)")
            b.set(xscale='log', xlabel='Frequency (Hz)', ylabel="−Z'' (Ω)")
            a.legend(frameon=False, loc='best')
            transformations.append('Signed supplied Z imaginary component displayed as −Z\'\'; no equivalent circuit, fit or phase inferred')

        elif recipe == 'chronoamperometry':
            rows = _read(folder, 'data.csv', ('time_s', 'current_density_mA_cm2'), ('sample',))
            for key in ('cell_configuration', 'reference_electrode', 'current_sign_convention'):
                _required_text(opt, key)
            potential = float(opt.get('applied_potential_V', np.nan))
            if not np.isfinite(potential): raise ValueError('Finite applied_potential_V required')
            lo, hi = _range(opt.get('zoom_time_s'), 'Chronoamperometry time zoom')
            groups = _groups(rows, ('sample',))
            if len(groups) > len(colors): raise ValueError('Too many CA series for palette')
            for idx, ((sample,), group) in enumerate(groups.items()):
                x = np.array([r['time_s'] for r in group])
                _ordered(x, f'CA {sample} time')
                if x[0] < 0 or lo < x[0] or hi > x[-1]:
                    raise ValueError('CA time and zoom must lie inside nonnegative supplied data')
                y = [r['current_density_mA_cm2'] for r in group]
                for ax in (a, b): ax.plot(x, y, color=colors[idx], label=sample)
            a.set(xlabel='Time (s)', ylabel='Current density (mA/cm$^2$)')
            b.set(xlabel='Time (s)', ylabel='Current density (mA/cm$^2$)', xlim=(lo, hi))
            a.legend(frameon=False, loc='best')
            transformations.append('Full and zoom views use same supplied potentiostatic current; no charge integration or nucleation fit')

        else:  # ocv_rest
            rows = _read(folder, 'data.csv', ('time_h', 'voltage_V'), ('sample',))
            for key in ('cell_configuration', 'initial_state', 'rest_condition'):
                _required_text(opt, key)
            temp = float(opt.get('temperature_C', np.nan))
            if not np.isfinite(temp): raise ValueError('Finite temperature_C required')
            lo, hi = _range(opt.get('zoom_time_h'), 'OCV time zoom')
            groups = _groups(rows, ('sample',))
            if len(groups) > len(colors): raise ValueError('Too many OCV series for palette')
            for idx, ((sample,), group) in enumerate(groups.items()):
                x = np.array([r['time_h'] for r in group])
                _ordered(x, f'OCV {sample} time')
                if x[0] < 0 or lo < x[0] or hi > x[-1]:
                    raise ValueError('OCV time and zoom must lie inside nonnegative supplied data')
                y = np.array([r['voltage_V'] for r in group])
                if np.any(y <= 0): raise ValueError('Cell voltage must be positive; verify OCV reference and cell')
                for ax in (a, b): ax.plot(x, y, color=colors[idx], label=sample)
            a.set(xlabel='Rest time (h)', ylabel='Open-circuit voltage (V)')
            b.set(xlabel='Rest time (h)', ylabel='Open-circuit voltage (V)', xlim=(lo, hi))
            a.legend(frameon=False, loc='best')
            transformations.append('Full and early-rest views use same supplied OCV; voltage relaxation is not converted to capacity loss or self-discharge rate')

        fw, fh = fig.get_size_inches()*25.4
        for letter, ax in axes.items():
            ax.spines[['top','right','bottom','left']].set_visible(True)
            ax.grid(False)
            ax.tick_params(length=2.3, width=.6, pad=2)
            box = ax.get_position()
            fig.text(box.x0-8/fw, box.y1+2/fh, letter, fontsize=8, fontweight='bold', ha='left', va='bottom')
        alignment = measure_layout(fig, axes, relations)
        if alignment['failures']: raise ValueError(alignment['failures'])
        fig.brf_export_rc = rc
        return fig, dict(recipe=recipe, status='optional_variant', style=style,
                         alignment=alignment, requested_font='Arial/Helvetica',
                         actual_font=family, resolved_font_path=font_path,
                         transformations=transformations, calculations={},
                         test_conditions=meta['test_conditions'],
                         data_status=meta.get('data_status', 'author_supplied'),
                         source_files=meta['source_files'], reference=meta['reference'])
