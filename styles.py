"""
應用程式樣式定義
提供現代化的UI樣式
"""

# 主樣式表（整體圓角卡片風格）
MAIN_STYLESHEET = """
    QMainWindow {
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #f1f3f5,
            stop:1 #dee2e6
        );
    }
    
    QWidget#centralWidget {
        background-color: #ffffff;
        border-radius: 18px;
        border: 1px solid #dee2e6;
    }
    
    QGroupBox {
        font-weight: bold;
        font-size: 13px;
        color: #2c3e50;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        margin-top: 16px;
        padding-top: 18px;
        background-color: #ffffff;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 18px;
        padding: 0 10px;
        background-color: #ffffff;
        color: #495057;
    }
    
    QPushButton {
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        font-size: 13px;
        min-height: 20px;
    }
    
    QPushButton:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }
    
    QPushButton:pressed {
        opacity: 0.8;
    }
    
    QTableWidget {
        border: 1px solid #dee2e6;
        border-radius: 10px;
        gridline-color: #e9ecef;
        background-color: white;
        selection-background-color: #e3f2fd;
        font-size: 12px;
    }
    
    QTableWidget::item {
        padding: 5px;
    }
    
    QHeaderView::section {
        background-color: #f8f9fa;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #dee2e6;
        font-weight: bold;
        color: #495057;
    }
    
    QLineEdit, QSpinBox {
        padding: 8px;
        border: 2px solid #ced4da;
        border-radius: 10px;
        background-color: white;
        font-size: 13px;
        selection-background-color: #e3f2fd;
    }
    
    QLineEdit:focus, QSpinBox:focus {
        border: 2px solid #4dabf7;
        outline: none;
    }
    
    QLabel {
        color: #212529;
    }
    
    QScrollBar:vertical {
        border: none;
        background: #f8f9fa;
        width: 12px;
        margin: 0;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background: #adb5bd;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #868e96;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
"""

# 買進按鈕樣式
BUY_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ff6b6b, stop:1 #ee5a6f);
        color: white;
        font-weight: bold;
        font-size: 14px;
        padding: 12px;
        border-radius: 6px;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ff5252, stop:1 #e63946);
    }
"""

# 賣出按鈕樣式
SELL_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #51cf66, stop:1 #40c057);
        color: white;
        font-weight: bold;
        font-size: 14px;
        padding: 12px;
        border-radius: 6px;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #40c057, stop:1 #37b24d);
    }
"""

# 查詢按鈕樣式
SEARCH_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #4dabf7, stop:1 #339af0);
        color: white;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 6px;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #339af0, stop:1 #228be6);
    }
"""

# 價格標籤樣式（漲）
PRICE_UP_STYLE = "color: #e63946; font-weight: bold;"

# 價格標籤樣式（跌）
PRICE_DOWN_STYLE = "color: #2b8a3e; font-weight: bold;"

# 價格標籤樣式（平）
PRICE_FLAT_STYLE = "color: #495057; font-weight: bold;"
