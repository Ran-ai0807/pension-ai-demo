import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import json

API_KEY = "sk-2bf21edd80a04a409d01d6c6d674fe14"
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

st.set_page_config(page_title="AI养老生态智能精算系统", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
    h1, h2, h3 { color: #1d1d1f; font-weight: 600; }
    .stMetric { background-color: rgba(255, 255, 255, 0.8); padding: 15px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); border: 1px solid rgba(255, 255, 255, 0.6); }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.6); backdrop-filter: blur(10px); border-right: 1px solid rgba(0, 0, 0, 0.05); }
    .ai-report { background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("AI 驱动的养老金融全景决策沙盘")
st.caption("政策端精算 × 个人端税优 × 智能方案推荐 × 健康情感联动 × 大语言模型中枢")
with st.sidebar:
    st.header("1. 评估模式")
    mode = st.radio("面向人群", ["年轻预备役（积累期）", "银发一族（消耗期）"])
    gender = st.selectbox("性别", ["男", "女"])
    
    st.header("2. 政策端精算")
    base_salary = st.number_input("当前/预期月薪（元）", 3000, 50000, 10000)
    pay_years = st.slider("累计缴费年限（年）", 15, 40, 25)
    retire_age = st.slider("计划退休年龄", 55, 65, 60)
    avg_wage = st.number_input("当地社平工资（元/月）", 5000, 20000, 8000)
    pay_index = st.slider("平均缴费工资指数", 0.6, 3.0, 1.0, 0.1)
    
    if mode == "年轻预备役（积累期）":
        st.header("3. 个人资产预估")
        savings = st.number_input("目前存款（万元）", 0, 500, 20)
        monthly_income = st.number_input("预计退休后总收入（元）", 2000, 30000, 8000)
        monthly_spend = st.number_input("预计退休后月支出（元）", 2000, 30000, 6000)
    else:
        st.header("3. 老人当前档案")
        savings = st.number_input("当前养老储备（万元）", 0, 500, 80)
        monthly_income = st.number_input("当前月总收入（元）", 2000, 30000, 5000)
        monthly_spend = st.number_input("当前每月支出（元）", 2000, 30000, 4500)
        
    st.header("4. 个人养老金规划")
    pp_contribute = st.number_input("每年缴存额度（元）", 0, 12000, 12000, step=1000)
    pp_years = st.slider("预计缴存年限（年）", 1, 30, 15)
    pp_withdraw_years = st.slider("预计领取年限（年）", 10, 30, 15)
    
    st.header("5. 投资偏好")
    risk_pref = st.selectbox("风险偏好方案", ["保守型", "稳健型", "激进型", "自定义"])
    
    if risk_pref == "保守型":
        default_eq = 20
    elif risk_pref == "稳健型":
        default_eq = 50
    elif risk_pref == "激进型":
        default_eq = 80
    else:
        default_eq = 50
        
    custom_eq = st.slider("自定义权益类比例 %", 0, 100, default_eq)

    st.header("6. 健康与情感")
    health = st.select_slider("健康自评", ["较差", "一般", "良好"], value="一般")
    lonely = st.selectbox("陪伴情况", ["独居，很少与人交流", "偶尔有人探望", "家人日常陪伴"])
st.markdown("### AI 智能对话与意图解析")
user_text = st.text_area("请用大白话描述您的现状或担忧（AI 将自动提取参数并覆盖左侧滑块）：", 
                         placeholder="例如：我40岁，单亲妈妈，每个月有5000房贷，现在公司还在裁员，我很焦虑...", 
                         height=100)

if st.button("启动 AI 深度演算与全量评估", type="primary", use_container_width=True):
    ai_raw_report = ""
    ai_audit = ""
    
    if user_text:
        with st.spinner("AI 大脑正在解析您的语义、检索算法伦理文献并进行逻辑推演..."):
            prompt = f"""
            你是一个具备极高专业素养的养老金融精算师和算法伦理审计员。
            用户背景：{user_text}
            任务：
            1. 理解用户的白话描述，提炼出核心财务矛盾。
            2. 结合学术研究对该用户进行风险审计。
            3. 给出带有同理心的人话版评估档案。
            4. 输出权益类资产比例（equity_ratio）和建议年缴个人养老金金额（pp_contribute）。
            严格输出JSON格式：{{"equity_ratio": 数值, "pp_contribute": 数值, "audit_text": "审计警告", "human_report": "人话档案"}}
            """
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                res_data = json.loads(response.choices[0].message.content)
                custom_eq = res_data.get("equity_ratio", custom_eq)
                pp_contribute = res_data.get("pp_contribute", pp_contribute)
                ai_audit = res_data.get("audit_text", "")
                ai_raw_report = res_data.get("human_report", "")
            except Exception as e:
                st.error(f"AI 解析失败，请检查 API 网络或额度。错误：{e}")
                
    if ai_raw_report:
        html_content = f'<div class="ai-report"><h4>AI 专属诊断档案</h4><p>{ai_raw_report}</p><p style="color:red; font-weight:bold;">{ai_audit}</p></div>'
        st.markdown(html_content, unsafe_allow_html=True)
def calc_pension(base_salary, pay_years, avg_wage, pay_index, retire_age):
    months_map = {55: 170, 60: 139, 65: 101}
    months = months_map.get(retire_age, 139)
    base_pension = avg_wage * (1 + pay_index) / 2 * pay_years * 0.01
    personal_account = base_salary * 0.08 * 12 * pay_years
    account_pension = personal_account / months
    total_pension = base_pension + account_pension
    result_dict = {
        "基础养老金": round(base_pension, 2), 
        "个人账户养老金": round(account_pension, 2), 
        "合计月养老金": round(total_pension, 2)
    }
    return result_dict

def calc_pp(pp_contribute, pp_years, eq_ratio):
    total_contribute = pp_contribute * pp_years
    expected_return = (eq_ratio / 100) * 0.07 + (1 - eq_ratio / 100) * 0.03
    future_value = 0
    for _ in range(pp_years):
        future_value = (future_value + pp_contribute) * (1 + expected_return)
    tax_saved = total_contribute * 0.1
    tax_on_withdraw = future_value * 0.03
    net_value = future_value - tax_on_withdraw + tax_saved
    result_dict = {
        "累计本金": total_contribute, 
        "预计账户价值": round(future_value, 2), 
        "净收益": round(net_value, 2), 
        "预期年化": round(expected_return * 100, 1)
    }
    return result_dict

pension_result = calc_pension(base_salary, pay_years, avg_wage, pay_index, retire_age)
pp_result = calc_pp(pp_contribute, pp_years, custom_eq)
replacement_rate = pension_result["合计月养老金"] / base_salary * 100

st.subheader("模块一：政策端宏观评估")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("基础养老金（月）", f"¥{pension_result['基础养老金']:,}")
with col2:
    st.metric("个人账户养老金（月）", f"¥{pension_result['个人账户养老金']:,}")
with col3:
    st.metric("合计月养老金", f"¥{pension_result['合计月养老金']:,}", delta=f"替代率 {replacement_rate:.1f}%")

st.divider()

st.subheader("模块二：个人养老金税优与自定义配置")
p1, p2, p3, p4 = st.columns(4)
with p1:
    st.metric("累计本金", f"¥{pp_result['累计本金']:,}")
with p2:
    st.metric("预计账户价值", f"¥{pp_result['预计账户价值']:,}", delta=f"年化 {pp_result['预期年化']}%")
with p3:
    st.metric("预计节税", f"¥{pp_result['累计本金']*0.1:,}")
with p4:
    st.metric("净收益（含税优）", f"¥{pp_result['净收益']:,}")

df_pie = pd.DataFrame({"资产类型": ["固收类", "权益类"], "比例": [100-custom_eq, custom_eq]})
fig_pie = px.pie(df_pie, names="资产类型", values="比例", hole=0.6, color_discrete_sequence=['#007AFF', '#34C759'])
fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=250, paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_pie, use_container_width=True)
st.divider()

