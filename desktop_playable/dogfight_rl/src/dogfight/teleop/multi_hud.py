"""Read-only three-dog teleop match status."""
class ThreeDogHUD:
    def __init__(self,battle_config,autonomous=False):
        import omni.ui as ui
        self.window=ui.Window('DOGFIGHT — 3 Real Dogs',width=760,height=225 if autonomous else 170,position_x=20,position_y=35)
        with self.window.frame:
            with ui.VStack(spacing=2):
                self.status=ui.Label('',style={'font_size':17})
                self.dogs=ui.Label('',style={'font_size':16})
                ui.Label('A/B/C: autonomous FSM + A* + PPO | V routes ON/OFF' if autonomous else 'A red: WASD/QE | B blue: keypad 8/2 forward/back, 4/6 turn, 7/9 & 1/3 arcs, 5 stop')
                ui.Label('Space pause+STOP | C resume | R reset all | Esc exit')
                self.navigation=ui.Label('',style={'font_size':14}) if autonomous else None
                ui.Label(f"Continuous lasers: {battle_config['damage']:g} damage per hit / {battle_config['cooldown_s']:g} s; walls block rays.")
    def update(self,state,agents,controls):
        result=('WINNER '+state['winner'].upper() if state['winner'] else 'DRAW') if state['round_over'] else 'PAUSED — press C' if state['paused'] else 'BATTLE ACTIVE'
        self.status.text=f"THREE REAL DOGS | {result} | {state['time_s']:.1f} s"
        self.dogs.text='\n'.join(f"{name.upper()} HP {state['agents'][name]['health']:.0f}/{state['max_health']:.0f} {'ALIVE' if agent.is_alive() else 'DEAD'} | vx {agent.last_velocity_command.vx:+.2f} yaw {agent.last_velocity_command.yaw_rate:+.2f}" for name,agent in agents.items())
        if self.navigation:
            self.navigation.text='\n'.join(f"{n}: {s['state']} -> {s['target_id'] or '-'} | goal {tuple(round(v,1) for v in s['navigation_goal']) if s['navigation_goal'] else '-'} | {s['distance_m']:.1f}m | visible {s['visible']} | {s['planning']}" if s['distance_m'] is not None else f"{n}: {s['state']} | {s['planning']}" for n,s in state.get('navigation',{}).items())
    def close(self):self.window.destroy()
