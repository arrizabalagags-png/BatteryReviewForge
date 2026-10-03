"""Declared teaching models; never supply missing author data.

Pure functions are also used by the repository showcase. Recipe copies remain
self contained. References define model boundaries, not numerical measurements.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import sys

PACK = Path(__file__).resolve().parents[1]
GAMRY = 'https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/'
CE_CAUTION = 'https://www.nature.com/articles/s41467-025-60833-y'
LI_PROTOCOL = 'https://www.nature.com/articles/s41560-020-0648-z'
BRAGG = 'https://dictionary.iucr.org/Bragg%27s_law'


def inventory_cycles(initial_capacity, count, steady_loss, transient_loss, decay_cycles):
    """Finite inventory, one irreversible loss, no excess or compensation.

    Qchg[n]=L[n-1], Qdis[n]=eta[n]*Qchg[n], L[n]=Qdis[n]. This restrictive
    toy is NOT a universal CE-to-capacity rule for real cells.
    """
    if (not math.isfinite(initial_capacity) or initial_capacity <= 0
            or not isinstance(count, int) or isinstance(count, bool) or count < 1
            or not math.isfinite(decay_cycles) or decay_cycles <= 0
            or not all(math.isfinite(x) and x >= 0 for x in (steady_loss, transient_loss))
            or steady_loss + transient_loss >= 1):
        raise ValueError('Finite positive capacity/count/decay and loss fraction in [0,1) required.')
    inventory = initial_capacity
    rows = []
    for cycle in range(1, count + 1):
        eta = 1 - steady_loss - transient_loss * math.exp(-(cycle - 1) / decay_cycles)
        charge = inventory
        discharge = eta * charge
        lost = charge - discharge
        inventory = discharge
        rows.append({'cycle': cycle, 'charge': charge, 'discharge': discharge,
                     'ce_pct': 100 * discharge / charge, 'lost': lost,
                     'inventory_after': inventory})
    return rows


def fullcell_voltage(fraction, direction='discharge', low=2.9, high=4.2):
    """Bounded monotonic display relation; not a material thermodynamic fit."""
    if (not all(math.isfinite(x) for x in (fraction, low, high))
            or not 0 <= fraction <= 1 or not low < high or direction not in {'charge', 'discharge'}):
        raise ValueError('Fraction 0..1, ordered voltage window and valid direction required.')
    shape = .55 * fraction + .45 * fraction ** 7
    return low + (high - low) * shape if direction == 'charge' else high - (high - low) * shape


def halfcell_cycles(initial_capacity, count, activation_fraction, activation_cycles,
                    fade_per_cycle, late_fade_per_cycle2, late_fade_start,
                    steady_ce_loss, transient_ce_loss, ce_decay_cycles):
    """Excess-Li half-cell: accessible cathode capacity and CE are independent.

    The chosen accessible-activity function is a phenomenological display law.
    Qcharge=Qdis/eta accounts for the external coulombic difference but that
    difference does not drive the cathode's capacity fade in this model.
    """
    numeric = (initial_capacity, activation_fraction, activation_cycles,
               fade_per_cycle, late_fade_per_cycle2, late_fade_start,
               steady_ce_loss, transient_ce_loss, ce_decay_cycles)
    if (not all(math.isfinite(x) for x in numeric) or initial_capacity <= 0
            or not isinstance(count, int) or isinstance(count, bool) or count < 1
            or not 0 <= activation_fraction < 1 or activation_cycles <= 0
            or fade_per_cycle < 0 or late_fade_per_cycle2 < 0 or late_fade_start < 0
            or steady_ce_loss < 0 or transient_ce_loss < 0
            or steady_ce_loss + transient_ce_loss >= 1 or ce_decay_cycles <= 0):
        raise ValueError('Invalid half-cell teaching model parameters.')
    rows = []
    cumulative_side_charge = 0.0
    for cycle in range(1, count + 1):
        activity = ((1 - activation_fraction * math.exp(-(cycle - 1) / activation_cycles))
                    * math.exp(-fade_per_cycle * (cycle - 1)
                               - late_fade_per_cycle2 * max(cycle - late_fade_start, 0) ** 2))
        discharge = initial_capacity * activity
        eta = 1 - steady_ce_loss - transient_ce_loss * math.exp(-(cycle - 1) / ce_decay_cycles)
        charge = discharge / eta
        side_charge = charge - discharge
        cumulative_side_charge += side_charge
        rows.append({'cycle': cycle, 'charge': charge, 'discharge': discharge,
                     'ce_pct': 100 * discharge / charge, 'lost': side_charge,
                     'accessible_fraction': activity,
                     'cumulative_side_charge': cumulative_side_charge})
    return rows


def symmetric_rc_rows(sample, half_cycles, points_per_half, current_mA_cm2,
                      half_capacity_mAh_cm2, rs_ohm_cm2, rp_ohm_cm2, tau_h):
    """Right-continuous current, continuous RC state, unique timestamps.

    V=j*Rs+eta; d eta/dt=(j*Rp-eta)/tau. Apparent C=tau/Rp is an
    equivalent-circuit teaching element, not measured lithium double-layer C.
    Passed Q is external charge, not certified plated lithium mass.
    """
    numeric = (current_mA_cm2, half_capacity_mAh_cm2, rs_ohm_cm2, rp_ohm_cm2, tau_h)
    if (not all(math.isfinite(x) and x > 0 for x in numeric)
            or not isinstance(half_cycles, int) or isinstance(half_cycles, bool) or half_cycles < 1
            or not isinstance(points_per_half, int) or isinstance(points_per_half, bool) or points_per_half < 2):
        raise ValueError('Positive current, half-capacity, RC parameters and integer resolution required.')
    duration = half_capacity_mAh_cm2 / current_mA_cm2
    start_states = []
    eta = 0.0
    for half in range(half_cycles):
        start_states.append(eta)
        current = (1 if half % 2 == 0 else -1) * current_mA_cm2
        target = current * rp_ohm_cm2  # mA * ohm = mV; identical area basis
        eta = target + (eta - target) * math.exp(-duration / tau_h)
    rows = []
    for index in range(half_cycles * points_per_half + 1):
        half = min(index // points_per_half, half_cycles - 1)
        phase = (index - half * points_per_half) / points_per_half
        current = (1 if half % 2 == 0 else -1) * current_mA_cm2
        target = current * rp_ohm_cm2
        state = target + (start_states[half] - target) * math.exp(-phase * duration / tau_h)
        previous_signed = half_capacity_mAh_cm2 if half % 2 else 0.0
        rows.append({'sample': sample, 'time_h': index * duration / points_per_half,
                     'half_cycle': half + 1, 'current_mA_cm2': current,
                     'fraction_of_half_cycle': phase, 'voltage_mV': current * rs_ohm_cm2 + state,
                     'polarization_mV': state, 'passed_in_half_mAh_cm2': phase * half_capacity_mAh_cm2,
                     'cumulative_signed_mAh_cm2': previous_signed + current * phase * duration})
    return rows


def bragg_angle(d_A, wavelength_A=1.5406):
    """First-order 2theta in degrees; d and wavelength both in Angstrom."""
    if (not math.isfinite(d_A) or not math.isfinite(wavelength_A)
            or wavelength_A <= 0 or d_A <= wavelength_A / 2):
        raise ValueError('Positive wavelength and d > wavelength/2 required.')
    return 2 * math.degrees(math.asin(wavelength_A / (2 * d_A)))


def reference(url, title, supports):
    return {'url': url, 'title': title, 'supports': supports,
            'scope': 'model_definition_only', 'checked_date': '2026-10-01'}


def scientific_basis(kind):
    """Demo assumptions, separate from real author input and its acceptance."""
    basis = {'schema_version': 1, 'model_class': 'analytic_model',
             'data_origin': 'original_synthetic',
             'parameter_origin': 'explicit teaching choices; not reported measurements',
             'validation_scope': 'Declared teaching model; no experimental/material certification'}
    if kind == 'full_cell':
        basis.update(model_class='phenomenological_model',
                     equations=['eta_n=1-l_ss-l_tr*exp(-(n-1)/tau_cycles)',
                                'Qcharge_n=L_(n-1); Qdischarge_n=eta_n*Qcharge_n; L_n=Qdischarge_n',
                                'CE_n=100*Qdischarge_n/Qcharge_n; loss_n=Qcharge_n-Qdischarge_n',
                                's(f)=0.55*f+0.45*f^7; Vdis=4.2-1.3*s(f); Vchg=2.9+1.3*s(f)'],
                     assumptions=['No excess cyclable inventory, no electrode compensation, no active-material loss or reversible self-discharge.',
                                  'Inventory-only loss is a restrictive teaching case, not a real-cell acceptance criterion.',
                                  'Voltage shape is a bounded monotonic display relation, not an NMC/graphite model.'],
                     parameters={'count_cycles': 40, 'A': {'initial_mAh_g': 170, 'loss_ss': .0012, 'loss_tr': .005, 'tau_cycles': 5},
                                 'B': {'initial_mAh_g': 164, 'loss_ss': .002, 'loss_tr': .007, 'tau_cycles': 5}, 'voltage_window_V': [2.9, 4.2]},
                     references=[reference(CE_CAUTION, 'Deciphering coulombic loss in lithium-ion batteries and beyond',
                                           'Charge conservation and warning that coulombic loss need not equal capacity loss; all numerical parameters are self-chosen.')],
                     limitations=['No chemistry, life, N/P, electrolyte volume, electrode compensation or mechanism is certified.',
                                  'CE/product relationship applies only under this toy inventory model.'])
    elif kind == 'li_li':
        basis.update(equations=['T_half=Q_half/abs(j); j alternates sign each T_half',
                                'd eta/dt=(j*Rp-eta)/tau; V=j*Rs+eta',
                                'eta(t)=j*Rp+(eta_start-j*Rp)*exp(-t/tau); Qpassed=integral(j dt)'],
                     assumptions=['Zero open-circuit offset; constant positive passive linear terminal RC parameters.',
                                  'Applied current is a right-continuous zero-order hold; RC state stays continuous at switching.',
                                  'External charge is not a lithium-deposition mass measurement.'],
                     parameters={'half_cycles': 40, 'j_mA_cm2': 1, 'Q_half_mAh_cm2': 1,
                                 'A': {'Rs_ohm_cm2': 10, 'Rp_ohm_cm2': 24, 'tau_h': .08},
                                 'B': {'Rs_ohm_cm2': 12, 'Rp_ohm_cm2': 35, 'tau_h': .12}},
                     references=[reference(GAMRY, 'Basics of Electrochemical Impedance Spectroscopy',
                                           'Ohm law, capacitor differential relation and passive equivalent circuits; values are not measured.'),
                                 reference(LI_PROTOCOL, 'Understanding and applying coulombic efficiency in lithium metal batteries',
                                           'Cell configuration and plating/stripping protocol boundaries; no symmetric trace certifies CE or full-cell stability.')],
                     limitations=['No SEI, dendrite, short circuit, transfer mass, lifetime or CE claim follows from this ideal terminal RC trace.'])
    elif kind == 'operando_xrd':
        basis.update(model_class='phenomenological_model',
                     equations=['2theta=2*asin(lambda/(2*d)) in degrees (first order)',
                                'd1(p)=2.38*(1-0.012*p) A; d2(p)=2.18*(1+0.008*p) A',
                                'I(2theta,p)=background+sum(amplitude*exp(-0.5*((2theta-center)/sigma)^2))',
                                'V(p)=3.1+1.1*p'],
                     assumptions=['Two independent fictitious d-spacings, not indexed planes of a refined shared crystal.',
                                  'p is chosen fractional progression, not measured SOC; voltage is an independent display function.',
                                  'Gaussian widths, amplitudes and background are display parameters, not structure factors or measured diffraction.'],
                     parameters={'wavelength_A': 1.5406, 'd1_initial_A': 2.38, 'd2_initial_A': 2.18,
                                 'strain1_at_p1': -.012, 'strain2_at_p1': .008,
                                 'sigma_deg': [.21, .28], 'amplitudes_au': [1, .6], 'background_au': .04},
                     references=[reference(BRAGG, "IUCr Online Dictionary: Bragg's law",
                                           'Diffraction angle versus wavelength and d spacing; no material assignment or literature numerical data.')],
                     limitations=['No phase transition, crystallographic refinement, material identity or voltage-driven causality is demonstrated.'])
    else:
        raise ValueError('Unknown teaching model: ' + str(kind))
    return basis


def write_csv(path, headers, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def generate_tables(kind, root):
    """Write known model to explicit demo target; never an author fallback."""
    samples = ['Demo sample A', 'Demo sample B']
    basis = scientific_basis(kind)
    if kind == 'full_cell':
        rows, profiles = [], []
        for sample, key in zip(samples, ('A', 'B')):
            p = basis['parameters'][key]
            ledger = inventory_cycles(p['initial_mAh_g'], 40, p['loss_ss'], p['loss_tr'], p['tau_cycles'])
            for r in ledger:
                rows.append((sample, r['cycle'], r['discharge'], r['ce_pct'], r['charge'], r['lost'], r['inventory_after']))
            for cycle in (1, 20, 40):
                q = ledger[cycle - 1]['discharge']
                profiles.extend((sample, cycle, j * q / 25, fullcell_voltage(j / 25)) for j in range(26))
        write_csv(root / 'cycling.csv', ['sample', 'cycle', 'capacity', 'ce', 'charge_capacity', 'irreversible_loss', 'inventory_after'], rows)
        write_csv(root / 'profiles.csv', ['sample', 'cycle', 'capacity', 'voltage'], profiles)
    elif kind == 'li_li':
        rows = []
        for sample, key in zip(samples, ('A', 'B')):
            p = basis['parameters'][key]
            trace = symmetric_rc_rows(sample, 40, 20, 1, 1, p['Rs_ohm_cm2'], p['Rp_ohm_cm2'], p['tau_h'])
            rows.extend((sample, r['time_h'], r['voltage_mV'], r['current_mA_cm2'], r['half_cycle'],
                         r['passed_in_half_mAh_cm2'], r['cumulative_signed_mAh_cm2']) for r in trace)
        write_csv(root / 'trace.csv', ['sample', 'time', 'voltage', 'current_mA_cm2', 'half_cycle', 'passed_in_half_mAh_cm2', 'cumulative_signed_mAh_cm2'], rows)
    elif kind == 'operando_xrd':
        rows, voltage = [], []
        for sample in samples[:1]:
            for j in range(16):
                progress = j / 15
                voltage.append((sample, progress, 3.1 + 1.1 * progress))
                centers = (bragg_angle(2.38 * (1 - .012 * progress)), bragg_angle(2.18 * (1 + .008 * progress)))
                for k in range(65):
                    theta = 35 + k * .125
                    intensity = .04 + math.exp(-.5 * ((theta - centers[0]) / .21) ** 2) + .6 * math.exp(-.5 * ((theta - centers[1]) / .28) ** 2)
                    rows.append((sample, theta, progress, intensity))
        write_csv(root / 'diffraction.csv', ['sample', 'two_theta', 'progress', 'intensity'], rows)
        write_csv(root / 'voltage.csv', ['sample', 'progress', 'voltage'], voltage)
    (root / 'model.json').write_text(json.dumps(basis, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return basis


def main():
    sys.path.insert(0, str(PACK / 'src'))
    from output_safety import new_directory
    from cli_runtime import configure_utf8
    configure_utf8()
    parser = argparse.ArgumentParser(description='仅生成有明确方程/假设的原创合成示例；不能替代作者数据。')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root, _ = new_directory(args.out.resolve())
    config = json.loads((PACK / 'config.demo.json').read_text(encoding='utf-8-sig'))
    generate_tables(config['resource_id'], root)
    for table in config['data'].values():
        table['path'] = Path(table['path']).name
    (root / 'config.demo.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('原创合成数据：' + str(root))


if __name__ == '__main__':
    main()
