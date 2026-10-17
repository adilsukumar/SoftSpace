"""Planar corotational Euler-Bernoulli beam FEM, elastic assumed material.
N, mm, MPa. Geometry follows engineering-v3.json. No fabricated-material validation.
"""
import csv,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-final-results';OUT.mkdir(exist_ok=True)
CONFIG=json.loads((ROOT/'engineering-final.json').read_text())

def assemble(q, reference, lengths, initial_angles, E,A,I, tangent=True):
    n=len(reference);g=np.zeros(3*n);H=np.zeros((3*n,3*n)) if tangent else None;energy=0
    xyz=reference+q.reshape(n,3)[:,:2];rot=q.reshape(n,3)[:,2];stress=[]
    for e in range(n-1):
        Ee=E[e] if np.ndim(E) else E;Ae=A[e] if np.ndim(A) else A;Ie=I[e] if np.ndim(I) else I
        delta=xyz[e+1]-xyz[e];l=np.linalg.norm(delta);t=delta/l;normal=np.array([-t[1],t[0]])
        angle=math.atan2(delta[1],delta[0])-initial_angles[e]
        angle=math.atan2(math.sin(angle),math.cos(angle))
        phi=np.array([rot[e]-angle,rot[e+1]-angle]);L=lengths[e]
        Kb=Ee*Ie/L*np.array([[4.,2.],[2.,4.]])
        m=Kb@phi;N=Ee*Ae/L*(l-L);mSum=m.sum()
        jl=np.array([-t[0],-t[1],0,t[0],t[1],0])
        ja=np.array([-normal[0]/l,-normal[1]/l,0,normal[0]/l,normal[1]/l,0])
        B=np.vstack([-ja,-ja]);B[0,2]+=1;B[1,5]+=1
        f=N*jl+B.T@m;idx=np.arange(3*e,3*e+6);g[idx]+=f
        energy+=.5*Ee*Ae/L*(l-L)**2+.5*phi@Kb@phi
        stress.append((N/Ae,max(abs(m))/Ie))
        if tangent:
            h=(Ee*Ae/L)*np.outer(jl,jl)+B.T@Kb@B
            hl=(np.eye(2)-np.outer(t,t))/l
            x,y=delta;ha=np.array([[2*x*y,y*y-x*x],[y*y-x*x,-2*x*y]])/l**4
            for a,sign_a in [(0,-1),(3,1)]:
                for b,sign_b in [(0,-1),(3,1)]:
                    h[a:a+2,b:b+2]+=sign_a*sign_b*(N*hl-mSum*ha)
            H[np.ix_(idx,idx)]+=h
    return energy,g,H,stress