st.subheader("模块三：多方案横向对比")
scenarios = []
for idx in [0.6, 1.0, 1.5, 2.0, 3.0]:
    res = calc_pension(base_salary, pay_years, avg_wage, idx, retire_age)
    row_data = {
        "缴费指数": str(idx), 
        "月养老金": res["合计月养老金"], 
        "替代率(%)": round(res["合计月养老金"]/base_salary*100, 1)
    }
    scenarios.append(row_data)
    
df_sc = pd.DataFrame(scenarios)
fig_sc = px.bar(df_sc, x="缴费指数", y="月养老金", text="月养老金", color_discrete_sequence=['#007AFF'])
fig_sc.update_traces(texttemplate='¥%{text:,.0f}', textposition='outside')
fig_sc.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_sc, use_container_width=True)
st.dataframe(df_sc.set_index("缴费指数"), use_container_width=True)

st.divider()

st.subheader("模块四：健康与情感联动评估")
hc1, hc2, hc3 = st.columns(3)
with hc1:
    st.metric("建议权益比例", f"{custom_eq}%")
    st.metric("建议固收比例", f"{100-custom_eq}%")
with hc2:
    st.metric("健康风险分", "中风险")
    st.metric("综合风险等级", "需关注")
    st.info("建议接入智能监护设备。")
with hc3:
    if "独居" in lonely:
        st.metric("陪伴需求强度", "强")
        st.warning("重点关注防诈骗风险与AI幻觉。")
    else:
        st.metric("陪伴需求强度", "弱")
        st.success("情感满足度良好。")

