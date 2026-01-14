"""
台灣證券交易所 + 美股 API 整合模組
提供台股 / 美股的股價查詢和股票名稱查詢功能
"""
import requests
from datetime import datetime


class StockAPI:
    """股價 API 整合（支援台股與美股）"""

    # 常見台股名稱對照表
    STOCK_NAMES_TW = {
        "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2308": "台達電",
        "2412": "中華電", "2303": "聯電", "1301": "台塑", "1303": "南亞",
        "2891": "中信金", "2882": "國泰金", "2886": "兆豐金", "2892": "第一金",
        "2881": "富邦金", "2301": "光寶科", "2379": "瑞昱", "2382": "廣達",
        "2357": "華碩", "2327": "國巨", "3008": "大立光", "2409": "友達",
        "3481": "群創", "1101": "台泥", "2002": "中鋼", "2912": "統一超",
        "2207": "和泰車", "2603": "長榮", "2609": "陽明", "2618": "長榮航"
    }

    # 常見美股名稱對照表
    STOCK_NAMES_US = {
        "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
        "AMZN": "Amazon", "META": "Meta Platforms", "TSLA": "Tesla",
        "NVDA": "NVIDIA", "BRK.B": "Berkshire Hathaway B",
        "JPM": "JPMorgan Chase", "V": "Visa"
    }

    @staticmethod
    def _is_tw_stock(stock_code: str) -> bool:
        """判斷是否為台股（純數字代碼視為台股）"""
        return stock_code.isdigit()

    @staticmethod
    def get_realtime_price(stock_code):
        """
        取得即時股價
        - 台股：使用 TWSE API
        - 美股：使用 Yahoo Finance Quote API（公開、免金鑰）
        """
        if StockAPI._is_tw_stock(stock_code):
            return StockAPI._get_tw_realtime_price(stock_code)
        return StockAPI._get_us_realtime_price(stock_code)

    # ===== 台股 API =====
    @staticmethod
    def _get_tw_realtime_price(stock_code):
        """台股：優先使用 TWSE 個股日成交資訊 API，失敗時改用即時資訊 API"""
        try:
            # 方法1：使用 TWSE 個股日成交資訊 API（最新交易日數據）
            today = datetime.now().strftime("%Y%m%d")
            url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
            params = {
                'response': 'json',
                'date': today,
                'stockNo': stock_code
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    latest = data['data'][-1]
                    # 數據格式：日期, 成交股數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌價差, 成交筆數
                    price = float(latest[6].replace(',', ''))  # 收盤價
                    open_price = float(latest[3].replace(',', ''))  # 開盤價
                    high = float(latest[4].replace(',', ''))  # 最高價
                    low = float(latest[5].replace(',', ''))  # 最低價
                    volume = int(latest[1].replace(',', ''))  # 成交股數
                    change = float(latest[7].replace(',', '').replace('X', '0'))  # 漲跌價差
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

        # 方法2：備用方案 - 使用個股即時資訊
        try:
            url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
            params = {
                'ex_ch': f'tse_{stock_code}.tw',
                'json': '1',
                'delay': '0'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, params=params, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if 'msgArray' in data and len(data['msgArray']) > 0:
                    info = data['msgArray'][0]
                    price_str = info.get('z', '0')  # 最新成交價
                    open_str = info.get('o', '0')  # 開盤價
                    high_str = info.get('h', '0')  # 最高價
                    low_str = info.get('l', '0')  # 最低價
                    volume_str = info.get('v', '0')  # 成交量
                    change_str = info.get('y', '0')  # 昨收

                    if price_str and price_str != '-':
                        price = float(price_str)
                        open_price = float(open_str) if open_str != '-' else price
                        high = float(high_str) if high_str != '-' else price
                        low = float(low_str) if low_str != '-' else price
                        volume = int(volume_str) if volume_str != '-' else 0
                        yesterday_close = float(change_str) if change_str != '-' else price

                        change = price - yesterday_close
                        change_percent = (change / yesterday_close * 100) if yesterday_close > 0 else 0

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
            print(f"即時資訊API錯誤: {e}")

        return None

    # ===== 美股 API（Yahoo Finance） =====
    @staticmethod
    def _get_us_realtime_price(stock_code):
        """
        美股：使用 Yahoo Finance Quote API
        來源：https://query1.finance.yahoo.com/v7/finance/quote?symbols=
        """
        try:
            url = "https://query1.finance.yahoo.com/v7/finance/quote"
            params = {"symbols": stock_code}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                return None

            data = response.json()
            result = data.get("quoteResponse", {}).get("result", [])
            if not result:
                return None

            info = result[0]
            price = info.get("regularMarketPrice")
            prev_close = info.get("regularMarketPreviousClose")
            open_price = info.get("regularMarketOpen", price)
            high = info.get("regularMarketDayHigh", price)
            low = info.get("regularMarketDayLow", price)
            volume = info.get("regularMarketVolume", 0)

            if price is None or prev_close is None:
                return None

            change = price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0

            return {
                "price": float(price),
                "change": float(change),
                "change_percent": float(change_percent),
                "volume": int(volume),
                "high": float(high),
                "low": float(low),
                "open": float(open_price),
            }
        except Exception as e:
            print(f"美股 API 錯誤: {e}")
            return None

    @staticmethod
    def get_stock_name(stock_code):
        """獲取股票名稱（自動判斷台股 / 美股）"""
        # 先從對照表查找
        if StockAPI._is_tw_stock(stock_code):
            if stock_code in StockAPI.STOCK_NAMES_TW:
                return StockAPI.STOCK_NAMES_TW[stock_code]
        else:
            if stock_code.upper() in StockAPI.STOCK_NAMES_US:
                return StockAPI.STOCK_NAMES_US[stock_code.upper()]

        # 嘗試從 API 獲取名稱
        if StockAPI._is_tw_stock(stock_code):
            # 台股：TWSE 即時資訊
            try:
                url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
                params = {
                    'ex_ch': f'tse_{stock_code}.tw',
                    'json': '1',
                    'delay': '0'
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, params=params, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'msgArray' in data and len(data['msgArray']) > 0:
                        name = data['msgArray'][0].get('n', '')
                        if name:
                            return name
            except Exception as e:
                print(f"獲取台股名稱錯誤: {e}")
        else:
            # 美股：Yahoo Finance
            try:
                url = "https://query1.finance.yahoo.com/v7/finance/quote"
                params = {"symbols": stock_code}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = requests.get(url, params=params, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("quoteResponse", {}).get("result", [])
                    if result:
                        name = result[0].get("shortName") or result[0].get("longName")
                        if name:
                            return name
            except Exception as e:
                print(f"獲取美股名稱錯誤: {e}")

        # 找不到時直接回傳代碼本身
        return stock_code
