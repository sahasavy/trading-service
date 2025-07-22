def compute_ema_signals(df, fast, slow):
    df['EMA_FAST'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['EMA_SLOW'] = df['close'].ewm(span=slow, adjust=False).mean()
    cross_up = ((df['EMA_FAST'] > df['EMA_SLOW']) &
                (df['EMA_FAST'].shift(1) <= df['EMA_SLOW'].shift(1)))
    cross_down = ((df['EMA_FAST'] < df['EMA_SLOW']) &
                  (df['EMA_FAST'].shift(1) >= df['EMA_SLOW'].shift(1)))
    df['EMA_CROSS_SIGNAL'] = cross_up.shift(1).fillna(False).astype(int)
    df['EMA_CROSS_SIGNAL_SHORT'] = cross_down.shift(1).fillna(False).astype(int)
