import streamlit as st
import pandas as pd
import altair as alt

# =========================
# Configuração da Página
# =========================
st.set_page_config(
    page_title="Calculadora 99Pay",
    page_icon="💹",
    layout="wide"
)

# =========================
# Utilidades
# =========================
def format_currency(value: float) -> str:
    """Formata um número para o padrão monetário brasileiro (R$)."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_period(days: int) -> str:
    """Formata um período em dias para string amigável."""
    if days <= 0:
        return f"{days} dias"
    if days == 1:
        return "1 dia"

    # Anos exatos
    if days % 365 == 0:
        years = days // 365
        return f"{years} ano{'s' if years > 1 else ''}"

    # Meses aproximados
    if days == 31:
        return "1 mês"
    if days % 30 == 0:
        months = days // 30
        return f"{months} {'meses' if months > 1 else 'mês'}"

    # Semanas exatas
    if days % 7 == 0:
        weeks = days // 7
        return f"{weeks} semana{'s' if weeks > 1 else ''}"

    return f"{days} dias"

def calculate_daily_cdi(annual_cdi_percent: float) -> float:
    """Converte CDI anual (%) para taxa diária (decimal)."""
    annual_cdi = annual_cdi_percent / 100.0
    return (1 + annual_cdi) ** (1 / 365) - 1

def calculate_daily_savings_values(initial_value: float, days: int) -> list[float]:
    """
    Simula poupança com rendimento creditado a cada 30 dias.
    Regra simplificada: 0,5% ao mês, sem TR.
    """
    monthly_rate = 0.005
    daily_values = []
    current_value = initial_value

    for day in range(1, days + 1):
        if day % 30 == 0:
            current_value *= (1 + monthly_rate)
        daily_values.append(current_value)
    return daily_values

def calculate_99pay_returns(initial_investment: float,
                            days: int,
                            annual_cdi_percent: float,
                            bonus_percent: float = 0.0) -> pd.DataFrame:
    """
    Calcula rendimentos diários na 99Pay em duas faixas:
    - Faixa 1: até R$ 5.000 à 110% do CDI + bônus (se houver)
    - Faixa 2: excedente a 80% do CDI
    """
    daily_cdi = calculate_daily_cdi(annual_cdi_percent)
    tier1_multiplier = 1.10 + (bonus_percent / 100.0)  # 110% + bônus
    tier1_display_percent = 110 + bonus_percent

    current_value = initial_investment
    rows = []

    for day in range(1, days + 1):
        day_start = current_value
        tier1_base = min(day_start, 5000.0)
        tier2_base = max(0.0, day_start - 5000.0)

        tier1_yield = tier1_base * daily_cdi * tier1_multiplier
        tier2_yield = tier2_base * daily_cdi * 0.80
        total_yield = tier1_yield + tier2_yield

        current_value += total_yield

        rows.append({
            "Dia": day,
            "Valor Inicial": day_start,
            f"Rendimento Faixa 1 ({tier1_display_percent:.0f}%)": tier1_yield,
            "Rendimento Faixa 2 (80%)": tier2_yield,
            "Rendimento Total Dia": total_yield,
            "Valor Final": current_value
        })

    return pd.DataFrame(rows)

# =========================
# Interface
# =========================
st.title("💹 Calculadora de Rendimentos 99Pay")
st.markdown(
    "Simulação diária com faixas de rendimento da 99Pay e comparação com a poupança "
    "(0,5% a.m., sem TR, crédito a cada 30 dias)."
)

DEFAULT_CDI = 11.15  # ajuste seu padrão preferido aqui

with st.sidebar:
    st.header("Parâmetros da Simulação")

    # -------------------------
    # Formulário: garante submissão atômica dos inputs
    # -------------------------
    with st.form(key="simulation_form", clear_on_submit=False):
        # Valor investido
        initial_investment = st.number_input(
            "Valor Investido (R$)",
            min_value=0.01,
            value=None,                   # permite iniciar vazio
            step=0.01,                    # centavos
            format="%.2f",
            placeholder="Ex: 5000,00",
            key="initial_investment"
        )

        # Bônus adicional
        bonus_percent = st.number_input(
            "Bônus Adicional (%)",
            min_value=0.0,
            value=0.00,
            step=0.01,
            format="%.2f",
            key="bonus_percent"
        )

        # Período (em dias)
        days = st.number_input(
            "Período (em dias)",
            min_value=1,
            value=None,                   # permite iniciar vazio
            step=1,
            placeholder="Ex: 365",
            key="days"
        )

        # CDI anual
        # IMPORTANTE: definimos o default SOMENTE via value=... (sem pré-set em session_state)
        annual_cdi_percent = st.number_input(
            "Taxa CDI Anual (%)",
            min_value=0.01,
            value=DEFAULT_CDI,            # fonte única de valor inicial
            step=0.01,
            format="%.2f",
            key="cdi_rate"
        )

        st.markdown("---")
        calculate_button = st.form_submit_button(
            "Calcular Rendimento",
            type="primary",
            use_container_width=True
        )

    # -------------------------
    # Ações auxiliares (fora do form)
    # -------------------------
    if st.button(f"Redefinir CDI para {DEFAULT_CDI:.2f}%", use_container_width=True):
        # Como o widget tem key='cdi_rate', podemos resetar direto no estado
        st.session_state.cdi_rate = DEFAULT_CDI
        st.rerun()

    if st.button("Limpar Simulação", use_container_width=True):
        # Zera/limpa os campos controlados por key
        st.session_state.initial_investment = None
        st.session_state.days = None
        st.session_state.bonus_percent = 0.00
        st.session_state.cdi_rate = DEFAULT_CDI
        st.rerun()

# =========================
# Resultados
# =========================
if calculate_button:
    # Validações simples
    if (initial_investment is None) or (initial_investment <= 0):
        st.error("Informe um **Valor Investido (R$)** válido (maior que zero).", icon="🚨")
    elif (days is None) or (days < 1):
        st.error("Informe um **Período (em dias)** válido (mínimo 1).", icon="🚨")
    elif (annual_cdi_percent is None) or (annual_cdi_percent <= 0):
        st.error("Informe uma **Taxa CDI Anual (%)** válida (maior que zero).", icon="🚨")
    else:
        # Cálculo 99Pay
        results_df = calculate_99pay_returns(
            initial_investment=initial_investment,
            days=int(days),
            annual_cdi_percent=annual_cdi_percent,
            bonus_percent=bonus_percent
        )

        final_value = float(results_df["Valor Final"].iloc[-1])
        total_yield = final_value - float(initial_investment)
        percent_yield = (total_yield / float(initial_investment)) * 100.0

        # Poupança (comparação)
        savings_daily_values = calculate_daily_savings_values(float(initial_investment), int(days))
        savings_final_value = savings_daily_values[-1] if savings_daily_values else float(initial_investment)
        savings_yield = savings_final_value - float(initial_investment)
        savings_percent_yield = (savings_yield / float(initial_investment)) * 100.0 if initial_investment > 0 else 0.0

        # --------- Resumo ----------
        st.header("Resumo da Simulação")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Tempo do Investimento", format_period(int(days)))
        c2.metric("Valor Investido", format_currency(float(initial_investment)))
        c3.metric("Valor Final (99Pay)", format_currency(final_value))

        pay_color = "normal"
        savings_color = "normal"
        if int(days) >= 30:
            if percent_yield > savings_percent_yield:
                savings_color = "inverse"
            elif savings_percent_yield > percent_yield:
                pay_color = "inverse"

        c4.metric(
            "Rendimento Total (99Pay)",
            format_currency(total_yield),
            f"{percent_yield:.2f}%",
            delta_color=pay_color
        )

        if int(days) >= 30:
            c5.metric(
                "Rendimento Poupança (est.)",
                format_currency(savings_yield),
                f"{savings_percent_yield:.2f}%",
                delta_color=savings_color,
                help="Estimativa com 0,5% a.m. (sem TR), crédito a cada 30 dias."
            )
        else:
            c5.metric(
                "Rendimento Poupança (est.)",
                "N/A",
                help="A poupança requer no mínimo 30 dias para render."
            )

        # --------- Gráfico ----------
        st.header("Evolução Comparativa")

        series = []

        main_label = f'99Pay ({110 + bonus_percent:.0f}%)'
        s_pay = results_df[['Dia', 'Valor Final']].rename(columns={'Valor Final': 'Valor'})
        s_pay['Investimento'] = main_label
        series.append(s_pay)

        if bonus_percent > 0:
            no_bonus_df = calculate_99pay_returns(
                initial_investment=float(initial_investment),
                days=int(days),
                annual_cdi_percent=float(annual_cdi_percent),
                bonus_percent=0.0
            )
            s_no_bonus = no_bonus_df[['Dia', 'Valor Final']].rename(columns={'Valor Final': 'Valor'})
            s_no_bonus['Investimento'] = '99Pay (110%)'
            series.append(s_no_bonus)

        s_savings = pd.DataFrame({
            'Dia': list(range(1, int(days) + 1)),
            'Valor': savings_daily_values,
            'Investimento': 'Poupança'
        })
        series.append(s_savings)

        chart_df = pd.concat(series, ignore_index=True)
        chart_df['Dia'] = pd.to_numeric(chart_df['Dia'], errors='coerce').astype(int)
        chart_df['Valor'] = pd.to_numeric(chart_df['Valor'], errors='coerce').astype(float)
        chart_df['Investimento'] = chart_df['Investimento'].astype(str)
        chart_df = chart_df.dropna().sort_values(['Dia', 'Investimento'])

        chart = alt.Chart(chart_df).mark_line(point=True).encode(
            x=alt.X('Dia:Q', title='Dia do Investimento', axis=alt.Axis(format='d', labelFlush=True)),
            y=alt.Y('Valor:Q', title='Valor Acumulado (R$)',
                    axis=alt.Axis(format='$.2f'), scale=alt.Scale(nice=True, zero=False)),
            color=alt.Color('Investimento:N', legend=alt.Legend(title="Tipo de Investimento"))
            ,
            tooltip=[
                alt.Tooltip('Dia', title='Dia'),
                alt.Tooltip('Investimento', title='Tipo'),
                alt.Tooltip('Valor', title='Valor', format='$.2f')
            ]
        ).properties(
            width=900,
            height=480,
            title='Evolução do Investimento'
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # --------- Tabela ----------
        st.header("Resultados Diários Detalhados")
        display_df = results_df.copy()
        for col in display_df.columns:
            if col != 'Dia':
                display_df[col] = display_df[col].apply(format_currency)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("Preencha os parâmetros na barra lateral e clique em **Calcular Rendimento** para ver os resultados.")

# =========================
# Rodapé
# =========================
st.markdown("---")
st.markdown("Desenvolvido por **NerdFinança$** | Versão 2.3 – Agosto/2025")
