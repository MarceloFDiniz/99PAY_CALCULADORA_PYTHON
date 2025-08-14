# 💹 Calculadora de Rendimentos 99Pay

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-ff4b4b?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?style=for-the-badge&logo=pandas)
![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-orange?style=for-the-badge)

Uma calculadora interativa e visual para simular os rendimentos compostos diários da carteira digital 99Pay. Descubra o potencial do seu dinheiro com base nas regras de rendimento específicas da plataforma.

> **Nota:** Este projeto é uma ferramenta de simulação para fins educacionais e de planejamento. Os valores são estimativas e podem não refletir com exatidão os rendimentos futuros.

---

<!-- ## 📸 Visão Geral da Aplicação

*Substitua a imagem abaixo por um screenshot da sua aplicação em execução!* 

---

-->

## ✨ Funcionalidades Principais

- **Simulação de Rendimentos Compostos:** Calcule os ganhos diários, reinvestindo automaticamente os rendimentos.
- **Regras da 99Pay:** O cálculo considera as duas faixas de rendimento:
  - **110% do CDI** para valores até R$ 5.000,00.
  - **80% do CDI** para o valor que exceder R$ 5.000,00.
- **Interface Interativa:** Utilize sliders e campos de número para ajustar facilmente os parâmetros da simulação.
- **Visualização Gráfica:** Um gráfico dinâmico mostra a evolução do seu investimento ao longo do tempo.
- **Relatório Detalhado:** Uma tabela exibe o rendimento e o saldo final para cada dia do período simulado.
- **Comparativo com a Poupança:** Veja uma estimativa de quanto seu dinheiro renderia na poupança no mesmo período.
- **Parâmetros Customizáveis:** Defina o valor inicial, o período em dias e a taxa CDI anual.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias:

- **[Python](https://www.python.org/)**: Linguagem de programação principal.
- **[Streamlit](https://streamlit.io/)**: Framework para a criação da interface web interativa.
- **[Pandas](https://pandas.pydata.org/)**: Biblioteca para manipulação e análise de dados, usada para estruturar os resultados.
- **[Altair](https://altair-viz.github.io/)**: Biblioteca para a criação de gráficos declarativos e interativos.

---

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para executar a calculadora em sua máquina.

### Pré-requisitos

- [Python 3.9+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) (opcional, para clonar o repositório)

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/MarceloFDiniz/99PAY_CALCULADORA_PYTHON.git
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    - No Windows:
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - No macOS/Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Instale as dependências:**
    O projeto utiliza o arquivo `requirements.txt` para gerenciar as bibliotecas necessárias.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run calculadora_99pay_streamlit.py
    ```

5.  **Acesse no navegador:**
    Após executar o comando acima, uma aba no seu navegador será aberta com a aplicação em `http://localhost:8501`.

---

## 🧠 Lógica de Cálculo

A calculadora simula o rendimento diário com base nas seguintes regras, que são aplicadas a cada 24 horas sobre o saldo do dia anterior:

1.  **Taxa CDI Diária:** A taxa CDI anual informada é convertida para uma taxa diária equivalente, considerando juros compostos ao longo de 365 dias.
2.  **Divisão por Faixas:** O saldo total é dividido em duas partes:
    - **Faixa 1:** O valor até o limite de R$ 5.000,00.
    - **Faixa 2:** O valor que excede R$ 5.000,00.
3.  **Cálculo do Rendimento:**
    - O valor na **Faixa 1** rende **110%** da taxa CDI diária.
    - O valor na **Faixa 2** rende **80%** da taxa CDI diária.
4.  **Juros Compostos:** O rendimento total do dia (soma das duas faixas) é adicionado ao saldo, que se torna a base de cálculo para o dia seguinte.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Se você tem sugestões de melhorias, novas funcionalidades ou encontrou algum bug, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

---

## 📄 Licença

Este projeto está licenciado sob a **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

Isso significa que você é livre para compartilhar e adaptar o código para **fins não comerciais**, desde que dê o crédito apropriado e licencie suas modificações sob os mesmos termos.

Para uso comercial, por favor, entre em contato com o autor para obter uma licença apropriada. Veja o arquivo `LICENSE` para mais detalhes.

---

*Desenvolvido por NerdFinança$ e aprimorado com a ajuda do Gemini Code Assist.*