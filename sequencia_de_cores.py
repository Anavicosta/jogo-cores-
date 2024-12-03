import pygame
import random
import time
import sqlite3

# Inicializar o pygame
pygame.init()

# Definir as dimensões da tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sequência de Cores")

# Definir as cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
cores = [VERMELHO, VERDE, AZUL, AMARELO]
nomes_cores = ["Vermelho", "Verde", "Azul", "Amarelo"]

# Fonte para o texto
fonte = pygame.font.SysFont(None, 50)

# Função para desenhar o texto na tela
def desenhar_texto(texto, cor, x, y):
    imagem = fonte.render(texto, True, cor)
    tela.blit(imagem, (x, y))

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect("ranking.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS ranking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        pontos INTEGER
    )''')
    conn.commit()
    return conn, c

# Função para salvar a pontuação no banco de dados
def salvar_ranking(nome, pontos):
    conn, c = conectar_banco()
    c.execute("INSERT INTO ranking (nome, pontos) VALUES (?, ?)", (nome, pontos))
    conn.commit()
    conn.close()

# Função para exibir o ranking
def exibir_ranking():
    conn, c = conectar_banco()
    c.execute("SELECT nome, pontos FROM ranking ORDER BY pontos DESC LIMIT 5")
    ranking = c.fetchall()
    tela.fill(PRETO)
    desenhar_texto("Ranking:", BRANCO, 100, 100)
    y = 200
    for i, (nome, pontos) in enumerate(ranking):
        desenhar_texto(f"{i+1}. {nome} - {pontos} pontos", BRANCO, 100, y)
        y += 50
    pygame.display.update()
    time.sleep(3)

# Função para gerar uma sequência aleatória de cores
def gerar_sequencia(nivel):
    return [random.choice(cores) for _ in range(nivel)]

# Função para desenhar a sequência de cores na tela
def desenhar_sequencia(sequencia, tempo_restante):
    tela.fill(PRETO)  # Limpa a tela antes de desenhar
    y = 50
    for cor in sequencia:
        pygame.draw.rect(tela, cor, pygame.Rect(100, y, 600, 100))
        y += 120
    desenhar_texto(f"Tempo restante: {int(tempo_restante)}s", BRANCO, 300, 500)
    pygame.display.update()

# Função para desenhar as cores embaralhadas na parte inferior
def desenhar_cores_embaralhadas(cores_embaralhadas):
    y = 400
    largura = 150
    for i, cor in enumerate(cores_embaralhadas):
        pygame.draw.rect(tela, cor, pygame.Rect(100 + (i * largura), y, largura, 100))
    pygame.display.update()

# Função para jogar uma fase
def jogar_fase(fase, nome_jogador):
    pontos = 0
    nivel = fase + 2  # A quantidade de cores na sequência aumenta a cada fase
    sequencia = gerar_sequencia(nivel)
    tempo_inicio = time.time()
    tempo_limite = max(3, 7 - fase)  # O tempo limite para cada fase diminui com a dificuldade, mas não fica menor que 3 segundos

    # Embaralhar as cores para a parte inferior da tela
    cores_embaralhadas = random.sample(cores, len(cores))

    while True:
        # Calculando o tempo restante
        tempo_restante = tempo_limite - (time.time() - tempo_inicio)

        if tempo_restante <= 0:
            break  # Fim da fase, tempo acabou

        # Desenhar a sequência de cores e as cores embaralhadas
        desenhar_sequencia(sequencia, tempo_restante)
        desenhar_cores_embaralhadas(cores_embaralhadas)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Verificar se o clique foi dentro de um dos retângulos de cores embaralhadas
                for i, cor in enumerate(cores_embaralhadas):
                    if 100 + (i * 150) <= x <= 100 + (i * 150) + 150 and 400 <= y <= 500:
                        if cor == sequencia[0]:
                            sequencia.pop(0)
                            pontos += 10
                            if len(sequencia) == 0:
                                break  # Fase completada com sucesso
                        else:
                            return 0  # Erro, o jogador perdeu a fase

    return pontos

# Função para obter o nome do jogador
def obter_nome_jogador():
    texto_digitado = ""
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return texto_digitado
                elif evento.key == pygame.K_BACKSPACE:
                    texto_digitado = texto_digitado[:-1]
                else:
                    texto_digitado += evento.unicode
        tela.fill(PRETO)
        desenhar_texto(f"Digite seu nome: {texto_digitado}", BRANCO, 100, 100)
        pygame.display.update()

# Função principal
def game():
    tela.fill(PRETO)
    desenhar_texto("Sequência de Cores", BRANCO, LARGURA//4, ALTURA//3)
    desenhar_texto("Pressione Enter para começar", BRANCO, LARGURA//4, ALTURA//2)
    pygame.display.update()

    nome_jogador = obter_nome_jogador()

    pontos_totais = 0
    total_fases = 5  # Número de fases aumentadas
    for fase in range(1, total_fases + 1):  # Mais fases
        pontos_totais += jogar_fase(fase, nome_jogador)
        if pontos_totais == 0:  # Perdeu, não avança
            break

    if pontos_totais > 0:
        salvar_ranking(nome_jogador, pontos_totais)

    exibir_ranking()

    pygame.quit()
    quit()

# Iniciar o jogo
if __name__ == "__main__":
    game()
