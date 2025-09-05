# conditions.py
from continent import continentes

class Condition:
    def __init__(self, player):
        self.player = player

    def check(self, territories):
        """Deve retornar True se o jogador vencer"""
        raise NotImplementedError

class DominarAmericas(Condition):
    def check(self, territories):
        todos = continentes["america_do_sul"] + continentes["america_central_norte"]
        return all(t in territories[self.player.nome] for t in todos)

class DominarEuropa(Condition):
    def check(self, territories):
        return all(t in territories[self.player.nome] for t in continentes["europa"])

class DominarAsiaOceania(Condition):
    def check(self, territories):
        return all(t in territories[self.player.nome] for t in continentes["asia_oceania"])

class DominarAfrica(Condition):
    def check(self, territories):
        return all(t in territories[self.player.nome] for t in continentes["africa"])