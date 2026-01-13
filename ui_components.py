"""
UI 組件模組
創建可重用的UI組件
"""
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLineEdit, QSpinBox,
    QGroupBox, QMessageBox
)
from PySide6.QtGui import QFont, QColor
from styles import (
    BUY_BUTTON_STYLE, SELL_BUTTON_STYLE, SEARCH_BUTTON_STYLE,
    PRICE_UP_STYLE, PRICE_DOWN_STYLE, PRICE_FLAT_STYLE
)


class StockSearchWidget(QWidget):
    """股票搜尋組件"""
    
    def __init__(self, on_search_callback):
        super().__init__()
        self.on_search_callback = on_search_callback
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("股票查詢")
        group_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("股票代碼:"))
        
        self.stock_input = QLineEdit("2330")
        self.stock_input.setPlaceholderText("輸入股票代碼（如：2330）")
        self.stock_input.returnPressed.connect(self.on_search_callback)
        search_layout.addWidget(self.stock_input)
        
        search_btn = QPushButton("查詢")
        search_btn.setStyleSheet(SEARCH_BUTTON_STYLE)
        search_btn.clicked.connect(self.on_search_callback)
        search_layout.addWidget(search_btn)
        
        group_layout.addLayout(search_layout)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def get_stock_code(self):
        """獲取輸入的股票代碼"""
        return self.stock_input.text().strip()


class PriceDisplayWidget(QWidget):
    """股價顯示組件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("即時行情")
        price_layout = QVBoxLayout()
        price_layout.setSpacing(10)
        
        # 股票名稱
        self.stock_name_label = QLabel("台積電 (2330)")
        self.stock_name_label.setFont(QFont("Microsoft JhengHei", 16, QFont.Bold))
        self.stock_name_label.setStyleSheet("color: #212529; padding: 5px;")
        price_layout.addWidget(self.stock_name_label)
        
        # 價格（大號字體）
        self.price_label = QLabel("價格: --")
        self.price_label.setFont(QFont("Microsoft JhengHei", 28, QFont.Bold))
        self.price_label.setStyleSheet("padding: 10px 0;")
        price_layout.addWidget(self.price_label)
        
        # 漲跌資訊
        self.change_label = QLabel("漲跌: --")
        self.change_label.setFont(QFont("Microsoft JhengHei", 14))
        price_layout.addWidget(self.change_label)
        
        # 市場資訊（開盤、最高、最低、成交量）
        info_layout = QHBoxLayout()
        self.open_label = QLabel("開盤: --")
        self.high_label = QLabel("最高: --")
        self.low_label = QLabel("最低: --")
        self.volume_label = QLabel("成交量: --")
        
        for label in [self.open_label, self.high_label, self.low_label, self.volume_label]:
            label.setFont(QFont("Microsoft JhengHei", 11))
            label.setStyleSheet("color: #6c757d; padding: 5px;")
            info_layout.addWidget(label)
        
        price_layout.addLayout(info_layout)
        group.setLayout(price_layout)
        layout.addWidget(group)
    
    def update_price(self, stock_name, price_data):
        """更新價格顯示"""
        self.stock_name_label.setText(stock_name)
        
        price = price_data['price']
        change = price_data['change']
        change_percent = price_data['change_percent']
        
        # 更新價格
        self.price_label.setText(f"${price:,.2f}")
        
        # 更新漲跌（根據漲跌設置顏色和樣式）
        if change > 0:
            color_style = PRICE_UP_STYLE
            prefix = "+"
        elif change < 0:
            color_style = PRICE_DOWN_STYLE
            prefix = ""
        else:
            color_style = PRICE_FLAT_STYLE
            prefix = ""
        
        self.change_label.setText(
            f"漲跌: {prefix}{change:,.2f} ({prefix}{change_percent:.2f}%)"
        )
        self.change_label.setStyleSheet(color_style)
        self.price_label.setStyleSheet(color_style)
        
        # 更新其他資訊
        self.open_label.setText(f"開盤: {price_data['open']:,.2f}")
        self.high_label.setText(f"最高: {price_data['high']:,.2f}")
        self.low_label.setText(f"最低: {price_data['low']:,.2f}")
        self.volume_label.setText(f"成交量: {price_data['volume']:,}")


class TradingWidget(QWidget):
    """交易組件"""
    
    def __init__(self, on_buy_callback, on_sell_callback):
        super().__init__()
        self.on_buy_callback = on_buy_callback
        self.on_sell_callback = on_sell_callback
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("下單交易")
        trade_layout = QVBoxLayout()
        trade_layout.setSpacing(15)
        
        # 買進區域
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
        buy_btn.setStyleSheet(BUY_BUTTON_STYLE)
        buy_btn.clicked.connect(self.on_buy_callback)
        
        buy_layout.addLayout(buy_qty_layout)
        buy_layout.addWidget(buy_btn)
        buy_group.setLayout(buy_layout)
        trade_layout.addWidget(buy_group)
        
        # 賣出區域
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
        sell_btn.setStyleSheet(SELL_BUTTON_STYLE)
        sell_btn.clicked.connect(self.on_sell_callback)
        
        sell_layout.addLayout(sell_qty_layout)
        sell_layout.addWidget(sell_btn)
        sell_group.setLayout(sell_layout)
        trade_layout.addWidget(sell_group)
        
        group.setLayout(trade_layout)
        layout.addWidget(group)
    
    def get_buy_qty(self):
        """獲取買進數量"""
        return self.buy_qty.value()
    
    def get_sell_qty(self):
        """獲取賣出數量"""
        return self.sell_qty.value()


class AccountInfoWidget(QWidget):
    """帳戶資訊組件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("帳戶資訊")
        account_layout = QVBoxLayout()
        account_layout.setSpacing(10)
        
        self.cash_label = QLabel("現金: 1,000,000")
        self.cash_label.setFont(QFont("Microsoft JhengHei", 12))
        
        self.asset_label = QLabel("總資產: 1,000,000")
        self.asset_label.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        self.asset_label.setStyleSheet("color: #1971c2; padding: 5px;")
        
        account_layout.addWidget(self.cash_label)
        account_layout.addWidget(self.asset_label)
        group.setLayout(account_layout)
        layout.addWidget(group)
    
    def update_info(self, cash, total_asset):
        """更新帳戶資訊"""
        self.cash_label.setText(f"現金: {cash:,.0f}")
        self.asset_label.setText(f"總資產: {total_asset:,.0f}")


