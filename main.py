import sys
import os
import csv
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QGroupBox, QLabel
from PySide6.QtCore import QTimer, Qt

from stock_api import StockAPI
from account import Account
from ui_components import (
    StockSearchWidget, PriceDisplayWidget, TradingWidget,
    AccountInfoWidget, HoldingsTableWidget, HistoryTableWidget,
    HoldingsPieChartWidget
)
from styles import MAIN_STYLESHEET


class TradingApp(QMainWindow):
    """主交易應用程式"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("台股即時交易系統")
        self.setGeometry(100, 100, 1300, 850)
        
        # 資料初始化
        self.account = Account()
        self.last_log_date = None  # 用於每日記錄
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
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # 外層：垂直排列（主內容 + 底部版權列）
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setSpacing(8)
        outer_layout.setContentsMargins(18, 18, 18, 18)

        # 主內容：左右分欄
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # 左側面板：股票資訊和交易
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)

        # 右側面板：帳戶、持倉和記錄
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

        outer_layout.addLayout(main_layout)

        # 底部版權文字
        footer_label = QLabel(
            "Copyright © 2025 Six Star Cultur. All rights reserved."
        )
        footer_label.setStyleSheet(
            "color: #adb5bd; font-size: 11px; padding-top: 4px;"
        )
        footer_label.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(footer_label)
    
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

        # 台股持倉比例圓餅圖
        self.pie_widget = HoldingsPieChartWidget()
        layout.addWidget(self.pie_widget)
        
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

        # 每日紀錄一次總資產與盈虧
        self.log_daily_performance(total_asset, stock_prices)
    
    def update_display(self):
        """更新所有顯示"""
        self.update_account_display()
        self.update_holdings_table()
        self.update_history_table()
    
    def update_holdings_table(self):
        """更新持倉表格"""
        holdings_data = []
        pie_data = []  # 台股持倉用於圓餅圖
        stock_prices = {}
        total_value_tw = 0
        
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

            # 股票資訊欄位：台股 / 美股 + （稍後補上比例文字）
            is_tw = stock_code.isdigit()
            market_label = "台股" if is_tw else "美股"

            holdings_data.append(
                (f"{stock_name} ({stock_code})", shares, price, value, market_label)
            )

            # 台股才納入圓餅圖
            if is_tw:
                total_value_tw += value
                pie_data.append((f"{stock_name} ({stock_code})", value))
        
        self.holdings_table.update_data(holdings_data)

        # 更新圓餅圖（只顯示台股部位）
        if total_value_tw > 0 and pie_data:
            self.pie_widget.update_data(pie_data)
    
    def update_history_table(self):
        """更新交易記錄表格"""
        self.history_table.update_data(self.account.trade_history)

    # ===== 檔案紀錄功能 =====
    def log_daily_performance(self, total_asset, stock_prices):
        """
        將每日的總資產與盈虧，以及當日持股明細寫入檔案
        - portfolio_daily.csv：每日總覽（日期、現金、總資產、盈虧）
        - holdings_daily.csv：每日持股明細（日期、股票、股數、市值）
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.last_log_date == today_str:
            return  # 當天已經記錄過了

        self.last_log_date = today_str

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 1) 總資產每日概況
        summary_path = os.path.join(base_dir, "portfolio_daily.csv")
        file_exists = os.path.exists(summary_path)
        pnl = total_asset - self.account.initial_cash

        with open(summary_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["date", "time", "cash", "total_asset", "pnl"])
            writer.writerow([
                today_str,
                datetime.now().strftime("%H:%M:%S"),
                f"{self.account.cash:.2f}",
                f"{total_asset:.2f}",
                f"{pnl:.2f}",
            ])

        # 2) 每日持股明細
        holdings_path = os.path.join(base_dir, "holdings_daily.csv")
        file_exists_holdings = os.path.exists(holdings_path)

        with open(holdings_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists_holdings:
                writer.writerow(["date", "stock_code", "shares", "price", "value"])

            for stock_code, shares in self.account.holdings.items():
                price = stock_prices.get(stock_code, 0)
                value = price * shares
                writer.writerow([
                    today_str,
                    stock_code,
                    shares,
                    f"{price:.2f}",
                    f"{value:.2f}",
                ])


# ===== 程式入口 =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingApp()
    window.show()
    sys.exit(app.exec())
