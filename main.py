import streamlit as st

st.set_page_config(page_title="아이온2 필보 정산기", page_icon="💎", layout="wide")

st.title("💎 아이온2 필보 정산기")
st.caption("거래소 80% 정산 · 등록비 2% · 수수료 10% 모두 반영")

# ── 총 인원 (최상단) ────────────────────────────────────────
k = st.number_input("총 인원 (판매자 포함)", min_value=1, value=6, step=1)

st.divider()

left, right = st.columns(2, gap="large")

# ── 왼쪽: 판매 아이템 입력 ─────────────────────────────────
with left:
    st.subheader("판매 아이템")

    if "items" not in st.session_state:
        st.session_state.items = [
            {"name": "필보", "price": 7500000, "fail_open": False, "fails": []},
            {"name": "필보", "price": 7500000, "fail_open": False, "fails": []},
        ]

    items = st.session_state.items

    to_delete = None

    for i, item in enumerate(items):
        with st.container(border=True):
            col_num, col_name, col_del = st.columns([0.08, 0.78, 0.14])
            with col_num:
                st.markdown(
                    f"<div style='width:22px;height:22px;border-radius:50%;"
                    f"background:#FAEEDA;color:#633806;font-size:11px;font-weight:600;"
                    f"display:flex;align-items:center;justify-content:center;margin-top:6px'>"
                    f"{i+1}</div>",
                    unsafe_allow_html=True,
                )
            with col_name:
                item["name"] = st.text_input(
                    "아이템 이름",
                    value=item["name"],
                    placeholder="아이템 이름",
                    key=f"name_{i}",
                    label_visibility="collapsed",
                )
            with col_del:
                if len(items) > 1:
                    if st.button("✕", key=f"del_{i}", use_container_width=True):
                        to_delete = i

            item["price"] = st.number_input(
                "판매가 (원)",
                min_value=0,
                value=item["price"],
                step=10000,
                format="%d",
                key=f"price_{i}",
            )

            # 미판매 등록금 토글
            fail_count = len(item["fails"])
            fail_total = sum(f for f in item["fails"])
            fail_deduct = fail_total * 0.02

            chip_label = "미판매 등록금"
            if not item["fail_open"] and fail_count > 0:
                chip_label += f" · {fail_count}건  –{int(fail_deduct):,}원"

            item["fail_open"] = st.toggle(
                chip_label,
                value=item["fail_open"],
                key=f"fail_toggle_{i}",
            )

            if item["fail_open"]:
                # 초기 항목 자동 추가
                if len(item["fails"]) == 0:
                    item["fails"].append(0)

                st.markdown(
                    "<div style='background:rgba(162,45,45,.06);"
                    "border:0.5px solid rgba(162,45,45,.25);"
                    "border-radius:8px;padding:10px 12px;margin-top:4px'>",
                    unsafe_allow_html=True,
                )

                updated_fails = []
                fail_to_remove = None

                for j, fp in enumerate(item["fails"]):
                    fc1, fc2, fc3 = st.columns([0.22, 0.62, 0.16])
                    with fc1:
                        st.markdown(
                            f"<p style='font-size:12px;color:#A32D2D;"
                            f"margin:0;padding-top:10px'>{j+1}회차</p>",
                            unsafe_allow_html=True,
                        )
                    with fc2:
                        val = st.number_input(
                            f"등록가",
                            min_value=0,
                            value=fp,
                            step=10000,
                            format="%d",
                            key=f"fail_{i}_{j}",
                            label_visibility="collapsed",
                        )
                        updated_fails.append(val)
                    with fc3:
                        if len(item["fails"]) > 1:
                            if st.button("✕", key=f"fail_del_{i}_{j}"):
                                fail_to_remove = j
                        else:
                            st.write("")

                    # 차감액 미리보기
                    if val > 0:
                        st.caption(f"차감액: –{int(val * 0.02):,}원")

                item["fails"] = updated_fails
                if fail_to_remove is not None:
                    item["fails"].pop(fail_to_remove)

                if st.button("+ 재등록 추가", key=f"fail_add_{i}"):
                    item["fails"].append(0)

                # 차감 합계
                cur_fail_total = sum(item["fails"])
                if cur_fail_total > 0:
                    st.markdown(
                        f"<div style='border-top:0.5px solid rgba(162,45,45,.3);"
                        f"margin-top:8px;padding-top:6px;display:flex;"
                        f"justify-content:space-between'>"
                        f"<span style='font-size:11px;color:#A32D2D'>차감 합계 ×2%</span>"
                        f"<b style='font-size:12px;color:#A32D2D'>–{int(cur_fail_total * 0.02):,}원</b>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

    if to_delete is not None:
        st.session_state.items.pop(to_delete)
        st.rerun()

    if st.button("＋ 아이템 추가", use_container_width=True):
        st.session_state.items.append(
            {"name": "", "price": 0, "fail_open": False, "fails": []}
        )
        st.rerun()


# ── 계산 ───────────────────────────────────────────────────
total_sales = sum(item["price"] for item in items)
total_fail_deduct = sum(
    sum(f for f in item["fails"]) * 0.02
    for item in items
    if item["fail_open"]
)

pure_profit = total_sales * 0.78
listing_price = (pure_profit / (k - 0.12)) - total_fail_deduct
real_share = listing_price * 0.88
total_transfer = listing_price * (k - 1)
seller_pocket = pure_profit - total_transfer


# ── 오른쪽: 정산 결과 ──────────────────────────────────────
with right:
    st.subheader("정산 결과")

    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            "인당 실수령액",
            f"{int(real_share):,} 원" if total_sales > 0 else "—",
            help="등록비·수수료 제외 실이득",
        )
    with m2:
        st.metric(
            "팀원 등록 가격",
            f"{int(listing_price):,} 원" if total_sales > 0 else "—",
            help="거래소에 이 금액으로 올려주세요",
        )

    st.divider()

    # 판매 요약
    st.markdown("**판매 요약**")

    named = [
        f"{it['name']} {it['price']:,}원"
        for it in items
        if it["name"] and it["price"] > 0
    ]
    if named:
        st.caption("  ·  ".join(named))

    rows_summary = [
        ("아이템 합계", f"{int(total_sales):,} 원"),
        ("판매자 정산금 (×0.78)", f"{int(pure_profit):,} 원"),
    ]
    if total_fail_deduct > 0:
        rows_summary.append(("미판매 등록금 차감 (×2%)", f"–{int(total_fail_deduct):,} 원"))

    for label, value in rows_summary:
        col_l, col_r = st.columns([0.6, 0.4])
        with col_l:
            st.caption(label)
        with col_r:
            color = "red" if "차감" in label else "inherit"
            st.markdown(
                f"<p style='text-align:right;font-size:13px;font-weight:600;"
                f"color:{'#A32D2D' if '차감' in label else 'inherit'}'>{value}</p>",
                unsafe_allow_html=True,
            )

    st.divider()

    # 분배 내역
    st.markdown("**분배 내역**")

    rows_dist = [
        ("팀원 등록 가격", f"{int(listing_price):,} 원"),
        (f"팀원 {k-1}명 총 이체액", f"{int(total_transfer):,} 원"),
        ("판매자 잔액", f"{int(seller_pocket):,} 원"),
        ("팀원 최종 실수령액", f"{int(real_share):,} 원"),
    ]

    for label, value in rows_dist:
        col_l, col_r = st.columns([0.6, 0.4])
        with col_l:
            st.caption(label)
        with col_r:
            st.markdown(
                f"<p style='text-align:right;font-size:13px;font-weight:600'>{value}</p>",
                unsafe_allow_html=True,
            )