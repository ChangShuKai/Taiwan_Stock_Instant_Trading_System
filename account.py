"""
帳戶系統模組
處理股票交易、持倉管理和交易記錄
"""
from datetime import datetime


class Account:
    """交易帳戶系統"""
    
    def __init__(self, initial_cash=1_000_000):
        """
        初始化帳戶
        Args:
            initial_cash: 初始資金（預設100萬）
        """
        self.cash = initial_cash
        self.holdings = {}  # {stock_code: shares}
        self.trade_history = []  # 交易記錄
    
    def buy(self, stock_code, price, qty):
        """
        買入股票
        Args:
            stock_code: 股票代碼
            price: 買入價格
            qty: 買入數量
        Returns:
            bool: 是否成功
        """
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
        """
        賣出股票
        Args:
            stock_code: 股票代碼
            price: 賣出價格
            qty: 賣出數量
        Returns:
            bool: 是否成功
        """
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
        """
        計算總資產
        Args:
            stock_prices: {stock_code: price} 字典
        Returns:
            float: 總資產
        """
        total = self.cash
        for stock_code, shares in self.holdings.items():
            if stock_code in stock_prices:
                total += stock_prices[stock_code] * shares
        return total
