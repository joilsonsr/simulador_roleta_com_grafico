import json
from collections import Counter
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename


# Configuração das colunas da roleta
COLUNA_1 = {1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34}
COLUNA_2 = {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35}
COLUNA_3 = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36}

# Função para carregar estatísticas do JSON usando um seletor gráfico
def carregar_estatisticas():
    print("Selecione o arquivo 'estatisticas.json'...")
    Tk().withdraw()  # Oculta a janela principal do tkinter
    arquivo = askopenfilename(title="Selecione o arquivo estatisticas.json", filetypes=[("JSON Files", "*.json")])
    if not arquivo:
        print("Nenhum arquivo selecionado. Usando estatísticas padrão.")
        return {"coluna_1": 0, "coluna_2": 0, "coluna_3": 0}
    
    try:
        with open(arquivo, "r") as f:
            dados = json.load(f)
        return contar_frequencias(dados)
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Verifique o formato.")
        return {"coluna_1": 0, "coluna_2": 0, "coluna_3": 0}

def escolher_colunas_dinamicamente(frequencia_colunas, atrasos, repeticoes_recentes=None, repeticoes_antigas=0.2,
                                   peso_frequencia=0.5, peso_atraso=0.3, peso_repeticao=0.01, peso_repeticao_antiga=0.3):
    """
    Escolhe as duas colunas com base em múltiplos critérios dinâmicos.
    
    Parâmetros:
    - frequencia_colunas: Dicionário com a frequência de cada coluna.
    - atrasos: Dicionário com o número de sorteios desde a última aparição de cada coluna.
    - repeticoes_recentes: Dicionário opcional com o número de repetições recentes de cada coluna.
    - repeticoes_antigas: Dicionário opcional com o número de repetições antigas de cada coluna.
    - peso_frequencia: Peso atribuído à frequência (padrão: 0.5).
    - peso_atraso: Peso atribuído ao atraso (padrão: 0.3).
    - peso_repeticao: Peso atribuído às repetições recentes (padrão: -0.2).
    - peso_repeticao_antiga: Peso atribuído às repetições antigas (padrão: 0.3).
    
    Retorna:
    - Uma lista com as duas colunas escolhidas.
    - Um dicionário com as pontuações detalhadas de cada coluna.
    """
    # Inicializar pontuação para cada coluna
    pontuacao = {}
    for coluna in ["coluna_1", "coluna_2", "coluna_3"]:
        # Frequência: quanto maior, maior a pontuação
        freq = frequencia_colunas.get(coluna, 0)
        
        # Atraso: quanto maior o atraso, maior a pontuação (usando inverso para evitar divisão por zero)
        atraso = atrasos.get(coluna, 1)
        pontuacao_atraso = 1 / (atraso + 1)  # Adicionamos 1 para evitar divisão por zero
        
        # Repetições recentes: penalizar colunas que participaram de repetições recentes
        if repeticoes_recentes is not None:
            repeticao = repeticoes_recentes.get(coluna, 0)
        else:
            repeticao = 0
        
        # Repetições antigas: beneficiar colunas com mais repetições antigas
        if repeticoes_antigas is not None:
            repeticao_antiga = repeticoes_antigas.get(coluna, 0)
        else:
            repeticao_antiga = 0
        
        # Calcular pontuação combinada
        pontuacao[coluna] = (
            peso_frequencia * freq +
            peso_atraso * pontuacao_atraso -
            peso_repeticao * repeticao +
            peso_repeticao_antiga * repeticao_antiga
        )
    
    # Ordenar colunas pela pontuação (maior pontuação primeiro)
    colunas_ordenadas = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)
    
    # Retornar as duas colunas com maior pontuação e as pontuações detalhadas
    colunas_escolhidas = [coluna for coluna, _ in colunas_ordenadas[:2]]
    return colunas_escolhidas, {coluna: round(score, 2) for coluna, score in pontuacao.items()}

