"""Scalar membrane triangle FEM + nonlinear compression foundation + rigid obstacle.
This resolves lateral cover bridging but is not 3D fabric/foam/skin contact FEA.
Coordinates mm, nodal displacement mm, nodal forces N, pressures Pa.
"""
import csv,json,math
from pathlib import Path
import numpy as np
import screening as s
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-final-results';OUT.mkdir(exist_ok=True)

def mesh(scale=1,nt=64,nr=9):
    theta=np.arange(nt)*2*np.pi/nt;u=np.linspace(0,1,nr)
    tt,uu=np.meshgrid(theta,u,indexing='ij')
    x=(25+17.5*uu)*scale*np.cos(tt);y=(35+17.5*uu)*scale*np.sin(tt)
    xy=np.column_stack([x.ravel(),y.ravel()]);tri=[]
    for i in range(nt):
        for j in range(nr-1):
            a=i*nr+j;b=((i+1)%nt)*nr+j
            tri.extend([[a,b,a+1],[b,b+1,a+1]])
    tri=np.array(tri);points=xy[tri]
    signed=.5*((points[:,1,0]-points[:,0,0])*(points[:,2,1]-points[:,0,1])-(points[:,2,0]-points[:,0,0])*(points[:,1,1]-points[:,0,1]))
    area=abs(signed)
    Bx=np.column_stack([points[:,1,1]-points[:,2,1],points[:,2,1]-points[:,0,1],points[:,0,1]-points[:,1,1]])/(2*signed[:,None])
    By=np.column_stack([points[:,2,0]-points[:,1,0],points[:,0,0]-points[:,2,0],points[:,1,0]-points[:,0,0]])/(2*signed[:,None])
    local=area[:,None,None]*(Bx[:,:,None]*Bx[:,None,:]+By[:,:,None]*By[:,None,:])/1000
    lumped=np.zeros(len(xy));np.add.at(lumped,tri.ravel(),np.repeat(area/3,3))
    return xy,tri,lumped,local

def solve(head,arm='standard',ratio=.5,force=2,tension=1,contour=.5,nt=64,nr=9,foam_multiplier=1):
    xy,tri,area,K0=mesh(head['pad_scale'],nt,nr);x,y=xy.T;K=K0*tension
    rx,ry=(110,170) if head['name'].startswith('child') else (140,200)
    crown=contour*(x*x/(2*rx)+y*y/(2*ry))
    gap=x*x/(2*head['Rx_mm'])+y*y/(2*head['Ry_mm'])-crown
    initial_gap_min=float(gap.min())
    gap-=initial_gap_min
    aw,ah=s.ARMS[arm];scale=head['pad_scale']
    mask=(x>=-52*scale)&(x<=-9*scale)&(abs(y+16*scale)<=aw/2) if aw else np.zeros(len(x),bool)
    # Smooth rounded-arm top profile avoids the zero-radius obstacle discontinuity.
    # This is a chosen hypothetical cross-section; actual frame profiles must be scanned.
    arm_height=ah*.5*(1+np.cos(np.pi*np.clip(abs(y+16*scale)/max(aw/2,1e-9),0,1))) if aw else np.zeros(len(x))
    gap-=arm_height*mask
    zone=(x>=-45*scale)&(x<=-10*scale)&(y>=-22*scale)&(y<=-10*scale)
    material=np.where(zone,ratio,1)
    depth=20+crown # same local-depth formula used for the new CAD loft, no R5 edge drop.
    stress=s.FOAMS['medium']*foam_multiplier;knot=s.STRAIN
    slopes=np.diff(stress)/np.diff(knot)
    def foundation(d):
        strain=d/depth;inds=np.clip(np.searchsorted(knot,strain,side='right')-1,0,len(slopes)-1)
        p=np.interp(np.minimum(strain,.9),knot,stress)*material+np.maximum(0,strain-.9)*2e6*material
        dp=np.where(strain>.9,2e6,slopes[inds])*material/depth
        return p*area/1e6,dp*area/1e6
    def matvec(d):
        local_force=np.einsum('tij,tj->ti',K,d[tri]);out=np.zeros(len(d));np.add.at(out,tri.ravel(),local_force.ravel());return out
    diag=np.zeros(len(x));np.add.at(diag,tri.ravel(),np.diagonal(K,axis1=1,axis2=2).ravel())
    # Gershgorin row-sum bound plus local tangent bounds stabilizes projected descent.
    rowbound=np.zeros(len(x));np.add.at(rowbound,tri.ravel(),np.sum(abs(K),axis=2).ravel())
    def equilibrium(approach,warm=None):
        lower=np.maximum(0,approach-gap);d=lower.copy() if warm is None else np.maximum(lower,warm)
        for it in range(12000):
            f,kf=foundation(d);g=f+matvec(d)
            bound=np.max(rowbound+kf);trial=np.maximum(lower,d-g/max(bound,1e-12))
            projected=(d-trial)*bound
            d=trial
            if np.max(abs(projected))<2e-8:break
        else:raise RuntimeError('Contact equilibrium failed to converge')
        f,kf=foundation(d);g=f+matvec(d)
        active=d<=lower+1e-4
        # Zero-deflection lower bounds do not transmit head load unless obstacle touches.
        headactive=active & (approach-gap>=-2e-6)
        reaction=np.where(headactive,np.maximum(g,0),0)
        return d,reaction,float(np.max(abs(projected))),it+1
    lo=-ah-2;hi=18;warm=None;total_iters=0
    for outer in range(27):
        mid=(lo+hi)/2;d,reaction,residual,it=equilibrium(mid,warm);warm=d;total_iters+=it
        load=reaction.sum()
        if load<force:lo=mid
        else:hi=mid
    approach=(lo+hi)/2;d,reaction,residual,it=equilibrium(approach,warm)
    pressure=reaction*1e6/area;surface_gap=np.maximum(0,gap-approach+d)
    contact=reaction>1e-8
    result={'head':head['name'],'arm':arm,'zone_stiffness_ratio':ratio,'force_N':force,'cover_tension_N_m':tension,
            'contour_fraction':contour,'peak_kPa':float(pressure.max()/1000),
            'frame_peak_kPa':float(pressure[mask].max()/1000) if mask.any() else 0,
            'contact_area_fraction':float(area[contact].sum()/area.sum()),'max_gap_mm':float(surface_gap.max()),
            'max_compression_mm':float(d.max()),'force_residual_N':float(abs(reaction.sum()-force)),
            'projected_equilibrium_residual_N':residual,'nodes':len(xy),'triangles':len(tri),
            'iterations_total':total_iters+it}
    result['approach_mm']=float(approach)
    result['absolute_approach_mm']=float(approach+initial_gap_min)
    return result,(xy,tri,area,pressure,surface_gap,d)

