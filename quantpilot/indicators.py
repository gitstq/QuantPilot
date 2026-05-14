"""
QuantPilot 技术指标计算引擎

纯Python标准库实现，支持15+常用技术指标计算。
每个指标函数均包含完整的数学公式注释。

支持的指标:
    - MA (Simple Moving Average) 简单移动平均
    - EMA (Exponential Moving Average) 指数移动平均
    - SMA (Smoothed Moving Average) 平滑移动平均
    - MACD (Moving Average Convergence Divergence) 指数平滑异同移动平均线
    - RSI (Relative Strength Index) 相对强弱指标
    - Bollinger Bands 布林带
    - ATR (Average True Range) 真实波幅均值
    - KDJ 随机指标
    - OBV (On-Balance Volume) 能量潮
    - WR (Williams %R) 威廉指标
    - CCI (Commodity Channel Index) 顺势指标
    - DMI (Directional Movement Index) 趋向指标
    - ROC (Rate of Change) 变动速率
    - MFI (Money Flow Index) 资金流量指标
    - STOCH (Stochastic Oscillator) 随机振荡指标
    - VWAP (Volume Weighted Average Price) 成交量加权平均价
    - TRIX (Triple Exponential Moving Average) 三重指数平滑移动平均
"""

import math


def _validate_data(values):
    """
    验证输入数据。

    Args:
        values: 数值列表

    Raises:
        ValueError: 数据为空时
    """
    if not values:
        raise ValueError("输入数据不能为空")


def ma(values, period=20):
    """
    简单移动平均线 (Simple Moving Average, SMA/MA)

    数学公式:
        MA_n = (1/n) * sum(C_i), i = t-n+1 到 t

    其中:
        n = 周期
        C_i = 第i期的收盘价
        t = 当前期

    Args:
        values: 收盘价序列
        period: 周期，默认20

    Returns:
        list: MA值序列，前period-1个值为None
    """
    _validate_data(values)
    result = [None] * (period - 1)
    for i in range(period - 1, len(values)):
        window = values[i - period + 1: i + 1]
        result.append(sum(window) / period)
    return result


def ema(values, period=20):
    """
    指数移动平均线 (Exponential Moving Average, EMA)

    数学公式:
        EMA_1 = C_1
        EMA_t = alpha * C_t + (1 - alpha) * EMA_{t-1}

    其中:
        alpha = 2 / (period + 1)  平滑因子
        C_t = 第t期收盘价

    Args:
        values: 收盘价序列
        period: 周期，默认20

    Returns:
        list: EMA值序列，前period-1个值为None
    """
    _validate_data(values)
    if len(values) < period:
        return [None] * len(values)

    alpha = 2.0 / (period + 1)
    result = [None] * (period - 1)

    # 第一个EMA值使用SMA
    first_ema = sum(values[:period]) / period
    result.append(first_ema)

    for i in range(period, len(values)):
        current_ema = alpha * values[i] + (1 - alpha) * result[-1]
        result.append(current_ema)

    return result


def sma(values, period=20):
    """
    平滑移动平均线 (Smoothed Moving Average, SMMA/SMA)

    数学公式:
        SMMA_1 = SMA_1 = (1/n) * sum(C_i)
        SMMA_t = (SMMA_{t-1} * (n-1) + C_t) / n

    其中:
        n = 周期
        C_t = 第t期收盘价

    Args:
        values: 收盘价序列
        period: 周期，默认20

    Returns:
        list: SMMA值序列
    """
    _validate_data(values)
    if len(values) < period:
        return [None] * len(values)

    result = [None] * (period - 1)
    first_sma = sum(values[:period]) / period
    result.append(first_sma)

    for i in range(period, len(values)):
        current = (result[-1] * (period - 1) + values[i]) / period
        result.append(current)

    return result


