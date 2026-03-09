# 項目總覽與快速開始

## 文檔結構

本技術方案分為 6 個文檔：

1. **01-overview.md** - 項目概述
2. **02-phase1-samba.md** - 第一階段：Samba + AI 分析
3. **03-code-implementation.md** - 核心代碼實現
4. **04-phase2-web.md** - 第二階段：Web 端輸入
5. **05-phase3-ai.md** - 第三階段：智能化
6. **06-deployment-ops.md** - 部署與運維指南

---

## 快速開始（第 1 階段）

### 準備工作

**硬件：**
- NAS (192.168.0.20) - Samba 文件共享
- 主機 (192.168.0.22) - AI 程序運行

**軟件：**
- Python 3.11+
- Samba
- 企業微信應用

---

### 10 分鐘快速部署

#### Step 1: 配置 Samba (NAS)

```bash
# SSH 登入 NAS
ssh root@192.168.0.20

# 創建目錄
sudo mkdir -p /mnt/16TB1/tricycle-data/{sales,production,inventory,knowledge}

# 安裝 Samba
sudo apt install samba -y

# 配置
sudo nano /etc/samba/smb.conf
```

添加：
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
# 密碼：tricycle123

# 重啟
sudo systemctl restart smbd
```

---

#### Step 2: 掛載 Samba (主機)

```bash
# SSH 登入主機
ssh root@192.168.0.22

# 安裝工具
sudo apt install cifs-utils -y

# 創建掛載點
sudo mkdir -p /mnt/samba/tricycle-data

# 掛載
sudo mount -t cifs //192.168.0.20/tricycle-data /mnt/samba/tricycle-data \
  -o username=tricycle,password=tricycle123

# 測試
ls /mnt/samba/tricycle-data
```

---

#### Step 3: 部署 AI 程序

```bash
# 創建項目
sudo mkdir -p /opt/tricycle-agent
cd /opt/tricycle-agent

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install fastapi uvicorn openpyxl pandas watchdog requests schedule
```

---

#### Step 4: 配置企業微信

1. 登入企業微信管理後台：https://work.weixin.qq.com/
2. 應用管理 → 創建應用 → "智能助手"
3. 記錄：
   - CorpID: `ww1234567890abcdef`
   - AgentID: `1000001`
   - Secret: `abc123...`

---

#### Step 5: 創建配置文件

```bash
mkdir -p /opt/tricycle-agent/data
nano /opt/tricycle-agent/data/config.json
```

```json
{
  "wechat": {
    "corp_id": "ww1234567890abcdef",
    "agent_id": "1000001",
    "secret": "YOUR_SECRET"
  },
  "samba": {
    "path": "/mnt/samba/tricycle-data"
  }
}
```

---

#### Step 6: 複製代碼

從 `03-code-implementation.md` 複製代碼到對應文件：
- `backend/main.py`
- `backend/wechat_bot.py`
- `backend/data_dashboard.py`
- `backend/task_manager.py`
- `backend/file_monitor.py`

---

#### Step 7: 測試運行

```bash
cd /opt/tricycle-agent
source venv/bin/activate

# 測試數據看板
python backend/data_dashboard.py

# 啟動主程序
python backend/main.py
```

---

#### Step 8: 配置 Systemd

```bash
sudo nano /etc/systemd/system/tricycle-agent.service
```

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
sudo systemctl daemon-reload
sudo systemctl enable tricycle-agent
sudo systemctl start tricycle-agent
sudo systemctl status tricycle-agent
```

---

### 測試驗證

#### 1. 測試數據看板

```bash
# 複製測試數據
cp /mnt/16TB1/AI/三輪車項目/25年1-4月区域客户数据统计.xlsx \
   /mnt/samba/tricycle-data/sales/

# 檢查日誌
tail -f /opt/tricycle-agent/logs/app.log

# 應該收到企業微信推送
```

---

#### 2. 測試任務下發

在企業微信發送：
```
安排張三 3 天內完成 A 型號生產計劃
```

應該收到回覆：
```
✅ 任務已創建
負責人：張三
內容：A 型號生產計劃
截止時間：2026-03-10
```

---

#### 3. 測試知識庫

```bash
# 上傳測試文件
cp /path/to/產品圖.jpg /mnt/samba/tricycle-data/knowledge/
```

在企業微信發送：
```
產品圖
```

應該收到圖片。

---

## 常見問題

### Q1: Samba 掛載失敗？

**檢查：**
```bash
# 測試連接
smbclient //192.168.0.20/tricycle-data -U tricycle

# 檢查防火牆
sudo ufw allow samba
```

---

### Q2: 企業微信推送失敗？

**檢查：**
```python
# 測試 token
from wechat_bot import init_bot, send_message

init_bot(
    corp_id="YOUR_CORP_ID",
    agent_id="YOUR_AGENT_ID",
    secret="YOUR_SECRET"
)

send_message("測試消息")
```

---

### Q3: Excel 解析錯誤？

**檢查：**
```bash
# 測試文件
python -c "
import openpyxl
wb = openpyxl.load_workbook('/mnt/samba/tricycle-data/sales/test.xlsx')
print(wb.sheetnames)
"
```

---

## 下一步

### 第 1 週
- [x] 完成基礎部署
- [ ] 上傳真實數據測試
- [ ] 收集用戶反饋
- [ ] 優化看板格式

### 第 2 週
- [ ] 完善任務管理
- [ ] 添加知識庫內容
- [ ] 培訓統計部使用
- [ ] 準備正式上線

### 第 3-4 週
- [ ] 全員推廣
- [ ] 監控系統運行
- [ ] 持續優化
- [ ] 準備階段 2 開發

---

## 聯繫方式

**技術支持：**
- 企業微信：智能助手應用
- 電話：XXX-XXXX-XXXX
- 郵箱：support@example.com

**緊急聯繫：**
- 24/7 熱線：XXX-XXXX-XXXX

---

## 附錄

### A. 企業微信 API 文檔
https://developer.work.weixin.qq.com/document/

### B. Python 依賴版本
```
fastapi==0.104.1
uvicorn==0.24.0
openpyxl==3.1.2
pandas==2.1.3
watchdog==3.0.0
requests==2.31.0
schedule==1.2.0
```

### C. 系統要求
- Python 3.11+
- Ubuntu 22.04 LTS
- 8GB RAM
- 100GB 存儲

---

## 版本歷史

**v1.0 (2026-03-07)**
- 初始版本
- 完成第 1 階段技術方案
- 包含完整代碼實現
- 部署與運維指南

---

**文檔完成！** 🎉

現在可以開始實施第 1 階段部署。
