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

    # Escolha do modo de sincronização
    print("\nEscolha o modo de sincronização:")
    print("1 - Ordem dos jogadores definidas aleatoriamente (Priority Scheduling)")
    print("2 - Ordem dos jogadores do primeiro ao último (Round Robin Scheduling)")
    escolha = ""
    while escolha not in ("1", "2"):
        escolha = input("Sua escolha (1/2): ").strip()

    respect_order = escolha == "1"

    # Criação da lista completa de territórios
    todos_territorios = (
        continentes["america_do_sul"] +
        continentes["america_central_norte"] +
        continentes["europa"] +
        continentes["asia_oceania"] +
        continentes["africa"]
    )

    # Inicialização e início do jogo
    g = Game(jogadores, todos_territorios, respect_order=respect_order)
    g.iniciar_jogo()

if __name__ == "__main__":
    main()
