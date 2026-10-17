from pathlib import Path
p=Path(__file__).parent/'CushionNext'/'RefineBandV7.py';s=p.read_text();start=s.index('   for i in range(root.occurrences.count):');end=s.index('   if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions',start)
s=s[:start]+'''   for ext in [0,30]:
    occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create());pose=occ.component;pose.name=name+'_Extension_'+str(ext)+'_V7'
    bf=pose.features.baseFeatures.add();bf.startEdit();names=[]
    tr=adsk.core.Matrix3D.create();tr.translation=adsk.core.Vector3D.create(0,0,(ext-15)/10)
    for j in range(comp.bRepBodies.count):
     original=comp.bRepBodies.item(j);copy=temp.copy(original)
     if original.name in ['CircularCapBand_WithSliderGuides','SoftCrownPadding_5mm_Assumed'] or 'SliderClampKnob' in original.name:temp.transform(copy,tr)
     pose.bRepBodies.add(copy,bf);names.append(original.name)
    bf.finishEdit();design.timeline.moveToEnd()
    for j,bodyname in enumerate(names):pose.bRepBodies.item(j).name=bodyname;pose.bRepBodies.item(j).isVisible=True
    occ.isLightBulbOn=True
    if pose.bRepBodies.count!=28:raise RuntimeError('New pose does not contain28 bodies: '+str(pose.bRepBodies.count))
    posepath=base+'_Extension_'+str(ext)+'.step'
    if not design.exportManager.execute(design.exportManager.createSTEPExportOptions(posepath,pose)):raise RuntimeError('Pose export failed')
    report['files'].append(posepath);occ.isLightBulbOn=False
'''+s[end:];p.write_text(s);compile(s,str(p),'exec')
