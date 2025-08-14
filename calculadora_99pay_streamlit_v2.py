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

def calculate_daily_savings_values(initial_value: float, days: int) -> list[float]:
    """
    Calcula os valores diários acumulados da poupança (simplificado).
    Retorna uma lista com o valor acumulado para cada dia.
    """
    monthly_rate = 0.005
    daily_values = []
    current_value = initial_value

    for day in range(1, days + 1):
        # Adiciona o valor atual à lista (o valor só muda após o aniversário)
        daily_values.append(current_value)

        # No "aniversário" (final do dia 30, 60, etc.), o rendimento é calculado
        # para o próximo período.
        if day % 30 == 0:
            current_value *= (1 + monthly_rate)
    return daily_values

def calculate_99pay_returns(initial_investment: float, days: int, annual_cdi_percent: float, bonus_percent: float = 0.0) -> pd.DataFrame:
    """
    Calcula os rendimentos diários na 99Pay, considerando as duas faixas e um bônus opcional.
    Retorna um DataFrame do Pandas com os resultados diários.
    """
    daily_cdi = calculate_daily_cdi(annual_cdi_percent)
    
    # Taxa da primeira faixa com bônus
    tier1_rate = 1.10 + (bonus_percent / 100)
    tier1_display_percent = 110 + bonus_percent

    current_value = initial_investment
    daily_data = []

    for day in range(1, days + 1):
        day_start_value = current_value
        
        # Separa os valores por faixa de rendimento
        limit_tier1 = 5000.0
        tier1_value = min(day_start_value, limit_tier1)
        tier2_value = max(0, day_start_value - limit_tier1)
        
        # Calcula o rendimento de cada faixa
        tier1_yield = tier1_value * daily_cdi * tier1_rate  # Taxa com bônus
        tier2_yield = tier2_value * daily_cdi * 0.80  # 80% do CDI
        
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

# --- Interface do Usuário (Streamlit) ---

st.title("💹 Calculadora de Rendimentos 99 Pay")
st.markdown("Esta é uma versão em Python/Streamlit da calculadora, que simula os rendimentos compostos diários da carteira 99Pay.")

