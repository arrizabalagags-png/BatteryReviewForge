"""Optional, explicit-input recipes. No fitting, smoothing or inferred chemistry."""
from __future__ import annotations

import csv
import json
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont
import numpy as np

from .layout import axes_mm, measure_layout
from .style import colors_for
from .corpus import CORPUS_RECIPES, render_corpus
from .electrochem import ELECTROCHEM_RECIPES, render_electrochem

BASE_RECIPES = ('cyclic_voltammetry', 'differential_capacity', 'gitt_pulse',
                'ionic_conductivity', 'xps_components', 'raman_series')
RECIPES = BASE_RECIPES + CORPUS_RECIPES + ELECTROCHEM_RECIPES


def read_numeric(folder, name, fields):
    with (folder / name).open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) < 3 or not set(fields) <= set(rows[0]):
        raise ValueError(f'{name}: need >=3 rows and fields {fields}')
    result = {key: np.array([float(row[key]) for row in rows]) for key in fields}
    if not all(np.isfinite(values).all() for values in result.values()):
        raise ValueError(f'{name}: missing or non-finite values need author review')
    return rows, result


def increasing(values, label):
    if not np.all(np.diff(values) > 0):
        raise ValueError(f'{label} must strictly increase in acquisition order; split branches, do not sort silently')


def font():
    for family in ('Arial', 'Helvetica', 'Liberation Sans', 'DejaVu Sans'):
        try:
            path = findfont(FontProperties(family=family), fallback_to_default=False)
            if family not in ('Arial', 'Helvetica'):
                warnings.warn(f'Arial/Helvetica unavailable. Actual font: {family}; verify target journal.')
            return family, path
        except ValueError:
            pass
    raise ValueError('No supported sans-serif font available')


