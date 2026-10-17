"""Fail closed when measurement-dependent analyses have no measured inputs."""
import json
from pathlib import Path
P=Path(__file__).parent;D=P/'engineering-v19-results/prototype-handoff';s=json.loads((D/'measured_inputs_REQUIRED.json').read_text());checks={
 'foam_calibration':bool(s['measured'] and s['foam']['strain'] and s['foam']['compression_stress_kPa']),
 'cover_calibration':bool(s['measured'] and s['cover']['biaxial_stretch_data'] and s['cover']['friction_dry'] is not None),
 'headband_calibration':bool(s['measured'] and s['band']['force_width_points']),
 'hinge_retention_validation':bool(s['measured'] and s['hinge']['breakaway_and_running_torque_points'] and s['hinge']['cycle_torque_points']),
 'Sony_model_specific_fit':bool(s['measured'] and s['Sony_mount']['dimensions_mm'] and s['Sony_mount']['shape_reference']),
 'acoustic_validation':bool(s['measured'] and s['acoustic']['original_pad_reseated_spectra'] and s['acoustic']['new_pad_reseated_spectra']),
 'thermal_validation':bool(s['measured'] and s['thermal']['time_temperature_humidity_points'])}
r=dict(status='Input gated',ready=checks,all_ready=all(checks.values()),scope='Checks presence only. Even populated files need traceability, units, uncertainty and expert review before calibration. Blank forms do not count as simulated or measured tests.');(D/'input_readiness.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
