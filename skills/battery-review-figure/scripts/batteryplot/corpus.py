"""Six optional, explicit-input figure grammars from visually checked papers.

The source papers establish panel types and pairings, never demo data or
numerical parameters. No fitting, peak assignment or inferred chemistry.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from .layout import axes_mm, measure_layout
from .style import colors_for

CORPUS_RECIPES = ('ftir', 'nmr', 'rdf_coordination', 'msd', 'lsv', 'transference')


def _read(folder: Path, name: str, numeric: tuple[str, ...], labels: tuple[str, ...] = ()):
    path = folder / name
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    fields = set(numeric + labels)
    if len(rows) < 3 or not fields <= set(rows[0]):
        raise ValueError(f'{name}: need >=3 rows and columns {sorted(fields)}')
    for row in rows:
        for key in labels:
            if not row[key].strip():
                raise ValueError(f'{name}: empty {key} label')
        for key in numeric:
            try:
                row[key] = float(row[key])
            except (ValueError, TypeError) as exc:
                raise ValueError(f'{name}: {key} needs a number') from exc
            if not np.isfinite(row[key]):
                raise ValueError(f'{name}: {key} must be finite')
    return rows


def _groups(rows, keys):
    result = {}
    for row in rows:
        key = tuple(row[name] for name in keys)
        result.setdefault(key, []).append(row)
    return result


def _ordered(values, label):
    if len(values) < 3 or not np.all(np.diff(values) > 0):
        raise ValueError(f'{label}: >=3 values in strictly increasing acquisition order required; do not sort silently')


def _range(option, label):
    if not isinstance(option, list) or len(option) != 2:
        raise ValueError(f'{label}: give [lower, upper]')
    lo, hi = map(float, option)
    if not np.isfinite([lo, hi]).all() or lo >= hi:
        raise ValueError(f'{label}: finite lower < upper required')
    return lo, hi


def _required_text(opt, key):
    value = opt.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'render_options.{key} is required')
    return value.strip()


def _transference_value(values):
    """Bruce-Vincent style calculation only from author-supplied parameters."""
    fields = ('polarization_voltage_V', 'initial_current_mA', 'steady_current_mA',
              'initial_resistance_ohm', 'steady_resistance_ohm')
    if not isinstance(values, dict) or set(values) != set(fields):
        raise ValueError(f'known_parameters require exactly {fields}')
    p = {key: float(values[key]) for key in fields}
    if not np.isfinite(list(p.values())).all() or any(p[key] <= 0 for key in fields):
        raise ValueError('known_parameters must be finite and positive')
    dv = p['polarization_voltage_V']
    i0 = p['initial_current_mA'] / 1000
    iss = p['steady_current_mA'] / 1000
    r0, rss = p['initial_resistance_ohm'], p['steady_resistance_ohm']
    denominator = i0 * (dv - iss * rss)
    if denominator <= 0:
        raise ValueError('Invalid transference denominator; inspect supplied current/resistance convention')
    value = iss * (dv - i0 * r0) / denominator
    if not 0 <= value <= 1:
        raise ValueError('Calculated tLi+ outside 0..1; inspect supplied parameters and method')
    return value


def render_corpus(recipe, folder, *, style='forge'):
    """Render an optional grammar from declared author inputs and metadata."""
    if recipe not in CORPUS_RECIPES:
        raise ValueError('Unknown corpus recipe')
    folder = Path(folder)
    meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8-sig'))
    if not meta.get('test_conditions') or not meta.get('source_files') or not isinstance(meta.get('render_options'), dict):
        raise ValueError('metadata.json needs test_conditions, source_files and render_options')
    if not all((folder / name).is_file() for name in meta['source_files']):
        raise ValueError('A declared source file is missing')
    if meta.get('figure_grammar_id') != f'optional:{recipe}' or meta.get('reference', {}).get('default_template') is not False:
        raise ValueError('Corpus recipes must remain explicit optional variants')
    opt = meta['render_options']
    # Imported at call time so specialist can route here without a module cycle.
    from .specialist import font
    family, font_path = font()
    colors = colors_for(style)
    rc = {'font.family': family, 'mathtext.fontset': 'custom', 'mathtext.rm': family,
          'mathtext.it': family + ':italic', 'mathtext.bf': family + ':bold', 'mathtext.fallback': None,
          'font.size': 6.5, 'axes.labelsize': 6.5, 'xtick.labelsize': 6,
          'ytick.labelsize': 6, 'legend.fontsize': 6, 'text.color': '#202124',
          'axes.labelcolor': '#202124', 'axes.edgecolor': '#202124',
          'axes.linewidth': .6, 'lines.linewidth': .9, 'svg.fonttype': 'none', 'pdf.fonttype': 42}
    transformations = []
    calculations = {}
    with mpl.rc_context(rc):
        fig = plt.figure(figsize=(180/25.4, 88/25.4))
        axes = {'a': axes_mm(fig, left=19, top=10, width=62, height=60),
                'b': axes_mm(fig, left=107, top=10, width=62, height=60)}
        a, b = axes.values()
        relations = [('a', 'b', edge) for edge in ('top', 'bottom', 'height')]

        if recipe == 'ftir':
            rows = _read(folder, 'data.csv', ('wavenumber_cm_1', 'transmittance_percent'), ('sample',))
            groups = _groups(rows, ('sample',))
            if len(groups) > len(colors): raise ValueError('Too many FTIR spectra for palette')
            lo, hi = _range(opt.get('zoom_wavenumber_cm_1'), 'FTIR zoom')
            if opt.get('wavenumber_direction') != 'descending':
                raise ValueError('Declare descending FTIR wavenumber direction')
            for idx, ((sample,), group) in enumerate(groups.items()):
                x = np.array([r['wavenumber_cm_1'] for r in group])
                y = np.array([r['transmittance_percent'] for r in group])
                _ordered(x, f'FTIR {sample} wavenumber')
                if np.any((y < 0) | (y > 100)):
                    raise ValueError('FTIR transmittance must be 0..100%; absorbance requires another explicit grammar')
                for ax in (a, b): ax.plot(x, y, color=colors[idx], label=sample)
            for ax in (a, b):
                ax.set(xlabel='Wavenumber (cm$^{-1}$)', ylabel='Transmittance (%)')
                ax.set_xlim(ax.get_xlim()[1], ax.get_xlim()[0])
            b.set_xlim(hi, lo)
            a.legend(frameon=False, loc='best')
            transformations.append('Same supplied transmittance traces in full and zoom views; no absorbance conversion or band assignment')

        elif recipe == 'nmr':
            rows = _read(folder, 'data.csv', ('chemical_shift_ppm', 'intensity_au'), ('sample',))
            groups = _groups(rows, ('sample',))
            if len(groups) > len(colors): raise ValueError('Too many NMR spectra for palette')
            nucleus = _required_text(opt, 'nucleus')
            _required_text(opt, 'chemical_shift_reference')
            offset = float(opt.get('display_offset_au', -1))
            if not np.isfinite(offset) or offset < 0:
                raise ValueError('Explicit finite nonnegative NMR display offset required')
            lo, hi = _range(opt.get('zoom_chemical_shift_ppm'), 'NMR zoom')
            for idx, ((sample,), group) in enumerate(groups.items()):
                x = np.array([r['chemical_shift_ppm'] for r in group])
                y = np.array([r['intensity_au'] for r in group])
                _ordered(x, f'NMR {sample} chemical shift')
                for ax in (a, b): ax.plot(x, y + idx*offset, color=colors[idx], label=sample)
            for ax in (a, b):
                ax.set(xlabel=f'{nucleus} chemical shift (ppm)', ylabel='Intensity + offset (a.u.)')
                ax.set_xlim(ax.get_xlim()[1], ax.get_xlim()[0])
            b.set_xlim(hi, lo)
            a.legend(frameon=False, loc='best')
            transformations.append(f'Visual offset index*{offset:g} a.u.; original intensity preserved; no integration or concentration inference')

        elif recipe == 'rdf_coordination':
            rows = _read(folder, 'data.csv', ('distance_A', 'g_r', 'coordination_number'), ('pair',))
            groups = _groups(rows, ('pair',))
            if len(groups) > len(colors): raise ValueError('Too many atom pairs for palette')
            _required_text(opt, 'species_definition')
            _required_text(opt, 'coordination_source')
            cutoff = float(opt.get('coordination_cutoff_A', 0))
            if not np.isfinite(cutoff) or cutoff <= 0:
                raise ValueError('Positive coordination cutoff in Å required')
            density = opt.get('pair_number_density_A3')
            if not isinstance(density, dict) or set(density) != {pair for (pair,) in groups}:
                raise ValueError('pair_number_density_A3 must give one explicit number density for each pair')
            for idx, ((pair,), group) in enumerate(groups.items()):
                x = np.array([r['distance_A'] for r in group])
                gr = np.array([r['g_r'] for r in group])
                cn = np.array([r['coordination_number'] for r in group])
                _ordered(x, f'RDF {pair} distance')
                if np.any(gr < 0) or np.any(cn < 0) or np.any(np.diff(cn) < -1e-6):
                    raise ValueError('RDF must be nonnegative and supplied cumulative coordination nondecreasing')
                if cutoff < x.min() or cutoff > x.max():
                    raise ValueError('Coordination cutoff outside supplied distances')
                rho = float(density[pair])
                if not np.isfinite(rho) or rho <= 0:
                    raise ValueError('Pair number density must be finite positive Å^-3')
                integrand = x*x*gr
                integrated = np.r_[0, np.cumsum((integrand[1:]+integrand[:-1])*np.diff(x)/2)]
                expected = 4*np.pi*rho*integrated
                if not np.allclose(cn, expected, atol=.02, rtol=.005):
                    raise ValueError('Supplied coordination number is inconsistent with 4πρ∫r²g(r)dr')
                a.plot(x, gr, color=colors[idx], label=pair)
                b.plot(x, cn, color=colors[idx], label=pair)
            a.set(xlabel='Distance (Å)', ylabel='g(r)')
            b.set(xlabel='Distance (Å)', ylabel='Coordination number')
            for ax in (a, b): ax.axvline(cutoff, ls='--', lw=.6, color='#73777d')
            a.legend(frameon=False, loc='best')
            transformations.append('Supplied cumulative coordination checked against 4πρ∫r²g(r)dr using declared pair number densities; no species assignment inferred')

        elif recipe == 'msd':
            rows = _read(folder, 'data.csv', ('temperature_C', 'time_ps', 'msd_A2'), ('electrolyte',))
            _required_text(opt, 'simulated_species')
            _required_text(opt, 'simulation_method')
            temperatures = list(dict.fromkeys(r['temperature_C'] for r in rows))
            if len(temperatures) != 2:
                raise ValueError('MSD comparison requires exactly two declared temperatures')
            names = list(dict.fromkeys(r['electrolyte'] for r in rows))
            if len(names) > len(colors): raise ValueError('Too many electrolytes for palette')
            groups = _groups(rows, ('temperature_C', 'electrolyte'))
            for (temp, name), group in groups.items():
                x = np.array([r['time_ps'] for r in group])
                y = np.array([r['msd_A2'] for r in group])
                _ordered(x, f'MSD {name} at {temp:g} °C time')
                if x[0] < 0 or np.any(y < 0): raise ValueError('MSD requires nonnegative time and displacement')
                (a if temp == temperatures[0] else b).plot(x, y, color=colors[names.index(name)], label=name)
            for temp, ax in zip(temperatures, (a, b)):
                ax.set(xlabel='Time (ps)', ylabel='MSD (Å$^2$)')
                ax.text(.60, .96, f'{temp:g} °C', transform=ax.transAxes, ha='center', va='top', fontsize=6)
            a.legend(frameon=False, loc='upper left')
            transformations.append('Supplied simulated MSD only; no slope fit or diffusion coefficient calculation')

        elif recipe == 'lsv':
            rows = _read(folder, 'data.csv', ('voltage_V', 'current_density_uA_cm2'), ('electrolyte',))
            for field in ('working_electrode', 'counter_reference_electrode'):
                _required_text(opt, field)
            scan = float(opt.get('scan_rate_mV_s', 0))
            if not np.isfinite(scan) or scan <= 0: raise ValueError('Positive measured scan rate required')
            lo, hi = _range(opt.get('zoom_voltage_V'), 'LSV zoom')
            groups = _groups(rows, ('electrolyte',))
            if len(groups) > len(colors): raise ValueError('Too many LSV traces for palette')
            for idx, ((name,), group) in enumerate(groups.items()):
                x = np.array([r['voltage_V'] for r in group])
                y = np.array([r['current_density_uA_cm2'] for r in group])
                _ordered(x, f'LSV {name} voltage')
                for ax in (a, b): ax.plot(x, y, color=colors[idx], label=name)
            a.set(xlabel='Voltage (V)', ylabel='Current density (µA/cm$^2$)')
            b.set(xlabel='Voltage (V)', ylabel='Current density (µA/cm$^2$)')
            b.set_xlim(lo, hi)
            a.legend(frameon=False, loc='best')
            transformations.append('Same supplied LSV traces in full and zoom views; no onset threshold or electrochemical window inferred')

        else:  # transference
            rows = _read(folder, 'data.csv', ('time_s', 'current_mA'), ('electrolyte',))
            eis = _read(folder, 'eis.csv', ('z_real_ohm', 'z_imag_negative_ohm'), ('electrolyte', 'stage'))
            _required_text(opt, 'calculation_method')
            names = list(dict.fromkeys(r['electrolyte'] for r in rows))
            if len(names) > len(colors): raise ValueError('Too many transference traces for palette')
            known = opt.get('known_parameters', {})
            if not isinstance(known, dict) or set(known) - set(names):
                raise ValueError('known_parameters must map only supplied electrolytes')
            groups = _groups(rows, ('electrolyte',))
            eis_groups = _groups(eis, ('electrolyte', 'stage'))
            for idx, name in enumerate(names):
                group = groups[(name,)]
                x = np.array([r['time_s'] for r in group])
                y = np.array([r['current_mA'] for r in group])
                _ordered(x, f'{name} polarization time')
                if x[0] < 0 or np.any(y <= 0): raise ValueError('Polarization time nonnegative and current positive required')
                a.plot(x, y, color=colors[idx], label=name)
                for stage, ls in (('before', '-'), ('after', '--')):
                    key = (name, stage)
                    if key not in eis_groups or len(eis_groups[key]) < 3:
                        raise ValueError(f'{name} needs before and after EIS, >=3 rows each')
                    rg = eis_groups[key]
                    zr = np.array([r['z_real_ohm'] for r in rg])
                    zi = np.array([r['z_imag_negative_ohm'] for r in rg])
                    if np.any(zr < 0) or np.any(zi < 0): raise ValueError('EIS displayed ohm magnitudes must be nonnegative')
                    b.plot(zr, zi, ls=ls, color=colors[idx], label=f'{name} {stage}')
                if name in known:
                    calculations[name] = {'tLi_plus': _transference_value(known[name]),
                                          'method': opt['calculation_method'], 'inputs': known[name]}
            if set(k[0] for k in eis_groups) != set(names) or any(k[1] not in ('before', 'after') for k in eis_groups):
                raise ValueError('EIS names/stages must match current traces')
            a.set(xlabel='Time (s)', ylabel='Current (mA)')
            b.set(xlabel="Z' (Ω)", ylabel="−Z'' (Ω)")
            a.legend(frameon=False, loc='best')
            b.legend(frameon=False, fontsize=5, loc='best')
            transformations.append('Current transients and supplied before/after EIS displayed separately; tLi+ calculated only for complete explicit parameter sets')

        fw, fh = fig.get_size_inches()*25.4
        for letter, ax in axes.items():
            ax.spines[['top', 'right']].set_visible(False)
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
                         transformations=transformations, calculations=calculations,
                         test_conditions=meta['test_conditions'],
                         data_status=meta.get('data_status', 'author_supplied'),
                         source_files=meta['source_files'], reference=meta['reference'])
