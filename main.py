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
    print("Escolha o modo de sincronização:")
    print("1 - Ordem dos jogadores definidas aleatoriamente a cada rodada (Priority Scheduling)")
    print("2 - Ordem dos jogadores do primeiro ao último (FCFS)")
    print("3 - Modo de jogo livre, sem lock e scheduling")
    escolha = ""
    while escolha not in ("1", "2", "3"):
        escolha = input("Sua escolha (1/2/3): ").strip()

    # Criação da lista completa de territórios
    todos_territorios = (
        continentes["america_do_sul"] +
        continentes["america_central_norte"] +
        continentes["europa"] +
        continentes["asia_oceania"] +
        continentes["africa"]
    )

    if escolha == ("1", "2"):
        from game_lock import Game
        respect_order = escolha == "1"
        g = Game(jogadores, todos_territorios, respect_order=respect_order)
        g.iniciar_jogo()

    else:
        from game import Game
        g = Game(jogadores, todos_territorios)
        g.iniciar_jogo()

if __name__ == "__main__":
    main()
