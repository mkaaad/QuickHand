#  ![icon](assets/icon.ico) Quick Hand

## 📝 介绍

快速仿手写文字的图片生成器。基于 [Handright](https://github.com/Gsllchb/Handright/) 的 GUI。

开源免费，下载请到 [Release](https://github.com/mkaaad/QuickHand/releases) 界面。

界面预览：

![界面预览](assets/screenshot.png)

## 🔮 使用说明

原理：在水平位置、竖直位置和字体大小三个自由度上，对每个字的整体做随机扰动。随后在水平位置、竖直位置和旋转角度三个自由度上，对每个字的每个笔画做随机扰动。

Windows 用户：下载压缩包，解压，双击运行 `QuickHand.exe` 即可。

- 将字体文件（ttf/otf）放到软件根目录的 `fonts` 文件夹
- 将背景图片放到软件根目录的 `backgrounds` 文件夹

排版关系参考：

![排版参数](assets/params-reference.png)

## 🔨 自行构建

|架构 | Runner | 产物 |
|------|--------|------|
| Windows x86_64 | `windows-latest` | `.rar` |
| Linux x86_64 | `ubuntu-latest` | `.tar.gz` |
| macOS x86_64 | `macos-13` | `.tar.gz` |
| macOS arm64 | `macos-latest` | `.tar.gz` |

推送标签 `v*` 即触发构建，打包完成后自动发布到 Release。

如需本地构建：

```bash
pip install -r requirements.txt pyinstaller
cd src
pyinstaller --noconfirm -w \
  --hidden-import pkg_resources.py2_warn \
  -i icon.ico \
  --add-data "database.db;." \
  --add-data "style.css;." \
  --add-data "icon.ico;." \
  --add-data "fonts;fonts" \
  --add-data "backgrounds;backgrounds" \
  QuickHand.py
```

> Windows 上将 `--add-data` 的分隔符 `:` 换为 `;`。

构建后将 `fonts`、`backgrounds`、`database.db`、`style.css` 等资源复制到输出目录即可运行。

## 😀 交流

反馈请提交 [Issues](https://github.com/mkaaad/QuickHand/issues)。
