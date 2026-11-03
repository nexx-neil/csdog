"""All previous skills remain required; repeated evidence, not update counts."""
from .motion_evaluator import qualified

class CurriculumManager:
    def __init__(self,store,thresholds):self.store=store;self.thresholds=thresholds
    def observe(self,panel,checkpoint):
        stage=self.store.get('stage',0)
        if not panel.get('full'):return False
        # No seed reuse can count twice toward qualification.
        key=f'qualification_{stage}';history=self.store.get(key,[])
        signature=(str(checkpoint),tuple(panel['seeds']))
        if any((x['checkpoint'],tuple(x['seeds']))==signature for x in history):return False
        passed=qualified(panel,stage,self.thresholds)
        history=history+[dict(checkpoint=str(checkpoint),seeds=panel['seeds'],passed=passed)] if passed else []
        self.store.set(key,history)
        recent=history[-3:]
        independent=any(set(x['seeds'])&{2027,4099} for x in recent)
        if len(recent)>=3 and independent:
            if stage<3:self.store.set('stage',stage+1)
            else:self.store.set('status','SUCCESS')
            self.store.event('CURRICULUM_QUALIFIED',stage=stage,checkpoint=str(checkpoint),evidence=recent)
            return True
        return False
