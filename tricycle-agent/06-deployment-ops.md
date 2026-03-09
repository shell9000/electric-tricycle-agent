# 部署與運維指南

## 服務器配置

### 硬件要求

#### 階段 1（Samba + AI 分析）
```
CPU：4 核心
RAM：8 GB
存儲：100 GB
網絡：千兆網卡
```

#### 階段 2（Web 端）
```
CPU：8 核心
RAM：16 GB
存儲：200 GB
數據庫：PostgreSQL
網絡：千兆網卡
```

#### 階段 3（智能化）
```
CPU：16 核心
RAM：32 GB
GPU：NVIDIA RTX 3060 或以上（12GB VRAM）
存儲：500 GB SSD
網絡：千兆網卡
```

---

## 網絡架構

### 內網部署（推薦）

```
                    Internet
                       ↓
                  OpenWRT 路由器
                  (10.0.0.1)
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    NAS (Samba)    主機 (AI)      員工電腦
   192.168.0.20   192.168.0.22   192.168.0.x
```

**優點：**
- 數據安全（不出內網）
- 速度快（內網傳輸）
- 成本低（無需雲服務器）

---

### 混合部署（可選）

```
                    Internet
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
         雲服務器          內網服務器
      (Web 前端)         (數據庫 + AI)
              ↓                 ↑
              └─────VPN─────────┘
```

**優點：**
- 外網可訪問（出差、在家）
- 數據仍在內網（安全）

---

## 安全配置

### 1. 防火牆規則

```bash
# 只允許內網訪問
sudo ufw allow from 192.168.0.0/24 to any port 8000
sudo ufw allow from 10.0.0.0/24 to any port 8000

# 拒絕外網訪問
sudo ufw deny 8000

# 啟用防火牆
sudo ufw enable
```

---

### 2. Nginx 反向代理

```nginx
# /etc/nginx/sites-available/tricycle-agent

server {
    listen 80;
    server_name tricycle.local;

    # 限制訪問 IP
    allow 192.168.0.0/24;
    allow 10.0.0.0/24;
    deny all;

    # 前端
    location / {
        root /var/www/tricycle-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 後端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 企業微信回調
    location /wechat {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

---

### 3. 數據庫安全

```bash
# PostgreSQL 配置
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

```
# 只允許本地連接
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# 如需內網訪問
host    tricycle_db     tricycle_user   192.168.0.0/24          md5
```

---

### 4. 備份策略

#### 數據庫備份

```bash
#!/bin/bash
# /opt/tricycle-agent/scripts/backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/16TB1/tricycle-backup"

# 備份 PostgreSQL
pg_dump -U tricycle_user tricycle_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 保留最近 30 天
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "數據庫備份完成: db_$DATE.sql.gz"
```

**定時任務：**
```bash
# 每天凌晨 2:00 備份
0 2 * * * /opt/tricycle-agent/scripts/backup_db.sh
```

---

#### 文件備份

```bash
#!/bin/bash
# /opt/tricycle-agent/scripts/backup_files.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/16TB1/tricycle-backup"

# 備份代碼
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /opt/tricycle-agent

# 備份知識庫
tar -czf $BACKUP_DIR/knowledge_$DATE.tar.gz /mnt/samba/tricycle-data/knowledge

# 保留最近 30 天
find $BACKUP_DIR -name "code_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "knowledge_*.tar.gz" -mtime +30 -delete

echo "文件備份完成"
```

---

## 監控與日誌

### 1. 系統監控

```bash
# 安裝 Prometheus + Grafana
sudo apt install prometheus grafana -y

# 配置 Prometheus
sudo nano /etc/prometheus/prometheus.yml
```

```yaml
scrape_configs:
  - job_name: 'tricycle-agent'
    static_configs:
      - targets: ['localhost:8000']
```

---

### 2. 日誌管理

```python
# backend/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    """設置日誌"""
    
    # 創建日誌目錄
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 創建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 文件 handler（自動輪轉）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(level)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用
logger = setup_logger('tricycle-agent', 'logs/app.log')
logger.info("系統啟動")
```

---

### 3. 性能監控

```python
# backend/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# 請求計數
request_count = Counter('tricycle_requests_total', 'Total requests')

# 請求延遲
request_latency = Histogram('tricycle_request_latency_seconds', 'Request latency')

# 在線用戶
online_users = Gauge('tricycle_online_users', 'Online users')

# 使用
@app.middleware("http")
async def monitor_requests(request, call_next):
    request_count.inc()
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_latency.observe(duration)
    
    return response
```

---

## 故障排查

### 常見問題

#### 1. Samba 掛載失敗

**症狀：**
```
mount error(13): Permission denied
```

**解決：**
```bash
# 檢查用戶名密碼
sudo mount -t cifs //192.168.0.20/tricycle-data /mnt/samba/tricycle-data \
  -o username=tricycle,password=YOUR_PASSWORD,vers=3.0

# 檢查 Samba 服務
sudo systemctl status smbd

# 檢查防火牆
sudo ufw allow samba
```

