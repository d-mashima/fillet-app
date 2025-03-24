import streamlit as st
from sympy import symbols, Eq, solve
import math

st.title("フィレット距離計算ツール（法線ベクトル完全対応）")

# 入力欄（Rとrは空欄がデフォルト）
a = st.number_input("短側カット寸法の半分（a）", value=50.0)
b = st.number_input("長側カット寸法の半分（b）", value=100.0)
R_input = st.text_input("長側半径（R）", value="")  # 空欄デフォルト
r_input = st.text_input("短側半径（r）", value="")  # 空欄デフォルト
c = st.number_input("コーナー半径（c）", value=10.0)

# 空欄判定
use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

if st.button("計算する"):
    try:
        x, y = symbols('x y', real=True)
        R = float(R_input) if use_circle1 else None
        r = float(r_input) if use_circle2 else None

        # 式①（Rあり or y = a）
        if use_circle1:
            eq1 = Eq(x**2 + (y + R - a)**2, R**2)
        else:
            eq1 = Eq(y, a)

        # 式②（rあり or x = b）
        if use_circle2:
            eq2 = Eq((x + r - b)**2 + y**2, r**2)
        else:
            eq2 = Eq(x, b)

        # 交点の決定
        if not use_circle1 and not use_circle2:
            x0, y0 = b, a
        else:
            solutions = solve((eq1, eq2), (x, y), dict=True)
            x0, y0 = None, None
            for sol in solutions:
                x_eval = sol[x].evalf()
                y_eval = sol[y].evalf()
                if x_eval > 0 and y_eval > 0:
                    x0, y0 = x_eval, y_eval
                    break
            if x0 is None:
                st.error("第1象限に交点が見つかりませんでした。")
                st.stop()

        # フィレット中心の計算
        if not use_circle1 and not use_circle2:
            mx = b - c
            my = a - c
        else:
            # 法線ベクトル①（円または y = a）
            if use_circle1:
                x1, y1 = 0, -R + a
                dx1, dy1 = x0 - x1, y0 - y1
            else:
                dx1, dy1 = 0, -1  # 真下方向

            # 法線ベクトル②（円または x = b）
            if use_circle2:
                x2, y2 = -r + b, 0
                dx2, dy2 = x0 - x2, y0 - y2
            else:
                dx2, dy2 = -1, 0  # 真左方向

            # 合成ベクトル（正規化）
            mag1 = math.hypot(dx1, dy1)
            mag2 = math.hypot(dx2, dy2)
            ux = dx1 / mag1 + dx2 / mag2
            uy = dy1 / mag1 + dy2 / mag2
            magU = math.hypot(ux, uy)

            mx = x0 - c * (ux / magU)
            my = y0 - c * (uy / magU)

        # 距離 L = フィレット中心 → (b, a)
        L = math.sqrt((mx - b)**2 + (my - a)**2)

        # 出力
        st.success("【計算結果】")
        st.write(f"交点 (x₀, y₀)：({x0:.3f}, {y0:.3f})")
        st.write(f"フィレット中心 (m, n)：({mx:.3f}, {my:.3f})")
        st.write(f"距離 L（→(b, a)）：{L:.3f}")

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
3月24日 7:52



Enterで送信
