# 第二階段：Web 端輸入（3-6個月）

## 系統架構升級

```
┌─────────────────────────────────────────────────┐
│         Web 前端 (Vue.js 3)                      │
│  - 銷售錄入表單                                  │
│  - 生產進度管理                                  │
│  - 庫存查詢                                      │
│  - 數據看板                                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         後端 API (FastAPI)                       │
│  - RESTful API                                   │
│  - 數據驗證                                      │
│  - 權限控制                                      │
│  - AI 分析                                       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         數據庫 (PostgreSQL)                      │
│  - 銷售記錄                                      │
│  - 生產記錄                                      │
│  - 庫存記錄                                      │
│  - 用戶權限                                      │
└─────────────────────────────────────────────────┘
```

---

## Web 界面設計

### 1. 銷售錄入頁面

```
┌─────────────────────────────────────────┐
│  📱 銷售錄入                             │
├─────────────────────────────────────────┤
│  日期：[2026-03-07        ]             │
│  區域：[山東 ▼]                         │
│  客戶：[選擇客戶 ▼]                     │
│        或 [新增客戶]                    │
│  型號：[A型號 ▼]                        │
│  數量：[____] 台                        │
│  備註：[________________]               │
│                                         │
│  [提交] [取消]                          │
└─────────────────────────────────────────┘
```

### 2. 數據看板頁面

```
┌─────────────────────────────────────────┐
│  📊 銷售看板                             │
├─────────────────────────────────────────┤
│  今日銷量：1,234 台 (↑15%)              │
│  本月銷量：23,456 台 (↑8%)              │
│                                         │
│  [區域分佈圖表]                         │
│  [TOP 客戶排行]                         │
│  [型號銷量對比]                         │
│                                         │
│  [導出 Excel] [打印報表]                │
└─────────────────────────────────────────┘
```

### 3. 任務管理頁面

```
┌─────────────────────────────────────────┐
│  📋 任務管理                             │
├─────────────────────────────────────────┤
│  [進行中] [已完成] [延誤]               │
│                                         │
│  ☐ A 型號生產計劃                       │
│     負責人：張三                        │
│     截止：2026-03-10 (剩 2 天)          │
│     [查看詳情] [標記完成]               │
│                                         │
│  ☐ 採購原材料 ⚠️                        │
│     負責人：李四                        │
│     截止：2026-03-08 (剩 1 天)          │
│     [查看詳情] [申請延期]               │
│                                         │
│  [+ 新增任務]                           │
└─────────────────────────────────────────┘
```

---

## 技術實現

### 前端技術棧
- **框架**: Vue.js 3 (Composition API)
- **UI**: Tailwind CSS
- **圖表**: Chart.js / ECharts
- **HTTP**: Axios
- **路由**: Vue Router
- **狀態**: Pinia

### 後端 API 設計

#### 銷售相關
```
POST   /api/sales          # 新增銷售記錄
GET    /api/sales          # 查詢銷售記錄
GET    /api/sales/stats    # 銷售統計
GET    /api/sales/export   # 導出 Excel
```

#### 任務相關
```
POST   /api/tasks          # 創建任務
GET    /api/tasks          # 查詢任務列表
PUT    /api/tasks/:id      # 更新任務
DELETE /api/tasks/:id      # 刪除任務
```

#### 用戶相關
```
POST   /api/auth/login     # 登入
POST   /api/auth/logout    # 登出
GET    /api/users/me       # 當前用戶信息
```

---

## 數據庫設計 (PostgreSQL)

### 銷售記錄表
```sql
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    customer_id INT REFERENCES customers(id),
    model VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    amount DECIMAL(10, 2),
    notes TEXT,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_date ON sales(date);
CREATE INDEX idx_sales_region ON sales(region);
```

### 客戶表
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    contact VARCHAR(100),
    phone VARCHAR(20),
    region VARCHAR(50),
    city VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 任務表
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    assignee_id INT REFERENCES users(id),
    deadline DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'normal',
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 用戶表
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(20) NOT NULL,
    department VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 權限設計

### 角色權限矩陣

| 角色     | 銷售錄入 | 生產管理 | 庫存管理 | 數據看板 | 任務管理 | 系統設置 |
|----------|----------|----------|----------|----------|----------|----------|
| 老闆     | ✓        | ✓        | ✓        | ✓        | ✓        | ✓        |
| 銷售經理 | ✓        | ✗        | ✗        | ✓        | ✓        | ✗        |
| 銷售員   | ✓        | ✗        | ✗        | ✓        | ✗        | ✗        |
| 生產經理 | ✗        | ✓        | ✓        | ✓        | ✓        | ✗        |
| 統計員   | ✓        | ✓        | ✓        | ✓        | ✗        | ✗        |

---

## 前端項目結構

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── assets/              # 靜態資源
│   ├── components/          # 組件
│   │   ├── SalesForm.vue
│   │   ├── Dashboard.vue
│   │   ├── TaskList.vue
│   │   └── ...
│   ├── views/               # 頁面
│   │   ├── Home.vue
│   │   ├── Sales.vue
│   │   ├── Tasks.vue
│   │   └── Login.vue
│   ├── router/              # 路由
│   │   └── index.js
│   ├── stores/              # 狀態管理
│   │   ├── user.js
│   │   └── sales.js
│   ├── api/                 # API 請求
│   │   ├── sales.js
│   │   └── tasks.js
│   ├── utils/               # 工具函數
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js
```

---

## 部署方案

### 開發環境
```bash
# 前端
cd frontend
npm install
npm run dev

# 後端
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 生產環境

**前端（Nginx）：**
```bash
# 構建
npm run build

# Nginx 配置
server {
    listen 80;
    server_name tricycle.example.com;
    
    root /var/www/tricycle-frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**後端（Systemd）：**
```ini
[Unit]
Description=Tricycle Agent API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tricycle-agent
ExecStart=/opt/tricycle-agent/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 開發時間表

### Week 1-2: 後端 API
- [ ] 數據庫設計與創建
- [ ] 用戶認證系統
- [ ] 銷售 API
- [ ] 任務 API

### Week 3-4: 前端基礎
- [ ] 項目搭建
- [ ] 登入頁面
- [ ] 主框架（導航、側邊欄）
- [ ] 銷售錄入表單

### Week 5-6: 數據看板
- [ ] 圖表組件
- [ ] 統計分析
- [ ] 導出功能
- [ ] 任務管理頁面

### Week 7-8: 測試與優化
- [ ] 功能測試
- [ ] 性能優化
- [ ] 用戶培訓
- [ ] 正式上線

---

## 優勢對比

### 階段 1 vs 階段 2

| 特性         | 階段 1 (Samba)    | 階段 2 (Web)      |
|--------------|-------------------|-------------------|
| 數據錄入     | Excel 手動        | Web 表單即時      |
| 數據查詢     | 需要打開文件      | 即時查詢          |
| 權限控制     | 文件夾權限        | 細粒度角色權限    |
| 移動端       | 不支持            | 完全支持          |
| 數據驗證     | 事後驗證          | 即時驗證          |
| 協作         | 文件衝突          | 無衝突            |
| 學習成本     | 零                | 需要培訓          |
| 開發時間     | 1-2 週            | 4-6 週            |
| 成本         | ¥8K-15K           | ¥30K-50K          |
