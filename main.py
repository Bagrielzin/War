from jogador import Jogador
from game_lock import Game
from continent import continentes

def main():
    jogadores = []
    while True:
        try:
            num_jogadores = int(input("Quantos jogadores irão participar? (3 a 6): "))
            if 3 <= num_jogadores <= 6:
                break
            else:
                print("Número inválido. Deve ser entre 3 e 6 jogadores.")
        except ValueError:
            print("Digite um número válido.")

    for i in range(num_jogadores):
        nome = input(f"Nome do jogador {i+1}: ")
        jogadores.append(Jogador(nome))

    # Criação da lista completa de territórios
    todos_territorios = (
        continentes["america_do_sul"] +
        continentes["america_central_norte"] +
        continentes["europa"] +
        continentes["asia_oceania"] +
        continentes["africa"]
    )

    # Inicialização e início do jogo
    g = Game(jogadores, todos_territorios)
    g.iniciar_jogo()

if __name__ == "__main__":
    main()
