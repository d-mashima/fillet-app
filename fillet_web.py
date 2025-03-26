import streamlit as st
from sympy import symbols, Eq, solve
import math

st.set_page_config(page_title="フィレット距離計算ツール", layout="centered")

# ===== スタイル =====
st.markdown("""
    <style>
    .main {
        max-width: 320px;
        margin: auto;
        background-color: white;
        padding: 20px 30px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        font-family: "メイリオ", sans-serif;
    }
    .title {
        background-color: #005bac;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        text-align: center;
    }
    .section {
        background-color: #e9f5ff;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 13px;
    }
    input[type=number], input[type=text] {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">割り付け＋フィレット距離計算ツール</div>', unsafe_allow_html=True)

    # ===== 入力 =====
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
        mt = 13 if z < 50 else 20

        # ===== フィレット中心座標 =====
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

        # 初期割り付け数
        wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
        if z >= 50:
            wpz = 20
        wp_init = wpz
        dp_init = wpz
        a0 = math.floor(960 / (w + wpz))
        b0 = math.floor((1100 - mt * 2) / (d + wpz))

        # ===== 最適化関数（一般化） =====
        def optimize(a_ref, b_ref, unrestricted=False):
            best = None
            wp_range = range(1, int(960 / a_ref - w) + 1) if unrestricted else range(wp_init - 3, wp_init + 4)
            dp_limit = int((1100 - mt * 2) / b_ref - d)
            dp_range = range(1, dp_limit + 1) if unrestricted else range(dp_init - 3, dp_init + 4)

            for wp in wp_range:
                for dp in dp_range:
                    if wp < 1 or dp < 1:
                        continue
                    a = min(a_ref, math.floor(960 / (w + wp)))
                    b = min(b_ref, math.floor((1100 - mt * 2) / (d + dp)))
                    if a == 0 or b == 0:
                        continue
                    wc = w + wp
                    dc = d + dp
                    ds = mt * 2 + (d + dp) * b
                    L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c - 7
                    if L > 8:
                        score = a * b
                        if (best is None or
                            score > best['score'] or
                            (score == best['score'] and ds < best['ds'])):
                            best = {
                                'a': a, 'b': b, 'wp': wp, 'dp': dp,
                                'wc': wc, 'dc': dc, 'ds': ds, 'L': L,
                                'score': score
                            }
            return best

        # ===== 最適化手順 =====
        result = optimize(a0, b0, unrestricted=False)
        if not result:
            result1 = optimize(a0 - 1, b0, unrestricted=True)
            result2 = optimize(a0, b0 - 1, unrestricted=True)
            candidates = [r for r in [result1, result2] if r]
            if candidates:
                result = max(candidates, key=lambda x: (x['score'], -x['ds']))

        # ===== 出力 =====
        if result:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown("【最適化結果（L > 8 を満たす最大 a×b 構成）】")
            st.write(f"幅採り数 a = {result['a']}")
            st.write(f"送り採り数 b = {result['b']}")
            st.write(f"キャビピッチ wc = {result['wc']}")
            st.write(f"キャビピッチ dc = {result['dc']}")
            st.write(f"型寸送り ds = {result['ds']}")
            st.write(f"L = {result['L']:.3f}")
            st.markdown('<span style="color: green;">※Lが8以下のため、自動最適化されました。</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("L > 8 を満たす割り付けが見つかりませんでした。")

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
