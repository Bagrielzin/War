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
    def __init__(self, players, todos_territorios, respect_order=False):
        self.players = players
        self.todos_territorios = todos_territorios
        self.lock = threading.Lock()                # protege estrutura de territórios
        self.condition = threading.Condition()      # coordena turnos ordenados
        self.winner = None
        self.vitoria_condicao = None
        self.territories = {}
        self.respect_order = respect_order

        # scheduling / ordem fixa
        self.play_order = []     # lista de nomes na ordem de jogada
        self.turn_index = 0      # índice atual na play_order

        # contador de rodadas
        self.round_counter = 1

        self._distribuir_territorios_iniciais()
        if self.respect_order:
            self._schedule_players_priority()
        else:
            self._schedule_players_round_robin()
        print(f"\n=== Rodada {self.round_counter} ===")

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
                if territorios_jogador:
                    escolha = random.choice(territorios_jogador)
                    self.territories[escolha]["troops"] += 1

    def _schedule_players_priority(self):
        prioridades = {p.nome: random.randint(1, 100) for p in self.players}
        ordenado = sorted(self.players, key=lambda p: prioridades[p.nome], reverse=True)
        self.play_order = [p.nome for p in ordenado]
        print("\n=== Ordem de jogada (Priority Scheduling) ===")
        for i, p in enumerate(ordenado, start=1):
            print(f"{i}. {p.nome} (prioridade: {prioridades[p.nome]})")
        print("=============================================\n")

    def _schedule_players_round_robin(self):
        self.play_order = [p.nome for p in self.players]
        print("\n=== Ordem de jogada (Round Robin) ===")
        for i, nome in enumerate(self.play_order, start=1):
            print(f"{i}. {nome}")
        print("=====================================\n")

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
                territorios_jogador = [t for t, d in self.territories.items() if d["owner"] == jogador.nome]
            if not territorios_jogador:
                with self.condition:
                    if self.play_order and self.play_order[self.turn_index] == jogador.nome:
                        self._advance_turn()
                        self.condition.notify_all()
                print(f"[ELIMINADO] {jogador.nome} não possui mais territórios e saiu do jogo.")
                return

            with self.condition:
                while not self.winner and self.play_order[self.turn_index] != jogador.nome:
                    self.condition.wait()

                if self.winner:
                    return

                with self.lock:
                    self._reforcos_pre_ataque(jogador)

                    alvo = self._possiveis_alvos(jogador)
                    if alvo:
                        self.realizar_ataque(jogador, alvo)

                    if self.verificar_vitoria(jogador):
                        self.winner = jogador.nome
                        self.condition.notify_all()
                        return

                self._advance_turn()
                self.condition.notify_all()

    # ==== CONTROLE DE TURNOS ====
    def _advance_turn(self):
        total_players = len(self.play_order)
        if total_players == 0:
            return

        for _ in range(total_players):
            self.turn_index = (self.turn_index + 1) % total_players
            candidato = self.play_order[self.turn_index]
            with self.lock:
                territorios_cand = [t for t, d in self.territories.items() if d["owner"] == candidato]
            if territorios_cand:
                # Se o turno voltou ao primeiro jogador, incrementa rodada
                if self.turn_index == 0:
                    self.round_counter += 1
                    print(f"\n=== Rodada {self.round_counter} ===")
                return

        # Se sobrar apenas um jogador vivo
        with self.lock:
            vivos = [p.nome for p in self.players if any(d["owner"] == p.nome for d in self.territories.values())]
        if len(vivos) == 1:
            self.winner = vivos[0]

    # ==== AÇÕES DO TURNO ====
    def _reforcos_pre_ataque(self, jogador):
        territorios_jogador = [t for t, d in self.territories.items() if d["owner"] == jogador.nome]
        reforcos = max(1, len(territorios_jogador) // 4)
        for _ in range(reforcos):
            if territorios_jogador:
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
        vivos = [p.nome for p in self.players if any(d["owner"] == p.nome for d in self.territories.values())]
        if len(vivos) == 1:
            self.vitoria_condicao = f"{vivos[0]} eliminou todos os outros jogadores"
            return True
        return False

    # ==== FINALIZAÇÃO ====
    def exibir_estatisticas_finais(self):
        print("\n===== {} venceu o jogo!! =====".format(self.winner))
        print(f"Total de rodadas: {self.round_counter}")
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
