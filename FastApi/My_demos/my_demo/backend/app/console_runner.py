import os, sys, subprocess, importlib.util
from typing import Any, Dict
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'console_py'))

def _import_module(m):
    path=os.path.join(BASE,m+'.py');
    if not os.path.exists(path): raise FileNotFoundError(m)
    spec=importlib.util.spec_from_file_location(m,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod) #type: ignore
    return mod

def run_console_task(req):
    if getattr(req,'module',None) and getattr(req,'function',None):
        mod=_import_module(req.module); fn=getattr(mod, req.function)
        params=req.params or {}
        return {'mode':'import','output': (fn(**params) if isinstance(params,dict) else fn(params))}
    if getattr(req,'script',None):
        sp=os.path.join(BASE, req.script); args=[str(a) for a in (req.args or [])]
        proc=subprocess.run([sys.executable, sp]+args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {'mode':'subprocess','returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
    raise ValueError('Provide either (module + function) or (script).')
