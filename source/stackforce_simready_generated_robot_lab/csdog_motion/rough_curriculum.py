"""Small-robot terrain generator recipe; sensor/reward/policy wiring is a separate task."""
import math

LEVELS={
 'easy':{'slope_deg':3.,'stairs_m':(.01,.02),'boxes_m':(.005,.015),'noise_m':(.002,.006)},
 'medium':{'slope_deg':5.,'stairs_m':(.02,.03),'boxes_m':(.01,.02),'noise_m':(.003,.01)},
 'advanced':{'slope_deg':8.,'stairs_m':(.03,.05),'boxes_m':(.015,.03),'noise_m':(.005,.015)},
}

def build_rough_cfg(level='easy',seed=42):
    import isaaclab.terrains as tg
    from isaaclab.terrains import TerrainGeneratorCfg
    v=LEVELS[level]
    return TerrainGeneratorCfg(seed=seed,size=(6.,6.),num_rows=4,num_cols=8,border_width=2.,
        horizontal_scale=.1,vertical_scale=.001,curriculum=True,use_cache=False,color_scheme='height',
        sub_terrains={
         'flat':tg.MeshPlaneTerrainCfg(proportion=.25),
         'slope_up':tg.HfPyramidSlopedTerrainCfg(proportion=.125,slope_range=(0.,math.tan(math.radians(v['slope_deg']))),platform_width=2.,border_width=.25),
         'slope_down':tg.HfInvertedPyramidSlopedTerrainCfg(proportion=.125,slope_range=(0.,math.tan(math.radians(v['slope_deg']))),platform_width=2.,border_width=.25),
         'stairs_up':tg.MeshPyramidStairsTerrainCfg(proportion=.125,step_height_range=v['stairs_m'],step_width=.3,platform_width=2.,border_width=.5,holes=False),
         'stairs_down':tg.MeshInvertedPyramidStairsTerrainCfg(proportion=.125,step_height_range=v['stairs_m'],step_width=.3,platform_width=2.,border_width=.5,holes=False),
         'boxes':tg.MeshRandomGridTerrainCfg(proportion=.125,grid_width=.45,grid_height_range=v['boxes_m'],platform_width=2.),
         'rough':tg.HfRandomUniformTerrainCfg(proportion=.125,noise_range=v['noise_m'],noise_step=.001,border_width=.25),
        })
