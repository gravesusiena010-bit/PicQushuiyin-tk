# 🎨 高级图片去水印工具

一个功能强大、界面友好的图片去水印工具，支持多种算法、批量处理和实时预览。

## ✨ 主要特性

- 🖼️ **现代化GUI界面** - 基于tkinter设计的直观用户界面
- 🚀 **多种去水印算法** - 支持TELEA和Navier-Stokes算法
- 📁 **批量处理** - 支持文件夹批量处理，提高工作效率
- 🎯 **拖拽支持** - 直接拖拽文件或文件夹到界面
- 👀 **实时预览** - 处理前后对比预览，效果一目了然
- ⚙️ **参数调节** - 可调节修复半径、输出质量等参数
- 📊 **进度显示** - 实时显示处理进度和状态
- 📝 **详细日志** - 完整的操作日志记录

## 🛠️ 安装要求

### 系统要求
- Windows 10/11
- Python 3.8+

### 依赖库安装

```bash
# 克隆或下载项目到本地
cd 02-PicQushuiyin-tk

# 安装依赖包
pip install -r requirements.txt
```

### 主要依赖
- `opencv-python` - 图像处理核心库
- `numpy` - 数值计算库
- `Pillow` - Python图像库
- `tkinterdnd2` - 拖拽功能支持

## 🚀 快速开始

### 启动GUI界面

```bash
python watermark_remover_gui.py
```

### 命令行版本（原版）

```bash
# 处理单张图片
python advanced_watermark_remover.py photo.jpg

# 使用NS算法
python advanced_watermark_remover.py -a ns photo.jpg

# 批量处理
python advanced_watermark_remover.py -b ./images/
```

## 📖 使用指南

### GUI界面操作

1. **选择文件**
   - 点击"选择单个文件"处理单张图片
   - 点击"选择文件夹(批量)"批量处理
   - 直接拖拽文件到窗口

2. **算法设置**
   - **TELEA算法**: 快速处理，适合简单水印
   - **Navier-Stokes算法**: 精细处理，适合复杂纹理
   - **修复半径**: 1-10，控制修复区域大小
   - **输出质量**: 50-100，控制保存质量

3. **开始处理**
   - 点击"🚀 开始处理"按钮
   - 查看进度条和状态提示
   - 在预览面板查看结果

4. **预览功能**
   - **原图标签页**: 显示原始图片
   - **处理结果标签页**: 显示去水印效果
   - **对比视图标签页**: 并排对比

### 命令行操作

```bash
# 基本用法
python advanced_watermark_remover.py [选项] <图片路径>

# 选项说明
-a, --algorithm    选择算法 (telea/ns)
-r, --radius       修复半径 (1-10)
-b, --batch        批量处理模式
-h, --help         显示帮助
```

### 交互式操作（命令行版）

- **鼠标左键**: 选择水印区域
- **ESC**: 确认选择并开始处理
- **R**: 重新选择区域
- **B**: 切换到画笔模式
- **T**: 切换到矩形选择模式
- **+/-**: 调整画笔大小
- **Q**: 退出程序

## 📁 项目结构

```
02-PicQushuiyin-tk/
├── advanced_watermark_remover.py    # 命令行版本主程序
├── watermark_remover_gui.py         # GUI版本主程序
├── requirements.txt                 # 依赖包列表
├── README.md                       # 项目说明文档
├── config.ini                      # 配置文件
├── logs/                          # 日志文件目录
│   └── watermark_removal_*.log    # 操作日志
├── demo.jpeg                      # 示例图片
└── demo_image.jpg                 # 示例图片
```

## 🎯 支持的文件格式

- **输入格式**: JPG, JPEG, PNG, BMP, TIFF, TIF
- **输出格式**: 与输入格式相同
- **输出命名**: 原文件名 + `_no_watermark` + 原扩展名

## ⚙️ 算法说明

### TELEA算法
- **特点**: 快速行进方法
- **适用**: 简单水印、文字水印
- **优势**: 处理速度快
- **推荐**: 日常使用首选

### Navier-Stokes算法
- **特点**: 基于流体动力学
- **适用**: 复杂纹理、图案水印
- **优势**: 修复效果精细
- **推荐**: 高质量要求场景

## 📊 性能优化

- **多线程处理**: GUI版本使用后台线程，避免界面卡顿
- **内存管理**: 自动释放图像内存，支持大文件处理
- **批量优化**: 智能批量处理，提高效率
- **预览缓存**: 智能预览缩放，减少内存占用

## 🔧 配置选项

可以通过修改 `config.ini` 文件自定义默认设置：

```ini
[DEFAULT]
algorithm = telea
radius = 3
quality = 95
log_level = INFO
```

## 📝 日志系统

- **日志位置**: `logs/` 目录
- **命名格式**: `watermark_removal_YYYYMMDD_HHMMSS.log`
- **记录内容**: 操作时间、处理文件、算法参数、错误信息
- **日志级别**: INFO, WARNING, ERROR

## 🐛 常见问题

### Q: 程序启动失败
A: 检查Python版本和依赖包是否正确安装

### Q: 拖拽功能不工作
A: 确保安装了 `tkinterdnd2` 库

### Q: 处理大图片很慢
A: 尝试降低修复半径或使用TELEA算法

### Q: 水印去除效果不理想
A: 尝试不同算法或调整修复半径参数

### Q: 批量处理中断
A: 检查文件权限和磁盘空间

## 🔄 更新日志

### v2.0 (2025-06-26)
- ✨ 新增现代化GUI界面
- 🚀 支持拖拽文件操作
- 👀 添加实时预览功能
- 📊 增加进度显示
- 🎯 优化用户体验

### v1.0 (2024-12-19)
- 🎉 初始版本发布
- 🖼️ 支持多种去水印算法
- 📁 支持批量处理
- 📝 完整日志系统

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**李祥光** - *项目创建者和主要开发者*

- 📧 Email: 274030396@qq.com
- 🐙 GitHub: [lixiangguang]

## 🙏 致谢

- OpenCV 团队提供的强大图像处理库
- Python 社区的优秀开源项目
- 所有测试用户的宝贵反馈

---

⭐ 如果这个项目对你有帮助，请给它一个星标！