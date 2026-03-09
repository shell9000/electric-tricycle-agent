import sqlite3
import os
from datetime import datetime

class SalesDatabase:
    def __init__(self, db_path="/opt/tricycle-agent/data/sales.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 創建銷售數據表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT,
                customer TEXT,
                product TEXT,
                quantity INTEGER,
                amount REAL,
                date TEXT,
                upload_time TEXT,
                raw_data TEXT
            )
        ''')
        
        # 創建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_region ON sales(region)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer ON sales(customer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON sales(date)')
        
        conn.commit()
        conn.close()
    
    def clear_all(self):
        """清空所有數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sales')
        conn.commit()
        conn.close()
    
    def insert_sales_data(self, data_list):
        """批量插入銷售數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        upload_time = datetime.now().isoformat()
        
        for data in data_list:
            cursor.execute('''
                INSERT INTO sales (region, customer, product, quantity, amount, date, upload_time, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('region', ''),
                data.get('customer', ''),
                data.get('product', ''),
                data.get('quantity', 0),
                data.get('amount', 0.0),
                data.get('date', ''),
                upload_time,
                str(data)
            ))
        
        conn.commit()
        conn.close()
    
    def query_by_region(self, region):
        """按區域查詢"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as count,
                SUM(quantity) as total_quantity,
                SUM(amount) as total_amount
            FROM sales
            WHERE region LIKE ?
        ''', (f'%{region}%',))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'count': result[0] or 0,
            'total_quantity': result[1] or 0,
            'total_amount': result[2] or 0.0
        }
    
    def query_by_customer(self, customer):
        """按客戶查詢"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                region,
                customer,
                SUM(quantity) as total_quantity,
                SUM(amount) as total_amount,
                COUNT(*) as order_count
            FROM sales
            WHERE customer LIKE ?
            GROUP BY region, customer
        ''', (f'%{customer}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'region': r[0],
            'customer': r[1],
            'total_quantity': r[2],
            'total_amount': r[3],
            'order_count': r[4]
        } for r in results]
    
    def get_top_customers(self, limit=10):
        """獲取 TOP 客戶"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                customer,
                region,
                SUM(quantity) as total_quantity,
                SUM(amount) as total_amount
            FROM sales
            GROUP BY customer, region
            ORDER BY total_quantity DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'customer': r[0],
            'region': r[1],
            'total_quantity': r[2],
            'total_amount': r[3]
        } for r in results]
    
    def get_region_summary(self):
        """獲取區域匯總"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                region,
                COUNT(*) as order_count,
                SUM(quantity) as total_quantity,
                SUM(amount) as total_amount
            FROM sales
            GROUP BY region
            ORDER BY total_quantity DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'region': r[0],
            'order_count': r[1],
            'total_quantity': r[2],
            'total_amount': r[3]
        } for r in results]
    
    def search(self, keyword):
        """智能搜尋"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                region,
                customer,
                product,
                SUM(quantity) as total_quantity,
                SUM(amount) as total_amount
            FROM sales
            WHERE region LIKE ? OR customer LIKE ? OR product LIKE ?
            GROUP BY region, customer, product
            ORDER BY total_quantity DESC
            LIMIT 20
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'region': r[0],
            'customer': r[1],
            'product': r[2],
            'total_quantity': r[3],
            'total_amount': r[4]
        } for r in results]