def render_recipe(recipe, folder, *, style='forge'):
    """Return fig + report. metadata.render_options supplies scientific choices.

    Inputs have explicit units in column names. Missing options fail visibly.
    These recipes are optional variants, not newly validated default pairings.
    """
    if recipe not in RECIPES:
        raise ValueError('Unknown specialist recipe')
    if recipe in CORPUS_RECIPES:
        return render_corpus(recipe, folder, style=style)
    if recipe in ELECTROCHEM_RECIPES:
        return render_electrochem(recipe, folder, style=style)
    folder = Path(folder)
    meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8-sig'))
    if not meta.get('test_conditions') or not meta.get('source_files'):
        raise ValueError('metadata.json needs test_conditions and source_files')
    opt = meta['render_options']
    family, font_path = font()
    colors = colors_for(style)
    rc = {'font.family': family, 'mathtext.fontset': 'custom', 'mathtext.rm': family,
          'mathtext.it': family + ':italic', 'mathtext.bf': family + ':bold', 'mathtext.fallback': None,
          'font.size': 6.5, 'axes.labelsize': 6.5,
          'xtick.labelsize': 6, 'ytick.labelsize': 6, 'legend.fontsize': 6,
          'text.color': '#202124', 'axes.labelcolor': '#202124', 'axes.edgecolor': '#202124',
          'axes.linewidth': .6, 'lines.linewidth': .9, 'svg.fonttype': 'none', 'pdf.fonttype': 42}
    with mpl.rc_context(rc):
        stacked = recipe in ('gitt_pulse', 'xps_components')
        fig = plt.figure(figsize=(180/25.4, (116 if stacked else 88)/25.4))
        if stacked:
            axes = {'a': axes_mm(fig, left=19, top=9, width=147, height=48),
                    'b': axes_mm(fig, left=19, top=76, width=147, height=27)}
            relations = [('a', 'b', edge) for edge in ('left', 'right', 'width')]
        else:
            axes = {'a': axes_mm(fig, left=19, top=10, width=62, height=60),
                    'b': axes_mm(fig, left=107, top=10, width=62, height=60)}
            relations = [('a', 'b', edge) for edge in ('top', 'bottom', 'height')]
        a, b = axes.values()
        transformations = []

        if recipe == 'cyclic_voltammetry':
            _, d = read_numeric(folder, 'data.csv', ('scan_rate_mV_s', 'sequence', 'voltage_V', 'current_mA'))
            rates = list(dict.fromkeys(d['scan_rate_mV_s']))
            if len(rates) > len(colors) or min(rates) <= 0:
                raise ValueError('Positive scan rates and <= palette size required')
            reference = opt['reference_electrode']
            lo, hi = opt['zoom_voltage_V']
            if not lo < hi: raise ValueError('Invalid voltage zoom')
            for idx, rate in enumerate(rates):
                keep = d['scan_rate_mV_s'] == rate
                increasing(d['sequence'][keep], 'CV acquisition sequence')
                x, y = d['voltage_V'][keep], d['current_mA'][keep]
                for ax in (a, b):
                    ax.plot(x, y, color=colors[idx], label=f'{rate:g}')
            b.set_xlim(lo, hi)
            a.legend(title='Scan rate (mV/s)', title_fontsize=6, frameon=False, loc='upper left')
            for ax in (a, b): ax.set(xlabel=f'Potential (V vs {reference})', ylabel='Current (mA)')
            transformations.append(f'b is the same curves with voltage limits {lo}..{hi}; no peak fit')

        elif recipe == 'differential_capacity':
            _, d = read_numeric(folder, 'data.csv', ('cycle', 'voltage_V', 'capacity_mAh_g'))
            if opt['branch'] != 'charge': raise ValueError('This recipe is charge-only; split discharge explicitly')
            cycles = list(dict.fromkeys(d['cycle']))
            if len(cycles) > len(colors): raise ValueError('Too many cycles for this palette')
            for idx, cycle in enumerate(cycles):
                use = d['cycle'] == cycle
                x, q = d['voltage_V'][use], d['capacity_mAh_g'][use]
                increasing(x, 'Voltage'); increasing(q, 'Charge capacity')
                a.plot(q, x, color=colors[idx], label=f'{cycle:g}')
                b.plot(x, np.gradient(q, x, edge_order=2), color=colors[idx])
            a.set(xlabel='Specific capacity (mAh/g)', ylabel='Voltage (V)')
            b.set(xlabel='Voltage (V)', ylabel='dQ/dV (mAh/g/V)')
            a.legend(title='Charge cycle', title_fontsize=6, frameon=False)
            transformations.append('np.gradient(Q,V,edge_order=2), unsmoothed; charge branch, signed dQ/dV')

        elif recipe == 'gitt_pulse':
            _, d = read_numeric(folder, 'data.csv', ('time_min', 'voltage_V', 'current_mA'))
            increasing(d['time_min'], 'Time')
            a.plot(d['time_min'], d['voltage_V'], color=colors[0])
            a.set(xlabel='Time (min)', ylabel='Voltage (V)')
            b.step(d['time_min'], d['current_mA'], where='post', color=colors[1])
            b.set(xlabel='Time (min)', ylabel='Current (mA)')
            for ax in (a,b): ax.set_xlim(d['time_min'][0], d['time_min'][-1])
            transformations.append('Voltage and measured/supplied current share acquisition time; no diffusion coefficient inferred')

        elif recipe == 'ionic_conductivity':
            rows, d = read_numeric(folder, 'data.csv', ('temperature_C', 'conductivity_mS_cm'))
            samples = list(dict.fromkeys(row['sample'] for row in rows))
            if len(samples) > len(colors): raise ValueError('Too many samples for this palette')
            if min(d['temperature_C']) <= -273.15 or min(d['conductivity_mS_cm']) <= 0:
                raise ValueError('Positive Kelvin and conductivity required for logarithms')
            for idx, sample in enumerate(samples):
                keep = np.array([row['sample'] == sample for row in rows])
                t, s = d['temperature_C'][keep], d['conductivity_mS_cm'][keep]
                increasing(t, 'Temperature')
                a.plot(t, s, 'o-', ms=3, color=colors[idx], label=sample)
                b.plot(1000/(t+273.15), np.log(s/1000), 'o', ms=3, color=colors[idx])
            a.set(xlabel='Temperature (°C)', ylabel='Conductivity (mS/cm)')
            b.set(xlabel='1000/T (1/K)', ylabel='ln[conductivity / (S/cm)]')
            a.legend(frameon=False)
            transformations.append('Celsius to Kelvin; mS/cm to S/cm; natural log; no fitted activation energy')

        elif recipe == 'xps_components':
            if len(colors) < 3: raise ValueError('XPS components need at least three palette colors')
            fields = ('binding_energy_eV', 'intensity_counts', 'background_counts', 'component_1', 'component_2', 'component_3')
            _, d = read_numeric(folder, 'data.csv', fields)
            e = d['binding_energy_eV']
            if not (np.all(np.diff(e)>0) or np.all(np.diff(e)<0)):
                raise ValueError('Binding energy must be strictly monotonic')
            if len(opt['component_labels']) != 3 or not opt['fit_method'] or not opt['charge_reference']:
                raise ValueError('Supply component labels, external fit method and charge calibration')
            baseline = d['background_counts']
            model = baseline.copy()
            for idx, field in enumerate(fields[3:]):
                if min(d[field]) < 0: raise ValueError('Components must be baseline-subtracted nonnegative intensities')
                model += d[field]
                a.fill_between(e, baseline, baseline+d[field], color=colors[idx], alpha=.18)
                a.plot(e, baseline+d[field], color=colors[idx], label=opt['component_labels'][idx])
            a.plot(e, d['intensity_counts'], 'o', ms=1.5, mfc='none', mew=.45, color='#41454b', markevery=5, label='Data')
            a.plot(e, model, color='#202124', lw=.85, label='Sum')
            a.plot(e, baseline, '--', color='#686c72', lw=.7, label='Background')
            b.plot(e, d['intensity_counts']-model, color='#41454b', lw=.7)
            b.axhline(0, color='#686c72', lw=.5)
            for ax in (a,b): ax.set_xlim(max(e), min(e)); ax.set_xlabel('Binding energy (eV)')
            a.set_ylabel('Intensity (counts)'); b.set_ylabel('Residual (counts)')
            a.legend(frameon=False, ncol=2, loc='upper left', fontsize=5.5)
            transformations.append('Supplied components + background only; residual = data - sum; no peak fitting or chemical assignment performed')

        elif recipe == 'raman_series':
            rows, d = read_numeric(folder, 'data.csv', ('wavenumber_cm_1', 'intensity_counts'))
            samples = list(dict.fromkeys(row['sample'] for row in rows))
            if len(samples) > len(colors): raise ValueError('Too many spectra for this palette')
            offset = float(opt['display_offset_counts'])
            if not np.isfinite(offset) or offset < 0: raise ValueError('Explicit finite nonnegative display offset required')
            lo, hi = opt['zoom_wavenumber_cm_1']
            if not lo < hi: raise ValueError('Invalid wavenumber zoom')
            for idx, sample in enumerate(samples):
                keep = np.array([row['sample'] == sample for row in rows])
                x, y = d['wavenumber_cm_1'][keep], d['intensity_counts'][keep]
                increasing(x, 'Wavenumber')
                for ax in (a,b): ax.plot(x, y+idx*offset, color=colors[idx], label=sample)
            b.set_xlim(lo, hi)
            for ax in (a,b): ax.set(xlabel='Raman shift (cm$^{-1}$)', ylabel='Intensity + offset (counts)')
            a.legend(frameon=False, loc='upper right')
            transformations.append(f'Only visual offsets i*{offset:g} counts, stored original counts unchanged; b shares spectra and offsets')

        fw, fh = fig.get_size_inches()*25.4
        for letter, ax in axes.items():
            ax.spines[['top','right']].set_visible(False)
            ax.grid(False); ax.tick_params(length=2.3, width=.6, pad=2)
            box = ax.get_position()
            fig.text(box.x0-8/fw, box.y1+2/fh, letter, fontsize=8, fontweight='bold', ha='left', va='bottom')
        alignment = measure_layout(fig, axes, relations)
        if alignment['failures']: raise ValueError(alignment['failures'])
        # Export backends consult rcParams at save time, after this context exits.
        fig.brf_export_rc = rc
        return fig, dict(recipe=recipe, status='optional_variant', style=style, alignment=alignment,
                         requested_font='Arial/Helvetica', actual_font=family, resolved_font_path=font_path,
                         transformations=transformations, test_conditions=meta['test_conditions'],
                         data_status=meta.get('data_status','author_supplied'), source_files=meta['source_files'])
