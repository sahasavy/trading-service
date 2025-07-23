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
