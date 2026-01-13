import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QGroupBox
from PySide6.QtCore import QTimer

from stock_api import StockAPI
from account import Account
from ui_components import (
    StockSearchWidget, PriceDisplayWidget, TradingWidget,
    AccountInfoWidget, HoldingsTableWidget, HistoryTableWidget
)
from styles import MAIN_STYLESHEET


class TradingApp(QMainWindow):
    """主交易應用程式"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("投資先生 - 台股即時交易系統")
        self.setGeometry(100, 100, 1300, 850)
        
        # 資料初始化
        self.account = Account()
        self.current_stock_code = "2330"  # 預設台積電
        self.current_price_data = None
        
        # UI 設定
        self.setup_ui()
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # 啟動價格更新
        self.update_price()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_price)
        self.timer.start(5000)  # 每5秒更新一次
    
    def setup_ui(self):
        """設置UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 左側面板：股票資訊和交易
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # 右側面板：帳戶、持倉和記錄
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self):
        """創建左側面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 股票搜尋
        self.search_widget = StockSearchWidget(self.search_stock)
        layout.addWidget(self.search_widget)
        
        # 股價顯示
        self.price_widget = PriceDisplayWidget()
        layout.addWidget(self.price_widget)
        
        # 交易組件
        self.trading_widget = TradingWidget(self.buy_stock, self.sell_stock)
        layout.addWidget(self.trading_widget)
        
        layout.addStretch()
        return panel
    
    def create_right_panel(self):
        """創建右側面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 帳戶資訊
        self.account_widget = AccountInfoWidget()
        layout.addWidget(self.account_widget)
        
        # 持倉列表
        holdings_group = QWidget()
        holdings_layout = QVBoxLayout(holdings_group)
        holdings_layout.setContentsMargins(0, 0, 0, 0)
        holdings_title = QGroupBox("持倉明細")
        holdings_title_layout = QVBoxLayout()
        self.holdings_table = HoldingsTableWidget()
        holdings_title_layout.addWidget(self.holdings_table)
        holdings_title.setLayout(holdings_title_layout)
        holdings_layout.addWidget(holdings_title)
        layout.addWidget(holdings_group)
        
        # 交易記錄
        history_group = QWidget()
        history_layout = QVBoxLayout(history_group)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_title = QGroupBox("交易記錄")
        history_title_layout = QVBoxLayout()
        self.history_table = HistoryTableWidget()
        history_title_layout.addWidget(self.history_table)
        history_title.setLayout(history_title_layout)
        history_layout.addWidget(history_title)
        layout.addWidget(history_group)
        
        return panel
    
    def search_stock(self):
        """查詢股票"""
        stock_code = self.search_widget.get_stock_code()
        if stock_code:
            self.current_stock_code = stock_code
            self.update_price()
    
    def update_price(self):
        """更新股價"""
        if not self.current_stock_code:
            return
        
        data = StockAPI.get_realtime_price(self.current_stock_code)
        if data:
            self.current_price_data = data
            stock_name = StockAPI.get_stock_name(self.current_stock_code)
            self.price_widget.update_price(
                f"{stock_name} ({self.current_stock_code})",
                data
            )
            self.update_account_display()
    
    def buy_stock(self):
        """買進股票"""
        if not self.current_price_data:
            QMessageBox.warning(self, "錯誤", "無法獲取當前股價")
            return
        
        qty = self.trading_widget.get_buy_qty()
        price = self.current_price_data['price']
        
        if self.account.buy(self.current_stock_code, price, qty):
            QMessageBox.information(
                self, "成功",
                f"買進 {qty} 股 {self.current_stock_code} 成功\n"
                f"價格: {price:,.2f}\n"
                f"金額: {price * qty * 1.001425:,.0f}"
            )
            self.update_display()
        else:
            QMessageBox.warning(self, "錯誤", "現金不足")
    
    def sell_stock(self):
        """賣出股票"""
        if not self.current_price_data:
            QMessageBox.warning(self, "錯誤", "無法獲取當前股價")
            return
        
        qty = self.trading_widget.get_sell_qty()
        price = self.current_price_data['price']
        
        if self.account.sell(self.current_stock_code, price, qty):
            QMessageBox.information(
                self, "成功",
                f"賣出 {qty} 股 {self.current_stock_code} 成功\n"
                f"價格: {price:,.2f}\n"
                f"金額: {price * qty * 0.995575:,.0f}"
            )
            self.update_display()
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
        self.account_widget.update_info(self.account.cash, total_asset)
    
    def update_display(self):
        """更新所有顯示"""
        self.update_account_display()
        self.update_holdings_table()
        self.update_history_table()
    
    def update_holdings_table(self):
        """更新持倉表格"""
        holdings_data = []
        stock_prices = {}
        
        if self.current_stock_code and self.current_price_data:
            stock_prices[self.current_stock_code] = self.current_price_data['price']
        
        for stock_code, shares in self.account.holdings.items():
            if stock_code == self.current_stock_code and self.current_price_data:
                price = self.current_price_data['price']
            else:
                if stock_code not in stock_prices:
                    data = StockAPI.get_realtime_price(stock_code)
                    price = data['price'] if data else 0
                    if data:
                        stock_prices[stock_code] = price
                else:
                    price = stock_prices[stock_code]
            
            stock_name = StockAPI.get_stock_name(stock_code)
            value = price * shares
            holdings_data.append((f"{stock_name} ({stock_code})", shares, price, value))
        
        self.holdings_table.update_data(holdings_data)
    
    def update_history_table(self):
        """更新交易記錄表格"""
        self.history_table.update_data(self.account.trade_history)


# ===== 程式入口 =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingApp()
    window.show()
    sys.exit(app.exec())
