# Streamlit 用の調整後のフィレット計算ファイルを作成

streamlit_file_content = """
import streamlit as st
import math

# 入力値
w = st.number_input("短側寸法 w（製品巾）", value=175.0)
d = st.number_input("長側寸法 d（製品送り）", value=175.0)
c = st.number_input("フィレット半径 c", value=5.0)
convex = st.number_input("カットからの凸", value=3.0)
z = st.number_input("全高 z", value=50.0)
has_inner_outer_lid = st.checkbox("内外嵌合蓋", value=False)

# 内外嵌合蓋がある場合、凸を8に固定
if has_inner_outer_lid:
    convex = 8.0

# 固定値
max_width_limit = 975
mt = 20 if z >= 50 else 13
wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
if z >= 50:
    wpz = 20

# フィレット中心の計算
mx = d / 2 - c
my = w / 2 - c

# 初期化
a0 = math.floor(max_width_limit / (w + wpz))
b0 = math.floor((1100 - mt * 2) / (d + wpz))

# 最適化関数
def optimize_adjusted(a_ref, b_ref):
    best = None
    wp_range = range(1, int(max_width_limit / a_ref - w) + 1)
    dp_limit = int((1100 - mt * 2) / b_ref - d)
    dp_range = range(1, dp_limit + 1)

    for wp in wp_range:
        for dp in dp_range:
            if wp < 1 or dp < 1:
                continue
            a = min(a_ref, math.floor(max_width_limit / (w + wp)))
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

# 最適化実行
if st.button("計算する"):
    result_adjusted = optimize_adjusted(a0, b0)

    if result_adjusted:
        a = result_adjusted['a']
        wc = result_adjusted['wc']
        horizontal_check = a * wc <= max_width_limit

        # 結果表示
        st.write("### 調整後のフィレット計算結果")
        st.write("**幅取り数 (a)**:", result_adjusted['a'])
        st.write("**送り取り数 (b)**:", result_adjusted['b'])
        st.write("**キャビピッチ (wc)**:", result_adjusted['wc'], "mm")
        st.write("**送りキャビピッチ (dc)**:", result_adjusted['dc'], "mm")
        st.write("**型寸送り (ds)**:", result_adjusted['ds'], "mm")
        st.write("**フィレット距離 (L)**:", result_adjusted['L'], "mm")
        st.write("**製品数 (a×b)**:", result_adjusted['score'])
        st.write("**横取り判定**:", "OK" if horizontal_check else "NG")
    else:
        st.error("条件を満たす結果が見つかりませんでした。")
"""

# ファイルに保存
streamlit_file_path = '/mnt/data/adjusted_fillet_streamlit.py'
with open(streamlit_file_path, 'w') as file:
    file.write(streamlit_file_content)

streamlit_file_path
