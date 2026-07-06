# 모든 사이트를 한 번에 빌드: python3 build_all.py
import os, subprocess, sys
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sites")
gen = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine", "generator.py")
for s in sorted(os.listdir(base)):
    d = os.path.join(base, s)
    if os.path.isdir(d) and os.path.exists(os.path.join(d, "config.py")):
        subprocess.run([sys.executable, gen, d], check=True)