class HoldingsTableWidget(QTableWidget):
    """持倉表格組件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["股票", "股數", "現價", "市值"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setMaximumHeight(250)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
    
    def update_data(self, holdings_data):
        """更新持倉數據"""
        self.setRowCount(len(holdings_data))
        
        for row, (stock_name, shares, price, value) in enumerate(holdings_data):
            self.setItem(row, 0, QTableWidgetItem(stock_name))
            self.setItem(row, 1, QTableWidgetItem(str(shares)))
            self.setItem(row, 2, QTableWidgetItem(f"{price:,.2f}"))
            self.setItem(row, 3, QTableWidgetItem(f"{value:,.0f}"))


class HistoryTableWidget(QTableWidget):
    """交易記錄表格組件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["時間", "類型", "股票", "價格", "數量", "金額"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
    
    def update_data(self, history_data):
        """更新交易記錄數據"""
        self.setRowCount(len(history_data))
        
        for row, trade in enumerate(reversed(history_data)):
            self.setItem(row, 0, QTableWidgetItem(trade['time']))
            
            type_item = QTableWidgetItem(trade['type'])
            # 設置顏色
            if trade['type'] == '買進':
                type_item.setForeground(QColor("#e63946"))
            else:
                type_item.setForeground(QColor("#2b8a3e"))
            self.setItem(row, 1, type_item)
            
            self.setItem(row, 2, QTableWidgetItem(trade['stock_code']))
            self.setItem(row, 3, QTableWidgetItem(f"{trade['price']:,.2f}"))
            self.setItem(row, 4, QTableWidgetItem(str(trade['qty'])))
            self.setItem(row, 5, QTableWidgetItem(f"{trade['amount']:,.0f}"))