def calcular_repeticoes_recentes(resultados):
    """
    Calcula o número de repetições consecutivas recentes para cada coluna.

    Parâmetros:
    - resultados: Lista de tuplas no formato [[numero, cor], ...].

    Retorna:
    - Um dicionário com o número de repetições recentes para cada coluna.
    """
    # Mapeamento dos números para as colunas
    colunas = {
        1: "coluna_1", 4: "coluna_1", 7: "coluna_1", 10: "coluna_1", 13: "coluna_1", 16: "coluna_1",
        19: "coluna_1", 22: "coluna_1", 25: "coluna_1", 28: "coluna_1", 31: "coluna_1", 34: "coluna_1",
        2: "coluna_2", 5: "coluna_2", 8: "coluna_2", 11: "coluna_2", 14: "coluna_2", 17: "coluna_2",
        20: "coluna_2", 23: "coluna_2", 26: "coluna_2", 29: "coluna_2", 32: "coluna_2", 35: "coluna_2",
        3: "coluna_3", 6: "coluna_3", 9: "coluna_3", 12: "coluna_3", 15: "coluna_3", 18: "coluna_3",
        21: "coluna_3", 24: "coluna_3", 27: "coluna_3", 30: "coluna_3", 33: "coluna_3", 36: "coluna_3"
    }

    # Converter números para colunas
    resultados_colunas = []
    for numero, _ in resultados:
        if numero == 0:  # Ignorar o número 0 (verde)
            continue
        resultados_colunas.append(colunas[numero])

    # Calcular repetições consecutivas
    repeticoes_recentes = {"coluna_1": 0, "coluna_2": 0, "coluna_3": 0}
    coluna_atual = None
    contador = 0

    for col in resultados_colunas:
        if col == coluna_atual:
            contador += 1
        else:
            if contador > 1:  # Considerar apenas sequências de 2 ou mais repetições
                repeticoes_recentes[coluna_atual] = contador
            coluna_atual = col
            contador = 1

    # Verificar a última sequência
    if contador > 1:
        repeticoes_recentes[coluna_atual] = contador

    return repeticoes_recentes

