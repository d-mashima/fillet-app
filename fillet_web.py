import streamlit as st
from sympy import symbols, Eq, solve
import math

st.title("割り付け＋フィレット距離計算ツール")

# 入力
w = st.number_input("短側寸法 w（製品巾）", value=100.0)
d = st.number_input("長側寸法 d（製品送り）", value=200.0)
c = st.number_input("フィレット半径 c", value=10.0)
convex = st.number_input("凸（convex）", value=10.0)
z = st.number_input("全高 z", value=40.0)
R_input = st.text_input("短側の円半径（R, 式①）", value="")
r_input = st.text_input("長側の円半径（r, 式②）", value="")

use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

try:
    R = float(R_input) if use_circle1 else None
    r = float(r_input) if use_circle2 else None

    # 割り付けロジック
    mt = 13 if z < 50 else 20
    wpz_base = (20 + (convex - 20) / 2) * 0.9
    wpz = max(math.floor(wpz_base), 12)
    if z >= 50:
        wpz = 20
    dp = wpz

    a = math.floor(960 / (wpz + w))
    wp = math.floor((960 % (wpz + w)) / a) + wpz
    b = math.floor((1100 - mt * 2) / (d + dp))

    wc = w + wp
    dc = d + dp

    # フィレット中心計算
    x, y = symbols('x y', real=True)
    mx, my = None, None

    if use_circle1 and use_circle2:
        x1, y1 = 0.0, -R + w / 2
        x2, y2 = -r + d / 2, 0.0
        eq1 = Eq((x - x1)**2 + (y - y1)**2, (R - c)**2)
        eq2 = Eq((x - x2)**2 + (y - y2)**2, (r - c)**2)
        solutions = solve((eq1, eq2), (x, y), dict=True)
        for sol in solutions:
            if sol[x].evalf() > 0 and sol[y].evalf() > 0:
                mx = float(sol[x].evalf())
                my = float(sol[y].evalf())
                break
    elif use_circle1:
        m = d / 2 - c
        center_x, center_y = 0, -R + w / 2
        eq = Eq((m - center_x)**2 + (y - center_y)**2, (R - c)**2)
        sols = solve(eq, y)
        for y_val in sols:
            yf = y_val.evalf()
            if yf > 0:
                mx = m
                my = float(yf)
                break
    elif use_circle2:
        n = w / 2 - c
        center_x, center_y = -r + d / 2, 0
        eq = Eq((x - center_x)**2 + (n - center_y)**2, (r - c)**2)
        sols = solve(eq, x)
        for x_val in sols:
            xf = x_val.evalf()
            if xf > 0:
                mx = float(xf)
                my = n
                break
    else:
        mx = d / 2 - c
        my = w / 2 - c

    if mx is None or my is None:
        st.error("第1象限に有効なフィレット中心が見つかりませんでした。")
        st.stop()

    # 新定義の距離 L
    L = math.sqrt((mx - dc) ** 2 + (my - wc) ** 2) - c

    # ===== 出力 =====
    st.subheader("【計算結果】")
    st.write(f"幅採り数 a = {a}")
    st.write(f"送り採り数 b = {b}")
    st.write(f"キャビピッチ wc = {wc}")
    st.write(f"キャビピッチ dc = {dc}")
    st.write(f"距離 L（中心→(dc, wc) からフィレット半径を減算）= {L:.3f}")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
