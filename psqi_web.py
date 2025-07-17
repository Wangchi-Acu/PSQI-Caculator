#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from datetime import datetime
import csv, os

# ---------- 业务函数 ----------
def calculate_sleep_efficiency(bed, getup, choice):
    try:
        bed_t  = datetime.strptime(bed,  "%H:%M").time()
        get_t  = datetime.strptime(getup, "%H:%M").time()
        bed_dt = datetime(2000, 1, 1, bed_t.hour, bed_t.minute)
        get_dt = datetime(2000, 1, 2 if get_t < bed_t else 1, get_t.hour, get_t.minute)
        bed_d  = (get_dt - bed_dt).total_seconds() / 3600
        dur_map = {1: 7.5, 2: 6.5, 3: 5.5, 4: 4.5}
        actual  = dur_map.get(choice, 0)
        return (actual / bed_d * 100) if bed_d else 0
    except:
        return 0

def get_component_score(eff):
    if eff > 85: return 0
    elif 75 <= eff <= 84: return 1
    elif 65 <= eff <= 74: return 2
    else: return 3

def calculate_psqi(data):
    A = data['q6'] - 1
    lat = data['sleep_latency_choice'] - 1
    q5a = data['q5a'] - 1
    B = 0 if lat+q5a==0 else (1 if lat+q5a<=2 else 2 if lat+q5a<=4 else 3)
    C = data['sleep_duration_choice'] - 1
    eff = calculate_sleep_efficiency(data['bed_time'], data['getup_time'], data['sleep_duration_choice'])
    D = get_component_score(eff)
    E_items = ['q5b','q5c','q5d','q5e','q5f','q5g','q5h','q5i','q5j']
    E_score = sum(data[k]-1 for k in E_items)
    E = 0 if E_score==0 else 1 if E_score<=9 else 2 if E_score<=18 else 3
    F = data['q7'] - 1
    G_total = (data['q8']-1)+(data['q9']-1)
    G = 0 if G_total==0 else 1 if G_total<=2 else 2 if G_total<=4 else 3
    total = A+B+C+D+E+F+G
    return {'A':A,'B':B,'C':C,'D':D,'E':E,'F':F,'G':G,'total':total,'eff':eff}

# ---------- Streamlit 界面 ----------
st.set_page_config(page_title="匹兹堡睡眠质量指数(PSQI)", layout="centered")
st.title("江苏省中医院针灸科失眠专病门诊")
st.markdown(
    "<h3 style='color:#555555;'>匹兹堡睡眠质量指数（PSQI）在线问卷</h3>",
    unsafe_allow_html=True
)
st.markdown("> 请根据 **最近一个月** 的实际情况填写")

with st.form("psqi_form"):
    st.subheader("① 基本信息")
    name   = st.text_input("姓名")
    age    = st.number_input("年龄", 1, 120, 25)
    height = st.number_input("身高(cm)", 50, 250, 170)
    weight = st.number_input("体重(kg)", 20, 200, 65)
    contact= st.text_input("联系方式")

    st.subheader("② 睡眠习惯")
    bed   = st.text_input("晚上上床时间 (HH:MM)", value="23:30")
    getup = st.text_input("早上起床时间 (HH:MM)", value="07:00")
    latency = st.selectbox("入睡所需时间", ["≤15分钟","16-30分钟","31-60分钟","≥60分钟"], index=1)
    duration = st.selectbox("实际睡眠小时数", [">7小时","6-7小时","5-6小时","<5小时"], index=1)

    st.subheader("③ 睡眠问题（每周发生频率）")
    opts = ["没有","少于1次","1-2次","3次以上"]
    q5a = st.selectbox("a. 入睡困难", opts, index=0)
    q5b = st.selectbox("b. 夜间易醒或早醒", opts, index=0)
    q5c = st.selectbox("c. 夜间去厕所", opts, index=0)
    q5d = st.selectbox("d. 呼吸不畅", opts, index=0)
    q5e = st.selectbox("e. 咳嗽或鼾声高", opts, index=0)
    q5f = st.selectbox("f. 感觉冷", opts, index=0)
    q5g = st.selectbox("g. 感觉热", opts, index=0)
    q5h = st.selectbox("h. 做恶梦", opts, index=0)
    q5i = st.selectbox("i. 疼痛不适", opts, index=0)
    q5j = st.selectbox("j. 其他影响", opts, index=0)

    st.subheader("④ 其他")
    q6 = st.selectbox("总体睡眠质量", ["很好","较好","较差","很差"], index=1)
    q7 = st.selectbox("使用催眠药物", ["没有","少于1次","1-2次","3次以上"], index=0)
    q8 = st.selectbox("白天困倦", ["没有","少于1次","1-2次","3次以上"], index=0)
    q9 = st.selectbox("精力不足", ["没有","少于1次","1-2次","3次以上"], index=0)

    submitted = st.form_submit_button("提交问卷")

