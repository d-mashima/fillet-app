import streamlit as st
from sympy import symbols, Eq, solve, sqrt
import math

st.title("フィレット距離計算ツール（完全接触版）")

a = st.number_input("短側カット寸法の半分（a）", value=50.0)
b = st.number_input("長側カット寸法の半分（b）", value=100.0)
R_input = st.text_input("長側半径（R）", value="")
r_input = st.text_input("短側半径（r）", value="")
c = st.number_input("コーナー半径（c）", value=10.0)

use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

if st.button("計算する"):
    try:
        R = float(R_input) if use_circle1 else None
        r = float(r_input) if use_circle2 else None

        x, y = symbols('x y', real=True)
        mx, my = None, None

        if use_circle1 and use_circle2:
            # ✅ 両方円 → アポロニウス円
            x1, y1 = 0.0, -R + a
            x2, y2 = -r + b, 0.0
            eq1 = Eq((x - x1)**2 + (y - y1)**2, (R - c)**2)
            eq2 = Eq((x - x2)**2 + (y - y2)**2, (r - c)**2)
            solutions = solve((eq1, eq2), (x, y), dict=True)
            for sol in solutions:
                if sol[x].evalf() > 0 and sol[y].evalf() > 0:
                    mx = float(sol[x].evalf())
                    my = float(sol[y].evalf())
                    break

        elif use_circle1 and not use_circle2:
            # ✅ 式①: 円, 式②: 直線 x = b
            m = b - c  # 内向き
            center_x, center_y = 0, -R + a
            eq = Eq((m - center_x)**2 + (y - center_y)**2, (R - c)**2)
            sols = solve(eq, y)
            for y_val in sols:
                yf = y_val.evalf()
                if yf > 0:
                    mx = m
                    my = float(yf)
                    break

        elif not use_circle1 and use_circle2:
            # ✅ 式①: 直線 y = a, 式②: 円
            n = a - c  # 内向き
            center_x, center_y = -r + b, 0
            eq = Eq((x - center_x)**2 + (n - center_y)**2, (r - c)**2)
            sols = solve(eq, x)
            for x_val in sols:
                xf = x_val.evalf()
                if xf > 0:
                    mx = float(xf)
                    my = n
                    break

        else:
            # ✅ 両方直線 → 中心は (b - c, a - c)
            mx = b - c
            my = a - c

        if mx is None or my is None:
            st.error("第1象限に有効なフィレット中心が見つかりませんでした。")
            st.stop()

        # 距離 L（中心 → 角点）
        L = math.sqrt((mx - b)**2 + (my - a)**2)

        # 出力
        st.success("【計算結果】")
        st.write(f"フィレット中心 (m, n)：({mx:.3f}, {my:.3f})")
        st.write(f"距離 L（→(b, a)）：{L:.3f}")

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
