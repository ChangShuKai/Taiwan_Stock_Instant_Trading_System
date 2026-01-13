import sys
import json
import requests
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QSpinBox, QMessageBox, QTabWidget, QGroupBox,
    QHeaderView, QFrame, QScrollArea
)
from PySide6.QtCore import QTimer, Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette


# ===== 股價資料 API =====
class StockAPI:
    """台灣證券交易所 API 整合"""
    
    @staticmethod
    def get_realtime_price(stock_code):
        """
        獲取即時股價（使用 taiwanstock.online API）
        備用方案：使用 TWSE API
        """
        try:
            # 方法1：使用 taiwanstock.online API（免費即時報價）
            url = f"https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=1m&mkt=10&sym={stock_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'ta' in data and len(data['ta']) > 0:
                    latest = data['ta'][-1]
                    return {
                        'price': float(latest.get('c', 0)),
                        'change': float(latest.get('c', 0)) - float(latest.get('o', 0)),
                        'change_percent': ((float(latest.get('c', 0)) - float(latest.get('o', 0))) / float(latest.get('o', 1))) * 100,
                        'volume': int(latest.get('v', 0)),
                        'high': float(latest.get('h', 0)),
                        'low': float(latest.get('l', 0)),
                        'open': float(latest.get('o', 0))
                    }
        except Exception as e:
            print(f"API錯誤: {e}")
        
        # 方法2：備用方案 - 使用 TWSE API（收盤價）
        try:
            today = datetime.now().strftime("%Y%m%d")
            url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY"
            params = {
                'response': 'json',
                'date': today,
                'stockNo': stock_code
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    latest = data['data'][-1]
                    price = float(latest[6].replace(',', ''))
                    open_price = float(latest[3].replace(',', ''))
                    high = float(latest[4].replace(',', ''))
                    low = float(latest[5].replace(',', ''))
                    volume = int(latest[1].replace(',', ''))
                    change = price - open_price
                    change_percent = (change / open_price * 100) if open_price > 0 else 0
                    
                    return {
                        'price': price,
                        'change': change,
                        'change_percent': change_percent,
                        'volume': volume,
                        'high': high,
                        'low': low,
                        'open': open_price
                    }
        except Exception as e:
            print(f"TWSE API錯誤: {e}")
        
        return None
    
    @staticmethod
    def get_stock_name(stock_code):
        """獲取股票名稱"""
        try:
            url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for item in data['data']:
                        if item[0] == stock_code:
                            return item[1]
        except:
            pass
        return stock_code


# ===== 帳戶系統 =====
class Account:
    def __init__(self):
        self.cash = 1_000_000  # 初始資金 100萬
        self.holdings = {}  # {stock_code: shares}
        self.trade_history = []  # 交易記錄
    
    def buy(self, stock_code, price, qty):
        """買入股票"""
        fee = 0.001425  # 手續費 0.1425%
        cost = price * qty * (1 + fee)
        
        if self.cash >= cost:
            self.cash -= cost
            if stock_code not in self.holdings:
                self.holdings[stock_code] = 0
            self.holdings[stock_code] += qty
            
            self.trade_history.append({
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'type': '買進',
                'stock_code': stock_code,
                'price': price,
                'qty': qty,
                'amount': cost
            })
            return True
        return False
    
    def sell(self, stock_code, price, qty):
        """賣出股票"""
        if stock_code in self.holdings and self.holdings[stock_code] >= qty:
            fee = 0.001425  # 手續費
            tax = 0.003  # 證交稅 0.3%
            revenue = price * qty * (1 - fee - tax)
            
            self.cash += revenue
            self.holdings[stock_code] -= qty
            if self.holdings[stock_code] == 0:
                del self.holdings[stock_code]
            
            self.trade_history.append({
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'type': '賣出',
                'stock_code': stock_code,
                'price': price,
                'qty': qty,
                'amount': revenue
            })
            return True
        return False
    
    def get_total_asset(self, stock_prices):
        """計算總資產"""
        total = self.cash
        for stock_code, shares in self.holdings.items():
            if stock_code in stock_prices:
                total += stock_prices[stock_code] * shares
        return total


# ===== 價格更新執行緒 =====
class PriceUpdateThread(QThread):
    price_updated = Signal(str, dict)  # stock_code, price_data
    
    def __init__(self, stock_code):
        super().__init__()
        self.stock_code = stock_code
        self.running = True
    
    def run(self):
        while self.running:
            data = StockAPI.get_realtime_price(self.stock_code)
            if data:
                self.price_updated.emit(self.stock_code, data)
            self.msleep(3000)  # 每3秒更新一次
    
    def stop(self):
        self.running = False


# ===== 主視窗 =====
class TradingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("投資先生 - 台股即時交易系統")
        self.setGeometry(100, 100, 1200, 800)
        
        # 資料
        self.account = Account()
        self.current_stock_code = "2330"  # 預設台積電
        self.current_price_data = None
        self.price_thread = None
        
        # UI 設定
        self.setup_ui()
        self.setup_styles()
        
        # 啟動價格更新
        self.update_price()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_price)
        self.timer.start(5000)  # 每5秒更新一次
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左側：股票資訊和交易
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # 右側：持倉和記錄
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 股票選擇
        stock_group = QGroupBox("股票查詢")
        stock_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.stock_input = QLineEdit("2330")
        self.stock_input.setPlaceholderText("輸入股票代碼（如：2330）")
        search_btn = QPushButton("查詢")
        search_btn.clicked.connect(self.search_stock)
        search_layout.addWidget(QLabel("股票代碼:"))
        search_layout.addWidget(self.stock_input)
        search_layout.addWidget(search_btn)
        stock_layout.addLayout(search_layout)
        stock_group.setLayout(stock_layout)
        layout.addWidget(stock_group)
        
        # 股價資訊
        price_group = QGroupBox("即時行情")
        price_layout = QVBoxLayout()
        
        self.stock_name_label = QLabel("台積電 (2330)")
        self.stock_name_label.setFont(QFont("Arial", 16, QFont.Bold))
        price_layout.addWidget(self.stock_name_label)
        
        self.price_label = QLabel("價格: --")
        self.price_label.setFont(QFont("Arial", 24, QFont.Bold))
        price_layout.addWidget(self.price_label)
        
        self.change_label = QLabel("漲跌: --")
        self.change_label.setFont(QFont("Arial", 14))
        price_layout.addWidget(self.change_label)
        
        info_layout = QHBoxLayout()
        self.open_label = QLabel("開盤: --")
        self.high_label = QLabel("最高: --")
        self.low_label = QLabel("最低: --")
        self.volume_label = QLabel("成交量: --")
        info_layout.addWidget(self.open_label)
        info_layout.addWidget(self.high_label)
        info_layout.addWidget(self.low_label)
        info_layout.addWidget(self.volume_label)
        price_layout.addLayout(info_layout)
        
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        # 交易區域
        trade_group = QGroupBox("下單交易")
        trade_layout = QVBoxLayout()
        
        # 買進
        buy_group = QGroupBox("買進")
        buy_layout = QVBoxLayout()
        buy_qty_layout = QHBoxLayout()
        buy_qty_layout.addWidget(QLabel("數量:"))
        self.buy_qty = QSpinBox()
        self.buy_qty.setMinimum(1)
        self.buy_qty.setMaximum(10000)
        self.buy_qty.setValue(1000)
        buy_qty_layout.addWidget(self.buy_qty)
        buy_btn = QPushButton("買進")
        buy_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        buy_btn.clicked.connect(self.buy_stock)
        buy_layout.addLayout(buy_qty_layout)
        buy_layout.addWidget(buy_btn)
        buy_group.setLayout(buy_layout)
        trade_layout.addWidget(buy_group)
        
        # 賣出
        sell_group = QGroupBox("賣出")
        sell_layout = QVBoxLayout()
        sell_qty_layout = QHBoxLayout()
        sell_qty_layout.addWidget(QLabel("數量:"))
        self.sell_qty = QSpinBox()
        self.sell_qty.setMinimum(1)
        self.sell_qty.setMaximum(10000)
        self.sell_qty.setValue(1000)
        sell_qty_layout.addWidget(self.sell_qty)
        sell_btn = QPushButton("賣出")
        sell_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        sell_btn.clicked.connect(self.sell_stock)
        sell_layout.addLayout(sell_qty_layout)
        sell_layout.addWidget(sell_btn)
        sell_group.setLayout(sell_layout)
        trade_layout.addWidget(sell_group)
        
        trade_group.setLayout(trade_layout)
        layout.addWidget(trade_group)
        
        layout.addStretch()
        return panel
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 帳戶資訊
        account_group = QGroupBox("帳戶資訊")
        account_layout = QVBoxLayout()
        self.cash_label = QLabel("現金: 1,000,000")
        self.asset_label = QLabel("總資產: 1,000,000")
        self.asset_label.setFont(QFont("Arial", 12, QFont.Bold))
        account_layout.addWidget(self.cash_label)
        account_layout.addWidget(self.asset_label)
        account_group.setLayout(account_layout)
        layout.addWidget(account_group)
        
        # 持倉列表
        holdings_group = QGroupBox("持倉明細")
        holdings_layout = QVBoxLayout()
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(4)
        self.holdings_table.setHorizontalHeaderLabels(["股票", "股數", "現價", "市值"])
        self.holdings_table.horizontalHeader().setStretchLastSection(True)
        self.holdings_table.setMaximumHeight(200)
        holdings_layout.addWidget(self.holdings_table)
        holdings_group.setLayout(holdings_layout)
        layout.addWidget(holdings_group)
        
        # 交易記錄
        history_group = QGroupBox("交易記錄")
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["時間", "類型", "股票", "價格", "數量", "金額"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        return panel
    
    def setup_styles(self):
        """設定樣式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QLineEdit, QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
    
    def search_stock(self):
        """查詢股票"""
        stock_code = self.stock_input.text().strip()
        if stock_code:
            self.current_stock_code = stock_code
            stock_name = StockAPI.get_stock_name(stock_code)
            self.stock_name_label.setText(f"{stock_name} ({stock_code})")
            self.update_price()
    
    def update_price(self):
        """更新股價"""
        if not self.current_stock_code:
            return
        
        data = StockAPI.get_realtime_price(self.current_stock_code)
        if data:
            self.current_price_data = data
            price = data['price']
            change = data['change']
            change_percent = data['change_percent']
            
            # 更新價格顯示
            self.price_label.setText(f"價格: {price:,.2f}")
            
            # 更新漲跌（顏色）
            if change > 0:
                color = "#e74c3c"  # 紅色（漲）
                prefix = "+"
            elif change < 0:
                color = "#27ae60"  # 綠色（跌）
                prefix = ""
            else:
                color = "#34495e"  # 灰色
                prefix = ""
            
            self.change_label.setText(f"漲跌: {prefix}{change:,.2f} ({prefix}{change_percent:.2f}%)")
            self.change_label.setStyleSheet(f"color: {color};")
            self.price_label.setStyleSheet(f"color: {color};")
            
            # 更新其他資訊
            self.open_label.setText(f"開盤: {data['open']:,.2f}")
            self.high_label.setText(f"最高: {data['high']:,.2f}")
            self.low_label.setText(f"最低: {data['low']:,.2f}")
            self.volume_label.setText(f"成交量: {data['volume']:,}")
            
            # 更新帳戶資訊
            self.update_account_display()
    
    def buy_stock(self):
        """買進股票"""
        if not self.current_price_data:
            QMessageBox.warning(self, "錯誤", "無法獲取當前股價")
            return
        
        qty = self.buy_qty.value()
        price = self.current_price_data['price']
        
        if self.account.buy(self.current_stock_code, price, qty):
            QMessageBox.information(self, "成功", f"買進 {qty} 股 {self.current_stock_code} 成功")
            self.update_account_display()
            self.update_holdings_table()
            self.update_history_table()
        else:
            QMessageBox.warning(self, "錯誤", "現金不足")
    
    def sell_stock(self):
        """賣出股票"""
        if not self.current_price_data:
            QMessageBox.warning(self, "錯誤", "無法獲取當前股價")
            return
        
        qty = self.sell_qty.value()
        price = self.current_price_data['price']
        
        if self.account.sell(self.current_stock_code, price, qty):
            QMessageBox.information(self, "成功", f"賣出 {qty} 股 {self.current_stock_code} 成功")
            self.update_account_display()
            self.update_holdings_table()
            self.update_history_table()
        else:
            QMessageBox.warning(self, "錯誤", "持股不足")
    
    def update_account_display(self):
        """更新帳戶顯示"""
        stock_prices = {}
        if self.current_stock_code and self.current_price_data:
            stock_prices[self.current_stock_code] = self.current_price_data['price']
        
        # 獲取所有持倉的價格
        for stock_code in self.account.holdings.keys():
            if stock_code not in stock_prices:
                data = StockAPI.get_realtime_price(stock_code)
                if data:
                    stock_prices[stock_code] = data['price']
        
        total_asset = self.account.get_total_asset(stock_prices)
        self.cash_label.setText(f"現金: {self.account.cash:,.0f}")
        self.asset_label.setText(f"總資產: {total_asset:,.0f}")
    
    def update_holdings_table(self):
        """更新持倉表格"""
        self.holdings_table.setRowCount(len(self.account.holdings))
        
        row = 0
        stock_prices = {}
        for stock_code, shares in self.account.holdings.items():
            # 獲取價格
            if stock_code == self.current_stock_code and self.current_price_data:
                price = self.current_price_data['price']
            else:
                data = StockAPI.get_realtime_price(stock_code)
                price = data['price'] if data else 0
            
            stock_prices[stock_code] = price
            stock_name = StockAPI.get_stock_name(stock_code)
            
            self.holdings_table.setItem(row, 0, QTableWidgetItem(f"{stock_name} ({stock_code})"))
            self.holdings_table.setItem(row, 1, QTableWidgetItem(str(shares)))
            self.holdings_table.setItem(row, 2, QTableWidgetItem(f"{price:,.2f}"))
            self.holdings_table.setItem(row, 3, QTableWidgetItem(f"{price * shares:,.0f}"))
            
            row += 1
    
    def update_history_table(self):
        """更新交易記錄表格"""
        self.history_table.setRowCount(len(self.account.trade_history))
        
        for row, trade in enumerate(reversed(self.account.trade_history)):
            self.history_table.setItem(row, 0, QTableWidgetItem(trade['time']))
            self.history_table.setItem(row, 1, QTableWidgetItem(trade['type']))
            self.history_table.setItem(row, 2, QTableWidgetItem(trade['stock_code']))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{trade['price']:,.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(trade['qty'])))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{trade['amount']:,.0f}"))
            
            # 設置顏色
            if trade['type'] == '買進':
                self.history_table.item(row, 1).setForeground(QColor("#e74c3c"))
            else:
                self.history_table.item(row, 1).setForeground(QColor("#27ae60"))


# ===== 程式入口 =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingApp()
    window.show()
    sys.exit(app.exec())
