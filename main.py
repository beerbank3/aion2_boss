import streamlit as st

st.set_page_config(page_title="아이온2 필보 정산기", page_icon="💎", layout="wide")

BOSS_LIST = ["노블루드", "카루카", "구루타", "쉬바나", "기타"]

# ── 초기화 ─────────────────────────────────────────────────
if "items" not in st.session_state:
    st.session_state["items"] = []
if "uid_counter" not in st.session_state:
    st.session_state["uid_counter"] = 0


def new_uid():
    st.session_state["uid_counter"] += 1
    return st.session_state["uid_counter"]


def init_item(name=""):
    return {
        "uid": new_uid(),
        "name": name,
        "price": 0,
        "fail_open": False,
        "fails": [],          # [{"fuid": int, "price": int}, ...]
    }


def new_fail():
    return {"fuid": new_uid(), "price": 0}


# ── 이벤트 선처리 ──────────────────────────────────────────
# 보스 버튼 → 아이템 추가
for boss in BOSS_LIST:
    if st.session_state.pop(f"_add_boss_{boss}", False):
        st.session_state["items"].append(init_item(boss))
        st.rerun()

# 아이템 삭제
for item in list(st.session_state["items"]):
    if st.session_state.pop(f"_del_item_{item['uid']}", False):
        st.session_state["items"] = [
            it for it in st.session_state["items"] if it["uid"] != item["uid"]
        ]
        st.rerun()

# 미판매 항목 추가
for item in st.session_state["items"]:
    if st.session_state.pop(f"_add_fail_{item['uid']}", False):
        item["fails"].append(new_fail())
        st.rerun()

# 미판매 항목 삭제
for item in st.session_state["items"]:
    for f in list(item["fails"]):
        if st.session_state.pop(f"_del_fail_{item['uid']}_{f['fuid']}", False):
            item["fails"] = [x for x in item["fails"] if x["fuid"] != f["fuid"]]
            st.rerun()


# ── 헤더 ───────────────────────────────────────────────────
st.title("💎 아이온2 필보 정산기")
st.caption("거래소 80% 정산 · 등록비 2% · 수수료 10% 모두 반영")

k = st.number_input("총 인원 (판매자 포함)", min_value=1, value=6, step=1, key="members")

st.divider()

left, right = st.columns(2, gap="large")

