import streamlit as st

st.title("아이온2 필보 정산기")
st.caption("판매자 2%+20% / 팀원 2%+10% 수수료 모두 반영")

# 입력창
prices_str = st.text_input("아이템 총 판매 가격 (만원 단위)", "750 750")
k = st.number_input("총 인원 (판매자 포함)", min_value=1, value=6)

# [계산 로직]
total_sales = sum([int(p) for p in prices_str.split() if p.strip()]) * 10000

# 1. 판매자 순수 정산액 (0.78T)
pure_profit = total_sales * 0.78

# 2. 팀원들이 거래소에 등록해야 할 가격 (P)
# 공식: P = pure_profit / (k - 0.12)
listing_price = pure_profit / (k - 0.12)

# 3. 인당 최종 실수령액 (X = 0.88P)
real_share = listing_price * 0.88

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("👤 인당 최종 실수령액", f"{int(real_share):,} 원")
    st.caption("등록비/수수료 뺀 진짜 이득")
with col2:
    st.warning("🚀 팀원 등록 가격")
    st.header(f"{int(listing_price):,} 원")
    st.caption("팀원들이 올릴 잡동사니 가격")

with st.expander("계산 과정 및 검증"):
    st.write(f"1. 총 판매 정산금 (80% 정산 - 2% 등록비): {int(pure_profit):,}원")
    st.write(f"2. 팀원에게 보낼 돈 총합: {int(listing_price):,}원 × {k-1}명 = {int(listing_price * (k-1)):,}원")
    st.write(f"3. 판매자 잔액: {int(pure_profit - listing_price * (k-1)):,}원")
    st.write(f"4. 판매자가 처음에 쓴 등록비는 이미 정산금에서 뺐으므로 위 잔액이 실제 이득입니다.")
    st.write(f"5. 팀원 실수령: {int(listing_price):,}원 - (10%수수료 + 2%등록비) = {int(real_share):,}원")