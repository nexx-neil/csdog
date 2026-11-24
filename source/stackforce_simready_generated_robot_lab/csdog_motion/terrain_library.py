"""Independent terrain catalog; recipes are proposed challenges, not robot capabilities."""
import math
import numpy as np

WALKING_KINDS=('flat','pyramid_slope','inverted_slope','pyramid_stairs','inverted_stairs',
               'blocks','waves','rails','scattered_obstacles','rough','compound','double_box')
SKILL_KINDS=('stepping_stones','gap','pit','crawl_ring')
LEVELS={
 'bridge':dict(slope_deg=5.,stairs_m=(.02,.03),blocks_m=(.01,.025),noise_m=(.002,.008),wave_m=(.005,.015),gap_m=(.05,.10)),
 'mixed':dict(slope_deg=8.,stairs_m=(.03,.05),blocks_m=(.02,.04),noise_m=(.004,.012),wave_m=(.01,.025),gap_m=(.10,.18)),
 'hard':dict(slope_deg=12.,stairs_m=(.05,.08),blocks_m=(.03,.06),noise_m=(.006,.02),wave_m=(.02,.04),gap_m=(.18,.28)),
}

def compound_height(x,y,difficulty,recipe):
    """Flat spawn, continuous ramp, two steps, then checkered rubble; no holes."""
    if not 0<=difficulty<=1:raise ValueError('difficulty must be in[0,1]')
    x,y=np.broadcast_arrays(np.asarray(x),np.asarray(y));radius=np.maximum(abs(x),abs(y))
    step=recipe['stairs_m'][0]+difficulty*(recipe['stairs_m'][1]-recipe['stairs_m'][0])
    rise=np.clip(radius-.85,0,.40)*math.tan(math.radians(recipe['slope_deg']*(.5+.5*difficulty)))
    steps=step*((radius>=1.25).astype(float)+(radius>=1.50).astype(float))
    checker=(np.floor((x+3)/.25)+np.floor((y+3)/.25))%2
    rubble=(radius>=1.85)*checker*(recipe['blocks_m'][0]+difficulty*(recipe['blocks_m'][1]-recipe['blocks_m'][0]))
    return rise+steps+rubble

def compound_mesh(difficulty,cfg):
    import trimesh
    nx,ny=[round(v/.05)+1 for v in cfg.size]
    x,y=np.meshgrid(np.linspace(0,cfg.size[0],nx),np.linspace(0,cfg.size[1],ny),indexing='ij')
    z=compound_height(x-cfg.size[0]/2,y-cfg.size[1]/2,difficulty,LEVELS[cfg.library_level])
    v=np.stack((x,y,z),-1).reshape(-1,3);i,j=np.meshgrid(np.arange(nx-1),np.arange(ny-1),indexing='ij');a=(i*ny+j).ravel()
    faces=np.concatenate((np.stack((a,a+ny,a+1),1),np.stack((a+1,a+ny,a+ny+1),1)))
    return [trimesh.Trimesh(vertices=v,faces=faces,process=False)],np.array([cfg.size[0]/2,cfg.size[1]/2,0.])

def build_library_cfg(level='bridge',group='walking',seed=12011):
    if level not in LEVELS or group not in ('walking','skills'):raise ValueError('Unknown library level/group')
    import isaaclab.terrains as tg
    from isaaclab.utils import configclass
    v=LEVELS[level];flat=1.8
    if group=='walking':
        @configclass
        class CompoundCfg(tg.SubTerrainBaseCfg):
            function=compound_mesh
            library_level:str=level
        terrains={
          'flat':tg.MeshPlaneTerrainCfg(),
          'pyramid_slope':tg.HfPyramidSlopedTerrainCfg(slope_range=(math.tan(math.radians(v['slope_deg']/2)),math.tan(math.radians(v['slope_deg']))),platform_width=flat,border_width=.25),
          'inverted_slope':tg.HfInvertedPyramidSlopedTerrainCfg(slope_range=(math.tan(math.radians(v['slope_deg']/2)),math.tan(math.radians(v['slope_deg']))),platform_width=flat,border_width=.25),
          'pyramid_stairs':tg.MeshPyramidStairsTerrainCfg(step_height_range=v['stairs_m'],step_width=.30,platform_width=flat,border_width=.5),
          'inverted_stairs':tg.MeshInvertedPyramidStairsTerrainCfg(step_height_range=v['stairs_m'],step_width=.30,platform_width=flat,border_width=.5),
          'blocks':tg.MeshRandomGridTerrainCfg(grid_width=.28,grid_height_range=v['blocks_m'],platform_width=flat),
          'waves':tg.HfWaveTerrainCfg(amplitude_range=v['wave_m'],num_waves=4,border_width=.25),
          'rails':tg.MeshRailsTerrainCfg(rail_height_range=v['blocks_m'],rail_thickness_range=(.08,.12),platform_width=flat),
          'scattered_obstacles':tg.HfDiscreteObstaclesTerrainCfg(obstacle_width_range=(.20,.50),obstacle_height_range=v['blocks_m'],num_obstacles=36,platform_width=flat,border_width=.25),
          'rough':tg.HfRandomUniformTerrainCfg(noise_range=v['noise_m'],noise_step=.001,border_width=.25),
          'compound':CompoundCfg(),
          'double_box':tg.MeshBoxTerrainCfg(box_height_range=v['stairs_m'],platform_width=flat,double_box=True),
        }
        assert tuple(terrains)==WALKING_KINDS
    else:
        terrains={
          'stepping_stones':tg.HfSteppingStonesTerrainCfg(stone_height_max=v['blocks_m'][1],stone_width_range=(.30,.45),stone_distance_range=v['gap_m'],holes_depth=-.25,platform_width=flat,border_width=.25),
          'gap':tg.MeshGapTerrainCfg(gap_width_range=v['gap_m'],platform_width=flat),
          'pit':tg.MeshPitTerrainCfg(pit_depth_range=v['stairs_m'],platform_width=flat,double_pit=True),
          'crawl_ring':tg.MeshFloatingRingTerrainCfg(ring_width_range=(.25,.45),ring_height_range=(.32,.40),ring_thickness=.06,platform_width=flat),
        }
        assert tuple(terrains)==SKILL_KINDS
    for cfg in terrains.values():cfg.proportion=1/len(terrains)
    return tg.TerrainGeneratorCfg(seed=seed,size=(6.,6.),num_rows=3,num_cols=len(terrains),border_width=2.,horizontal_scale=.05,vertical_scale=.001,curriculum=True,use_cache=False,color_scheme='height',sub_terrains=terrains)

def scenario(level,group,seed,row):
    if level not in LEVELS or group not in ('walking','skills') or row not in range(3):raise ValueError('Unknown scenario')
    return {'schema_version':1,'name':'csdog_terrain_library_v1','level':level,'group':group,'seed':seed,'row':row,
            'recipe':LEVELS[level],'kinds':list(WALKING_KINDS if group=='walking' else SKILL_KINDS),
            'scope':'external scenario override; fixed v33 actor/controller diagnostic; no model compatibility/promotion claim',
            'skill_group_robot_execution_enabled':False,'policy_trained_for_library':False}
