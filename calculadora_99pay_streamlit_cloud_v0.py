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

def calculate_daily_cdi(annual_cdi_percent: float) -> float:
    """Converte a taxa CDI anual para uma taxa diária."""
    annual_cdi = annual_cdi_percent / 100
    # A fórmula segue a original em JS, usando 365 dias corridos.
    return (1 + annual_cdi) ** (1 / 365) - 1

def calculate_savings_return(initial_value: float, days: int) -> float:
    """Calcula o rendimento estimado da poupança (simplificado)."""
    if days < 30:
        return 0
    
    # Suposição simplificada de 0.5% a.m. + 0% TR, como no código original.
    monthly_rate = 0.005
    num_cycles = days // 30
    
    final_value = initial_value * ((1 + monthly_rate) ** num_cycles)
    return final_value - initial_value

def calculate_99pay_returns(initial_investment: float, days: int, annual_cdi_percent: float) -> pd.DataFrame:
    """
    Calcula os rendimentos diários na 99Pay, considerando as duas faixas.
    Retorna um DataFrame do Pandas com os resultados diários.
    """
    daily_cdi = calculate_daily_cdi(annual_cdi_percent)
    
    current_value = initial_investment
    daily_data = []

    for day in range(1, days + 1):
        day_start_value = current_value
        
        # Separa os valores por faixa de rendimento
        tier1_value = min(day_start_value, 5000)
        tier2_value = max(0, day_start_value - 5000)
        
        # Calcula o rendimento de cada faixa
        tier1_yield = tier1_value * daily_cdi * 1.10  # 110% do CDI
        tier2_yield = tier2_value * daily_cdi * 0.80  # 80% do CDI
        
        total_daily_yield = tier1_yield + tier2_yield
        current_value += total_daily_yield
        
        daily_data.append({
            "Dia": day,
            "Valor Inicial": day_start_value,
            "Rendimento Faixa 1 (110%)": tier1_yield,
            "Rendimento Faixa 2 (80%)": tier2_yield,
            "Rendimento Total Dia": total_daily_yield,
            "Valor Final": current_value
        })
        
    return pd.DataFrame(daily_data)

# --- Interface do Usuário (Streamlit) ---

st.title("💹 Calculadora de Rendimentos 99 Pay")
st.markdown("Esta é uma versão em Python/Streamlit da calculadora, que simula os rendimentos compostos diários da carteira 99Pay.")

# --- Barra Lateral para Entradas ---
with st.sidebar:
    st.header("Parâmetros da Simulação")

    initial_investment = st.number_input(
        "Valor Investido (R$)", 
        min_value=0.01, 
        value=None, # Inicia vazio
        placeholder="Ex: 5000.00",
        step=100.0,
        format="%.2f",
        help="Montante inicial que você deseja investir."
    )

    days = st.number_input(
        "Período (em dias)", 
        min_value=1, 
        value=None, # Inicia vazio
        placeholder="Ex: 365",
        step=1,
        help="Por quantos dias o dinheiro ficará investido."
    )

    # --- Lógica para o input de CDI com botão de reset ---
    DEFAULT_CDI = 11.15
    # Inicializa o valor do CDI no estado da sessão se ainda não existir
    if 'cdi_rate' not in st.session_state:
        st.session_state.cdi_rate = DEFAULT_CDI

    # Função callback para o botão de reset
    def reset_cdi_callback():
        st.session_state.cdi_rate = DEFAULT_CDI

    annual_cdi_percent = st.number_input(
        "Taxa CDI Anual (%)", 
        min_value=0.01, 
        step=0.01,
        help="A taxa DI (CDI) vigente no período. O valor padrão é uma referência.",
        key='cdi_rate' # Vincula este input ao estado da sessão
    )

    st.button(
        f"Redefinir CDI para {DEFAULT_CDI}%",
        on_click=reset_cdi_callback,
        use_container_width=True
    )

    st.markdown("---")
    calculate_button = st.button("Calcular Rendimento", type="primary", use_container_width=True)

