# Third-Party Notices — Dogfight V0

Dogfight V0 was implemented locally. No upstream source file or substantial
code block was copied into this project. The following repositories were read
for architectural ideas only on 2026-09-18:

## MARLadona Isaac Lab

- Repository: https://github.com/leggedrobotics/marladona-isaac-lab
- Reviewed commit: `8a24b2355518de0f39a1825d0961c3285a4c5a17`
- License: Apache License 2.0
- Ideas reviewed: external-extension layout, configurable agent collections,
  multi-agent state/reset organization.

## Isaac Fighter

- Repository: https://github.com/Numi2/isaac-fighter
- Reviewed commit: `0f63107add794b331996a111df519a201a91e245`
- License: BSD 3-Clause
- Ideas reviewed: combat rule isolation, terminal outcome state, replay and
  future policy-pool separation. No self-play code was imported.

## Arena-Rosnav

- Repository: https://github.com/Arena-Rosnav/arena-rosnav
- Reviewed commit: `5de9d380d94e01963dc48f7a3f62c1b99c9c9556`
- License: MIT
- Ideas reviewed: map/world, spawn, goal, robot, and planner separation. No ROS
  or Gazebo code/dependency was imported.

Isaac Lab/Isaac Sim APIs are consumed from the user's pre-existing frozen
environment; their source trees were not modified.