if submitted:
    data = {
        "name":name, "age":age, "height":height, "weight":weight, "contact":contact,
        "bed_time":bed, "getup_time":getup,
        "sleep_latency_choice":["≤15分钟","16-30分钟","31-60分钟","≥60分钟"].index(latency)+1,
        "sleep_duration_choice":[">7小时","6-7小时","5-6小时","<5小时"].index(duration)+1,
        "q5a":opts.index(q5a)+1,"q5b":opts.index(q5b)+1,"q5c":opts.index(q5c)+1,
        "q5d":opts.index(q5d)+1,"q5e":opts.index(q5e)+1,"q5f":opts.index(q5f)+1,
        "q5g":opts.index(q5g)+1,"q5h":opts.index(q5h)+1,"q5i":opts.index(q5i)+1,
        "q5j":opts.index(q5j)+1,"q6":["很好","较好","较差","很差"].index(q6)+1,
        "q7":opts.index(q7)+1,"q8":opts.index(q8)+1,"q9":opts.index(q9)+1
    }
    res = calculate_psqi(data)

        # ---------- 生成目录 & 文件名 ----------
    save_dir = r"F:\10量表结果"
    os.makedirs(save_dir, exist_ok=True)                       # 若目录不存在则创建
    now_str = datetime.now().strftime("%Y%m%d_%H%M")           # 年月日_时分
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    csv_name = f"{now_str}_{safe_name}.csv"
    csv_path = os.path.join(save_dir, csv_name)

    # ---------- 写本地文件 ----------
    head = ["姓名","年龄","身高","体重","联系方式","上床时间","起床时间","入睡选项","睡眠选项",
            "q5a","q5b","q5c","q5d","q5e","q5f","q5g","q5h","q5i","q5j","q6","q7","q8","q9",
            "A","B","C","D","E","F","G","总分","效率%"]
    row = [data[k] for k in ["name","age","height","weight","contact","bed_time","sleep_latency_choice","getup_time","sleep_duration_choice",
                             "q5a","q5b","q5c","q5d","q5e","q5f","q5g","q5h","q5i","q5j","q6","q7","q8","q9"]] \
          + [res[k] for k in ["A","B","C","D","E","F","G","total"]] + [f"{res['eff']:.1f}"]
    pd.DataFrame([row], columns=head).to_csv(csv_path, index=False, encoding='utf-8-sig')

    # ---------- 网页下载按钮 ----------
    with open(csv_path, "rb") as f:
        st.download_button(
            label="📥 下载本次结果 (CSV)",
            data=f,
            file_name=csv_name,
            mime="text/csv"
        )

        st.success("提交成功！结果已保存到本地，并可下载 CSV")
    # -------------------- 详细得分展示 --------------------
    st.subheader("📊 各成分得分")
    score_df = pd.DataFrame({
        "成分": ["A 睡眠质量", "B 入睡时间", "C 睡眠时间",
                 "D 睡眠效率", "E 睡眠障碍", "F 催眠药物", "G 日间功能"],
        "得分": [res["A"], res["B"], res["C"],
                 res["D"], res["E"], res["F"], res["G"]]
    })
    # 表格
    st.dataframe(score_df, use_container_width=True)

    # 条形图
    chart = st.bar_chart(score_df.set_index("成分")["得分"])

    # 总分与解读
    level = "很好" if res["total"] <= 5 else \
            "尚可" if res["total"] <= 10 else \
            "一般" if res["total"] <= 15 else "很差"
    st.metric("🎯 PSQI 总分", f"{res['total']} 分", delta=None)
    st.info(f"综合评定：睡眠质量 **{level}**")