# ── 왼쪽 ───────────────────────────────────────────────────
with left:
    st.subheader("판매 아이템")

    # 보스 추가 버튼
    st.caption("보스를 선택해 아이템 추가")
    boss_cols = st.columns(len(BOSS_LIST))
    for idx, boss in enumerate(BOSS_LIST):
        with boss_cols[idx]:
            st.button(boss, key=f"_add_boss_{boss}", use_container_width=True)

    items = st.session_state["items"]

    if not items:
        st.markdown(
            "<div style='text-align:center;padding:2rem 0;"
            "color:rgba(120,120,120,.5);font-size:13px'>"
            "위 버튼을 눌러 아이템을 추가하세요</div>",
            unsafe_allow_html=True,
        )
    else:
        for idx, item in enumerate(items):
            uid = item["uid"]

            with st.container(border=True):
                # 아이템명 + 삭제
                c_name, c_del = st.columns([0.85, 0.15])
                with c_name:
                    item["name"] = st.text_input(
                        "아이템명",
                        value=item["name"],
                        placeholder="아이템 이름",
                        key=f"name_{uid}",
                        label_visibility="collapsed",
                    )
                with c_del:
                    st.button("✕", key=f"_del_item_{uid}", use_container_width=True)

                # 판매가
                item["price"] = st.number_input(
                    "판매가 (원)",
                    min_value=0,
                    value=item["price"],
                    step=10000,
                    format="%d",
                    key=f"price_{uid}",
                )

                # 미판매 등록금 토글
                fail_total = sum(f["price"] for f in item["fails"])
                n_fails = len(item["fails"])

                toggle_label = "미판매 등록금"
                if not item["fail_open"] and n_fails > 0 and fail_total > 0:
                    toggle_label += f" · {n_fails}건  –{int(fail_total * 0.02):,}원"

                item["fail_open"] = st.toggle(
                    toggle_label,
                    value=item["fail_open"],
                    key=f"fail_toggle_{uid}",
                )

                if item["fail_open"]:
                    # 처음 열면 항목 1개 자동 추가
                    if not item["fails"]:
                        item["fails"].append(new_fail())
                        st.rerun()

                    st.markdown(
                        "<div style='background:rgba(162,45,45,.05);"
                        "border:0.5px solid rgba(162,45,45,.2);"
                        "border-radius:8px;padding:8px 10px;margin-top:4px'>",
                        unsafe_allow_html=True,
                    )

                    for j, f in enumerate(item["fails"]):
                        fuid = f["fuid"]
                        fc1, fc2, fc3 = st.columns([0.18, 0.64, 0.18])
                        with fc1:
                            st.markdown(
                                f"<p style='font-size:12px;color:#A32D2D;"
                                f"padding-top:8px;margin:0'>{j+1}회차</p>",
                                unsafe_allow_html=True,
                            )
                        with fc2:
                            new_val = st.number_input(
                                "등록가",
                                min_value=0,
                                value=f["price"],
                                step=10000,
                                format="%d",
                                key=f"fail_{uid}_{fuid}",
                                label_visibility="collapsed",
                            )
                            f["price"] = new_val
                            if new_val > 0:
                                st.caption(f"차감 –{int(new_val * 0.02):,}원")
                        with fc3:
                            if len(item["fails"]) > 1:
                                st.button(
                                    "✕",
                                    key=f"_del_fail_{uid}_{fuid}",
                                    use_container_width=True,
                                )

                    st.button("+ 재등록 추가", key=f"_add_fail_{uid}")

                    cur_total = sum(f["price"] for f in item["fails"])
                    if cur_total > 0:
                        st.markdown(
                            f"<div style='border-top:0.5px solid rgba(162,45,45,.25);"
                            f"margin-top:8px;padding-top:6px;"
                            f"display:flex;justify-content:space-between;align-items:center'>"
                            f"<span style='font-size:11px;color:#A32D2D'>차감 합계 ×2%</span>"
                            f"<b style='font-size:12px;color:#A32D2D'>"
                            f"–{int(cur_total * 0.02):,}원</b></div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown("</div>", unsafe_allow_html=True)


# ── 계산 ───────────────────────────────────────────────────
items = st.session_state["items"]

total_sales = sum(it["price"] for it in items)

total_fail_deduct = sum(
    sum(f["price"] for f in it["fails"]) * 0.02
    for it in items
    if it["fail_open"] and it["fails"]
)

pure_profit    = total_sales * 0.78
listing_price  = (pure_profit / (k - 0.12)) - total_fail_deduct
real_share     = listing_price * 0.88
total_transfer = listing_price * (k - 1)
seller_pocket  = pure_profit - total_transfer
has_data       = total_sales > 0


# ── 오른쪽: 정산 결과 ──────────────────────────────────────
def detail_row(label, value, red=False):
    cl, cr = st.columns([0.6, 0.4])
    with cl:
        st.caption(label)
    with cr:
        st.markdown(
            f"<p style='text-align:right;font-size:13px;font-weight:600;"
            f"color:{'#A32D2D' if red else 'inherit'};margin:0'>{value}</p>",
            unsafe_allow_html=True,
        )


with right:
    st.subheader("정산 결과")

    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            "인당 실수령액",
            f"{int(real_share):,} 원" if has_data else "—",
            help="등록비·수수료 제외 실이득",
        )
    with m2:
        st.metric(
            "팀원 등록 가격",
            f"{int(listing_price):,} 원" if has_data else "—",
            help="거래소에 이 금액으로 등록하세요",
        )

    st.divider()

    named = [
        f"{it['name']} {it['price']:,}원"
        for it in items
        if it["name"] and it["price"] > 0
    ]
    if named:
        st.caption("  ·  ".join(named))

    st.markdown("**판매 요약**")
    detail_row("아이템 합계", f"{int(total_sales):,} 원" if has_data else "—")
    detail_row("판매자 정산금 (×0.78)", f"{int(pure_profit):,} 원" if has_data else "—")
    if total_fail_deduct > 0:
        detail_row("미판매 등록금 차감 (×2%)", f"–{int(total_fail_deduct):,} 원", red=True)

    st.divider()

    st.markdown("**분배 내역**")
    detail_row("팀원 등록 가격", f"{int(listing_price):,} 원" if has_data else "—")
    detail_row(f"팀원 {int(k)-1}명 총 이체액", f"{int(total_transfer):,} 원" if has_data else "—")
    detail_row("판매자 잔액", f"{int(seller_pocket):,} 원" if has_data else "—")
    detail_row("팀원 최종 실수령액", f"{int(real_share):,} 원" if has_data else "—")