---

#### 2. 企業微信推送失敗

**症狀：**
```
{"errcode": 40014, "errmsg": "invalid access_token"}
```

**解決：**
```python
# 檢查 token 是否過期
# 重新獲取 token
token = bot.get_access_token()

# 檢查 CorpID、AgentID、Secret 是否正確
```

---

#### 3. 數據庫連接失敗

**症狀：**
```
psycopg2.OperationalError: could not connect to server
```

**解決：**
```bash
# 檢查 PostgreSQL 服務
sudo systemctl status postgresql

# 檢查連接配置
sudo nano /etc/postgresql/15/main/postgresql.conf
# listen_addresses = 'localhost'

# 重啟服務
sudo systemctl restart postgresql
```

---

#### 4. Excel 解析錯誤

**症狀：**
```
openpyxl.utils.exceptions.InvalidFileException
```

**解決：**
```python
# 檢查文件格式
import openpyxl

try:
    wb = openpyxl.load_workbook(file_path)
except Exception as e:
    logger.error(f"文件格式錯誤: {e}")
    # 嘗試用 pandas 讀取
    import pandas as pd
    df = pd.read_excel(file_path)
```

---

## 性能優化

### 1. 數據庫優化

```sql
-- 創建索引
CREATE INDEX idx_sales_date ON sales(date);
CREATE INDEX idx_sales_region ON sales(region);
CREATE INDEX idx_sales_customer ON sales(customer_id);

-- 定期清理
VACUUM ANALYZE sales;

-- 查詢優化
EXPLAIN ANALYZE SELECT * FROM sales WHERE date > '2026-01-01';
```

---

### 2. API 優化

```python
# 使用緩存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_sales_stats(date):
    """緩存銷售統計"""
    return calculate_stats(date)

# 異步處理
from fastapi import BackgroundTasks

@app.post("/api/sales")
async def create_sale(sale: Sale, background_tasks: BackgroundTasks):
    # 立即返回
    sale_id = save_sale(sale)
    
    # 後台處理
    background_tasks.add_task(send_notification, sale_id)
    
    return {"id": sale_id}
```

---

### 3. 前端優化

```javascript
// 懶加載
const Dashboard = () => import('./views/Dashboard.vue')

// 虛擬滾動（大列表）
import { VirtualScroller } from 'vue-virtual-scroller'

// 圖片壓縮
import imageCompression from 'browser-image-compression'
```

---

## 升級指南

### 從階段 1 升級到階段 2

```bash
# 1. 備份數據
/opt/tricycle-agent/scripts/backup_db.sh

# 2. 安裝 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 3. 遷移數據
python scripts/migrate_sqlite_to_postgres.py

# 4. 部署前端
cd frontend
npm run build
sudo cp -r dist/* /var/www/tricycle-frontend/

# 5. 更新後端
cd backend
git pull
pip install -r requirements.txt

# 6. 重啟服務
sudo systemctl restart tricycle-agent
```

---

### 從階段 2 升級到階段 3

```bash
# 1. 安裝 GPU 驅動
sudo apt install nvidia-driver-535 -y

# 2. 安裝 CUDA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"
sudo apt update
sudo apt install cuda -y

# 3. 安裝 AI 模型
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers

# 4. 部署模型
python scripts/deploy_models.py

# 5. 重啟服務
sudo systemctl restart tricycle-agent
```

---

## 用戶培訓

### 培訓計劃

#### 第 1 週：基礎培訓
- 系統介紹
- 登入與權限
- 基本操作演示

#### 第 2 週：實操培訓
- 銷售錄入
- 數據查詢
- 任務管理

#### 第 3 週：進階培訓
- 數據看板
- 報表導出
- 常見問題處理

---

### 培訓材料

**用戶手冊：**
- 圖文教程
- 視頻教程
- 常見問題 FAQ

**快速參考卡：**
- 常用功能
- 快捷鍵
- 聯繫方式

---

## 技術支持

### 支持渠道

1. **企業微信群**
   - 即時響應
   - 問題討論

2. **工單系統**
   - 問題追蹤
   - 優先級管理

3. **遠程協助**
   - TeamViewer
   - 向日葵

---

### SLA（服務等級協議）

| 優先級 | 響應時間 | 解決時間 |
|--------|----------|----------|
| P0 緊急 | 30 分鐘  | 4 小時   |
| P1 高   | 2 小時   | 1 天     |
| P2 中   | 1 天     | 3 天     |
| P3 低   | 3 天     | 1 週     |

---

## 總結

本文檔涵蓋：
- ✅ 服務器配置
- ✅ 網絡架構
- ✅ 安全配置
- ✅ 備份策略
- ✅ 監控日誌
- ✅ 故障排查
- ✅ 性能優化
- ✅ 升級指南
- ✅ 用戶培訓
- ✅ 技術支持

**下一步：**
開始實施第 1 階段部署！
