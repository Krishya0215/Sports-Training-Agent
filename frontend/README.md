# 运动训练知识问答系统 - 前端

基于Vue 3的现代化前端界面，采用简洁、高级的设计风格。

## 技术栈

- Vue 3 - 渐进式JavaScript框架
- Vue Router - 路由管理
- Pinia - 状态管理
- Axios - HTTP客户端
- Vite - 构建工具

## 设计特点

- 🎨 黑白配色，简洁现代
- 📱 响应式设计，适配多端
- ⚡ 流畅动画，优雅交互
- 🔍 直观导航，易于使用

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口
│   ├── assets/           # 静态资源
│   │   └── styles/       # 全局样式
│   ├── components/       # 公共组件
│   │   └── Navbar.vue    # 导航栏
│   ├── views/            # 页面视图
│   │   ├── Home.vue      # 首页
│   │   ├── Chat.vue      # 问答页面
│   │   ├── Knowledge.vue # 知识库管理
│   │   └── Memory.vue    # 记忆系统
│   ├── router/           # 路由配置
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html
├── package.json
└── vite.config.js
```

## 功能模块

### 1. 首页 (Home)

- 系统介绍和统计数据
- 快速入口
- 核心功能展示

### 2. 问答页面 (Chat)

- 实时对话界面
- 对话历史记录
- 智能建议问题
- 上下文感知

### 3. 知识库管理 (Knowledge)

- 文档列表展示
- 搜索和筛选
- 知识库加载
- 统计信息

### 4. 记忆系统 (Memory)

- 四层记忆可视化
- 工作记忆、情景记忆、语义记忆、感知记忆
- 最近活动记录
- 记忆状态监控

## API接口

前端通过 `/api` 代理与后端通信：

```javascript
// 查询问答
POST /api/query
Body: { question: string }

// 加载知识库
POST /api/knowledge/load

// 获取记忆摘要
GET /api/memory/summary

// 清空工作记忆
POST /api/memory/clear

// 获取对话历史
GET /api/chat/history
```

## 配置说明

### 代理配置

在 `vite.config.js` 中配置后端代理：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 样式变量

在 `src/assets/styles/global.css` 中定义全局样式变量：

```css
:root {
  --color-bg: #f5f5f7;
  --color-surface: #ffffff;
  --color-text-primary: #1d1d1f;
  --color-text-secondary: #86868b;
  --color-accent: #0071e3;
  /* ... */
}
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 开发建议

1. 使用Vue DevTools进行调试
2. 遵循Vue 3 Composition API最佳实践
3. 保持组件单一职责
4. 使用语义化的HTML标签
5. 注意性能优化和代码分割

## 许可证

MIT License
