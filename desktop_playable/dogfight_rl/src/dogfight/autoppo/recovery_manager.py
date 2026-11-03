"""Diagnostics choose bounded search directions; acceptance never changes."""
from .motion_evaluator import safe,score

class RecoveryManager:
    @staticmethod
    def diagnose(m,reference=None):
        if m is None:return 'TRAINING_STAGNATION'
        if not safe(m):return 'WRONG_DIRECTION' if m['tracking']<0 else 'NUMERICAL_INSTABILITY' if not all(__import__('math').isfinite(v) for v in m.values() if isinstance(v,(int,float))) else 'POLICY_REGRESSION'
        if reference and (score(m)<score(reference)-.25 or m['gait_fraction']+.1<reference['gait_fraction']):return 'POLICY_REGRESSION'
        if m['forward_velocity']<.04:return 'STANDING_LOCAL_OPTIMUM'
        if min(m['complete_stride_count'])==0:
            reasons=m.get('rejection_counts',{})
            if reasons.get('INSUFFICIENT_SUPPORT',0)>0:return 'INSUFFICIENT_SUPPORT'
            return 'SLIDING_REWARD_EXPLOIT' if m['support_slip']>.12 else 'NO_VALID_STRIDE'
        if m['support_slip']>.08:return 'SLIDING_REWARD_EXPLOIT'
        if m['stop_linear_speed']>.03 or m['stop_yaw_rate']>.08:return 'STOP_DRIFT'
        return 'TRAINING_STAGNATION'
    @staticmethod
    def process_failure(text):
        low=text.lower()
        if 'out of memory' in low or 'cuda_error_out_of_memory' in low:return 'GPU_OOM'
        if any(x in low for x in ['nan','nonfinite','numerical']):return 'NUMERICAL_INSTABILITY'
        if 'identity' in low or 'incompatible' in low:return 'CHECKPOINT_INCOMPATIBLE'
        if 'contact' in low and 'error' in low:return 'CONTACT_DETECTION_ERROR'
        return 'PROCESS_EXIT'
