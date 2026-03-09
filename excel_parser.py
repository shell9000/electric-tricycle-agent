def parse_excel_to_database(file_content, filename):
    """解析 Excel 並存入數據庫"""
    try:
        import openpyxl
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
                
                # 區域
                if any(k in key_lower for k in ['区域', '地区', 'region', '省']):
                    data_item['region'] = str(value) if value else ''
                
                # 客戶
                elif any(k in key_lower for k in ['客户', '客戶', 'customer', '姓名', '名称']):
                    data_item['customer'] = str(value) if value else ''
                
                # 產品
                elif any(k in key_lower for k in ['产品', '產品', 'product', '型号', '型號']):
                    data_item['product'] = str(value) if value else ''
                
                # 數量
                elif any(k in key_lower for k in ['数量', '數量', 'quantity', '台数', '台數']):
                    try:
                        data_item['quantity'] = int(float(value)) if value else 0
                    except:
                        data_item['quantity'] = 0
                
                # 金額
                elif any(k in key_lower for k in ['金额', '金額', 'amount', '价格', '價格']):
                    try:
                        data_item['amount'] = float(value) if value else 0.0
                    except:
                        data_item['amount'] = 0.0
                
                # 日期
                elif any(k in key_lower for k in ['日期', 'date', '时间', '時間']):
                    data_item['date'] = str(value) if value else ''
            
            data_list.append(data_item)
        
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
            result += f"{i}. {c['customer']} ({c['region']})：{c['total_quantity']} 台\n"
        
        result += f"\n✅ 現在可以在企業微信查詢真實數據！"
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ 數據導入失敗：{str(e)}"
