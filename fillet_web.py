import streamlit as st
from sympy import symbols, Eq, solve
import math

st.title("フィレット距離計算ツール（条件分岐対応）")

# 入力欄
a = st.number_input("短側カット寸法の半分（a）", value=50.0)
b = st.number_input("長側カット寸法の半分（b）", value=100.0)
R_input = st.text_input("長側半径（R）", value="1000")
r_input = st.text_input("短側半径（r）", value="1000")
c = st.number_input("コーナー半径（c）", value=10.0)

# 入力処理（空欄対応）
use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

if st.button("計算する"):
    try:
        x, y = symbols('x y', real=True)
        R = float(R_input) if use_circle1 else None
        r = float(r_input) if use_circle2 else None

        # 式定義
        if use_circle1:
            eq1 = Eq(x**2 + (y + R - a)**2, R**2)
        else:
            eq1 = Eq(y, a)

        if use_circle2:
            eq2 = Eq((x + r - b)**2 + y**2, r**2)
        else:
            eq2 = Eq(x, b)

        # 交点計算
        if not use_circle1 or not use_circle2:
            # どちらかが直線になっている場合は交点を (b, a) に固定
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

        # フィレット中心計算（内向き）
        if use_circle1:
            x1, y1 = 0, -R + a
        else:
            x1, y1 = x0, y0 - 1  # 仮の方向ベクトル用（真下）

        if use_circle2:
            x2, y2 = -r + b, 0
        else:
            x2, y2 = x0 - 1, y0  # 仮の方向ベクトル用（左）

        dx1, dy1 = float(x0 - x1), float(y0 - y1)
        dx2, dy2 = float(x0 - x2), float(y0 - y2)
        mag1 = math.hypot(dx1, dy1)
        mag2 = math.hypot(dx2, dy2)

        ux = dx1 / mag1 + dx2 / mag2
        uy = dy1 / mag1 + dy2 / mag2
        magU = math.hypot(ux, uy)

        # フィレット中心（交点から内向き）
        mx = float(x0) - c * (ux / magU)
        my = float(y0) - c * (uy / magU)

        # 距離 L（中心 → (b, a)）
        L = math.sqrt((mx - b)**2 + (my - a)**2)

        # 出力
        st.success("【計算結果】")
        st.write(f"交点 (x₀, y₀)：({x0:.3f}, {y0:.3f})")
        st.write(f"フィレット中心 (m, n)：({mx:.3f}, {my:.3f})")
        st.write(f"距離 L（→(b, a)）：{L:.3f}")

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
