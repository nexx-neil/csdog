from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';O=E/'reports'
rows=[
('base_linear_velocity_reward','原函数','5,std1,ramp1/.5','5,std .25，低速下ramp不触发','机身系线速度，绝对误差exp'),
('base_angular_velocity_reward','原函数','5,std2','5,std .5','世界Z/机身yaw定义按官方；目标机身wz'),
('GaitReward','继承官方六个核','10,std .1,max .2,threshold .5','2,std .1,max .2,threshold .1','真实末端manifold时钟50Hz；仅合适平移，纯yaw/低侧移/静止关闭；近地无力<5mm状态否决'),
('air_time_reward','适配','5,mode .3,threshold .5','5,mode .25,threshold .1','恢复dense mode-time核；真实接触/几何联合；零指令仅鼓励支撑，不因漂移自动鼓励摆腿'),
('foot_clearance_reward','适配','weight .5,target .1,std .05,tanh2','weight .5,target .03,std .0045,tanh2','恢复官方exp总误差核，位置换整根小腿凸包最低表面，速度用帽区点真实世界速度'),
('foot_slip_penalty','适配','-.5,threshold1','-.5,threshold1','接触斑速度v_COM+omega×r，足底保守分类，膝/胫触地否决'),
('action_smoothness_penalty','原函数','-1','首轮-1；唯一优化轮-.2','raw动作L2差；Gaussian无wrapper clip，第二轮仅权重变更'),
('air_time_variance_penalty','适配','-1,clamp .5','-1,clamp .5','相同两个var之和，只替换last_air/contact时钟'),
('base_motion_penalty','原函数','-2','-2','0.8*vz²+0.2*sum|wxy|'),
('base_orientation_penalty','原函数','-3','-3','投影重力xy范数'),
('joint_position_penalty','原函数/参数缩放','-.7,stand scale5,threshold .5','-.7,stand scale5,threshold .1','保留默认几何站姿；不启用失败的servo_bias'),
('joint_velocity_penalty','原函数','-.01','-.01','源码虽然传髋关节asset_cfg，函数实际对全joint_vel求norm；V3保留实际行为'),
('joint_acceleration_penalty','原函数','-1e-4','-1e-4','同样源码不实际使用asset_cfg.body_ids/joint_ids，因此全12关节'),
('joint_torques_penalty','原函数','-5e-4','-5e-4','显式PD施加的真实指令转矩；common比较下旧策略也使用同驱动'),
]
text='# SPOT_REWARD_ALIGNMENT\n\n所有官方值来自本机固定源码与official_source_audit.json。不是ANYmal基础奖励叠加；V3直接实例化SpotRewardsCfg并逐项替换脚部适配。未列出的旧ANYmal奖励全部不进入V3。14项均启用，没有以占位项伪装已实现。\n\n|奖励|使用类型|官方值|V3实际值|理由/限制|\n|---|---|---|---|---|\n'
for row in rows:text+='|'+'|'.join(row)+'|\n'
text+='\n接触沿用V2保守末端分类，并非独立foot刚体。足部时间分辨率20ms；500Hz物理不会自动把这个Python适配时钟变成500Hz。任何近地抖动的一致率、自相关均只作代理；必须结合>15mm整膝离地、周期与视频。Gait训练几何可信门限5mm与严格评估摆动15mm分开说明，不能把前者当作达成正常步态。\n\n奖励量级（末10次rollout加权奖励率；权重变化后Reward不可直接当性能优劣）：\n\n|项|首轮|优化轮|\n|---|---:|---:|\n'
for term in ['air_time','base_angular_velocity','base_linear_velocity','foot_clearance','gait','action_smoothness','air_time_variance','base_motion','base_orientation','foot_slip','joint_acc','joint_pos','joint_torques','joint_vel']:
 vals=[]
 for stage in ['first','second']:
  p=E/stage/'metrics.jsonl'
  if p.exists():
   data=[json.loads(x) for x in p.read_text().splitlines()][-10:];vals.append(f"{np.mean([r['contribution_'+term] for r in data]):.6f}")
  else:vals.append('未运行')
 text+='|'+term+'|'+'|'.join(vals)+'|\n'
(O/'SPOT_REWARD_ALIGNMENT.md').write_text(text)
