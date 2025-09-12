import random
import threading
import time
from conditions import DominarAmericas, DominarEuropa, DominarAsiaOceania, DominarAfrica
from continent import continentes
from connections import conexoes_extras

def pode_atacar(origem, destino):
    for lista in continentes.values():
        if origem in lista and destino in lista:
            return True
    return (origem, destino) in conexoes_extras or (destino, origem) in conexoes_extras

class Game:
    def __init__(self, players, todos_territorios):
        self.players = players
        self.todos_territorios = todos_territorios
        self.lock = threading.Lock()
        self.winner = None
        self.vitoria_condicao = None
        self.territories = {}
        self._distribuir_territorios_iniciais()

    # ==== CONFIGURAÇÃO INICIAL ====
    def _distribuir_territorios_iniciais(self):
        random.shuffle(self.todos_territorios)
        qtd_jogadores = len(self.players)
        for i, territorio in enumerate(self.todos_territorios):
            jogador = self.players[i % qtd_jogadores]
            self.territories[territorio] = {"owner": jogador.nome, "troops": 1}

        tropas_extras_por_jogador = 10
        for jogador in self.players:
            for _ in range(tropas_extras_por_jogador):
                territorios_jogador = [t for t, d in self.territories.items() if d["owner"] == jogador.nome]
                escolha = random.choice(territorios_jogador)
                self.territories[escolha]["troops"] += 1

    # ==== LOOP PRINCIPAL ====
    def iniciar_jogo(self):
        threads = [threading.Thread(target=self.jogar, args=(j,)) for j in self.players]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.exibir_estatisticas_finais()

    def jogar(self, jogador):
        while not self.winner:
            with self.lock:
                # Reforços antes do ataque
                self._reforcos_pre_ataque(jogador)

                # Escolhe alvo e ataca
                alvo = self._possiveis_alvos(jogador)
                if alvo:
                    self.realizar_ataque(jogador, alvo)

                # Verifica vitória após ataque
                if self.verificar_vitoria(jogador):
                    self.winner = jogador.nome
                    return

            time.sleep(0.05)

    # ==== AÇÕES DO TURNO ====
    def _reforcos_pre_ataque(self, jogador):
        territorios_jogador = [t for t, d in self.territories.items() if d["owner"] == jogador.nome]
        reforcos = max(1, len(territorios_jogador) // 4)
        for _ in range(reforcos):
            terr = random.choice(territorios_jogador)
            self.territories[terr]["troops"] += 1
        if reforcos > 0:
            print(f"\n[REFORÇOS] {jogador.nome} recebeu {reforcos} tropas adicionais distribuídas aleatoriamente.")

    def _possiveis_alvos(self, jogador):
        possiveis = []
        for origem, dados in self.territories.items():
            if dados["owner"] == jogador.nome and dados["troops"] >= 2:
                for destino, dest_data in self.territories.items():
                    if dest_data["owner"] != jogador.nome and pode_atacar(origem, destino):
                        possiveis.append((origem, destino))
        return random.choice(possiveis) if possiveis else None

    def realizar_ataque(self, jogador, alvo):
        origem, destino = alvo
        tropas_ataque = self.territories[origem]["troops"]
        tropas_defesa = self.territories[destino]["troops"]

        chance = 50 + (tropas_ataque - tropas_defesa) * 5
        chance = max(10, min(90, chance))

        sucesso = random.randint(1, 100) <= chance
        dono_anterior = self.territories[destino]["owner"]

        if sucesso:
            self.territories[destino]["owner"] = jogador.nome
            self.territories[destino]["troops"] = 1
            self.territories[origem]["troops"] -= 1
        else:
            self.territories[origem]["troops"] -= 1

        print(f"\n[ATAQUE] {jogador.nome} atacou {dono_anterior} de {origem} para {destino} "
              f"({tropas_ataque} vs {tropas_defesa}) | Chance: {chance}% | "
              f"{'Vitória' if sucesso else 'Derrota'} ")

    # ==== CONDIÇÕES DE VITÓRIA ====
    def verificar_vitoria(self, jogador):
        conditions = [
            (DominarAmericas(jogador), f"{jogador.nome} dominou toda a América"),
            (DominarEuropa(jogador), f"{jogador.nome} dominou toda a Europa"),
            (DominarAsiaOceania(jogador), f"{jogador.nome} dominou toda a Ásia e Oceania"),
            (DominarAfrica(jogador), f"{jogador.nome} dominou toda a África")
        ]
        mapa = {p.nome: [t for t, d in self.territories.items() if d["owner"] == p.nome] for p in self.players}

        for cond, mensagem in conditions:
            if cond.check(mapa):
                self.vitoria_condicao = mensagem
                return True
        return False

    # ==== FINALIZAÇÃO ====
    def exibir_estatisticas_finais(self):
        print("\n===== {} venceu o jogo!! =====".format(self.winner))
        if self.vitoria_condicao:
            print(self.vitoria_condicao)
            if "América" in self.vitoria_condicao:
                paises = sorted(continentes["america_do_sul"] + continentes["america_central_norte"])
            elif "Europa" in self.vitoria_condicao:
                paises = sorted(continentes["europa"])
            elif "África" in self.vitoria_condicao:
                paises = sorted(continentes["africa"])
            elif "Ásia e Oceania" in self.vitoria_condicao:
                paises = sorted(continentes["asia_oceania"])
            else:
                paises = []
            print(f"Países da condição de vitória: {paises}")

        print("\n=== Estatísticas Finais do Jogo ===\n")
        for jogador in self.players:
            territorios = sorted([t for t, d in self.territories.items() if d["owner"] == jogador.nome])
            print(f"{jogador.nome}: {len(territorios)} territórios")
            for t in territorios:
                tropas = self.territories[t]["troops"]
                print(f"  - {t}: {tropas} tropas")
            print("-----------------------------------\n")