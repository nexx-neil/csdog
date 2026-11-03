# Python / Isaac 扩展包

统一 Python 源码为 `src/dogfight` 和 `src/dogfight_v0`，包发现使用 setuptools 的 src 布局；pytest 同样只使用 src。环境未做 editable 重新安装，正式入口通过 PYTHONPATH 导入唯一源码。

Isaac 扩展元数据：`configs/battle/extension.toml`，`python.module` 的 `path = "../../src"`。扩展加载与 GUI 视觉需在 Isaac Kit 中单独验收；headless 脚本可独立验证包、场景和射线。
