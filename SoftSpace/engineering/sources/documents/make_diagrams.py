import sys,os
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
from PIL import Image
I=Path(__file__).parent/'images'
fig,axes=plt.subplots(1,2,figsize=(10,3.6))
for k,ax in enumerate(axes):
 ax.add_patch(Rectangle((0,0),7,.5,color='#b6bdc2'));ax.text(3.5,.2,'Side of the head',ha='center',fontsize=11)
 ax.add_patch(Rectangle((0,.55),7,1.5,color='#c4d6d3'));ax.add_patch(Rectangle((2.6,.55),1.3,1.5,color='#6d9d93' if k else '#c4d6d3'))
 ax.add_patch(Rectangle((2.9,.5),.7,.55,color='#3b4b58'));ax.text(3.25,1.25,'Glasses\narm',ha='center',fontsize=11)
 ax.plot([0,2.87,2.88,3.62,3.63,7] if k else [0,2.4,2.9,3.6,4.1,7],[.52,.52,1.08,1.08,.52,.52] if k else [.52,.52,1.07,1.07,.52,.52],color='#163f4f',lw=3)
 ax.text(3.5,2.35,'Softer local zone' if k else 'Uniform foam',ha='center',fontsize=15)
 ax.text(3.5,-.45,'Continuous cover follows the arm' if k else 'Arm can lift the cover and focus pressure',ha='center',fontsize=10)
 ax.set_xlim(-.25,7.25);ax.set_ylim(-.7,2.7);ax.axis('off')
fig.tight_layout();fig.savefig(I/'glasses_section.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(10,3.2))
for k,ax in enumerate(axes):
 ax.add_patch(Rectangle((2,0),1.1,1.7,color='#334855'));ax.add_patch(Rectangle((3.1,.15),.45,1.4,color='#8db3aa'));ax.add_patch(Rectangle((3.8,-.2),.5,2.1,color='#bbc2c6'))
 ax.text(2.5,2.2,'Music getting out' if k else 'Outside noise getting in',ha='center',fontsize=15)
 arrow=FancyArrowPatch((3.65,.9),(.1,.9),arrowstyle='->',mutation_scale=20,lw=2,color='#4b857a') if k else FancyArrowPatch((.1,.9),(3.65,.9),arrowstyle='->',mutation_scale=20,lw=2,color='#4b857a');ax.add_patch(arrow)
 ax.text(2.5,-.65,'Check playback at a fixed level' if k else 'Check isolation with and without glasses',ha='center',fontsize=11)
 ax.set_xlim(-.2,5.2);ax.set_ylim(-.9,2.7);ax.axis('off')
fig.tight_layout();fig.savefig(I/'leak_paths.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(10,3.0))
for ax,name,label in zip(axes,['V1','V2','pad'],['V1 cushion snapshot','V2 cover surface','V8 replacement pad']):
 ax.imshow(Image.open(I/(name+'.png')));ax.set_title(label,fontsize=12);ax.axis('off')
fig.tight_layout();fig.savefig(I/'pad_history.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(10,3.7))
for ax,name,label in zip(axes,['syga.jpg','sony.jpg','V8.png'],['SYGA child earmuffs [5]','Sony WH CH720N [8]','Our V8 digital concept']):
 ax.imshow(Image.open(I/name));ax.set_title(label,fontsize=12);ax.axis('off')
fig.tight_layout();fig.savefig(I/'market_pictures.png',dpi=170);plt.close(fig)
