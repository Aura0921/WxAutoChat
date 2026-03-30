---

## 💻 核心技术栈

- **编程语言**: Python 3.11+
- **AI 框架**: DeepSeek LLM, Moonshot AI
- **微信自动化**: wxauto
- **Web 框架**: Flask
- **数据库**: SQLite (SQLAlchemy ORM)
- **前端**: Bootstrap 5, JavaScript
- **日志**: Colorama, Logging
- **系统监控**: psutil

---

## 🎭 可用角色

项目预置了多个角色人设：

1. **ATRI（亚托莉）**
   - 来自《ATRI -My Dear Moments-》的女主角
   - 拥有丰富的情感表达和专属表情包
   
2. **MONO**
   - 可爱活泼的角色设定
   - 独特的对话风格
   
3. **NomalAI**
   - 通用 AI 助手设定
   - 适合日常对话

可通过 WebUI 配置界面自由切换角色。

---

## 📸 功能展示

### 1. 情感表情包系统
- 根据对话内容自动识别情感（开心、生气、悲伤、平静）
- 从预设表情包中选择最匹配的动图发送
- 支持自定义表情包扩展

### 2. 图片识别
- 发送图片给 AI 进行识别
- AI 会描述图片内容并给出回应
- 支持表情包识别

### 3. 图像生成
- 根据文字描述生成对应图片
- 使用 Janus-Pro-7B 模型
- 支持多种画风

### 4. 记忆系统
- 自动记录重要对话内容
- 定期整理和总结记忆
- 保持对话连贯性和一致性

---

## 🔧 常见问题

### Q1: 微信初始化失败怎么办？
A: 请确保：
- 微信已在 PC 端登录
- 有一个移动设备同时登录微信
- 微信窗口处于激活状态
- 重启程序重试

### Q2: 如何修改监听的用户？
A: 两种方式：
- 通过 WebUI 配置界面修改监听列表
- 直接编辑 `src/config/config.json` 文件

### Q3: 表情包如何自定义？
A: 在 `data/avatars/{角色}/emojis/` 目录下：
- `happy/`: 开心类表情
- `angry/`: 生气类表情
- `sad/`: 悲伤类表情
- `neutral/`: 平静类表情
将 GIF 动图放入对应文件夹即可

### Q4: API Key 在哪里获取？
A: 
- DeepSeek: [硅基流动](https://cloud.siliconflow.cn/i/aQXU6eC5)
- Moonshot: [月之暗面](https://platform.moonshot.cn/)

---

## 🌐 社区互动

- **QQ 交流群**：[715616260](https://jq.qq.com/?_wv=1027&k=5z4Q0i7o)
- **哔哩哔哩**：[视频频道](https://space.bilibili.com/209397245)
- **联系邮箱**：[yangchenglin2004@foxmail.com](mailto:yangchenglin2004@foxmail.com)

---

## 💖 支持与鸣谢

感谢所有为项目做出贡献的开发者！

特别感谢：
- 原项目作者：[iwyxdxl](https://github.com/iwyxdxl)
- 所有提供反馈和建议的社区成员

---

<div align="center">
  <sub>🛠️ 核心技术栈</sub>
  <br>
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/Python-3.11_➔_3.12-0073B7?logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://github.com/cluic/wxauto" target="_blank">
    <img src="https://img.shields.io/badge/wxauto-自动化框架 -0099E5?logo=wechat&logoColor=white" alt="wxauto">
  </a>
  <a href="https://deepseek.com/" target="_blank">
    <img src="https://img.shields.io/badge/DeepSeek-LLM 服务 -FF6B6B?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyIDJMMiA3bDEwIDUgMTAtNS0xMC01eiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0yIDE3bDEwIDUgMTAtNU0yIDEybDEwIDUgMTAtNSIvPjwvc3ZnPg==" alt="DeepSeek">
  </a>
</div>

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

[![Star History](https://api.star-history.com/svg?repos=iwyxdxl/My-Dream-Moments&type=Timeline)](https://star-history.com/#iwyxdxl/My-Dream-Moments)
