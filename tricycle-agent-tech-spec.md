# 電動三輪車企業智能體系統 - 技術方案文檔

**版本**: 1.0  
**日期**: 2026-03-07  
**客戶**: 電動三輪車企業（329人）  
**項目週期**: 三階段演進（1週 → 3-6個月 → 1年）

---

## 目錄

1. [項目概述](#項目概述)
2. [三階段演進方案](#三階段演進方案)
3. [第一階段：Samba + AI 分析](#第一階段samba--ai-分析)
4. [第二階段：Web 端輸入](#第二階段web-端輸入)
5. [第三階段：智能化](#第三階段智能化)
6. [技術架構](#技術架構)
7. [數據庫設計](#數據庫設計)
8. [API 設計](#api-設計)
9. [部署方案](#部署方案)
10. [成本估算](#成本估算)
11. [風險評估](#風險評估)

---

## 項目概述

### 業務目標
- 自動化數據整理（節省統計部 87.5% 時間）
- 任務管理智能化（延誤率降至 5%）
- 知識庫快速調取（節省 95% 查找時間）

### 核心功能
1. **任務下發智能體** - 老闆下任務、自動催辦、進度看板
2. **數據自動看板** - 銷售/生產/庫存數據自動分析
3. **知識庫調取** - 一句話搵產品圖、合同模板

### 技術選型
- **通訊平台**: 企業微信
- **後端框架**: FastAPI (Python 3.11+)
- **數據庫**: SQLite (階段1) → PostgreSQL (階段2+)
- **文件共享**: Samba
- **前端**: Vue.js 3 + Tailwind CSS (階段2)

---

## 三階段演進方案

### 演進路線圖

```
階段 1 (1-2週)          階段 2 (3-6個月)        階段 3 (1年)
Samba + AI 分析    →    Web 端輸入         →    智能化
員工用 Excel            員工用表單              語音/拍照輸入
零學習成本              提升效率                極致體驗
```

### 為什麼分階段？

**階段 1 優勢：**
- ✅ 快速落地（1-2週見效）
- ✅ 零學習成本（員工繼續用 Excel）
- ✅ 低風險（不改變現有流程）
- ✅ 建立信任（讓老闆看到效果）

**階段 2 時機：**
- 員工已習慣 AI 看板
- 老闆認可系統價值
- 願意投入更多預算
- 準備改變工作流程

**階段 3 願景：**
- 完全智能化
- 極致用戶體驗
- 行業領先水平

---

## 第一階段：Samba + AI 分析

### 系統架構

```
┌─────────────────────────────────────────────────┐
│              員工（Excel 製表）                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         Samba 共享文件夾 (NAS)                   │
│  \\192.168.0.20\tricycle-data\                  │
│  ├─ sales/      (銷售數據)                      │
│  ├─ production/ (生產數據)                      │
│  ├─ inventory/  (庫存數據)                      │
│  └─ knowledge/  (知識庫)                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         AI 監控程序 (192.168.0.22)               │
│  - 監控新文件                                    │
│  - 自動解析 Excel                                │
│  - 數據驗證                                      │
│  - 生成看板                                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         企業微信推送                              │
│  - 每日 8:00 / 18:00 自動看板                   │
│  - 異常預警即時推送                              │
│  - 任務提醒                                      │
└─────────────────────────────────────────────────┘
```

### 核心功能

#### 1. 數據自動看板

**輸入：** Excel 文件（25年1-4月区域客户数据统计.xlsx）

**處理流程：**
1. 監控 Samba 文件夾
2. 檢測到新文件 → 自動解析
3. 數據驗證（格式、完整性）
4. 生成分析報告
5. 推送企業微信

**輸出示例：**
```
📊 銷售日報 (2026-03-07)

【區域銷量】
🥇 山東區域：1,234 台 (↑15%)
🥈 河南區域：987 台 (↑8%)
🥉 安徽區域：856 台 (↓3%)
   河北區域：745 台 (↑12%)
   東北區域：623 台 (↓5%)

【TOP 客戶】
1. 庆云县常家镇-张总：238 台
2. 沂水县刘南宅-姚在军：106 台
3. 滨州阳信-宋强：71 台

【異常預警】
⚠️ 東北區域銷量下降 5%，需關注
✅ 整體銷量達標，完成率 108%
```

#### 2. 任務下發智能體

**使用場景：**
```
老闆 → 企業微信：
"安排張三 3 天內完成 A 型號生產計劃"

AI 自動：
1. 解析任務
   - 負責人：張三
   - 內容：A 型號生產計劃
   - 截止時間：2026-03-10

2. 發送通知
   → 張三收到任務通知

3. 記錄任務
   → 存入數據庫

4. 自動催辦
   - 截止前 1 天：提醒張三
   - 截止當天未完成：催促 + 通知老闆
```

**任務狀態追蹤：**
```
📋 任務看板 (2026-03-07)

【進行中】8 項
- A 型號生產計劃 (張三, 剩 2 天)
- 採購原材料 (李四, 剩 1 天) ⚠️
- ...

【已完成】12 項
【延誤】3 項 ⚠️
- B 型號質檢報告 (王五, 延誤 1 天)
- ...
```

#### 3. 知識庫調取

**使用場景：**
```
銷售 → 企業微信：
"A 型號產品圖"

AI 回覆：
[圖片] A 型號產品圖.jpg
參數：電池 60V、續航 80km、載重 500kg
價格：¥8,800
```

**知識庫內容：**
- 產品圖片（23 個型號）
- 合同模板（經銷商、採購）
- 操作手冊（生產、品質）
- 培訓視頻（新員工入職）

### 技術實現

#### 項目結構
```
/opt/tricycle-agent/
├── backend/
│   ├── main.py              # FastAPI 主程序
│   ├── wechat_bot.py        # 企業微信 bot
│   ├── task_manager.py      # 任務管理
│   ├── data_dashboard.py    # 數據看板
│   ├── knowledge_base.py    # 知識庫
│   └── file_monitor.py      # Samba 文件監控
├── data/
│   ├── tasks.db             # SQLite 任務數據庫
│   └── config.json          # 配置文件
├── knowledge/               # 知識庫文件
├── logs/                    # 日誌
├── requirements.txt
├── systemd/
│   └── tricycle-agent.service
└── README.md
```

#### 核心代碼模塊

**1. Samba 文件監控 (file_monitor.py)**
```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ExcelFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.xlsx'):
            print(f"新文件: {event.src_path}")
            process_excel(event.src_path)

def monitor_samba():
    observer = Observer()
    observer.schedule(
        ExcelFileHandler(), 
        path="/mnt/samba/tricycle-data/sales/",
        recursive=False
    )
    observer.start()
```

**2. Excel 解析 (data_dashboard.py)**
```python
import openpyxl
import pandas as pd

def parse_sales_data(file_path):
    wb = openpyxl.load_workbook(file_path)
    
    # 解析所有區域
    regions = {}
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        df = pd.DataFrame(ws.values)
        regions[sheet_name] = analyze_region(df)
    
    return generate_report(regions)
```

**3. 企業微信推送 (wechat_bot.py)**
```python
import requests

def send_wechat_message(content):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": AGENT_ID,
        "text": {"content": content}
    }
    requests.post(url, json=data, params={"access_token": get_token()})
```

### 部署步驟

#### Step 1: Samba 配置 (NAS: 192.168.0.20)

```bash
# 安裝 Samba
sudo apt install samba -y

# 創建共享目錄
sudo mkdir -p /mnt/16TB1/tricycle-data/{sales,production,inventory,knowledge}

# 配置 Samba
sudo nano /etc/samba/smb.conf
```

**smb.conf 配置：**
```ini
[tricycle-data]
    path = /mnt/16TB1/tricycle-data
    browseable = yes
    writable = yes
    valid users = tricycle
    create mask = 0664
    directory mask = 0775
```

```bash
# 創建用戶
sudo useradd tricycle
sudo smbpasswd -a tricycle

# 重啟 Samba
sudo systemctl restart smbd
```

#### Step 2: 主機掛載 Samba (192.168.0.22)

```bash
# 安裝 cifs-utils
sudo apt install cifs-utils -y

# 創建掛載點
sudo mkdir -p /mnt/samba/tricycle-data

# 掛載
sudo mount -t cifs //192.168.0.20/tricycle-data /mnt/samba/tricycle-data \
  -o username=tricycle,password=YOUR_PASSWORD

# 開機自動掛載
echo "//192.168.0.20/tricycle-data /mnt/samba/tricycle-data cifs username=tricycle,password=YOUR_PASSWORD 0 0" | sudo tee -a /etc/fstab
```

#### Step 3: 安裝 AI 程序

```bash
# 創建項目目錄
sudo mkdir -p /opt/tricycle-agent
cd /opt/tricycle-agent

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install fastapi uvicorn openpyxl pandas watchdog requests schedule
```

#### Step 4: 企業微信配置

1. 登入企業微信管理後台
2. 創建應用 "智能助手"
3. 獲取配置信息：
   - CorpID
   - AgentID
   - Secret
4. 配置回調 URL: `http://YOUR_IP:8000/wechat/callback`

#### Step 5: 啟動服務

```bash
# 創建 systemd service
sudo nano /etc/systemd/system/tricycle-agent.service
```

**tricycle-agent.service:**
```ini
[Unit]
Description=Tricycle Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tricycle-agent
ExecStart=/opt/tricycle-agent/venv/bin/python backend/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable tricycle-agent
sudo systemctl start tricycle-agent

# 檢查狀態
sudo systemctl status tricycle-agent
```

### 測試計劃

#### Week 1: 基礎功能測試

**Day 1-2: Samba + 文件監控**
- [ ] Samba 共享正常
- [ ] 文件監控程序運行
- [ ] 新文件自動檢測

**Day 3-4: 數據解析 + 看板生成**
- [ ] Excel 解析正確
- [ ] 數據驗證通過
- [ ] 看板格式美觀

**Day 5-7: 企業微信整合**
- [ ] 消息推送成功
- [ ] 任務下發功能
- [ ] 知識庫調取

#### Week 2: 實際數據測試

- [ ] 統計部上傳真實數據
- [ ] 老闆收到自動看板
- [ ] 任務管理流程測試
- [ ] 收集反饋並優化

---

## 第二階段：Web 端輸入

### 系統架構升級

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

### Web 界面設計

#### 1. 銷售錄入頁面

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

#### 2. 數據看板頁面

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

#### 3. 任務管理頁面

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

### 技術實現

#### 前端技術棧
- Vue.js 3 (Composition API)
- Tailwind CSS
- Chart.js (圖表)
- Axios (HTTP 請求)
- Vue Router (路由)
- Pinia (狀態管理)

#### 後端 API 設計

**銷售相關：**
```
POST   /api/sales          # 新增銷售記錄
GET    /api/sales          # 查詢銷售記錄
GET    /api/sales/stats    # 銷售統計
GET    /api/sales/export   # 導出 Excel
```

**任務相關：**
```
POST   /api/tasks          # 創建任務
GET    /api/tasks          # 查詢任務列表
PUT    /api/tasks/:id      # 更新任務
DELETE /api/tasks/:id      # 刪除任務
```

**用戶相關：**
```
POST   /api/auth/login     # 登入
POST   /api/auth/logout    # 登出
GET    /api/users/me       # 當前用戶信息
```

### 權限設計

```
角色權限矩陣：

角色         銷售錄入  生產管理  庫存管理  數據看板  任務管理  系統設置
─────────────────────────────────────────────────────────────
老闆           ✓        ✓        ✓        ✓        ✓        ✓
銷售經理       ✓        ✗        ✗        ✓        ✓        ✗
銷售員         ✓        ✗        ✗        ✓        ✗        ✗
生產經理       ✗        ✓        ✓        ✓        ✓        ✗
統計員         ✓        ✓        ✓        ✓        ✗        ✗
```

---

## 第三階段：智能化

### 語音輸入

**使用場景：**
```
銷售員（開車中）→ 語音：
"今日賣咗 20 台 A 型號畀張三"

AI 自動：
1. 語音識別
2. 意圖理解
3. 自動錄入
4. 確認回覆："已記錄，張三今日購買 A 型號 20 台"
```

### 拍照識別

**使用場景：**
```
倉管員 → 拍照出庫單

AI 自動：
1. OCR 識別
2. 提取信息（型號、數量、客戶）
3. 自動更新庫存
4. 生成出庫記錄
```

### 智能預測

**功能：**
- 銷量預測（基於歷史數據）
- 庫存預警（自動補貨提醒）
- 異常檢測（銷量異常、延誤風險）

---

## 數據庫設計

### 階段 1: SQLite

**tasks 表（任務管理）：**
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    assignee TEXT NOT NULL,
    deadline TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 階段 2: PostgreSQL

**完整數據庫設計：**

