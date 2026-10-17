"""Derive V5 builder without changing the saved V4 builder or exports."""
from pathlib import Path
p=Path(__file__).parent/'CushionNext'
s=(p/'EngineeringFinal.py').read_text(encoding='utf-8-sig')
s=s.replace("for family in ['adult','child']:\n            c=cfg[family]", "for recipe in json.load(open(os.path.join(out,'extendable-recipes.json'))):\n            family=recipe['family'];variant=recipe['name'];c=dict(cfg[family]);c['band_radius']=recipe['band_halfspan_mm'];c['band_thickness']=recipe['band_thickness_mm'];c['band_width']=recipe['band_width_mm'];band_z=110")
s=s.replace("'EarDefender_V4_'+family", "'EarDefender_V5_'+variant")
s=s.replace("band_z=110", "c['contour_fraction']=recipe['contour_fraction'];band_z=110")
s=s.replace("'cad_final_report.json'", "'cad_v5_report.json'")
s=s.replace("'ReplacementCushion_V4_'+family", "'ReplacementCushion_V5_'+variant")
s=s.replace("'OwnPassiveDefender_V4_'+family", "'OwnPassiveDefender_V5_'+variant")
s=s.replace("report[family+", "report[variant+")
s=s.replace("report[family]=", "report[variant]=")
s=s.replace("append(family+': cup/fork articulation clash')", "append(variant+': cup/fork articulation clash')")
s=s.replace("'BandEndPin'", "'SliderForkPin'")
# Tongue attaches at the existing fork pin; stays in the lower/cup assembly while the crown slides.
mark="                assembly.bRepBodies.add(yoke,bf);names.append(prefix+'PinnedMountFork')"
s=s.replace(mark,mark+"""
                tongue=side_box(R-2,R+2,-8,8,61,134)
                boolean(tongue,temp.createCylinderOrCone(point(x,-9,65),.11,point(x,9,65),.11),D)
                # Outboard stop clears the inward-curving crown; 1 mm end clearance at 30 mm extension.
                boolean(tongue,side_box(R+1.5,R+4.5,-5,5,130,134),U)
                assembly.bRepBodies.add(tongue,bf);names.append(prefix+'SlidingTongue_4x16')
""")
s=s.replace("center_z=65+h-circle", "center_z=band_z+h-circle")
start=s.index('            for side in [-1,1]:\n                lug=',s.index('            shaped=temp.copy(actual)'))
end=s.index('            actual.deleteMe()',start)
s=s[:start]+"""            for side in [-1,1]:
                x=side*R
                guide=box(x-4,x+4,-11,11,band_z-30,band_z+4)
                boolean(shaped,guide,U)
                channel=box(x-2.3,x+2.3,-8.3,8.3,60,145)
                boolean(shaped,channel,D)
                screw_bore=temp.createCylinderOrCone(point(x,7,band_z-15),.15,point(x,13,band_z-15),.15)
                boolean(shaped,screw_bore,D)
            # Guide clamp uses a hand knob; thread geometry and locking force are not validated.
            gb=assembly.features.baseFeatures.add();gb.startEdit();guide_names=[]
            for side in [-1,1]:
                x=side*R
                screw=temp.createCylinderOrCone(point(x,8,band_z-15),.14,point(x,13,band_z-15),.14)
                boolean(screw,temp.createCylinderOrCone(point(x,13,band_z-15),.45,point(x,16,band_z-15),.45),U)
                assembly.bRepBodies.add(screw,gb);guide_names.append(('Left' if side<0 else 'Right')+'SliderClampKnob_ThreadPlaceholder')
            gb.finishEdit();design.timeline.moveToEnd()
            for j,name in enumerate(guide_names):assembly.bRepBodies.item(assembly.bRepBodies.count-2+j).name=name
"""+s[end:]
s=s.replace("'CircularCapBand_WithPinnedLugs'", "'CircularCapBand_WithSliderGuides'")
start=s.index('            adjustments=[]')
end=s.index("            path=os.path.join",start)
s=s[:start]+"""            adjustments=[]
            bandbody=assembly.bRepBodies.itemByName('CircularCapBand_WithSliderGuides')
            for extension in range(0,31,5):
                overlap=0;translation=adsk.core.Matrix3D.create();translation.translation=adsk.core.Vector3D.create(0,0,(extension-15)/10)
                for side in [-1,1]:
                    prefix='Left' if side<0 else 'Right';probe=temp.copy(bandbody);temp.transform(probe,translation)
                    for name in ['PinnedMountFork','SlidingTongue_4x16','ClosedCup']:
                        intersection=temp.copy(probe)
                        if temp.booleanOperation(intersection,temp.copy(assembly.bRepBodies.itemByName(prefix+name)),I):overlap+=max(intersection.volume,0)*1000
                adjustments.append({'extension_mm':extension,'moving_band_overlap_mm3':overlap,'tongue_engagement_mm':min(34,79-extension)})
            report[variant+'_slider_travel']=adjustments
            if max(x['moving_band_overlap_mm3'] for x in adjustments)>.01:report.setdefault('failed_gates',[]).append(variant+': slider travel interference')
"""+s[end:]
s=s.replace("report['status']='complete'", "report['status']='complete';report['recipes']=json.load(open(os.path.join(out,'extendable-recipes.json')))")
pose_marker="            if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(path+'.f3d'))"
pos=s.index(pose_marker)
s=s[:pos]+"""            for extension in [0,30]:
                pose_occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create());pose=pose_occ.component;pose.name=variant+'_Extension_'+str(extension)
                pb=pose.features.baseFeatures.add();pb.startEdit();pose_names=[]
                shift=adsk.core.Matrix3D.create();shift.translation=adsk.core.Vector3D.create(0,0,(extension-15)/10)
                for j in range(assembly.bRepBodies.count):
                    body=assembly.bRepBodies.item(j);copy=temp.copy(body)
                    if body.name in ['CircularCapBand_WithSliderGuides','SoftCrownPadding_5mm_Assumed'] or 'SliderClampKnob' in body.name:temp.transform(copy,shift)
                    pose.bRepBodies.add(copy,pb);pose_names.append(body.name)
                pb.finishEdit()
                for j,name in enumerate(pose_names):pose.bRepBodies.item(j).name=name
                pose_occ.isLightBulbOn=False
                pose_path=path+'_Extension_'+str(extension)+'.step'
                if not design.exportManager.execute(design.exportManager.createSTEPExportOptions(pose_path,pose)):raise RuntimeError('Pose export failed')
                report['files'].append(pose_path)
"""+s[pos:]
start=s.index("        report['limitations']=")
end=s.index("    except Exception:",start)
s=s[:start]+"""        report['limitations']=['Six provisional widths, each with 30 mm crown-to-cup slider travel and clamp knob.',
          'Guide friction, threads, pull-out, fatigue, child access, pinch risk and retention need physical validation.',
          'Slider section model omits overlap stiffness, guide notches and 3D torsion.',
          'Band coordinates are unloaded; no population coverage or measured comfort/attenuation established.',
          'Crown padding and child ear fit remain geometric assumptions; cover/foam properties unmeasured.']
        save_report();ui.messageBox('Six V5 sizes exported with sliding headbands. Read cad_v5_report.json for clearance gates. Simulation and physical validation remain provisional.','V5 extendable prototypes saved')
"""+s[end:]
(p/'EngineeringV5.py').write_text(s,encoding='utf-8')
runner=(p/'CushionNext.py').read_text(encoding='utf-8-sig').replace('EngineeringFinal.py','EngineeringV5.py')
(p/'CushionNext.py').write_text(runner,encoding='utf-8')
print('Prepared six-size V5 builder')
