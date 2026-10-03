"""Primary papers and official scientific methods checked on 2026-10-03.

Only equations, measurement definitions and applicability were consulted. No
paper image, digitised experimental trace, material constants or layout copied.
"""
REFS = {
 'battery': ('COMSOL: Theory for the Lithium-Ion Battery Interface', '', 'https://doc.comsol.com/6.4/doc/com.comsol.help.battery/battery_ug_electrochem_battery.06.63.html', 'Cell capacity, site occupation, Fick transport and elastic particle stress'),
 'kinetics': ('COMSOL: Electrode Kinetics Expressions', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.fce/fce_ug_electrochem.07.095.html', 'Reaction rates, concentration-dependent exchange current and limiting-current approximation'),
 'nernst': ('COMSOL: Modeling Electrochemical Reactions', '', 'https://doc.comsol.com/6.4/doc/com.comsol.help.fce/fce_ug_modeling.05.08.html', 'Equilibrium potential, activities, forward/backward rates and current sign'),
 'flux': ('COMSOL: The Nernst-Planck Equations', '', 'https://doc.comsol.com/6.4/doc/com.comsol.help.edecm/edecm_ug_electrochem.06.119.html', 'Diffusive, migrative and advective molar flux; SI units'),
 'doublelayer': ('COMSOL: Diffuse Double Layer', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.models.edecm.diffuse_double_layer/diffuse_double_layer.html', 'Debye length and dilute Gouy-Chapman-Stern double-layer limits'),
 'capacitance': ('COMSOL: Double-Layer Capacitance', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.fce/fce_ug_electrochem.07.039.html', 'Nonfaradaic charge and double-layer current'),
 'marcus': ('IUPAC Gold Book: Marcus equation', '10.1351/goldbook.M03702', 'https://goldbook.iupac.org/terms/view/M03702', 'Outer-sphere activation barrier; classical inverted-region caveat'),
 'heat': ('COMSOL: Theory for Electrochemical Heat Sources', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.battery/battery_ug_electrochem.07.106.html', 'Ohmic, reaction-overpotential and reversible entropy heat'),
 'thermal': ('COMSOL: Heat Transfer, Conservation of Energy', '', 'https://www.comsol.com/multiphysics/heat-transfer-conservation-of-energy', 'Energy conservation, conductive transport and explicit heat sources'),
 'thermalcell': ('COMSOL: Thermal Modeling of a Cylindrical Lithium-Ion Battery in 2D', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.models.battery.li_battery_thermal_2d_axi/li_battery_thermal_2d_axi.html', 'Spatial temperature and cooling boundary conditions'),
 'scattering': ('NIST: Small Angle Neutron Scattering Fundamentals', '', 'https://ncnr.nist.gov/programs/sans/pdf/sans_theory.pdf', 'Guinier, Porod and scattering-vector definitions'),
 'sphere': ('NIST: Sphere Model', '', 'https://www.ncnr.nist.gov/resources/sansmodels/Sphere.html', 'Sphere form factor and independently declared contrast/size'),
 'structure': ('On the nanoscale structural evolution of solid discharge products in lithium-sulfur batteries using operando scattering', '10.1038/s41467-022-33931-4', 'https://www.nature.com/articles/s41467-022-33931-4', 'Figure 2 and Methods: paired scattering/time, peak width, strain and crystallite-size caveats'),
 'xps': ('NIST: Practical Guide for Inelastic Mean Free Paths, Effective Attenuation Lengths, Mean Escape Depths, and Information Depths in XPS', '10.1116/1.5141079', 'https://www.nist.gov/publications/practical-guide-inelastic-mean-free-paths-effective-attenuation-lengths-mean-escape', 'Attenuation length, takeoff geometry and information depth; EAL is application dependent'),
 'sims': ('NIST/NBS: Secondary ion mass spectrometry', '10.6028/NBS.SP.427', 'https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication427.pdf', 'Secondary ion yield and matrix sensitivity; calibration and sputtering limitations'),
 'surface': ('Dynamic doping and interphase stabilization for cobalt-free and high-voltage Lithium metal batteries', '10.1038/s41467-025-58110-z', 'https://www.nature.com/articles/s41467-025-58110-z', 'Figure 4: surface spectra and ion-signal depth-profile roles only'),
 'beer': ('IUPAC Gold Book: Beer-Lambert law', '10.1351/goldbook.B00626', 'https://goldbook.iupac.org/terms/view/B00626', 'Absorbance/concentration/path-length relation and narrow-band condition'),
 'pfg': ('Direct observation of ion dynamics in supercapacitor electrodes using in situ diffusion NMR spectroscopy', '10.1038/nenergy2016216', 'https://www.nature.com/articles/nenergy2016216', 'Figure 1 and Methods: pulsed-field-gradient signal attenuation and diffusion'),
 'relaxation': ('Bruker: MR Relaxometry of Indiana Limestone rock core', '', 'https://www.bruker.com/ja/resources/library/application-notes-mr/mr-relaxometry-of-indiana-limestone-rock-core.html', 'Repetition/echo-time dependence and longitudinal/transverse relaxation fitting'),
 'solvation': ('Characterising lithium-ion electrolytes via operando Raman microspectroscopy', '10.1038/s41467-021-24297-0', 'https://www.nature.com/articles/s41467-021-24297-0', 'Raman response, concentration-gradient calibration and thermodynamic/transport distinctions'),
 'correlation': ('Fundamental investigations on the ionic transport and thermodynamic properties of non-aqueous potassium-ion electrolytes', '10.1038/s41467-023-39523-0', 'https://www.nature.com/articles/s41467-023-39523-0', 'Association, self-diffusion, collective conductivity and thermodynamic-factor distinctions'),
 'dispersion': ('COMSOL: Dispersion Theory', '', 'https://doc.comsol.com/6.4/doc/com.comsol.help.acdc/acdc_ug_theory.05.36.html', 'Debye permittivity relaxation and loss'),
 'sei': ('COMSOL: SEI Formation in a Lithium-Ion Battery', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.models.battery.sei_formation/sei_formation.html', 'Film growth, consumed inventory and resistive film loss'),
 'growth': ('Transition between growth of dense and porous films: theory of dual-layer SEI', '10.1039/D2CP00188H', 'https://pubs.rsc.org/en/content/articlehtml/2022/cp/d2cp00188h', 'Diffusion-limited square-root growth as a restricted model, not a universal law'),
 'aging': ('COMSOL: Capacity Loss', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.battery/battery_ug_electrochem_battery.06.26.html', 'Parasitic-current accounting, throughput and declared aging factors'),
 'stress': ('COMSOL: Diffusion-Induced Stress in a Lithium-Ion Battery', '', 'https://doc.comsol.com/6.3/doc/com.comsol.help.models.battery.lib_diffusion_induced_stress/lib_diffusion_induced_stress.html', 'Isotropic elastic diffusion stress, strain energy and quasi-static assumption'),
 'stresspotential': ('Sethuraman et al.: In Situ Measurements of Stress-Potential Coupling in Lithiated Silicon, JES 157 A1253–A1261 (2010)', '10.1149/1.3489378', 'https://arxiv.org/pdf/1108.0372', 'Eq. 1: negative first-order stress term in chemical potential; Eqs. 8–9 and 14: positive equilibrium-potential response to tensile stress. Hydrostatic specialization sigma_h=tr(sigma)/3, Omega=vSi*eta; the paper thin-film coefficient and measured values are not reused.'),
 'uncertainty': ('NIST TN 1297: Appendix A, Law of Propagation of Uncertainty', '', 'https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-law-propagation-uncertainty', 'First-order uncertainty propagation including covariance'),
 'calibration': ('NIST/SEMATECH: Uncertainties of calibrated values', '', 'https://www.itl.nist.gov/div898/handbook/mpc/section3/mpc367.htm', 'Calibration inverse uncertainty and check-standard interpretation'),
 'quadrature': ('NIST/SEMATECH: Uncertainty approach', '', 'https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc52.htm', 'Standard uncertainty, quadrature and correlated components'),
 'levich': ('Pine Research: Levich Study (RDE)', '', 'https://pineresearch.com/support-article/levich-study-rde/', 'Levich equation with 0.620 coefficient and Koutecky-Levich inverse-current form'),
 'nucleation': ('Theoretical and experimental studies of multiple nucleation', '10.1016/0013-4686(83)85163-9', 'https://www.sciencedirect.com/science/article/pii/0013468683851639', 'Diffusion-controlled three-dimensional multiple-nucleation transient theory'),
 'sand': ('Diffuse-charge effects on the transient response of electrochemical cells', '10.1103/PhysRevE.81.021503', 'https://web.mit.edu/bazant/www/papers/pdf/Soestbergen_2010_PRE.pdf', 'Sand time and diffusion-limited transient; applicability before depletion'),
 'line': ('XrayLarch: XANES analysis, linear methods and pre-edge peak fitting', '', 'https://xraypy.github.io/xraylarch/xafs_xanes.html', 'Sections 14.3.1–14.3.2: Gaussian/Lorentzian/Voigt models and normalized convex spectral mixture'),
 'raman': ('IUPAC: Raman scattering', '10.1351/goldbook.08667', 'https://goldbook.iupac.org/terms/view/08667/plain', 'Polarizability and Stokes/anti-Stokes energy-level distinction; projection and occupation factors are independently derived'),
 'harmonic': ('IUPAC: harmonic approximation', '10.1351/goldbook.HT07041', 'https://goldbook.iupac.org/terms/view/HT07041/pdf', 'Mass-weighted harmonic displacement approximation; diatomic reduced-mass specialization derived independently'),
 'thermo': ('IUPAC Green Book: Quantities, Units and Symbols in Physical Chemistry, third edition', '', 'https://iupac.org/wp-content/uploads/2019/05/IUPAC-GB3-2012-2ndPrinting-PDFsearchable.pdf', 'Sections 2.9, 2.11, 2.12, 2.15: statistical weights, activity/free energy, equilibrium kinetics and transport quantities'),
 'coverage': ('NIST/SEMATECH: Confidence Limits for the Mean', '', 'https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm', 'Student-t interval, n-1 degrees of freedom and repeated-sampling interpretation'),
}

def reference(key, supports):
    title, doi, url, location = REFS[key]
    return dict(title=title, doi=doi, url=url, figure_panel=location,
        supports=supports, checked_at='2026-10-03',
        scope='Method/equation/caveat reference only. Original analytic teaching inputs; no copied paper points, pixels or experimental inference.')
