import sys,runpy,os
sys.path.insert(0,'${WORKSPACE}\\solver-libraries')
sys.path.insert(0,'${WORKSPACE}')
os.environ['OPENBLAS_NUM_THREADS']='1'
runpy.run_path('${WORKSPACE}\\verify_v19_quadratic.py',run_name='__main__')
