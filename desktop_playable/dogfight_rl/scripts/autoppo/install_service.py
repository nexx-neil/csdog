"""Install the current user's validated, reboot-persistent local training service."""
from pathlib import Path
import sys,subprocess
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import BASE
from dogfight.autoppo.experiment_manager import validate_gate

def main():
    validate_gate(BASE)
    source=ROOT/'configs/autoppo/csdog-autoppo-lab.service'
    dest=Path.home()/'.config/systemd/user/csdog-autoppo-lab.service'
    if dest.exists() and '# Managed by CSDog AutoPPO Lab' not in dest.read_text():raise RuntimeError('Refusing to replace an unrelated service')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(source.read_text())
    subprocess.run(['systemctl','--user','daemon-reload'],check=True)
    subprocess.run(['systemctl','--user','enable','csdog-autoppo-lab.service'],check=True)
    linger=subprocess.check_output(['loginctl','show-user',__import__('getpass').getuser(),'-p','Linger'],text=True).strip()
    if linger!='Linger=yes':raise RuntimeError('Service installed, but reboot without login requires user lingering')
    print(str(dest));print(linger)
if __name__=='__main__':main()
