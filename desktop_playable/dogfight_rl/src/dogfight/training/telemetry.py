"""GPU-memory telemetry extracted from the historical PPO entrypoint."""
import subprocess

class GpuSampler:
    def __init__(self):
        self.samples_mib: list[int] = []

    def sample(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                check=True, capture_output=True, text=True,
            )
            self.samples_mib.append(int(result.stdout.splitlines()[0].strip()))
        except Exception:
            pass

    def start(self):
        self.sample()

    def close(self):
        self.sample()