st.subheader("模块五：生态健康度雷达图")
fin_score = 70
hea_score = 60
if "独居" in lonely:
    emo_score = 30
else:
    emo_score = 80
    
radar = go.Figure(data=go.Scatterpolar(r=[fin_score, hea_score, emo_score, fin_score], theta=["金融稳健度", "健康安全度", "情感满足度", "金融稳健度"], fill="toself", fillcolor="rgba(0, 122, 255, 0.2)", line_color="#007AFF"))
radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=300, paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(radar, use_container_width=True)

st.subheader("模块六：长寿风险与资金耗尽模拟")
net_withdraw = max(0, (monthly_spend - monthly_income - pension_result["合计月养老金"]) * 12)
np.random.seed(42)
n_sim = 500
returns = np.random.normal(0.04, 0.08, (n_sim, 40))
balances = np.zeros((n_sim, 41))
balances[:, 0] = savings * 10000
for t in range(1, 41):
    withdraw = net_withdraw * (1.03 ** (t - 1))
    balances[:, t] = balances[:, t-1] * (1 + returns[:, t-1]) - withdraw
    balances[:, t] = np.maximum(balances[:, t], 0)
depletion = []
for i in range(n_sim):
    zero = np.where(balances[i] <= 0)[0]
    depletion.append(retire_age + (zero[0] if len(zero) > 0 else 40))
fig_hist = px.histogram(x=depletion, nbins=20, labels={"x": "资金耗尽年龄", "y": "频次"}, color_discrete_sequence=['#FF3B30'])
fig_hist.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_hist, use_container_width=True)
st.caption(f"每月需额外动用存款：¥{net_withdraw/12:,.0f} | 500次模拟中位耗尽年龄：{int(np.median(depletion))} 岁")
st.divider()

st.subheader("模块七：退休后综合现金流推演")
pp_monthly_income = pp_result["预计账户价值"] / (pp_withdraw_years * 12)
savings_monthly_income = savings * 10000 * 0.04 / 12
cash_flow_data = pd.DataFrame({
    "收入来源": ["国家社保", "个人养老金", "存款理财补充"], 
    "金额": [pension_result["合计月养老金"], pp_monthly_income, savings_monthly_income]
})
fig_cf = px.bar(cash_flow_data, x="金额", y="收入来源", orientation='h', text="金额", color_discrete_sequence=['#FF9500'])
fig_cf.update_traces(texttemplate='¥%{text:,.0f}', textposition='outside')
fig_cf.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_cf, use_container_width=True)
total_monthly = pension_result["合计月养老金"] + pp_monthly_income + savings_monthly_income
st.success(f"**推演结果**：退休后您预计每月可支配总收入约为 **¥{total_monthly:,.0f}**。")

st.divider()

st.subheader("模块八：个人养老金配置智能推荐")
if custom_eq >= 70: 
    rec_text = "建议配置：60% 权益类 + 30% 固收类 + 10% 存款理财。"
elif custom_eq >= 40: 
    rec_text = "建议配置：40% 权益类 + 50% 固收类 + 10% 存款。"
else: 
    rec_text = "建议配置：10% 权益类 + 60% 固收类 + 30% 活期理财。"
st.info(rec_text)

if user_text:
    st.subheader("模块九：自由文本深度诊断")
    st.write(f"系统识别您的输入：“{user_text}”")

st.divider()

if st.button("生成全量《个人养老资产评估白皮书》", use_container_width=True):
    with st.spinner("AI 正在汇总所有精算数据与图表结论，撰写数千字专业白皮书..."):
        report_prompt = f"你是一个顶尖的养老金融分析师。请根据以下精算结果，为用户撰写一份高度专业、图文并茂、结构完整的《个人养老资产评估白皮书》。用户特征：{user_text if user_text else '由系统默认参数生成'}。基础社保月领：{pension_result['合计月养老金']}元，替代率：{replacement_rate:.1f}%。个人养老金账户最终价值：{pp_result['预计账户价值']}元。资产配置比例：权益类{custom_eq}%，固收类{100-custom_eq}%。蒙特卡洛模拟预估中位资金耗尽年龄：{int(np.median(depletion))}岁。退休后每月总现金流：{total_monthly}元。报告要求：1. 分为四个章节：宏观政策分析、个人资产诊断、长寿风险预警、资产配置建议。2. 语言要专业、客观，但要通俗易懂。3. 必须强调算法审计的重要性，提醒用户警惕AI偏见。4. 输出 Markdown 格式。"
        try:
            report_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": report_prompt}],
            )
            st.markdown("---")
            st.markdown(report_response.choices[0].message.content)
            st.success("报告生成完毕！您可以截图保存或复制到 Word 中。")
        except Exception as e:
            st.error(f"报告生成失败：{e}")