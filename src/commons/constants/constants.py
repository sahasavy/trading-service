from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderPosition(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeEvent(Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class TradeExitReason(Enum):
    STOP_LOSS = "STOP LOSS"
    TARGET = "TARGET"
    CROSS_DOWN = "EMA CROSS DOWN"
    CROSS_UP = "EMA CROSS UP"
    MAX_HOLD = "MAX HOLD"
    EOD = "END OF DAY"


class Exchange(Enum):
    NSE = "NSE"
    BSE = "BSE"


class Segment(Enum):
    EQUITY_DELIVERY = "EQUITY_DELIVERY"
    EQUITY_INTRADAY = "EQUITY_INTRADAY"
    FNO_FUTURE = "FNO_FUTURE"
    FNO_OPTION = "FNO_OPTION"


class CandleInterval(Enum):
    MIN_1 = "minute"
    MIN_3 = "3minute"
    MIN_5 = "5minute"
    MIN_10 = "10minute"
    MIN_15 = "15minute"
    MIN_30 = "30minute"
    MIN_60 = "60minute"
    DAY = "day"
