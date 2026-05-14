# 🤝 贡献指南 | Contributing Guide

感谢你对 QuantPilot 的关注！我们欢迎任何形式的贡献。

## 📋 如何贡献

### 🐛 报告 Bug
1. 在 [Issues](../../issues) 中搜索是否已有相同问题
2. 如果没有，创建新 Issue，包含：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 运行环境（Python 版本、操作系统）

### 💡 提出新功能
1. 在 [Issues](../../issues) 中创建 Feature Request
2. 描述功能需求和使用场景
3. 等待维护者评估和讨论

### 🔧 提交代码
1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 编写代码和测试
4. 确保所有测试通过：`python -m unittest discover tests/ -v`
5. 提交代码：`git commit -m "feat: 你的功能描述"`
6. 推送分支：`git push origin feature/your-feature`
7. 创建 Pull Request

### 📝 提交规范
请使用 Angular 提交规范：
- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### 🧪 代码规范
- 遵循 PEP 8 编码规范
- 保持零外部依赖原则
- 新功能必须附带单元测试
- 代码注释使用英文

## 📄 许可证
本项目采用 MIT 开源许可证。提交代码即表示你同意将代码以 MIT 许可证授权。