# Função para carregar resultados das rodadas usando um seletor gráfico
def carregar_resultados():
    Tk().withdraw()  # Oculta a janela principal do tkinter
    arquivo = askopenfilename(title="Selecione o arquivo resultados.json", filetypes=[("JSON Files", "*.json")])
    if not arquivo:
        print("Nenhum arquivo selecionado. Usando resultados padrão.")
        return []
    
    try:
        print("Selecione o arquivo "+arquivo)
        with open(arquivo, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Verifique o formato.")
        return []

# Função para contar frequência das colunas
def contar_frequencias(resultados):
    contagem = Counter()
    for numero, _ in resultados:
        if numero in COLUNA_1:
            contagem["coluna_1"] += 1
        elif numero in COLUNA_2:
            contagem["coluna_2"] += 1
        elif numero in COLUNA_3:
            contagem["coluna_3"] += 1
    return dict(contagem)

# Função para calcular atrasos das colunas
def calcular_atrasos(resultados):
    atrasos = {"coluna_1": 0, "coluna_2": 0, "coluna_3": 0}
    ultima_coluna = {"coluna_1": -len(resultados), "coluna_2": -len(resultados), "coluna_3": -len(resultados)}
    
    for i, (numero, _) in enumerate(resultados):
        if numero in COLUNA_1:
            ultima_coluna["coluna_1"] = i
        elif numero in COLUNA_2:
            ultima_coluna["coluna_2"] = i
        elif numero in COLUNA_3:
            ultima_coluna["coluna_3"] = i
    
    total_rodadas = len(resultados)
    for coluna, ultima_aparicao in ultima_coluna.items():
        atrasos[coluna] = total_rodadas - ultima_aparicao
    return atrasos

# Função para calcular frequência recente
def calcular_frequencia_recente(resultados):
    contagem = Counter()
    for numero, _ in resultados:
        if numero in COLUNA_1:
            contagem["coluna_1"] += 1
        elif numero in COLUNA_2:
            contagem["coluna_2"] += 1
        elif numero in COLUNA_3:
            contagem["coluna_3"] += 1
    return dict(contagem)

# Função para obter a coluna de um número
def obtem_coluna(numero):
    if numero in COLUNA_1:
        return "coluna_1"
    elif numero in COLUNA_2:
        return "coluna_2"
    elif numero in COLUNA_3:
        return "coluna_3"
    return None
def gerar_pesos(frequencia,atrasos,repeticoes_recentes,repeticoes_antigas):
    """
    Gera pesos dinâmicos com base nos dados fornecidos pelas funções auxiliares.
    
    Parâmetros:
    - resultados_analisados: Lista de listas com os resultados analisados.
    
    Retorna:
    - Um dicionário com os pesos ajustados para cada critério:
      - peso_frequencia
      - peso_atraso
      - peso_repeticao
      - peso_repeticao_antiga
    """
    # Obter os dados das funções auxiliares
    
    # Calcular o peso da frequência
    total_frequencia = sum(frequencia.values())
    peso_frequencia = 1 / (total_frequencia + 1) if total_frequencia > 0 else 0.5

    # Calcular o peso do atraso
    total_atrasos = sum(atrasos.values())
    peso_atraso = total_atrasos / len(resultados_analisados) if len(resultados_analisados) > 0 else 0.3

    # Calcular o peso das repetições recentes
    total_repeticoes_recentes = sum(repeticoes_recentes.values())
    peso_repeticao = -total_repeticoes_recentes / len(resultados_analisados) if len(resultados_analisados) > 0 else -0.2

    # Calcular o peso das repetições antigas
    total_repeticoes_antigas = sum(repeticoes_antigas.values())
    peso_repeticao_antiga = total_repeticoes_antigas / len(resultados_analisados) if len(resultados_analisados) > 0 else 0.3

    # Normalizar os pesos para garantir que somem 1
    soma_pesos = peso_frequencia + peso_atraso + abs(peso_repeticao) + peso_repeticao_antiga
    peso_frequencia /= soma_pesos
    peso_atraso /= soma_pesos
    peso_repeticao /= soma_pesos
    peso_repeticao_antiga /= soma_pesos

    return {
        "peso_frequencia": peso_frequencia,
        "peso_atraso": peso_atraso,
        "peso_repeticao": peso_repeticao,
        "peso_repeticao_antiga": peso_repeticao_antiga,
    }
# Função para calcular a coluna com o maior numero em um conjunto {"coluna_1":10, "coluna_2":5,"coluna_3":1}
def calcular_max_col(atrasos):
    max_coluna = max(atrasos, key=atrasos.get)
    return atrasos[max_coluna]
def calcular_min_col(atrasos):
    min_coluna = min(atrasos, key=atrasos.get)
    return atrasos[min_coluna]
# Função para simular apostas
def simular_apostas(resultados,resultados_analisados, saldo_inicial=100, aposta_base=10, estrategia="martingale"):
  
    saldo = saldo_inicial
    historico = []
    aposta_atual = aposta_base
    fibonacci_sequence = [1, 1]  # Sequência de Fibonacci inicial
    fib_index = 0  # Índice para acompanhar a sequência de Fibonacci
    
    # Estratégia Labouchere
    labouchere_sequencia = [1, 2, 3]  # Sequência inicial
    labouchere_vitoria = False

    # Estratégia Paroli
    paroli_contador = 0
    paroli_multiplicador = 2

    # Gestão de Risco
    max_perdas_consecutivas = 3  # Limite máximo de perdas consecutivas
    stop_gain = 20  # Alvo de lucro
    stop_loss = -5  # Limite de perda total
    perdas_consecutivas = 0
    colunas =[]
    inicia = True
    for i, (numero, _) in enumerate(resultados):
              
        frequencia_colunas = contar_frequencias(resultados_analisados)
        atrasos = calcular_atrasos(resultados_analisados)
        # Calcular repetições recentes
        repeticoes_recentes = calcular_repeticoes_recentes(resultados_analisados) 
        repeticoes_antigas = calcular_repeticoes_antigas(resultados_analisados)
   
       
        if 0 in resultados[i] or perdas_consecutivas >1:
            frequencia_colunas = contar_frequencias(resultados_analisados)
            atrasos = calcular_atrasos(resultados_analisados)
            # Calcular repetições recentes
            repeticoes_recentes = calcular_repeticoes_recentes(resultados_analisados) 
            repeticoes_antigas = calcular_repeticoes_antigas(resultados_analisados)
            pesos = gerar_pesos(frequencia_colunas, atrasos,repeticoes_recentes,repeticoes_antigas)
            colunas, _ = escolher_colunas_dinamicamente(
            frequencia_colunas=frequencia_colunas,
            atrasos=atrasos,
            repeticoes_recentes=repeticoes_recentes,
            repeticoes_antigas=repeticoes_antigas,
            peso_frequencia=pesos['peso_frequencia'],
            peso_atraso=pesos['peso_atraso'],
            peso_repeticao=pesos['peso_repeticao'],
            peso_repeticao_antiga=pesos['peso_repeticao_antiga']
            )
           
        else:   
           
            colunas,  pontuacoes = escolher_colunas_dinamicamente(
            frequencia_colunas=frequencia_colunas,
            atrasos=atrasos,
            repeticoes_recentes=repeticoes_recentes,
            repeticoes_antigas=repeticoes_antigas,
            peso_frequencia=0.7,
            peso_atraso=0.3,
            peso_repeticao=0.0,
            peso_repeticao_antiga=0.2   
            )
        
        # Define o valor da aposta com base na estratégia
        if estrategia == "labouchere":
            if not labouchere_sequencia:
                labouchere_sequencia = [1, 2, 3]  # Reinicia a sequência se estiver vazia
            aposta_atual = labouchere_sequencia[0] + labouchere_sequencia[-1]
            aposta_atual = min(aposta_atual, saldo)  # Garante que a aposta não exceda o saldo
        elif estrategia == "paroli":
            aposta_atual = aposta_base * (paroli_multiplicador ** paroli_contador)
            aposta_atual = min(aposta_atual, saldo)  # Garante que a aposta não exceda o saldo
    
        # Registra a aposta retirando do saldo
        saldo -= aposta_atual
        if saldo <= 0:
            saldo += aposta_atual
            print("Saldo insuficiente para gera uma nova aposta! Apostas encerradas.")
            break
        # Verifica se o número está em uma das colunas escolhidas
        vitoria = any(numero in globals()[coluna.upper()] for coluna in colunas)
        # print("ganhou ?",vitoria)
        if vitoria:
            saldo += (aposta_atual / 2) * 3  # Ganha o dobro da aposta
            
            # Atualiza a estratégia de aposta
            if estrategia == "martingale":
                aposta_atual = aposta_base  # Volta à aposta inicial
            elif estrategia == "fibonacci":
                fib_index = max(0, fib_index - 2)  # Retrocede dois passos na sequência
                aposta_atual = fibonacci_sequence[fib_index]
            elif estrategia == "dalembert":
                aposta_atual = max(aposta_base, aposta_atual - aposta_base)  # Diminui uma unidade
            elif estrategia == "labouchere":
                if len(labouchere_sequencia) > 1:
                    labouchere_sequencia.pop(0)  # Remove o primeiro elemento
                    labouchere_sequencia.pop(-1)  # Remove o último elemento
                else:
                    labouchere_sequencia = []  # Zera a sequência
            elif estrategia == "paroli":
                paroli_contador += 1  # Incrementa o contador de vitórias consecutivas
            
            perdas_consecutivas = 0  # Reseta o contador de perdas consecutivas
            historico.append((numero, "Vitória", aposta_atual, saldo))
            
            # Stop Gain
            if saldo - saldo_inicial >= stop_gain:
                print(f"Alvo de lucro atingido ({stop_gain}). Encerrando apostas.")
                break
        else:
            # Atualiza a estratégia de aposta
            if estrategia == "martingale":
                aposta_atual *= 2  # Dobra a aposta
            elif estrategia == "fibonacci":
                fib_index += 1
                if fib_index >= len(fibonacci_sequence):
                    fibonacci_sequence.append(fibonacci_sequence[-1] + fibonacci_sequence[-2])
                aposta_atual = fibonacci_sequence[fib_index]
            elif estrategia == "dalembert":
                aposta_atual += aposta_base  # Aumenta uma unidade
            elif estrategia == "labouchere":
                labouchere_sequencia.append(aposta_atual)  # Adiciona a aposta perdida ao final da sequência
            elif estrategia == "paroli":
                paroli_contador = 0  # Reseta o contador de vitórias consecutivas
            
            perdas_consecutivas += 1  # Incrementa o contador de perdas consecutivas
            historico.append((numero, "Derrota", aposta_atual, saldo))
            
            # Stop Loss
            if saldo - saldo_inicial <= stop_loss:
                print(f"Limite de perda total atingido ({stop_loss}). Encerrando apostas.")
                break
            
            # Limite de Perdas Consecutivas
            if perdas_consecutivas >= max_perdas_consecutivas:
                print(f"Limite de {max_perdas_consecutivas} perdas consecutivas atingido. Encerrando apostas.")
                break
        
        resultados_analisados.pop(0)
        resultados_analisados.append(resultados[i])
    ganho_liquido = saldo - saldo_inicial
    return saldo, historico, ganho_liquido


def calcular_repeticoes_antigas(resultados, limite_tempo=5):
    """
    Calcula o número de repetições antigas para cada coluna.

    Parâmetros:
    - resultados: Lista de tuplas no formato [[numero, cor], ...].
    - limite_tempo: Número de sorteios atrás para considerar uma repetição como "antiga".

    Retorna:
    - Um dicionário com o número de repetições antigas para cada coluna.
    """
    # Mapeamento dos números para as colunas
    colunas = {
        1: "coluna_1", 4: "coluna_1", 7: "coluna_1", 10: "coluna_1", 13: "coluna_1", 16: "coluna_1",
        19: "coluna_1", 22: "coluna_1", 25: "coluna_1", 28: "coluna_1", 31: "coluna_1", 34: "coluna_1",
        2: "coluna_2", 5: "coluna_2", 8: "coluna_2", 11: "coluna_2", 14: "coluna_2", 17: "coluna_2",
        20: "coluna_2", 23: "coluna_2", 26: "coluna_2", 29: "coluna_2", 32: "coluna_2", 35: "coluna_2",
        3: "coluna_3", 6: "coluna_3", 9: "coluna_3", 12: "coluna_3", 15: "coluna_3", 18: "coluna_3",
        21: "coluna_3", 24: "coluna_3", 27: "coluna_3", 30: "coluna_3", 33: "coluna_3", 36: "coluna_3"
    }

    # Converter números para colunas
    resultados_colunas = []
    for numero, _ in resultados:
        if numero == 0:  # Ignorar o número 0 (verde)
            continue
        resultados_colunas.append(colunas[numero])

    # Dividir os resultados em dois grupos: recentes e antigos
    resultados_antigos = resultados_colunas[limite_tempo:]  # Resultados além do limite de tempo
    resultados_recentes = resultados_colunas[:limite_tempo]  # Resultados dentro do limite de tempo

    # Calcular repetições antigas
    repeticoes_antigas = {"coluna_1": 0, "coluna_2": 0, "coluna_3": 0}
    coluna_atual = None
    contador = 0

    for col in resultados_antigos:
        if col == coluna_atual:
            contador += 1
        else:
            if contador > 1:  # Considerar apenas sequências de 2 ou mais repetições
                repeticoes_antigas[coluna_atual] += contador
            coluna_atual = col
            contador = 1

    # Verificar a última sequência
    if contador > 1:
        repeticoes_antigas[coluna_atual] += contador

    return repeticoes_antigas
# Função para plotar gráficos individuais
def plotar_grafico(historico, estrategia, saldo_final, ganho_liquido):
    rodadas = list(range(1, len(historico) + 1))
    saldos = [saldo for _, _, _, saldo in historico]
    
    plt.figure(figsize=(10, 6))
    plt.plot(rodadas, saldos, marker='o', linestyle='-', color='b', label=f"Estratégia: {estrategia.capitalize()}")
    plt.title(f"Evolução do Saldo ({estrategia.capitalize()})")
    plt.xlabel("Rodadas")
    plt.ylabel("Saldo")
    plt.grid(True)
    
    # Anotação para saldo final e ganho líquido
    plt.annotate(f"Saldo Final: {saldo_final:.2f}\nGanho Líquido: {ganho_liquido:.2f}", 
                 xy=(1, 1), xycoords='axes fraction', 
                 xytext=(-20, -20), textcoords='offset points',
                 ha='right', va='top', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
    
    plt.legend()
    plt.show()

# Função para plotar gráfico comparativo
def plotar_grafico_comparativo(historicos, estrategias,ganho_liquidos):
    plt.figure(figsize=(12, 8))
    for estrategia, historico,ganho in zip(estrategias, historicos,ganho_liquidos):
        rodadas = list(range(1, len(historico) + 1))
        saldos = [saldo for _, _, _, saldo in historico]
        plt.plot(rodadas, saldos, marker='o', linestyle='-', label=f"{estrategia.capitalize()} - ganho {ganho}")
        plt.title("Comparação de Estratégias")
    plt.xlabel("Rodadas")
    plt.ylabel("Saldo")
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # Carregar estatísticas e resultados
    resultados = carregar_resultados()
    tmt = 30
    resultados_analisados = resultados[:tmt]
    resultados =  resultados[tmt:]
   
    # Simular apostas com diferentes estratégias
    estrategias = ["martingale", "fibonacci", "dalembert", "paroli", "labouchere","nenhuma_estrategia"]
    historicos = []
    saldos_finais = []
    ganhos_liquidos = []
    
    for estrategia in estrategias:
        print(f"\n--- Simulação com estratégia: {estrategia.capitalize()} ---")
        saldo_final, historico_apostas, ganho_liquido = simular_apostas(
            resultados,resultados_analisados, saldo_inicial=10, aposta_base=1, estrategia=estrategia
        )
        print(f"Saldo final após as apostas: {saldo_final}")
        print(f"Ganho líquido: {ganho_liquido}")
        
        # Armazenar os dados para o gráfico comparativo
        historicos.append(historico_apostas)
        saldos_finais.append(saldo_final)
        ganhos_liquidos.append(ganho_liquido)
        
        # Plotar gráfico individual
        plotar_grafico(historico_apostas, estrategia, saldo_final, ganho_liquido)
    
    # Plotar gráfico comparativo
    plotar_grafico_comparativo(historicos, estrategias, ganhos_liquidos)