# --- Barra Lateral para Entradas ---
with st.sidebar:
    st.header("Parâmetros da Simulação")

    # Função de callback para limpar os inputs e a simulação
    def clear_simulation_callback():
        st.session_state.initial_investment = None
        st.session_state.bonus_percent = 0.0
        st.session_state.days = None
        # O CDI é mantido, pois tem seu próprio botão de reset

    initial_investment = st.number_input(
        "Valor Investido (R$)", 
        min_value=0.01, 
        value=None, # Inicia vazio
        placeholder="Ex: 5000.00",
        step=100.0,
        format="%.2f",
        help="Montante inicial que você deseja investir.",
        key="initial_investment"
    )

    bonus_percent = st.number_input(
        "Bônus Adicional (%)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.1f",
        help="Opcional. Bônus a ser somado à taxa da primeira faixa (110% do CDI). Ex: 10 para 120%.",
        key="bonus_percent"
    )

    days = st.number_input(
        "Período (em dias)", 
        min_value=1, 
        value=None, # Inicia vazio
        placeholder="Ex: 365",
        step=1,
        help="Por quantos dias o dinheiro ficará investido.",
        key="days"
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
    # Colunas para os botões de ação
    col1, col2 = st.columns(2)

    with col1:
        calculate_button = st.button("Calcular Rendimento", type="primary", use_container_width=True)
    
    with col2:
        st.button("Limpar Simulação", on_click=clear_simulation_callback, use_container_width=True)

# --- Painel Principal para Resultados ---
if calculate_button:
    # Validação de entradas (verifica se os campos não estão vazios)
    if not initial_investment or not days:
        st.error("Por favor, preencha os campos 'Valor Investido' e 'Período' para continuar.")
    else:
        # Executa os cálculos
        results_df = calculate_99pay_returns(initial_investment, days, annual_cdi_percent, bonus_percent)
        
        # Extrai os valores finais para o resumo
        final_value = results_df["Valor Final"].iloc[-1]
        total_yield = final_value - initial_investment
        percent_yield = (total_yield / initial_investment) * 100
        
        # Calcula o rendimento da poupança a partir dos valores diários
        savings_daily_values = calculate_daily_savings_values(initial_investment, days)
        savings_final_value = savings_daily_values[-1] if savings_daily_values else initial_investment
        savings_yield = savings_final_value - initial_investment
        savings_percent_yield = (savings_yield / initial_investment) * 100 if initial_investment > 0 else 0
        
        # --- Exibe o Resumo ---
        st.header("Resumo da Simulação")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Valor Investido", format_currency(initial_investment))
        col2.metric("Valor Final", format_currency(final_value))
        col3.metric("Rendimento Total (99Pay)", format_currency(total_yield), f"{percent_yield:.2f}%")
        
        if days >= 30:
            col4.metric(
                "Rendimento Poupança (est.)",
                format_currency(savings_yield),
                f"{savings_percent_yield:.2f}%",
                help="Estimativa com rendimento de 0.5% a.m. e sem considerar a Taxa Referencial (TR)."
            )
        else:
            col4.metric(
                "Rendimento Poupança (est.)", "N/A", help="A poupança requer no mínimo 30 dias para render."
            )

        # --- Preparação dos Dados para o Gráfico ---
        
        # 1. Dados da simulação principal (com ou sem bônus)
        main_label = f'99Pay ({110 + bonus_percent:.0f}%)'
        chart_data = results_df[['Dia', 'Valor Final']].copy()
        chart_data.rename(columns={'Valor Final': 'Valor'}, inplace=True)
        chart_data['Investimento'] = main_label

        # Lista para conter todos os dataframes a serem combinados
        all_chart_data = [chart_data]

        # 2. Dados da simulação sem bônus (para comparação, se houver bônus)
        if bonus_percent > 0:
            no_bonus_df = calculate_99pay_returns(initial_investment, days, annual_cdi_percent, bonus_percent=0.0)
            no_bonus_chart_data = no_bonus_df[['Dia', 'Valor Final']].copy()
            no_bonus_chart_data.rename(columns={'Valor Final': 'Valor'}, inplace=True)
            no_bonus_chart_data['Investimento'] = '99Pay (110%)'
            all_chart_data.append(no_bonus_chart_data)

        # 3. Dados da poupança (apenas se o período for de no mínimo 30 dias)
        if days >= 30:
            savings_chart_data = pd.DataFrame({
                'Dia': range(1, days + 1),
                'Valor': savings_daily_values
            })
            savings_chart_data['Investimento'] = 'Poupança'
            all_chart_data.append(savings_chart_data)

        # 4. Combina todos os dados em um único DataFrame
        final_chart_df = pd.concat(all_chart_data, ignore_index=True)

        # --- Exibe o Gráfico com Múltiplas Linhas ---
        min_val = final_chart_df["Valor"].min()
        max_val = final_chart_df["Valor"].max()
        # Adiciona um preenchimento (padding) para a escala não ficar colada nos limites
        padding = (max_val - min_val) * 0.05
        if padding == 0: # Evita erro se não houver variação
            padding = min_val * 0.01

        # Gráfico base com encodings compartilhados para as camadas
        base = alt.Chart(final_chart_df).encode(
            x=alt.X('Dia:Q', title='Dia do Investimento'),
            y=alt.Y('Valor:Q',
                    scale=alt.Scale(domain=[min_val - padding, max_val + padding]),
                    title='Valor Acumulado (R$)',
                    axis=alt.Axis(format='~s') # Formata eixo (ex: 10k, 1M)
                   ),
            color=alt.Color('Investimento:N', title='Investimento', legend=alt.Legend(orient="top-left")),
            tooltip=[
                alt.Tooltip('Dia', title='Dia'),
                alt.Tooltip('Investimento', title='Tipo'),
                alt.Tooltip('Valor', title='Valor Acumulado', format='R$,.2f')
            ]
        )

        # Camada 1: Linhas do gráfico
        line = base.mark_line(strokeWidth=2)

        # Camada 2: Pontos transparentes para melhorar a área de hover do tooltip
        # Os pontos herdam o encoding de 'base', incluindo o eixo Y, que é crucial.
        points = base.mark_circle(opacity=0, size=50)

        # Combina as camadas, torna interativo e aplica configurações de estilo
        chart = (line + points).interactive().properties(
            title=alt.TitleParams(
                text="Evolução Comparativa do Investimento",
                anchor='middle',
                fontSize=18
            ),
            height=450
        ).configure_view(
            strokeWidth=0 # Remove a borda ao redor da área do gráfico
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=13,
            labelPadding=10,  # Adiciona espaço entre o eixo e seus rótulos
            titlePadding=15   # Adiciona espaço entre o título do eixo e o eixo
        ).configure_axisBottom(
            labelAngle=0      # Garante que os rótulos do eixo X fiquem na horizontal
        )

        st.altair_chart(chart, use_container_width=True, theme="streamlit")

        # --- Exibe a Tabela de Resultados Diários ---
        st.header("Resultados Diários Detalhados")
        
        # Formata o DataFrame para exibição
        display_df = results_df.copy()
        # Seleciona todas as colunas que não são 'Dia' para formatação
        currency_columns = [col for col in display_df.columns if col != 'Dia']
        for col in currency_columns:
            display_df[col] = display_df[col].apply(format_currency)
            
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("Preencha os parâmetros na barra lateral e clique em 'Calcular Rendimento' para ver os resultados.")

# --- Rodapé ---
st.markdown("---")
st.markdown("Desenvolvido por **NerdFinança$** | Versão Python/Streamlit criada por Gemini Code Assist")
