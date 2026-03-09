# 第一階段：Samba + AI 分析（1-2週）

## 系統架構

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

---

## 核心功能

### 1. 數據自動看板

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

---

### 2. 任務下發智能體

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

---

### 3. 知識庫調取

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

---

## 項目結構

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

---

## 部署步驟

### Step 1: Samba 配置 (NAS: 192.168.0.20)

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

---

### Step 2: 主機掛載 Samba (192.168.0.22)

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

---

### Step 3: 安裝 AI 程序

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

---

### Step 4: 企業微信配置

1. 登入企業微信管理後台
2. 創建應用 "智能助手"
3. 獲取配置信息：
   - CorpID
   - AgentID
   - Secret
4. 配置回調 URL: `http://YOUR_IP:8000/wechat/callback`

---

### Step 5: 啟動服務

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

---

## 測試計劃

### Week 1: 基礎功能測試

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

### Week 2: 實際數據測試

- [ ] 統計部上傳真實數據
- [ ] 老闆收到自動看板
- [ ] 任務管理流程測試
- [ ] 收集反饋並優化