def main():
    xy,tri,area,K=mesh()
    # Constant deflection must have zero membrane force; exact annular area limit.
    assert np.max(abs(np.einsum('tij,tj->ti',K,np.ones((len(tri),3)))))<1e-12
    assert abs(area.sum()/(math.pi*(42.5*52.5-25*35))-1)<.003
    # With T=0 and matched flat geometry, compare analytic uniform foam pressure.
    flat=dict(s.HEADS[4],Rx_mm=1e20,Ry_mm=1e20)
    r,_=solve(flat,'none',1,force=1.2e3*area.sum()/1e6,tension=0,contour=0)
    assert abs(r['peak_kPa']-1.2)<1e-5
    rows=[]
    for head in [s.HEADS[1],s.HEADS[4]]:
        for arm in ['none','standard','thick']:
            for ratio in [1,.5]:
                for T in [0,1,5,20]:
                    r,fields=solve(head,arm,ratio,tension=T);rows.append(r)
                    if arm=='standard' and ratio==.5 and T==1:
                        x,y=fields[0].T;p=fields[3];mx=p.max()
                        marks=''.join(f'<circle cx="{260+xx*3.3:.2f}" cy="{245-yy*3.3:.2f}" r="2.7" fill="rgb({int(50+205*pp/mx)},70,{int(230*(1-pp/mx))})"/>' for xx,yy,pp in zip(x,y,p))
                        svg='<svg xmlns="http://www.w3.org/2000/svg" width="520" height="520"><rect width="100%" height="100%" fill="white"/><text x="15" y="25" font-family="sans-serif">'+head['name']+' coupled membrane contact</text>'+marks+f'<text x="15" y="480" font-family="sans-serif">Peak {mx/1000:.3f} kPa; assumed material, 2 N/cup</text><text x="15" y="505" font-family="sans-serif">Scalar membrane + foam foundation; not full 3D contact</text></svg>'
                        (OUT/(head['name']+'-contact.svg')).write_text(svg)
    refinement=[]
    for nt,nr in [(48,7),(64,9),(96,13),(128,17),(192,25)]:
        r,_=solve(s.HEADS[4],nt=nt,nr=nr);refinement.append(r)
    assert max(r['force_residual_N'] for r in rows)<1e-5
    with (OUT/'contact_cases.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'case_count':len(rows),'verification':['constant membrane displacement null mode','annular mesh area','T=0 analytic foam compression','force balance and projected KKT residual'],
             'cases':rows,'mesh_refinement':refinement,'model':'scalar prestressed membrane triangle FEM on nonlinear independent compression foundation with unilateral rigid-head obstacle',
             'limitations':['Cover tension prescribed, not derived from measured fabric stretch','Rounded glasses-arm top uses a raised-cosine section, not a measured frame','No in-plane fabric motion, friction, skin deformation, lateral foam Poisson coupling, seams or edge rounding','No acoustic attenuation derived from pressure maps','Synthetic head shapes and foam curves','Contact CAD uses sharp curved rims; R2 from V2 was not applied here']}
    summary['peak_pressure_mesh_change_percent']=100*abs(refinement[-1]['peak_kPa']/refinement[-2]['peak_kPa']-1)
    summary['peak_pressure_mesh_converged_under_5_percent']=summary['peak_pressure_mesh_change_percent']<5
    (OUT/'contact_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'case_count':len(rows),'refinement':refinement},indent=2))

if __name__=='__main__':main()

