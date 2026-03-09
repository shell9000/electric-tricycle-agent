# 核心代碼實現

## 1. 文件監控 (file_monitor.py)

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from data_dashboard import process_excel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelFileHandler(FileSystemEventHandler):
    """監控 Excel 文件變化"""
    
    def on_created(self, event):
        if event.src_path.endswith(('.xlsx', '.xls')):
            logger.info(f"檢測到新文件: {event.src_path}")
            try:
                process_excel(event.src_path)
            except Exception as e:
                logger.error(f"處理文件失敗: {e}")
    
    def on_modified(self, event):
        if event.src_path.endswith(('.xlsx', '.xls')):
            logger.info(f"文件已更新: {event.src_path}")
            try:
                process_excel(event.src_path)
            except Exception as e:
                logger.error(f"處理文件失敗: {e}")

def start_monitor(path="/mnt/samba/tricycle-data/sales"):
    """啟動文件監控"""
    event_handler = ExcelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    logger.info(f"開始監控目錄: {path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitor()
```

---

## 2. 數據看板 (data_dashboard.py)

```python
import openpyxl
import pandas as pd
from datetime import datetime
from wechat_bot import send_message

def parse_sales_excel(file_path):
    """解析銷售 Excel 文件"""
    wb = openpyxl.load_workbook(file_path)
    
    regions_data = {}
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # 轉換為 DataFrame
        data = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # 跳過空行
                data.append({
                    '市級': row[0],
                    '名稱': row[1],
                    '聯繫人': row[2],
                    '銷量匯總': row[3] or 0,
                    '1月': row[4] or 0,
                    '2月': row[5] or 0,
                    '3月': row[6] or 0,
                    '4月': row[7] or 0
                })
        
        df = pd.DataFrame(data)
        regions_data[sheet_name] = df
    
    return regions_data

def analyze_sales(regions_data):
    """分析銷售數據"""
    analysis = {
        'total_sales': 0,
        'regions': {},
        'top_customers': []
    }
    
    all_customers = []
    
    for region, df in regions_data.items():
        region_total = df['銷量匯總'].sum()
        analysis['total_sales'] += region_total
        analysis['regions'][region] = {
            'total': region_total,
            'customers': len(df)
        }
        
        # 收集所有客戶
        for _, row in df.iterrows():
            all_customers.append({
                'region': region,
                'name': row['名稱'],
                'contact': row['聯繫人'],
                'sales': row['銷量匯總']
            })
    
    # TOP 客戶排行
    all_customers.sort(key=lambda x: x['sales'], reverse=True)
    analysis['top_customers'] = all_customers[:10]
    
    return analysis

def generate_report(analysis):
    """生成報告文本"""
    report = f"📊 銷售日報 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    # 區域銷量
    report += "【區域銷量】\n"
    sorted_regions = sorted(
        analysis['regions'].items(), 
        key=lambda x: x[1]['total'], 
        reverse=True
    )
    
    medals = ['🥇', '🥈', '🥉']
    for i, (region, data) in enumerate(sorted_regions):
        medal = medals[i] if i < 3 else '  '
        report += f"{medal} {region}：{int(data['total'])} 台\n"
    
    # TOP 客戶
    report += "\n【TOP 客戶】\n"
    for i, customer in enumerate(analysis['top_customers'][:5], 1):
        report += f"{i}. {customer['contact']}：{int(customer['sales'])} 台\n"
    
    # 總計
    report += f"\n【總銷量】{int(analysis['total_sales'])} 台\n"
    
    return report

def process_excel(file_path):
    """處理 Excel 文件並推送報告"""
    print(f"開始處理文件: {file_path}")
    
    # 解析數據
    regions_data = parse_sales_excel(file_path)
    
    # 分析數據
    analysis = analyze_sales(regions_data)
    
    # 生成報告
    report = generate_report(analysis)
    
    # 推送企業微信
    send_message(report)
    
    print("報告已生成並推送")
    return report

if __name__ == "__main__":
    # 測試
    test_file = "/mnt/16TB1/AI/三輪車項目/25年1-4月区域客户数据统计.xlsx"
    report = process_excel(test_file)
    print(report)
```

---

## 3. 企業微信 Bot (wechat_bot.py)

```python
import requests
import json
import time
from datetime import datetime, timedelta

class WeChatBot:
    def __init__(self, corp_id, agent_id, secret):
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.secret = secret
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """獲取 access_token"""
        if self.access_token and self.token_expires_at > datetime.now():
            return self.access_token
        
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("errcode") == 0:
            self.access_token = data["access_token"]
            self.token_expires_at = datetime.now() + timedelta(seconds=7000)
            return self.access_token
        else:
            raise Exception(f"獲取 token 失敗: {data}")
    
    def send_text(self, content, touser="@all"):
        """發送文本消息"""
        token = self.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        
        data = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content
            }
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("errcode") == 0:
            print("消息發送成功")
            return True
        else:
            print(f"消息發送失敗: {result}")
            return False
    
    def send_markdown(self, content, touser="@all"):
        """發送 Markdown 消息"""
        token = self.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        
        data = {
            "touser": touser,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {
                "content": content
            }
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("errcode") == 0:
            print("消息發送成功")
            return True
        else:
            print(f"消息發送失敗: {result}")
            return False

# 全局實例
bot = None

def init_bot(corp_id, agent_id, secret):
    """初始化 bot"""
    global bot
    bot = WeChatBot(corp_id, agent_id, secret)

def send_message(content, touser="@all"):
    """發送消息（簡化接口）"""
    if bot is None:
        raise Exception("Bot 未初始化，請先調用 init_bot()")
    return bot.send_text(content, touser)

if __name__ == "__main__":
    # 測試
    init_bot(
        corp_id="YOUR_CORP_ID",
        agent_id="YOUR_AGENT_ID",
        secret="YOUR_SECRET"
    )
    send_message("測試消息")
```

---

## 4. 任務管理 (task_manager.py)

```python
import sqlite3
from datetime import datetime, timedelta
import re

class TaskManager:
    def __init__(self, db_path="data/tasks.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                assignee TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def parse_task(self, text):
        """解析任務文本"""
        # 例如: "安排張三 3 天內完成 A 型號生產計劃"
        
        # 提取負責人
        assignee_match = re.search(r'安排(\S+)', text)
        assignee = assignee_match.group(1) if assignee_match else None
        
        # 提取天數
        days_match = re.search(r'(\d+)\s*天', text)
        days = int(days_match.group(1)) if days_match else 7
        
        # 提取任務內容
        content_match = re.search(r'完成(.+)', text)
        title = content_match.group(1).strip() if content_match else text
        
        # 計算截止時間
        deadline = datetime.now() + timedelta(days=days)
        
        return {
            'title': title,
            'assignee': assignee,
            'deadline': deadline.strftime('%Y-%m-%d'),
            'days': days
        }
    
    def create_task(self, title, assignee, deadline, created_by=None):
        """創建任務"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (title, assignee, deadline, created_by)
            VALUES (?, ?, ?, ?)
        """, (title, assignee, deadline, created_by))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_tasks(self, status=None):
        """查詢任務"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM tasks WHERE status = ?
                ORDER BY deadline ASC
            """, (status,))
        else:
            cursor.execute("""
                SELECT * FROM tasks
                ORDER BY deadline ASC
            """)
        
        tasks = cursor.fetchall()
        conn.close()
        
        return tasks
    
    def update_task_status(self, task_id, status):
        """更新任務狀態"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, task_id))
        
        conn.commit()
        conn.close()
    
    def check_overdue_tasks(self):
        """檢查逾期任務"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE status = 'pending' AND deadline < ?
        """, (today,))
        
        overdue_tasks = cursor.fetchall()
        conn.close()
        
        return overdue_tasks
    
    def generate_task_report(self):
        """生成任務報告"""
        pending = self.get_tasks('pending')
        completed = self.get_tasks('completed')
        overdue = self.check_overdue_tasks()
        
        report = f"📋 任務看板 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        report += f"【進行中】{len(pending)} 項\n"
        for task in pending[:5]:
            days_left = (datetime.strptime(task[3], '%Y-%m-%d') - datetime.now()).days
            warning = " ⚠️" if days_left <= 1 else ""
            report += f"- {task[1]} ({task[2]}, 剩 {days_left} 天){warning}\n"
        
        report += f"\n【已完成】{len(completed)} 項\n"
        
        if overdue:
            report += f"\n【延誤】{len(overdue)} 項 ⚠️\n"
            for task in overdue[:3]:
                report += f"- {task[1]} ({task[2]})\n"
        
        return report

if __name__ == "__main__":
    # 測試
    tm = TaskManager()
    
    # 解析任務
    task_info = tm.parse_task("安排張三 3 天內完成 A 型號生產計劃")
    print(task_info)
    
    # 創建任務
    task_id = tm.create_task(
        title=task_info['title'],
        assignee=task_info['assignee'],
        deadline=task_info['deadline'],
        created_by="老闆"
    )
    print(f"任務已創建，ID: {task_id}")
    
    # 生成報告
    report = tm.generate_task_report()
    print(report)
```

---

## 5. 主程序 (main.py)

```python
from fastapi import FastAPI, Request
from wechat_bot import init_bot, send_message
from task_manager import TaskManager
from data_dashboard import process_excel
import schedule
import threading
import time
import json

app = FastAPI()

# 配置
with open('data/config.json', 'r') as f:
    config = json.load(f)

# 初始化
init_bot(
    corp_id=config['wechat']['corp_id'],
    agent_id=config['wechat']['agent_id'],
    secret=config['wechat']['secret']
)

tm = TaskManager()

# 企業微信回調
@app.post("/wechat/callback")
async def wechat_callback(request: Request):
    """處理企業微信消息"""
    data = await request.json()
    
    msg_type = data.get('MsgType')
    content = data.get('Content', '')
    from_user = data.get('FromUserName')
    
    if msg_type == 'text':
        # 判斷是否為任務指令
        if '安排' in content and '完成' in content:
            # 解析任務
            task_info = tm.parse_task(content)
            
            # 創建任務
            task_id = tm.create_task(
                title=task_info['title'],
                assignee=task_info['assignee'],
                deadline=task_info['deadline'],
                created_by=from_user
            )
            
            # 回覆確認
            reply = f"✅ 任務已創建\n"
            reply += f"負責人：{task_info['assignee']}\n"
            reply += f"內容：{task_info['title']}\n"
            reply += f"截止時間：{task_info['deadline']}"
            
            send_message(reply, touser=from_user)
            
            # 通知負責人
            notify = f"📋 新任務\n{task_info['title']}\n截止時間：{task_info['deadline']}"
            send_message(notify, touser=task_info['assignee'])
    
    return {"status": "ok"}

# 定時任務
def scheduled_tasks():
    """定時任務"""
    # 每日 8:00 推送任務看板
    schedule.every().day.at("08:00").do(lambda: send_message(tm.generate_task_report()))
    
    # 每日 18:00 推送任務看板
    schedule.every().day.at("18:00").do(lambda: send_message(tm.generate_task_report()))
    
    # 每小時檢查逾期任務
    schedule.every().hour.do(check_overdue)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def check_overdue():
    """檢查逾期任務"""
    overdue = tm.check_overdue_tasks()
    if overdue:
        msg = f"⚠️ 有 {len(overdue)} 個任務已逾期，請盡快處理！"
        send_message(msg)

# 啟動定時任務線程
threading.Thread(target=scheduled_tasks, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 6. 配置文件 (data/config.json)

```json
{
  "wechat": {
    "corp_id": "YOUR_CORP_ID",
    "agent_id": "YOUR_AGENT_ID",
    "secret": "YOUR_SECRET"
  },
  "samba": {
    "host": "192.168.0.20",
    "share": "tricycle-data",
    "username": "tricycle",
    "password": "YOUR_PASSWORD"
  },
  "schedule": {
    "daily_report_times": ["08:00", "18:00"],
    "check_overdue_interval": 60
  }
}
```

---

## 7. 依賴文件 (requirements.txt)

```
fastapi==0.104.1
uvicorn==0.24.0
openpyxl==3.1.2
pandas==2.1.3
watchdog==3.0.0
requests==2.31.0
schedule==1.2.0
```
