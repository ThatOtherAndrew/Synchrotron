import subprocess
import time

subprocess.Popen([r'C:\Program Files\SuperCollider-3.13.0\scsynth.exe', '-t', '57120', '-l', '2'])  # noqa: S603
time.sleep(10)
print('\nRunning sclang...\n')
subprocess.run([r'C:\Program Files\SuperCollider-3.13.0\sclang.exe', './startup.scd'], check=True)  # noqa: S603
