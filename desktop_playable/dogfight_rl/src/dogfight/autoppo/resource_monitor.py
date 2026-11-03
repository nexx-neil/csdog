"""Low-frequency local resource telemetry. Never signal unrelated processes."""
import subprocess,shutil,time

def sample(path):
    data=dict(time=time.time(),disk_free_gib=shutil.disk_usage(path).free/1024**3)
    try:
        text=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True,timeout=5)
        used,total,util,temp=[float(x.strip()) for x in text.splitlines()[0].split(',')]
        data.update(gpu_memory_mib=used,gpu_total_mib=total,gpu_utilization_percent=util,gpu_temperature_c=temp)
    except (OSError,ValueError,subprocess.SubprocessError) as e:data['gpu_query_error']=str(e)
    return data

def prune_temporary(base):
    # Only aged, uncommitted scratch files in the NEW lab tree, never historical
    # runs or any committed checkpoint. All bank members and failures are retained.
    root=base.resolve();removed=[]
    for p in (root/'trials').glob('*/attempt_*/.*.tmp'):
        if p.is_file() and time.time()-p.stat().st_mtime>172800:
            p.unlink();removed.append(str(p))
    return removed
