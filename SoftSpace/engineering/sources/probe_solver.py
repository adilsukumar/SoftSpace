import sys,ctypes
class MemoryStatus(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(name,ctypes.c_ulonglong) for name in ['total','available','total_page','available_page','total_virtual','available_virtual','available_extended']]
m=MemoryStatus();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
print('Physical RAM available GiB',round(m.available/2**30,2),'load',m.load,flush=True)
sys.path.insert(0,'solver-libraries')
import gmsh,scipy,numpy
gmsh.initialize();print('gmsh',gmsh.__version__,'scipy',scipy.__version__,'numpy',numpy.__version__);gmsh.finalize()
