"""Build an educational ELF without printing its source; create new directory only."""
from pathlib import Path
import argparse
import subprocess
import tempfile
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("output", type=Path)
args = parser.parse_args()
if args.output.exists():
    parser.error("output already exists; choose a new directory")
compiler, strip = shutil.which("gcc"), shutil.which("strip")
if not compiler or not strip:
    parser.error("gcc and strip are required (Ubuntu/WSL)")
source = Path(__file__).with_name("blind_reference.c")
with tempfile.TemporaryDirectory(prefix="bifrost-blind-") as tmp:
    binary = Path(tmp) / "mystery"
    subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O0", "-fno-inline", str(source), "-o", str(binary)], check=True)
    subprocess.run([strip, "--strip-all", str(binary)], check=True)
    args.output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(binary, args.output / "mystery")
    (args.output / "mystery").chmod(0o755)
print("Built mystery. Analyse it before opening blind_reference.c.")