def solve(radius,width,thickness,opening,E=2000,elements=40,load_steps=8,arch_height=None,reference=None,section_thickness=None,section_width=None):
    if reference is not None:
        ref=np.asarray(reference);elements=len(ref)-1
    elif arch_height is None:
        theta=np.linspace(math.pi,0,elements+1)
        ref=np.column_stack([radius*np.cos(theta),radius*np.sin(theta)])
    else:
        circle=(radius**2+arch_height**2)/(2*arch_height)
        half_angle=math.asin(radius/circle)
        theta=np.linspace(-half_angle,half_angle,elements+1)
        ref=np.column_stack([circle*np.sin(theta),circle*np.cos(theta)-(circle-arch_height)])
    d=np.diff(ref,axis=0);lengths=np.linalg.norm(d,axis=1);angles=np.arctan2(d[:,1],d[:,0])
    thickness=np.asarray(section_thickness) if section_thickness is not None else thickness
    width=np.asarray(section_width) if section_width is not None else width
    A=width*thickness;I=width*thickness**3/12;n=elements+1
    fixed=np.array([0,1,3*(n-1),3*(n-1)+1]);free=np.setdiff1d(np.arange(3*n),fixed)
    q=np.zeros(3*n);history=[]
    for step in range(1,load_steps+1):
        delta=opening*step/load_steps;q[fixed]=[-delta/2,0,delta/2,0]
        for it in range(100):
            energy,g,H,stress=assemble(q,ref,lengths,angles,E,A,I)
            residual=np.max(np.abs(g[free]))
            if residual<2e-7:break
            move=np.linalg.solve(H[np.ix_(free,free)],-g[free])
            slope=g[free]@move
            if slope>=0:
                # Stabilize indefinite Newton directions; converge the original unmodified residual.
                hf=H[np.ix_(free,free)];shift=max(0,-float(np.linalg.eigvalsh(hf)[0]))+1e-3
                move=np.linalg.solve(hf+shift*np.eye(len(free)),-g[free]);slope=g[free]@move
            alpha=1
            for bt in range(24):
                trial=q.copy();trial[free]+=alpha*move
                te,_,_,_=assemble(trial,ref,lengths,angles,E,A,I,False)
                if te<=energy+1e-4*alpha*slope+1e-10:break
                alpha*=.5
            else:raise RuntimeError('Beam line search failed')
            q=trial
        else:raise RuntimeError('Beam equilibrium did not converge')
        history.append({'opening_mm':delta,'force_per_cup_N':float(g[3*(n-1)]),'free_residual':float(residual)})
    energy,g,_,stress=assemble(q,ref,lengths,angles,E,A,I,False)
    peak=max(abs(axial)+bending*(thickness[e] if np.ndim(thickness) else thickness)/2 for e,(axial,bending) in enumerate(stress))
    return {'force_per_cup_N':float(g[3*(n-1)]),'max_elastic_stress_MPa':float(peak),
            'max_elastic_strain':float(peak/E),'free_dof_residual_N_or_Nmm':float(np.max(np.abs(g[free]))),
            'reaction_symmetry_error_N':float(abs(g[0]+g[3*(n-1)])),
            'crown_height_mm':float((ref+q.reshape(n,3)[:,:2])[n//2,1]),
            'energy_Nmm':float(energy),'elements':elements,'history':history},ref+q.reshape(n,3)[:,:2]

def verification():
    # Analytic small-opening semicircular beam: delta = F*pi*R^3/(2EI).
    r,_=solve(100,28,3.2,.01,elements=80)
    exact=2*2000*(28*3.2**3/12)*.01/(math.pi*100**3)
    assert abs(r['force_per_cup_N']/exact-1)<.005,(r,exact)
    # Directional tangent check against central finite differences at a displaced state.
    ref=np.array([[0.,0.],[5.,1.],[10.,0.]])
    d=np.diff(ref,axis=0);L=np.linalg.norm(d,axis=1);a=np.arctan2(d[:,1],d[:,0])
    q=np.array([0,0,.01,.01,-.02,-.01,.03,.01,.02]);v=np.arange(9)/1000
    _,g,H,_=assemble(q,ref,L,a,2000,60,20)
    eps=1e-4
    gp=assemble(q+eps*v,ref,L,a,2000,60,20,False)[1]
    gm=assemble(q-eps*v,ref,L,a,2000,60,20,False)[1]
    assert np.linalg.norm((gp-gm)/(2*eps)-H@v)/np.linalg.norm(H@v)<1e-6
    return {'small_opening_analytic_force_N':exact,'computed_force_N':r['force_per_cup_N'],'tangent_check':'passed'}

def main():
    checks=verification();rows=[];refinement=[]
    for family in ['adult','child']:
        c=CONFIG[family]
        for head in c['head_breadths']:
            opening=head+2*CONFIG['band']['mount_offset_per_side']-2*c['band_radius']
            result,coords=solve(c['band_radius'],c['band_width'],c['band_thickness'],opening,arch_height=c.get('band_arch_height'))
            for E in CONFIG['band']['assumed_E_MPa']:
                r={k:v for k,v in result.items() if k!='history'}
                for key in ['force_per_cup_N','max_elastic_stress_MPa','energy_Nmm']:r[key]*=E/2000
                r.update(family=family,head_breadth_mm=head,band_opening_mm=opening,E_MPa=E)
                rows.append(r)
            if head==c['head_breadths'][1]:
                for elems in [20,40,80]:
                    rr,_=solve(c['band_radius'],c['band_width'],c['band_thickness'],opening,elements=elems,arch_height=c.get('band_arch_height'))
                    refinement.append(dict(family=family,elements=elems,force_N=rr['force_per_cup_N'],stress_MPa=rr['max_elastic_stress_MPa']))
                paths=[f'<polyline points="'+ ' '.join(f'{260+x*1.8:.2f},{280-y*1.8:.2f}' for x,y in coords)+'" fill="none" stroke="#176b66" stroke-width="5"/>']
                svg='<svg xmlns="http://www.w3.org/2000/svg" width="520" height="340"><rect width="100%" height="100%" fill="white"/><text x="15" y="25" font-family="sans-serif">'+family+' band: computed elastic deformed shape</text>'+''.join(paths)+'<text x="15" y="315" font-family="sans-serif">Assumed E=2000 MPa; planar beam model, not a fitted product</text></svg>'
                (OUT/(family+'-band.svg')).write_text(svg)
    with (OUT/'band_cases.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'model':'geometrically nonlinear planar corotational Euler-Bernoulli FEM','material':'assumed linear elastic',
             'verification':checks,'mesh_refinement':refinement,'cases':rows,
             'limitations':['No creep, fatigue, material nonlinearities, out-of-plane torsion, hinge compliance, assembly tolerance or measured validation.','Fixed equal-height pinned endpoints; measured mount geometry can change force.']}
    (OUT/'band_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
