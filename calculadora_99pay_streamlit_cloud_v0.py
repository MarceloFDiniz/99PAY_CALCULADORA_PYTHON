import streamlit as st
import pandas as pd
import altair as alt

# --- Configuração da Página ---
st.set_page_config(
    page_title="Calculadora 99Pay",
    page_icon="💹",
    layout="wide"
)

# --- Funções de Cálculo ---
def format_currency(value: float) -> str:
    """Formata um número para o padrão monetário brasileiro (R$)."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_period(days: int) -> str:
    """Formata um período em dias para uma string mais amigável (semanas, meses, anos)."""
    if days <= 0:
        return f"{days} dias"
    if days == 1:
        return "1 dia"

    # Anos exatos
    if days % 365 == 0:
        years = days // 365
        return f"{years} ano{'s' if years > 1 else ''}"

    # Meses (aproximado)
    if days == 31: # Caso especial para 1 mês
        return "1 mês"
    if days % 30 == 0:
        months = days // 30
        return f"{months} {'meses' if months > 1 else 'mês'}"

    # Semanas exatas
    if days % 7 == 0:
        weeks = days // 7
        return f"{weeks} semana{'s' if weeks > 1 else ''}"

    # Padrão
    return f"{days} dias"

def calculate_daily_cdi(annual_cdi_percent: float) -> float:
    """Converte a taxa CDI anual para uma taxa diária."""
    annual_cdi = annual_cdi_percent / 100
    return (1 + annual_cdi) ** (1 / 365) - 1

def calculate_daily_savings_values(initial_value: float, days: int) -> list[float]:
    """Calcula os valores diários acumulados da poupança com rendimento a cada 30 dias."""
    monthly_rate = 0.005
    daily_values = []
    current_value = initial_value
    
    for day in range(1, days + 1):
        if day % 30 == 0:
            current_value *= (1 + monthly_rate)
        daily_values.append(current_value)
    return daily_values

def calculate_99pay_returns(initial_investment: float, days: int, annual_cdi_percent: float, bonus_percent: float = 0.0) -> pd.DataFrame:
    """Calcula os rendimentos diários na 99Pay."""
    daily_cdi = calculate_daily_cdi(annual_cdi_percent)
    tier1_rate = 1.10 + (bonus_percent / 100)
    tier1_display_percent = 110 + bonus_percent

    current_value = initial_investment
    daily_data = []

    for day in range(1, days + 1):
        day_start_value = current_value
        tier1_value = min(day_start_value, 5000.0)
        tier2_value = max(0, day_start_value - 5000.0)
        
        tier1_yield = tier1_value * daily_cdi * tier1_rate
        tier2_yield = tier2_value * daily_cdi * 0.80
        total_daily_yield = tier1_yield + tier2_yield
        
        current_value += total_daily_yield
        daily_data.append({
            "Dia": day,
            "Valor Inicial": day_start_value,
            f"Rendimento Faixa 1 ({tier1_display_percent:.0f}%)": tier1_yield,
            "Rendimento Faixa 2 (80%)": tier2_yield,
            "Rendimento Total Dia": total_daily_yield,
            "Valor Final": current_value
        })
    return pd.DataFrame(daily_data)

# --- Interface do Usuário ---
st.title("💹 Calculadora de Rendimentos 99 Pay")
st.markdown("Esta é uma versão em Python/Streamlit da calculadora, que simula os rendimentos compostos diários da carteira 99Pay.")

# --- Barra Lateral ---
with st.sidebar:
    st.header("Parâmetros da Simulação")
    
    # Inicialização dos estados para os inputs
    DEFAULT_CDI = 14.90
    if 'cdi_rate' not in st.session_state:
        st.session_state.cdi_rate = DEFAULT_CDI
    if 'bonus_percent' not in st.session_state:
        # Define o valor inicial para o bônus no estado da sessão
        st.session_state.bonus_percent = 0.0

    # Inputs
    initial_investment = st.number_input(
        "Valor Investido (R$)",
        min_value=0.01,
        value=None,
        placeholder="Ex: 5000.00",
        step=100.0,
        format="%.2f",
        key="initial_investment"
    )
    
    bonus_percent = st.number_input(
        "Bônus Adicional (%)",
        min_value=0.0,
        # O valor é lido diretamente de st.session_state.bonus_percent via a 'key'
        step=1.0,
        format="%.1f",
        key="bonus_percent"
    )
    
    days = st.number_input(
        "Período (em dias)",
        min_value=1,
        value=None,
        placeholder="Ex: 365",
        step=1,
        key="days"
    )
            
    def reset_cdi_callback():
        st.session_state.cdi_rate = DEFAULT_CDI
        
    annual_cdi_percent = st.number_input(
        "Taxa CDI Anual (%)",
        min_value=0.01,
        step=0.01,
        key='cdi_rate'
    )
    
    st.button(
        f"Redefinir CDI para {DEFAULT_CDI}%",
        on_click=reset_cdi_callback,
        use_container_width=True
    )
    
    st.markdown("---")

    def clear_simulation_callback():
        """Reseta os campos do formulário para o estado inicial."""
        st.session_state.initial_investment = None
        st.session_state.days = None
        st.session_state.bonus_percent = 0.0
        st.session_state.cdi_rate = DEFAULT_CDI

    col1, col2 = st.columns(2)
    with col1:
        calculate_button = st.button("Calcular Rendimento", type="primary", use_container_width=True)
    with col2:
        st.button("Limpar Simulação", on_click=clear_simulation_callback, use_container_width=True)

# --- Resultados ---
if calculate_button:
    if not initial_investment or not days:
        st.error("Por favor, preencha os campos 'Valor Investido' e 'Período' para continuar.")
    else:
        # Cálculos principais
        results_df = calculate_99pay_returns(initial_investment, days, annual_cdi_percent, bonus_percent)
        final_value = results_df["Valor Final"].iloc[-1]
        total_yield = final_value - initial_investment
        percent_yield = (total_yield / initial_investment) * 100

        # Cálculo da poupança
        savings_daily_values = calculate_daily_savings_values(initial_investment, days)
        savings_final_value = savings_daily_values[-1] if savings_daily_values else initial_investment
        savings_yield = savings_final_value - initial_investment
        savings_percent_yield = (savings_yield / initial_investment) * 100 if initial_investment > 0 else 0

        # --- Cards de Resumo ---
        st.header("Resumo da Simulação")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric("Tempo do Investimento", format_period(days))
        col2.metric("Valor Investido", format_currency(initial_investment))
        col3.metric("Valor Final", format_currency(final_value))

        # Lógica para colorir os deltas das métricas de forma comparativa
        pay_color = "normal"  # Verde por padrão (para rendimento positivo)
        savings_color = "normal"
        if days >= 30:
            if percent_yield > savings_percent_yield:
                savings_color = "inverse"  # Vermelho para o menor rendimento
            elif savings_percent_yield > percent_yield:
                pay_color = "inverse"  # Vermelho para o menor rendimento
            # Se forem iguais, ambos permanecem "normal" (verde)

        col4.metric(
            "Rendimento Total (99Pay)",
            format_currency(total_yield),
            f"{percent_yield:.2f}%",
            delta_color=pay_color
        )

        if days >= 30:
            col5.metric(
                "Rendimento Poupança (est.)",
                format_currency(savings_yield),
                f"{savings_percent_yield:.2f}%",
                delta_color=savings_color,
                help="Estimativa com rendimento de 0.5% a.m. e sem considerar a Taxa Referencial (TR)."
            )
        else:
            col5.metric(
                "Rendimento Poupança (est.)",
                "N/A",
                help="A poupança requer no mínimo 30 dias para render."
            )

        # --- Gráfico ---
        st.header("Evolução Comparativa")
        all_chart_data = []
        main_label = f'99Pay ({110 + bonus_percent:.0f}%)'
        chart_data = results_df[['Dia', 'Valor Final']].rename(columns={'Valor Final': 'Valor'})
        chart_data['Investimento'] = main_label
        all_chart_data.append(chart_data)

        if bonus_percent > 0:
            no_bonus_df = calculate_99pay_returns(initial_investment, days, annual_cdi_percent, 0.0)
            no_bonus_chart = no_bonus_df[['Dia', 'Valor Final']].rename(columns={'Valor Final': 'Valor'})
            no_bonus_chart['Investimento'] = '99Pay (110%)'
            all_chart_data.append(no_bonus_chart)

        if days >= 1:
            savings_chart = pd.DataFrame({
                'Dia': range(1, days + 1),
                'Valor': savings_daily_values,
                'Investimento': 'Poupança'
            })
            all_chart_data.append(savings_chart)

        # Combinação final dos dados
        final_chart_df = pd.concat(all_chart_data, ignore_index=True)
        final_chart_df = final_chart_df.assign(
            Dia=pd.to_numeric(final_chart_df['Dia'], errors='coerce').astype(int),
            Valor=pd.to_numeric(final_chart_df['Valor'], errors='coerce').astype(float),
            Investimento=final_chart_df['Investimento'].astype(str)
        ).dropna().sort_values(['Dia', 'Investimento'])

        # Criação do gráfico
        chart = alt.Chart(final_chart_df).mark_line(point=True).encode(
            x=alt.X('Dia:Q', 
                    title='Dia do Investimento',
                    axis=alt.Axis(format='d', labelFlush=True)),
            
            y=alt.Y('Valor:Q', 
                    title='Valor Acumulado (R$)',
                    axis=alt.Axis(format='$.2f'),
                    scale=alt.Scale(nice=True, zero=False)),
                    
            color=alt.Color('Investimento:N', 
                           legend=alt.Legend(title="Tipo de Investimento"),
                           scale=alt.Scale(scheme='category10')),
            
            tooltip=[
                alt.Tooltip('Dia', title='Dia'),
                alt.Tooltip('Investimento', title='Tipo'),
                alt.Tooltip('Valor', title='Valor', format='$.2f')
            ]
        ).properties(
            width=800,
            height=500,
            title='Evolução do Investimento'
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # --- Tabela Detalhada ---
        st.header("Resultados Diários Detalhados")
        display_df = results_df.copy()
        currency_cols = [col for col in display_df.columns if col != 'Dia']
        for col in currency_cols:
            display_df[col] = display_df[col].apply(format_currency)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("Preencha os parâmetros na barra lateral e clique em 'Calcular Rendimento' para ver os resultados.")

# --- Rodapé ---
st.markdown("---")
st.markdown("Desenvolvido por **NerdFinança$** | Versão 2.2 - Atualização Agosto/2025")
