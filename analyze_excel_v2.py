def analyze_excel_v2(file_content, filename):
    """分析 Excel 文件並存入數據庫（優化版）"""
    try:
        import openpyxl
        from io import BytesIO
        from database import SalesDatabase
        
        # 讀取 Excel
        wb = openpyxl.load_workbook(BytesIO(file_content))
        sheet = wb.active
        
        # 初始化數據庫
        db = SalesDatabase()
        
        # 解析數據
        data_list = []
        headers = []
        
        for i, row in enumerate(sheet.iter_rows(values_only=True), 1):
            if i == 1:
                # 第一行作為表頭
                headers = [str(cell).strip() if cell else f'col_{j}' for j, cell in enumerate(row)]
                print(f"表頭: {headers}")
                continue
            
            # 跳過空行
            if not any(row):
                continue
            
            # 構建數據字典
            row_data = {}
            for j, cell in enumerate(row):
                if j < len(headers):
                    row_data[headers[j]] = cell
            
            # 智能識別字段
            data_item = {
                'region': '',
                'customer': '',
                'product': '',
                'quantity': 0,
                'amount': 0.0,
                'date': ''
            }
            
            # 嘗試匹配字段
            for key, value in row_data.items():
                key_lower = key.lower()
                
                # 區域：市级、区域、地区、省
                if '市级' in key or '市級' in key or '区域' in key_lower or '地区' in key_lower or 'region' in key_lower or '省' in key_lower or '城市' in key_lower:
                    data_item['region'] = str(value) if value else ''
                
                # 客戶：名称、客户、姓名
                elif '名称' in key or '名稱' in key or '客户' in key or '客戶' in key or 'customer' in key_lower or '姓名' in key or '商家' in key:
                    data_item['customer'] = str(value) if value else ''
                
                # 產品
                elif '产品' in key or '產品' in key or 'product' in key_lower or '型号' in key or '型號' in key:
                    data_item['product'] = str(value) if value else ''
                
                # 數量：销量、数量、台数
                elif '销量' in key or '銷量' in key or '数量' in key or '數量' in key or 'quantity' in key_lower or '台数' in key or '台數' in key or '汇总' in key or '匯總' in key:
                    try:
                        data_item['quantity'] = int(float(value)) if value else 0
                    except:
                        data_item['quantity'] = 0
                
                # 金額
                elif '金额' in key or '金額' in key or 'amount' in key_lower or '价格' in key or '價格' in key:
                    try:
                        data_item['amount'] = float(value) if value else 0.0
                    except:
                        data_item['amount'] = 0.0
                
                # 日期
                elif '日期' in key or 'date' in key_lower or '时间' in key or '時間' in key:
                    data_item['date'] = str(value) if value else ''
            
            data_list.append(data_item)
            print(f"行{i}: 區域={data_item['region']}, 客戶={data_item['customer'][:20]}, 數量={data_item['quantity']}")
        
        # 清空舊數據並插入新數據
        db.clear_all()
        db.insert_sales_data(data_list)
        
        # 生成統計報告
        region_summary = db.get_region_summary()
        top_customers = db.get_top_customers(5)
        
        result = f"📊 Excel 數據已導入數據庫\n\n"
        result += f"文件名：{filename}\n"
        result += f"總記錄數：{len(data_list)} 條\n\n"
        
        result += f"【區域統計】\n"
        for r in region_summary[:5]:
            result += f"• {r['region']}：{r['total_quantity']} 台\n"
        
        result += f"\n【TOP 5 客戶】\n"
        for i, c in enumerate(top_customers, 1):
            result += f"{i}. {c['customer'][:30]} ({c['region']})：{c['total_quantity']} 台\n"
        
        result += f"\n✅ 現在可以在企業微信查詢真實數據！"
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ 數據導入失敗：{str(e)}"