# --- Painel Principal para Resultados ---
if calculate_button:
    # Validação de entradas (verifica se os campos não estão vazios)
    if not initial_investment or not days:
        st.error("Por favor, preencha os campos 'Valor Investido' e 'Período' para continuar.")
    else:
        # Executa os cálculos
        results_df = calculate_99pay_returns(initial_investment, days, annual_cdi_percent)
        
        # Extrai os valores finais para o resumo
        final_value = results_df["Valor Final"].iloc[-1]
        total_yield = final_value - initial_investment
        percent_yield = (total_yield / initial_investment) * 100
        savings_yield = calculate_savings_return(initial_investment, days)
        savings_percent_yield = (savings_yield / initial_investment) * 100 if initial_investment > 0 else 0
        
        # --- Exibe o Resumo ---
        st.header("Resumo da Simulação")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Valor Investido", format_currency(initial_investment))
        col2.metric("Valor Final", format_currency(final_value))
        col3.metric("Rendimento Total (99Pay)", format_currency(total_yield), f"{percent_yield:.2f}%")
        col4.metric(
            "Rendimento Poupança (est.)",
            format_currency(savings_yield),
            f"{savings_percent_yield:.2f}%",
            help="Estimativa com rendimento de 0.5% a.m. e sem considerar a Taxa Referencial (TR)."
        )

        # --- Exibe o Gráfico ---
        chart_data = results_df.rename(columns={"Valor Final": "99Pay"})

        # Define uma escala dinâmica para o eixo Y para melhor visualização
        min_val = chart_data["99Pay"].min()
        max_val = chart_data["99Pay"].max()
        # Adiciona um preenchimento (padding) para a escala não ficar colada nos limites
        padding = (max_val - min_val) * 0.05
        if padding == 0: # Evita erro se não houver variação
            padding = min_val * 0.01

        # Gráfico base
        base = alt.Chart(chart_data).encode(
            x=alt.X('Dia:Q', title='Dia do Investimento'),
        )

        # Camada da linha
        line = base.mark_line(strokeWidth=2).encode(
            y=alt.Y('99Pay:Q',
                    scale=alt.Scale(domain=[min_val - padding, max_val + padding]),
                    title='Valor Acumulado (R$)',
                    axis=alt.Axis(format='~s') # Formata eixo (ex: 10k, 1M)
                   )
        )

        # Camada de pontos transparentes para o tooltip
        points = base.mark_circle(size=60, opacity=0).encode(
            y=alt.Y('99Pay:Q'),
            tooltip=[
                alt.Tooltip('Dia', title='Dia'),
                alt.Tooltip('99Pay', title='Valor em Carteira', format='R$,.2f')
            ]
        )

        # Combina as camadas, define altura e torna interativo
        chart = (line + points).interactive().properties(
            title=alt.TitleParams(
                text="Evolução do Investimento",
                anchor='middle',
                fontSize=18
            ),
            height=450,  # Aumenta a altura do gráfico
            # Remove autosize para melhor controle das dimensões
        ).configure_view(
            strokeWidth=0,
            # Adiciona margens para evitar cortes
            continuousHeight=350,
            continuousWidth=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=13,
            # Aumenta o padding dos rótulos
            labelPadding=10,
            # Aumenta o padding do título
            titlePadding=20
        ).configure_axisBottom(
            # Configuração específica para o eixo X
            labelAngle=0,  # Mantém as labels horizontais
            labelOverlap=True  # Permite sobreposição controlada
        )

        st.altair_chart(chart, use_container_width=True, theme="streamlit")

        # --- Exibe a Tabela de Resultados Diários ---
        st.header("Resultados Diários Detalhados")
        
        # Formata o DataFrame para exibição
        display_df = results_df.copy()
        currency_columns = ["Valor Inicial", "Rendimento Faixa 1 (110%)", "Rendimento Faixa 2 (80%)", "Rendimento Total Dia", "Valor Final"]
        for col in currency_columns:
            display_df[col] = display_df[col].apply(format_currency)
            
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("Preencha os parâmetros na barra lateral e clique em 'Calcular Rendimento' para ver os resultados.")

# --- Rodapé ---
st.markdown("---")
st.markdown("Desenvolvido por **NerdFinança$** | Versão Python/Streamlit criada por Gemini Code Assist")
