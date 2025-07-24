import pandas as pd


def compute_ema_signals(df, fast, slow):
    """
    Adds lookahead-safe EMA cross signals to df:
      - 'EMA_FAST'
      - 'EMA_SLOW'
      - 'EMA_CROSS_SIGNAL_LONG': 1 if previous bar fast crossed above slow (bullish), else 0
      - 'EMA_CROSS_SIGNAL_SHORT': 1 if previous bar fast crossed below slow (bearish), else 0
    """
    df['EMA_FAST'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['EMA_SLOW'] = df['close'].ewm(span=slow, adjust=False).mean()
    # Detect crossovers only, not just above/below
    cross_up = ((df['EMA_FAST'] > df['EMA_SLOW']) &
                (df['EMA_FAST'].shift(1) <= df['EMA_SLOW'].shift(1)))
    cross_down = ((df['EMA_FAST'] < df['EMA_SLOW']) &
                  (df['EMA_FAST'].shift(1) >= df['EMA_SLOW'].shift(1)))
    # Shift by 1 bar for lookahead safety
    df['EMA_CROSS_SIGNAL_LONG'] = cross_up.shift(1, fill_value=False).astype(int)
    df['EMA_CROSS_SIGNAL_SHORT'] = cross_down.shift(1, fill_value=False).astype(int)


def compute_sma_signals(df, fast, slow):
    df['SMA_FAST'] = df['close'].rolling(window=fast, min_periods=fast).mean()
    df['SMA_SLOW'] = df['close'].rolling(window=slow, min_periods=slow).mean()
    cross_up = (df['SMA_FAST'] > df['SMA_SLOW']) & (df['SMA_FAST'].shift(1) <= df['SMA_SLOW'].shift(1))
    cross_down = (df['SMA_FAST'] < df['SMA_SLOW']) & (df['SMA_FAST'].shift(1) >= df['SMA_SLOW'].shift(1))
    df['LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
    df['SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)


def compute_rsi_signals(df, period, overbought, oversold):
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    # Entry: RSI crosses below oversold, Exit: RSI crosses above overbought
    df['LONG_SIGNAL'] = ((df['RSI'] < oversold) & (df['RSI'].shift(1) >= oversold)
                         ).shift(1, fill_value=False).astype(int)
    df['SHORT_SIGNAL'] = ((df['RSI'] > overbought) & (df['RSI'].shift(1) <= overbought)
                          ).shift(1, fill_value=False).astype(int)


def compute_macd_signals(df, fast=12, slow=26, signal=9):
    df['EMA_FAST'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['EMA_SLOW'] = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = df['EMA_FAST'] - df['EMA_SLOW']
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    cross_up = (df['MACD'] > df['MACD_SIGNAL']) & (df['MACD'].shift(1) <= df['MACD_SIGNAL'].shift(1))
    cross_down = (df['MACD'] < df['MACD_SIGNAL']) & (df['MACD'].shift(1) >= df['MACD_SIGNAL'].shift(1))
    df['LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
    df['SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)


def compute_supertrend_signals(df, period=10, multiplier=3.0):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period, min_periods=period).mean()
    hl2 = (high + low) / 2
    basic_ub = hl2 + (multiplier * atr)
    basic_lb = hl2 - (multiplier * atr)
    final_ub = basic_ub.copy()
    final_lb = basic_lb.copy()

    for i in range(1, len(df)):
        if close.iloc[i - 1] > final_ub.iloc[i - 1]:
            final_ub.iloc[i] = basic_ub.iloc[i]
        else:
            final_ub.iloc[i] = min(basic_ub.iloc[i], final_ub.iloc[i - 1])
        if close.iloc[i - 1] < final_lb.iloc[i - 1]:
            final_lb.iloc[i] = basic_lb.iloc[i]
        else:
            final_lb.iloc[i] = max(basic_lb.iloc[i], final_lb.iloc[i - 1])

    supertrend = pd.Series(index=df.index, dtype="float64")
    in_uptrend = True
    for i in range(period, len(df)):
        if in_uptrend:
            if close.iloc[i] < final_ub.iloc[i]:
                in_uptrend = False
        else:
            if close.iloc[i] > final_lb.iloc[i]:
                in_uptrend = True
        supertrend.iloc[i] = final_lb.iloc[i] if in_uptrend else final_ub.iloc[i]

    df['SUPERTREND'] = supertrend
    cross_up = (close > supertrend) & (close.shift(1) <= supertrend.shift(1))
    cross_down = (close < supertrend) & (close.shift(1) >= supertrend.shift(1))
    df['LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
    df['SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)


# Dispatcher for config-based strategy
def add_signals(df, strategy_name, strategy_params):
    if strategy_name == "EMA_CROSS":
        compute_ema_signals(df, strategy_params['fast'], strategy_params['slow'])
    elif strategy_name == "SMA_CROSS":
        compute_sma_signals(df, strategy_params['fast'], strategy_params['slow'])
    elif strategy_name == "RSI":
        compute_rsi_signals(df, strategy_params['period'], strategy_params['overbought'], strategy_params['oversold'])
    elif strategy_name == "MACD":
        compute_macd_signals(df,
                             fast=strategy_params.get('fast', 12),
                             slow=strategy_params.get('slow', 26),
                             signal=strategy_params.get('signal', 9)
                             )
    elif strategy_name == "SUPER_TREND":
        compute_supertrend_signals(df,
                                   period=strategy_params.get('period', 10),
                                   multiplier=strategy_params.get('multiplier', 3.0)
                                   )
    else:
        raise ValueError(f"Unsupported strategy: {strategy_name}")
