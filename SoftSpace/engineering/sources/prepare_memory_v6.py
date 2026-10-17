from pathlib import Path
p=Path(__file__).parent
f=p/'CushionNext'/'EngineeringV6.py'
s=f.read_text()
cleanup='''        # Archive only task-generated documents before closing them to release RAM.
        report['closed_backups']=[]
        for olddoc in [app.documents.item(j) for j in range(app.documents.count)]:
            if not olddoc.name.startswith(('EarDefender_V4_','EarDefender_V5_','EarDefender_V6_')):continue
            olddoc.activate()
            olddesign=adsk.fusion.Design.cast(app.activeProduct)
            backup=os.path.join(out,'Recovery_'+olddoc.name.replace('*','')+'_'+stamp+'.f3d')
            if olddesign and olddesign.exportManager.execute(olddesign.exportManager.createFusionArchiveExportOptions(backup)) and os.path.getsize(backup)>0:
                report['closed_backups'].append(backup);save_report();olddoc.close(False)
            else:raise RuntimeError('Could not archive generated document before close')
        audit={'status':'started','sizes':[],'limitations':['Assumed material density ranges','Unloaded geometry; not worn fit','No physical comfort validation']}
'''
s=s.replace('        for recipe in json.load',cleanup+'        for recipe in json.load',1)
audit=(p/'CushionNext'/'AuditV6.py').read_text()
start=audit.index('            comp=comps[0];')
end=audit.index("            json.dump(report,",start)
body=audit[start:end].replace("report['sizes']","audit['sizes']").replace('            comp=comps[0];','            comp=assembly;')
s=s.replace('            app.activeViewport.fit();save_report()',body+'''            json.dump(audit,open(os.path.join(out,'cad_v6_audit.json'),'w'),indent=2)
            app.activeViewport.fit();save_report()
            if recipe['name']!='adult_large':doc.close(False)
''')
s=s.replace("        report['status']='complete';report['recipes']", "        audit['status']='complete';json.dump(audit,open(os.path.join(out,'cad_v6_audit.json'),'w'),indent=2)\n        report['status']='complete';report['recipes']",1)
f.write_text(s)
compile(s,str(f),'exec')
print('Memory-safe V6 builder with per-size audit ready')
