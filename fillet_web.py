import streamlit as st
from sympy import symbols, Eq, solve
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="フィレット距離計算ツール", layout="centered")
st.title("割り付け＋フィレット距離計算ツール（グラフ付き）")

# ===== 入力 =====
a = st.number_input("短側カット寸法の半分（a）", value=50.0)
b = st.number_input("長側カット寸法の半分（b）", value=100.0)
z = st.number_input("全高（z）", value=40.0)
convex = st.number_input("凸（convex）", value=10.0)
c = st.number_input("フィレット半径（c）", value=10.0)
R_input = st.text_input("短側（式①）の半径（R）", value="")
r_input = st.text_input("長側（式②）の半径（r）", value="")

# ===== 入力整形 =====
use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

try:
    R = float(R_input) if use_circle1 else None
    r = float(r_input) if use_circle2 else None

    # ===== 割り付けロジック =====
    w = 2 * a
    d = 2 * b
    mt = 13 if z < 50 else 20
    wpz_base = (20 + (convex - 20) / 2) * 0.9
    wpz = max(math.floor(wpz_base), 12)
    if z >= 50:
        wpz = 20
    dp = wpz

    num_a = math.floor(960 / (wpz + w))
    wp = math.floor((960 % (wpz + w)) / num_a) + wpz
    dc = d + dp
    wc = w + wp

    st.subheader("【割り付け計算結果】")
    st.write(f"巾ピッチ wp = {wp}")
    st.write(f"送りピッチ dp = {dp}")
    st.write(f"キャビピッチ（巾方向）wc = {wc}")
    st.write(f"キャビピッチ（送り方向）dc = {dc}")

    # ===== フィレット中心計算 =====
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

    elif use_circle1 and not use_circle2:
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

    elif not use_circle1 and use_circle2:
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

    # ===== 距離 L（新定義）=====
    L = math.sqrt((mx - dc)**2 + (my - wc)**2) - c

    st.subheader("【フィレット計算結果】")
    st.write(f"フィレット中心座標：(mx, my) = ({mx:.3f}, {my:.3f})")
    st.write(f"距離 L（中心→(dc, wc) から半径を引いた値）：{L:.3f}")

    # ===== グラフ表示 =====
    st.subheader("【フィレット中心とキャビピッチ位置 図示】")
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel("x（長側方向）")
    ax.set_ylabel("y（短側方向）")

    ax.plot(mx, my, 'ro', label='フィレット中心 (mx, my)')
    ax.plot(dc, wc, 'bo', label='キャビピッチ点 (dc, wc)')
    ax.plot(d / 2, w / 2, 'go', label='角点 (d/2, w/2)')

    circle = plt.Circle((mx, my), c, color='r', fill=False, linestyle='--')
    ax.add_patch(circle)

    ax.legend()
    ax.set_xlim(0, max(dc, mx) + 20)
    ax.set_ylim(0, max(wc, my) + 20)

    st.pyplot(fig)

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
