"""Assembly correction and limited hard-edge finishing; preserves V5."""
from pathlib import Path
p=Path(__file__).parent/'CushionNext'
s=(p/'EngineeringV5.py').read_text(encoding='utf-8-sig')
s=s.replace('V5','V6').replace('cad_v5_report','cad_v6_report')
s=s.replace("c['ear_opening_height']+2,-1.2,0)","c['ear_opening_height']+2,-1.4,-.2)")
s=s.replace('boolean(cup,temp.copy(carrier),D)',"seat=ring(c['pad_outer_width']+3,c['pad_outer_height']+3,c['ear_opening_width']+2,c['ear_opening_height']+2,-1.4,0)\n            boolean(cup,seat,D)")
marker='            occ.isLightBulbOn=False'
pos=s.index(marker)
s=s[:pos]+"""            # Finish accessible exterior bounding-box corners without altering the soft cushion shape.
            finishing=[]
            for name in [assembly.bRepBodies.item(j).name for j in range(assembly.bRepBodies.count)]:
                if not any(t in name for t in ['SlidingTongue','PinnedMountFork','PivotPin','SliderForkPin','RetainingCap']):continue
                body=assembly.bRepBodies.itemByName(name);bounds=body.boundingBox;edges=adsk.core.ObjectCollection.create()
                for j in range(body.edges.count):
                    edge=body.edges.item(j)
                    if 'Pin' in name and 'PinnedMountFork' not in name or 'RetainingCap' in name:
                        edges.add(edge);continue
                    if not adsk.core.Line3D.cast(edge.geometry):continue
                    q=edge.pointOnEdge
                    boundary=sum(min(abs(v-lo),abs(v-hi))<.002 for v,lo,hi in [(q.x,bounds.minPoint.x,bounds.maxPoint.x),(q.y,bounds.minPoint.y,bounds.maxPoint.y),(q.z,bounds.minPoint.z,bounds.maxPoint.z)])
                    if boundary>=2:edges.add(edge)
                if not edges.count:continue
                try:
                    fi=assembly.features.filletFeatures.createInput()
                    radius=.015 if 'Pin' in name and 'PinnedMountFork' not in name or 'RetainingCap' in name else .03
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(edges,adsk.core.ValueInput.createByReal(radius),False)
                    ff=assembly.features.filletFeatures.add(fi);design.timeline.moveToEnd()
                    finishing.append({'body':name,'radius_mm':radius*10,'edges_selected':edges.count,'status':'applied'})
                except Exception as ex:finishing.append({'body':name,'status':'not_applied','reason':str(ex)})
            report[variant+'_edge_finishing']=finishing
"""+s[pos:]
# Remove the now-obsolete discrete holes from prongs except the actual 65 mm tongue pivot.
s=s.replace('for height in [55,65,75]:','for height in [65]:')
s=s.replace("'Crown padding and child ear fit remain geometric assumptions; cover/foam properties unmeasured.'", "'Crown padding and child ear fit remain geometric assumptions; cover/foam properties unmeasured.',\n          'Carrier is shifted behind the cover; seat cleared to avoid duplicate solid volume. Retention/bond process remains unvalidated.',\n          'Exterior corner fillets are limited and recorded per body; imported foam wrap still needs manufacturing surface/seam definition.',\n          'Reduced FEM uses ideal rectangular slider sections and omits small corner fillets.'")
(p/'EngineeringV6.py').write_text(s,encoding='utf-8')
runner=(p/'CushionNext.py').read_text(encoding='utf-8-sig')
for old in ['AuditV5.py','EngineeringV5.py','EngineeringFinal.py']:runner=runner.replace(old,'EngineeringV6.py')
(p/'CushionNext.py').write_text(runner,encoding='utf-8')
audit=(p/'AuditV5.py').read_text(encoding='utf-8-sig').replace('V5','V6').replace('cad_v5_audit','cad_v6_audit')
(p/'AuditV6.py').write_text(audit,encoding='utf-8')
print('Prepared V6 assembly correction and finishing')