def macd(values, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD指标 (Moving Average Convergence Divergence)

    数学公式:
        DIF (MACD线) = EMA_fast - EMA_slow
        DEA (信号线) = EMA(DIF, signal_period)
        MACD柱 = 2 * (DIF - DEA)

    其中:
        EMA_fast = EMA(C, fast_period)    通常为12日EMA
        EMA_slow = EMA(C, slow_period)    通常为26日EMA
        DEA = EMA(DIF, signal_period)     通常为9日EMA

    Args:
        values: 收盘价序列
        fast_period: 快线周期，默认12
        slow_period: 慢线周期，默认26
        signal_period: 信号线周期，默认9

    Returns:
        tuple: (dif_list, dea_list, macd_hist_list)
    """
    _validate_data(values)

    ema_fast = ema(values, fast_period)
    ema_slow = ema(values, slow_period)

    # 计算DIF
    dif = []
    for i in range(len(values)):
        if ema_fast[i] is None or ema_slow[i] is None:
            dif.append(None)
        else:
            dif.append(ema_fast[i] - ema_slow[i])

    # 计算DEA（DIF的EMA）
    dif_values = [d if d is not None else 0 for d in dif]
    dea_full = ema(dif_values, signal_period)

    # 对齐DEA
    dea = [None] * len(values)
    for i in range(len(values)):
        if dif[i] is not None and i < len(dea_full) and dea_full[i] is not None:
            dea[i] = dea_full[i]

    # 计算MACD柱
    macd_hist = []
    for i in range(len(values)):
        if dif[i] is not None and dea[i] is not None:
            macd_hist.append(2 * (dif[i] - dea[i]))
        else:
            macd_hist.append(None)

    return dif, dea, macd_hist


def rsi(values, period=14):
    """
    RSI相对强弱指标 (Relative Strength Index)

    数学公式:
        RS = avg_gain / avg_loss
        RSI = 100 - 100 / (1 + RS)

    其中:
        avg_gain = (1/period) * sum(gain_t)   # 初始平均涨幅
        avg_loss = (1/period) * sum(loss_t)   # 初始平均跌幅
        后续使用平滑方法:
            avg_gain_t = (avg_gain_{t-1} * (period-1) + gain_t) / period
            avg_loss_t = (avg_loss_{t-1} * (period-1) + loss_t) / period
        gain_t = max(C_t - C_{t-1}, 0)       # 当日涨幅
        loss_t = max(C_{t-1} - C_t, 0)       # 当日跌幅

    Args:
        values: 收盘价序列
        period: 周期，默认14

    Returns:
        list: RSI值序列，前period个值为None
    """
    _validate_data(values)
    if len(values) < period + 1:
        return [None] * len(values)

    result = [None] * period

    # 计算初始涨跌幅
    gains = []
    losses = []
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    # 初始平均涨跌幅
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(100 - 100 / (1 + rs))

    # 后续RSI
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - 100 / (1 + rs))

    return result


def bollinger_bands(values, period=20, std_multiplier=2.0):
    """
    布林带 (Bollinger Bands)

    数学公式:
        Middle Band = SMA(C, period)
        Upper Band = Middle + std_multiplier * STD(C, period)
        Lower Band = Middle - std_multiplier * STD(C, period)
        BandWidth = (Upper - Lower) / Middle

    其中:
        SMA = 简单移动平均
        STD = 标准差
        std_multiplier = 标准差倍数，通常为2

    Args:
        values: 收盘价序列
        period: 周期，默认20
        std_multiplier: 标准差倍数，默认2.0

    Returns:
        tuple: (upper_band, middle_band, lower_band)
    """
    _validate_data(values)
    if len(values) < period:
        empty = [None] * len(values)
        return empty, empty, empty

    upper = [None] * (period - 1)
    middle = [None] * (period - 1)
    lower = [None] * (period - 1)

    for i in range(period - 1, len(values)):
        window = values[i - period + 1: i + 1]
        m = sum(window) / period
        variance = sum((x - m) ** 2 for x in window) / period
        std = math.sqrt(variance)

        middle.append(m)
        upper.append(m + std_multiplier * std)
        lower.append(m - std_multiplier * std)

    return upper, middle, lower


def atr(highs, lows, closes, period=14):
    """
    真实波幅均值 (Average True Range, ATR)

    数学公式:
        TR = max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)
        ATR = SMA(TR, period)

    其中:
        TR = 真实波幅 (True Range)
        H_t = 第t期最高价
        L_t = 第t期最低价
        C_{t-1} = 前一期收盘价
        ATR使用平滑移动平均(SMMA)计算

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        period: 周期，默认14

    Returns:
        list: ATR值序列
    """
    _validate_data(closes)
    n = len(closes)
    if n < 2:
        return [None] * n

    # 计算TR序列
    tr_list = [None]  # 第一个数据没有前一日收盘价
    for i in range(1, n):
        tr1 = highs[i] - lows[i]
        tr2 = abs(highs[i] - closes[i - 1])
        tr3 = abs(lows[i] - closes[i - 1])
        tr_list.append(max(tr1, tr2, tr3))

    # 计算ATR（使用SMMA）
    result = [None] * n
    valid_tr = [t for t in tr_list if t is not None]

    if len(valid_tr) < period:
        return result

    # 找到第一个有效TR的索引
    first_valid_idx = tr_list.index(valid_tr[0])

    # 初始ATR
    start = first_valid_idx + period - 1
    if start >= n:
        return result

    initial_atr = sum(valid_tr[:period]) / period
    result[start] = initial_atr

    # 后续ATR使用平滑
    for i in range(start + 1, n):
        if tr_list[i] is not None:
            current_atr = (result[i - 1] * (period - 1) + tr_list[i]) / period
            result[i] = current_atr

    return result


def kdj(highs, lows, closes, n=9, m1=3, m2=3):
    """
    KDJ随机指标

    数学公式:
        RSV = (C_t - LL_n) / (HH_n - LL_n) * 100

        K_t = (2/3) * K_{t-1} + (1/3) * RSV_t
        D_t = (2/3) * D_{t-1} + (1/3) * K_t
        J_t = 3 * K_t - 2 * D_t

    其中:
        RSV = 未成熟随机值 (Raw Stochastic Value)
        LL_n = n日内最低价
        HH_n = n日内最高价
        K, D 初始值均为50

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        n: RSV周期，默认9
        m1: K平滑系数，默认3
        m2: D平滑系数，默认3

    Returns:
        tuple: (k_list, d_list, j_list)
    """
    _validate_data(closes)
    n_data = len(closes)
    k_values = [None] * n_data
    d_values = [None] * n_data
    j_values = [None] * n_data

    if n_data < n:
        return k_values, d_values, j_values

    prev_k = 50.0
    prev_d = 50.0

    for i in range(n - 1, n_data):
        highest = max(highs[i - n + 1: i + 1])
        lowest = min(lows[i - n + 1: i + 1])

        if highest == lowest:
            rsv = 50.0
        else:
            rsv = (closes[i] - lowest) / (highest - lowest) * 100

        k = (2.0 / m1) * prev_k + (1.0 / m1) * rsv
        d = (2.0 / m2) * prev_d + (1.0 / m2) * k
        j = 3 * k - 2 * d

        k_values[i] = k
        d_values[i] = d
        j_values[i] = j

        prev_k = k
        prev_d = d

    return k_values, d_values, j_values


def obv(closes, volumes):
    """
    能量潮指标 (On-Balance Volume, OBV)

    数学公式:
        如果 C_t > C_{t-1}:  OBV_t = OBV_{t-1} + V_t
        如果 C_t < C_{t-1}:  OBV_t = OBV_{t-1} - V_t
        如果 C_t == C_{t-1}: OBV_t = OBV_{t-1}

    其中:
        C_t = 第t期收盘价
        V_t = 第t期成交量
        OBV_0 = 0

    Args:
        closes: 收盘价序列
        volumes: 成交量序列

    Returns:
        list: OBV值序列
    """
    _validate_data(closes)
    n = len(closes)
    if n == 0:
        return []

    result = [0]
    for i in range(1, n):
        if closes[i] > closes[i - 1]:
            result.append(result[-1] + volumes[i])
        elif closes[i] < closes[i - 1]:
            result.append(result[-1] - volumes[i])
        else:
            result.append(result[-1])

    return result


def wr(highs, lows, closes, period=14):
    """
    威廉指标 (Williams %R)

    数学公式:
        WR = (HH_n - C_t) / (HH_n - LL_n) * (-100)

    其中:
        HH_n = n周期内最高价
        LL_n = n周期内最低价
        C_t = 当前收盘价
        WR取值范围: [-100, 0]
        WR > -20 为超买区间
        WR < -80 为超卖区间

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        period: 周期，默认14

    Returns:
        list: WR值序列
    """
    _validate_data(closes)
    n = len(closes)
    result = [None] * n

    if n < period:
        return result

    for i in range(period - 1, n):
        highest = max(highs[i - period + 1: i + 1])
        lowest = min(lows[i - period + 1: i + 1])

        if highest == lowest:
            result[i] = -50.0
        else:
            result[i] = (highest - closes[i]) / (highest - lowest) * (-100)

    return result


def cci(highs, lows, closes, period=20):
    """
    顺势指标 (Commodity Channel Index, CCI)

    数学公式:
        TP = (H + L + C) / 3
        SMA_TP = SMA(TP, period)
        MD = (1/period) * sum(|TP_i - SMA_TP|)
        CCI = (TP - SMA_TP) / (0.015 * MD)

    其中:
        TP = 典型价格 (Typical Price)
        SMA_TP = TP的简单移动平均
        MD = 平均偏差 (Mean Deviation)
        0.015 = 常数，使约70%-80%的CCI值落在 [-100, +100] 之间

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        period: 周期，默认20

    Returns:
        list: CCI值序列
    """
    _validate_data(closes)
    n = len(closes)
    result = [None] * n

    if n < period:
        return result

    # 计算TP
    tp = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(n)]

    for i in range(period - 1, n):
        tp_window = tp[i - period + 1: i + 1]
        sma_tp = sum(tp_window) / period
        md = sum(abs(t - sma_tp) for t in tp_window) / period

        if md == 0:
            result[i] = 0.0
        else:
            result[i] = (tp[i] - sma_tp) / (0.015 * md)

    return result


def dmi(highs, lows, closes, period=14):
    """
    趋向指标 (Directional Movement Index, DMI)

    数学公式:
        +DM = H_t - H_{t-1}  (当 +DM > -DM 且 +DM > 0)
        -DM = L_{t-1} - L_t  (当 -DM > +DM 且 -DM > 0)
        TR = max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)

        +DI = 100 * SMMA(+DM, period) / SMMA(TR, period)
        -DI = 100 * SMMA(-DM, period) / SMMA(TR, period)
        DX = 100 * |+DI - (-DI)| / (+DI + (-DI))
        ADX = SMMA(DX, period)

    其中:
        +DI = 正方向指标
        -DI = 负方向指标
        ADX = 平均趋向指标

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        period: 周期，默认14

    Returns:
        tuple: (pdi_list, ndi_list, adx_list)
    """
    _validate_data(closes)
    n = len(closes)
    pdi_values = [None] * n
    ndi_values = [None] * n
    adx_values = [None] * n

    if n < period + 1:
        return pdi_values, ndi_values, adx_values

    # 计算DM和TR
    plus_dm_list = [0]
    minus_dm_list = [0]
    tr_list = [highs[0] - lows[0]]

    for i in range(1, n):
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]

        if up_move > down_move and up_move > 0:
            plus_dm_list.append(up_move)
        else:
            plus_dm_list.append(0)

        if down_move > up_move and down_move > 0:
            minus_dm_list.append(down_move)
        else:
            minus_dm_list.append(0)

        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        tr_list.append(tr)

    # 使用SMMA计算平滑值
    def calc_smma(values, period):
        result = [None] * len(values)
        if len(values) < period:
            return result
        initial = sum(values[:period]) / period
        result[period - 1] = initial
        for i in range(period, len(values)):
            result[i] = (result[i - 1] * (period - 1) + values[i]) / period
        return result

    smma_plus_dm = calc_smma(plus_dm_list, period)
    smma_minus_dm = calc_smma(minus_dm_list, period)
    smma_tr = calc_smma(tr_list, period)

    # 计算DI
    dx_list = [None] * n
    for i in range(n):
        if smma_plus_dm[i] is not None and smma_tr[i] is not None and smma_tr[i] != 0:
            pdi_values[i] = 100 * smma_plus_dm[i] / smma_tr[i]
            ndi_values[i] = 100 * smma_minus_dm[i] / smma_tr[i]

            di_sum = pdi_values[i] + ndi_values[i]
            if di_sum != 0:
                dx_list[i] = 100 * abs(pdi_values[i] - ndi_values[i]) / di_sum

    # 计算ADX
    valid_dx = [(i, d) for i, d in enumerate(dx_list) if d is not None]
    if len(valid_dx) >= period:
        start_idx = valid_dx[0][0]
        initial_adx = sum(d for _, d in valid_dx[:period]) / period
        adx_start = valid_dx[period - 1][0]
        adx_values[adx_start] = initial_adx

        for idx in range(adx_start + 1, n):
            if dx_list[idx] is not None and adx_values[idx - 1] is not None:
                adx_values[idx] = (
                    adx_values[idx - 1] * (period - 1) + dx_list[idx]
                ) / period

    return pdi_values, ndi_values, adx_values


def roc(values, period=12):
    """
    变动速率指标 (Rate of Change, ROC)

    数学公式:
        ROC = ((C_t - C_{t-period}) / C_{t-period}) * 100

    其中:
        C_t = 当前收盘价
        C_{t-period} = period期前的收盘价
        ROC以百分比表示价格变化率

    Args:
        values: 收盘价序列
        period: 周期，默认12

    Returns:
        list: ROC值序列
    """
    _validate_data(values)
    n = len(values)
    result = [None] * n

    for i in range(period, n):
        if values[i - period] != 0:
            result[i] = (
                (values[i] - values[i - period]) / values[i - period] * 100
            )

    return result


def mfi(highs, lows, closes, volumes, period=14):
    """
    资金流量指标 (Money Flow Index, MFI)

    数学公式:
        TP = (H + L + C) / 3
        MF = TP * V
        如果 TP_t > TP_{t-1}:  正资金流 = MF_t
        如果 TP_t < TP_{t-1}:  负资金流 = MF_t

        MFI = 100 - 100 / (1 + 正资金流比)

    其中:
        TP = 典型价格
        MF = 资金流量 (Money Flow)
        正资金流比 = period内正资金流之和 / period内负资金流之和
        MFI取值范围: [0, 100]
        MFI > 80 为超买
        MFI < 20 为超卖

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        volumes: 成交量序列
        period: 周期，默认14

    Returns:
        list: MFI值序列
    """
    _validate_data(closes)
    n = len(closes)
    result = [None] * n

    if n < period + 1:
        return result

    # 计算TP和MF
    tp = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(n)]
    mf = [tp[i] * volumes[i] for i in range(n)]

    for i in range(period, n):
        positive_flow = 0.0
        negative_flow = 0.0

        for j in range(i - period + 1, i + 1):
            if tp[j] > tp[j - 1]:
                positive_flow += mf[j]
            elif tp[j] < tp[j - 1]:
                negative_flow += mf[j]

        if negative_flow == 0:
            result[i] = 100.0
        else:
            money_ratio = positive_flow / negative_flow
            result[i] = 100 - 100 / (1 + money_ratio)

    return result


def stoch(highs, lows, closes, k_period=14, d_period=3):
    """
    随机振荡指标 (Stochastic Oscillator)

    数学公式:
        %K = (C_t - LL_n) / (HH_n - LL_n) * 100
        %D = SMA(%K, d_period)

    其中:
        %K = 快速随机值
        %D = 慢速随机值（%K的移动平均）
        LL_n = n周期内最低价
        HH_n = n周期内最高价
        C_t = 当前收盘价

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        k_period: %K周期，默认14
        d_period: %D平滑周期，默认3

    Returns:
        tuple: (k_list, d_list)
    """
    _validate_data(closes)
    n = len(closes)
    k_values = [None] * n
    d_values = [None] * n

    if n < k_period:
        return k_values, d_values

    # 计算%K
    for i in range(k_period - 1, n):
        highest = max(highs[i - k_period + 1: i + 1])
        lowest = min(lows[i - k_period + 1: i + 1])

        if highest == lowest:
            k_values[i] = 50.0
        else:
            k_values[i] = (closes[i] - lowest) / (highest - lowest) * 100

    # 计算%D（%K的SMA）
    valid_k = [(i, k) for i, k in enumerate(k_values) if k is not None]
    if len(valid_k) >= d_period:
        for idx in range(d_period - 1, len(valid_k)):
            i = valid_k[idx][0]
            window_k = [valid_k[j][1] for j in range(idx - d_period + 1, idx + 1)]
            d_values[i] = sum(window_k) / d_period

    return k_values, d_values


def vwap(highs, lows, closes, volumes):
    """
    成交量加权平均价 (Volume Weighted Average Price, VWAP)

    数学公式:
        VWAP = sum(TP_i * V_i) / sum(V_i)

    其中:
        TP_i = (H_i + L_i + C_i) / 3  典型价格
        V_i = 第i期成交量
        VWAP通常按日内累计计算

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列
        volumes: 成交量序列

    Returns:
        list: VWAP值序列（累计计算）
    """
    _validate_data(closes)
    n = len(closes)
    result = [None] * n

    cumulative_tp_vol = 0.0
    cumulative_vol = 0.0

    for i in range(n):
        tp = (highs[i] + lows[i] + closes[i]) / 3
        cumulative_tp_vol += tp * volumes[i]
        cumulative_vol += volumes[i]

        if cumulative_vol != 0:
            result[i] = cumulative_tp_vol / cumulative_vol

    return result


def trix(values, period=12):
    """
    三重指数平滑移动平均 (Triple Exponential Moving Average, TRIX)

    数学公式:
        EMA1 = EMA(C, period)
        EMA2 = EMA(EMA1, period)
        EMA3 = EMA(EMA2, period)
        TRIX = (EMA3_t - EMA3_{t-1}) / EMA3_{t-1} * 100

    其中:
        TRIX对价格进行三次EMA平滑后，计算变化率
        TRIX > 0 表示上涨趋势
        TRIX < 0 表示下跌趋势

    Args:
        values: 收盘价序列
        period: 周期，默认12

    Returns:
        list: TRIX值序列
    """
    _validate_data(values)
    n = len(values)

    ema1 = ema(values, period)
    ema1_valid = [e if e is not None else 0 for e in ema1]

    ema2 = ema(ema1_valid, period)
    ema2_valid = [e if e is not None else 0 for e in ema2]

    ema3 = ema(ema2_valid, period)

    result = [None] * n
    for i in range(1, n):
        if ema3[i] is not None and ema3[i - 1] is not None and ema3[i - 1] != 0:
            result[i] = (ema3[i] - ema3[i - 1]) / ema3[i - 1] * 100

    return result


def sar(highs, lows, af_step=0.02, af_max=0.2):
    """
    抛物线止损指标 (Stop and Reverse, SAR)

    数学公式:
        初始状态: 多头
        EP = H_t (多头) 或 L_t (空头)  极值点
        AF = 初始加速因子 (af_step)

        多头SAR:
            SAR_t = SAR_{t-1} + AF * (EP - SAR_{t-1})
            如果 L_t < SAR_t: 反转为空头

        空头SAR:
            SAR_t = SAR_{t-1} + AF * (EP - SAR_{t-1})
            如果 H_t > SAR_t: 反转为多头

        AF每次创新高/低时增加af_step，最大为af_max

    Args:
        highs: 最高价序列
        lows: 最低价序列
        af_step: 加速因子步长，默认0.02
        af_max: 最大加速因子，默认0.2

    Returns:
        list: SAR值序列
    """
    _validate_data(highs)
    n = len(highs)
    result = [None] * n

    if n < 2:
        return result

    # 初始化
    is_long = True
    af = af_step
    ep = highs[0]
    sar_val = lows[0]

    for i in range(1, n):
        # 计算SAR
        sar_val = sar_val + af * (ep - sar_val)

        # 确保SAR不超出前两天的价格范围
        if i >= 2:
            if is_long:
                sar_val = min(sar_val, lows[i - 1])
                sar_val = min(sar_val, lows[i - 2])
            else:
                sar_val = max(sar_val, highs[i - 1])
                sar_val = max(sar_val, highs[i - 2])

        result[i] = sar_val

        # 检查是否反转
        if is_long:
            if lows[i] < sar_val:
                # 反转为空头
                is_long = False
                sar_val = ep
                ep = lows[i]
                af = af_step
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + af_step, af_max)
        else:
            if highs[i] > sar_val:
                # 反转为多头
                is_long = True
                sar_val = ep
                ep = highs[i]
                af = af_step
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + af_step, af_max)

    return result


def williams_ad(highs, lows, closes):
    """
    威廉累积/派发线 (Williams Accumulation/Distribution, A/D)

    数学公式:
        如果 C_t > C_{t-1}:
            AD_t = AD_{t-1} + (C_t - L_t)
        如果 C_t < C_{t-1}:
            AD_t = AD_{t-1} - (H_t - C_t)
        如果 C_t == C_{t-1}:
            AD_t = AD_{t-1}

    其中:
        AD_0 = 0
        衡量资金流入和流出

    Args:
        highs: 最高价序列
        lows: 最低价序列
        closes: 收盘价序列

    Returns:
        list: A/D值序列
    """
    _validate_data(closes)
    n = len(closes)
    if n == 0:
        return []

    result = [0]
    for i in range(1, n):
        if closes[i] > closes[i - 1]:
            result.append(result[-1] + (closes[i] - lows[i]))
        elif closes[i] < closes[i - 1]:
            result.append(result[-1] - (highs[i] - closes[i]))
        else:
            result.append(result[-1])

    return result


# 指标注册表，用于CLI列出可用指标
INDICATOR_REGISTRY = {
    "MA": {"func": ma, "desc": "简单移动平均线 (Simple Moving Average)", "params": ["period"]},
    "EMA": {"func": ema, "desc": "指数移动平均线 (Exponential Moving Average)", "params": ["period"]},
    "SMA": {"func": sma, "desc": "平滑移动平均线 (Smoothed Moving Average)", "params": ["period"]},
    "MACD": {"func": macd, "desc": "MACD指标 (Moving Average Convergence Divergence)", "params": ["fast", "slow", "signal"]},
    "RSI": {"func": rsi, "desc": "RSI相对强弱指标 (Relative Strength Index)", "params": ["period"]},
    "BOLL": {"func": bollinger_bands, "desc": "布林带 (Bollinger Bands)", "params": ["period", "std_multiplier"]},
    "ATR": {"func": atr, "desc": "真实波幅均值 (Average True Range)", "params": ["period"]},
    "KDJ": {"func": kdj, "desc": "KDJ随机指标", "params": ["n", "m1", "m2"]},
    "OBV": {"func": obv, "desc": "能量潮指标 (On-Balance Volume)", "params": []},
    "WR": {"func": wr, "desc": "威廉指标 (Williams %R)", "params": ["period"]},
    "CCI": {"func": cci, "desc": "顺势指标 (Commodity Channel Index)", "params": ["period"]},
    "DMI": {"func": dmi, "desc": "趋向指标 (Directional Movement Index)", "params": ["period"]},
    "ROC": {"func": roc, "desc": "变动速率指标 (Rate of Change)", "params": ["period"]},
    "MFI": {"func": mfi, "desc": "资金流量指标 (Money Flow Index)", "params": ["period"]},
    "STOCH": {"func": stoch, "desc": "随机振荡指标 (Stochastic Oscillator)", "params": ["k_period", "d_period"]},
    "VWAP": {"func": vwap, "desc": "成交量加权平均价 (Volume Weighted Average Price)", "params": []},
    "TRIX": {"func": trix, "desc": "三重指数平滑移动平均 (Triple EMA)", "params": ["period"]},
    "SAR": {"func": sar, "desc": "抛物线止损指标 (Stop and Reverse)", "params": ["af_step", "af_max"]},
    "WAD": {"func": williams_ad, "desc": "威廉累积/派发线 (Williams A/D)", "params": []},
}


def list_indicators():
    """
    列出所有可用的技术指标。

    Returns:
        list: 指标信息列表
    """
    return [
        {"name": name, "desc": info["desc"], "params": info["params"]}
        for name, info in INDICATOR_REGISTRY.items()
    ]


def compute_indicator(name, *args, **kwargs):
    """
    通过名称计算指标。

    Args:
        name: 指标名称（不区分大小写）
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        指标计算结果

    Raises:
        ValueError: 指标名称不存在
    """
    name_upper = name.upper()
    if name_upper not in INDICATOR_REGISTRY:
        available = ", ".join(INDICATOR_REGISTRY.keys())
        raise ValueError(
            "未知指标: '{}'，可用指标: {}".format(name, available)
        )
    return INDICATOR_REGISTRY[name_upper]["func"](*args, **kwargs)
