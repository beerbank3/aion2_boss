import streamlit as st

st.title("아이온2 필드 보스 정산 도우미")

# 입력창
prices_str = st.text_input("아이템 가격들을 입력하세요 (공백 구분, 만원 단위)", "1000 2000 3000")
k = st.number_input("나눌 인원 수", min_value=1, value=4)
a = st.number_input("빼야할 추가금이 있으면 알려주세요 (원 단위 그대로 입력)")

# 계산 로직
prices = [int(p) for p in prices_str.split() if p.strip()]
total_n = sum(prices) * 10000
actual_received = total_n * 0.8
reg_fee = total_n * 0.02
distributable = actual_received - reg_fee
if a > 0:
    distributable = distributable - a

# 결과 화면
st.divider()
st.metric("1인당 분배금", f"{int(distributable / k):,} 원")

with st.expander("세부 내역 보기"):
    st.write(f"총 판매액: {total_n:,}원")
    st.write(f"거래소 정산금(80%): {int(actual_received):,}원")
    st.write(f"등록 수수료(2%): {int(reg_fee):,}원")