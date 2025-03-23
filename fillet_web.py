import streamlit as st
from sympy import symbols, Eq, solve
import math

# タイトル
st.title("フィレット距離計算ツール")

# 入力
a = st.number_input("短側カット寸法の半分（a）", value=50.0)
b = st.number_input("長側カット寸法の半分（b）", value=100.0)
R = st.number_input("長側半径（R）", value=1000.0)
r = st.number_input("短側半径（r）", value=1000.0)
c = st.number_input("コーナー半径（c）", value=10.0)

if st.button("計算する"):
    x, y = symbols('x y', real=True)
    eq1 = Eq(x**2 + (y + R - a)**2, R**2)
    eq2 = Eq((x + r - b)**2 + y**2, r**2)
    solutions = solve((eq1, eq2), (x, y), dict=True)

    found = False
    for sol in solutions:
        x0 = sol[x].evalf()
        y0 = sol[y].evalf()
        if x0 > 0 and y0 > 0:
            found = True
            break

    if not found:
        st.error("第1象限に交点が見つかりませんでした。")
    else:
        x1, y1 = 0, -R + a
        x2, y2 = -r + b, 0

        dx1, dy1 = float(x0 - x1), float(y0 - y1)
        dx2, dy2 = float(x0 - x2), float(y0 - y2)
        mag1 = math.hypot(dx1, dy1)
        mag2 = math.hypot(dx2, dy2)

        ux = dx1 / mag1 + dx2 / mag2
        uy = dy1 / mag1 + dy2 / mag2
        magU = math.hypot(ux, uy)

        # フィレット中心（内向き）
        mx = float(x0) - c * (ux / magU)
        my = float(y0) - c * (uy / magU)

        # 新しいL定義（中心 → (b, a)）
        L = math.sqrt((mx - b)**2 + (my - a)**2)

        # 結果表示
        st.success("【計算結果】")
        st.write(f"交点 (x₀, y₀)：({x0:.3f}, {y0:.3f})")
        st.write(f"フィレット中心 (m, n)：({mx:.3f}, {my:.3f})")
        st.write(f"距離 L（→(b, a)）：{L:.3f}")
