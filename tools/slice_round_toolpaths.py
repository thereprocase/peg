#!/usr/bin/env python3
"""Slice a round-anchor review using recorded JSON inputs; never send to printer."""
import argparse,json,os
from pathlib import Path
import subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',type=Path,required=True)
p.add_argument('--definitions',type=Path,required=True)
p.add_argument('--settings',type=Path,required=True)
p.add_argument('--mesh',type=Path,required=True)
p.add_argument('--output',type=Path,required=True,help='Scratch REVIEW_ONLY.gcode file')
a=p.parse_args();settings=json.loads(a.settings.read_text())
a.output.parent.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env['CURA_ENGINE_SEARCH_PATH']=str(a.definitions.resolve())
command=[str(a.engine.resolve()),'slice','-m2','-j',str(a.definitions/'fdmprinter.def.json')]
for key,value in settings.items():
 value=str(value).lower() if isinstance(value,bool) else str(value)
 command+=['-s',f'{key}={value}']
command+=['-e0','-j',str(a.definitions/'fdmextruder.def.json'),'-s','machine_nozzle_size=0.4','-s','material_diameter=1.75','-l',str(a.mesh),'-o',str(a.output)]
a.output.with_suffix('.command.json').write_text(json.dumps(command,indent=2))
run=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
a.output.with_suffix('.log').write_text(run.stdout);run.check_returncode();print(a.output)
