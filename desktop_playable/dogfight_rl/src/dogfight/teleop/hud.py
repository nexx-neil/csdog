"""Low-rate omni.ui status view, no gameplay state ownership."""
class TeleopHUD:
    def __init__(self):
        import omni.ui as ui
        self.window=ui.Window('DOGFIGHT V0.2 — RealDog TELEOP',width=690,height=155,position_x=20,position_y=35)
        with self.window.frame:
            with ui.VStack(spacing=3):
                self.status=ui.Label('',style={'font_size':17})
                ui.Label('W/S forward/back | A/D turn | W+A/D, S+A/D arcs | Q/E force rotation')
                ui.Label('Space STOP LOCK | C unlock | R reset | Esc exit | click viewport to control')
                ui.Label('Focus loss locks STOP. Zero command is not a physical brake.')
    def update(self,settings,robot,agent,control,laser):
        d=agent.articulation.data;c=agent.last_velocity_command
        v=d.root_lin_vel_b[0];yaw=float(d.root_ang_vel_b[0,2])
        self.status.text=(f"Map {settings['map']['name']} | {agent.agent_id} | {robot['policy_version']} | TELEOP\n"
            f"cmd vx {c.vx:+.2f} vy {c.vy:+.2f} yaw {c.yaw_rate:+.2f} | actual {float(v[0]):+.2f}, {float(v[1]):+.2f} m/s yaw {yaw:+.2f}\n"
            f"Laser {laser.object_path or 'no hit'} @ {laser.distance:.2f} m | STOP LOCK: {'ON' if control.estop else 'OFF'}")
    def close(self):self.window.destroy()
