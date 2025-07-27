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


class IndicatorName(Enum):
    EMA_CROSS = "EMA_CROSS"
    SMA_CROSS = "SMA_CROSS"
    RSI = "RSI"
    MACD = "MACD"
    SUPER_TREND = "SUPER_TREND"
    ADX = "ADX"
    BOLLINGER = "BOLLINGER"
    CCI = "CCI"
    DONCHIAN = "DONCHIAN"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    WILLIAMS_R = "WILLIAMS_R"
    STOCHASTIC = "STOCHASTIC"
    ATR = "ATR"
    KELTNER = "KELTNER"
    ROC = "ROC"
    OBV = "OBV"
    ULTIMATE_OSC = "ULTIMATE_OSC"
    MOMENTUM = "MOMENTUM"
    PSAR = "PSAR"
    ENVELOPE = "ENVELOPE"
    PIVOT = "PIVOT"
    VWAP = "VWAP"
    MFI = "MFI"
    CHAIKIN_MF = "CHAIKIN_MF"
    AROON = "AROON"
    TEMA = "TEMA"
    DEMA = "DEMA"
    HULL_MA = "HULL_MA"
    STOCH_RSI = "STOCH_RSI"
    TRIX = "TRIX"


class DataframeSplit(Enum):
    ALL = "ALL"
    TRAIN = "TRAIN"
    TEST = "TEST"
