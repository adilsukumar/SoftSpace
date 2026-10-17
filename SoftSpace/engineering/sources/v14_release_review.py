"""Explicit design limits and next physical measurements, no invented passes."""
import json,hashlib
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v14-results'
rows=[
 {'interface':'Pin and front guide bore','nominal_radial_clearance_mm':.05,'basis':'2.2mm pin in2.3mm bore','status':'Manufacturing capability not established'},
 {'interface':'Collar and housing cavity','nominal_radial_clearance_mm':.1,'basis':'6.8mm collar in7mm cavity','status':'Check tolerance wear friction debris and roundness'},
 {'interface':'Coil allocation and housing','nominal_radial_clearance_mm':.325,'basis':'6.35mm coil outer envelope in7mm cavity','status':'Actual coil shape and buckling not simulated'},
 {'interface':'Coil inner allocation and cap guide boss','nominal_radial_clearance_mm':.825,'basis':'5.65mm coil inner envelope over4mm guide','status':'Actual coil ends and compression fixture unvalidated'},
 {'interface':'Cap screw envelope and clearance hole','nominal_radial_clearance_mm':.1,'basis':'1.6mm nominal shaft in1.8mm hole','status':'Nominal hardware only; supplier drawing and torque absent'},
 {'interface':'Cap nut envelope and pocket','nominal_across_flats_difference_mm':.1,'basis':'3.2mm nut in3.3mm pocket','status':'Nut insertion access and antirotation strength unvalidated'},
 {'interface':'Pull knob and stem','nominal_radial_clearance_mm':0,'basis':'2.2mm through bore around2.2mm shaft','status':'Contact envelope only; this does not model a retained thread or prove pullout resistance'}]
out={'revision':'V14','manufacturing_release':False,'interfaces':rows,'digital_release_blockers':[
 'Specify an actual retained knob connection and its thread or equivalent, cap fastener grade, torque and loosening resistance',
 'Add and check angular stops and finger clearance; present pin lock is not a complete pinch or folding safety solution',
 'Solve or measure assembled bearing contact, screw preload, guide friction, clamp retention and tolerance effects',
 'Define materials and manufacturing process using actual nonlinear compression, cover stretch, friction, ageing and fatigue data',
 'Improve and recheck child packing; earlier V12 child box reductions are only1to3percent',
 'Native editable Fusion reconstruction has not been done after V10; V14 is STEP candidate geometry'],
 'physical_work_required':[
 {'test':'Sony original pad and mount measurement','method':'Measure both pads opening, outer shape, uncompressed thickness, mounting lip and groove dimensions. Record photos and repeat measurements; user deferred this task.','comparison':'Original WH CH720N only; no universal mount inference'},
 {'test':'Foam and cover calibration','method':'Measure compression and recovery at several strains and speeds, warm and humid conditions, cover stretch and friction. Identify actual purchased grade and lot.','comparison':'Uniform reference pad versus softer glasses zone using same cover and mounting'},
 {'test':'Worn force and fit','method':'Measure band force across intended fit range and clamp positions; measure pad compression on representative head fixtures with several glasses arm shapes.','comparison':'Same head geometry, seating procedure and duration; no force threshold called universally comfortable'},
 {'test':'Incoming noise attenuation','method':'Use a controlled sound field and calibrated microphones or qualified laboratory fixtures. Repeat original and candidate seating, glasses frames and orientations; record frequency dependent levels and uncertainty.','comparison':'No music playing; comparable passive or ANC state and same fixture. Do not substitute a cavity estimate for measured attenuation'},
 {'test':'Outgoing playback leakage and response','method':'On the Sony, match measured internal playback level before comparing outside levels at fixed distances and directions. Record response and ANC behaviour after reseating each pad.','comparison':'Same headphone, source, settings and room; original, uniform new and glasses zone pads'},
 {'test':'Durability and servicing','method':'Measure release and pullout forces, cycle folds and sliders, inspect fastener loosening, overload and controlled drop samples, cleaning effects, sweat exposure and ageing. Define acceptance levels before test.','comparison':'Same sample preparation and test conditions; a static material ratio is not fatigue or drop evidence'},
 {'test':'Heat texture and sensory acceptance','method':'With voluntary informed participants, offer immediate removal and breaks; collect individual feedback on pressure, heat, texture, rubbing sounds, bulk and ease of control. Include autistic people in design decisions.','comparison':'Matched alternative products where appropriate; report individual variation and stop reasons, not a universal preference'}],
 'market_limit':'Existing selected market review and70material-family register are not exhaustive. No final price, Indian stock absence, pain relief, zero leakage or market superiority established.'}
(O/'release_review.json').write_text(json.dumps(out,indent=2));print('Release limits and physical comparison protocol saved')
