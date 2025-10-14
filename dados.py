import pandas as pd

df = pd.read_csv('War.csv', delimiter=',')

analise_estatistica = df.groupby(['Modo', 'Numero_jogadores'])['Rodadas'].agg(
    ['mean', 'median', 'std', 'min', 'max']
)

analise_estatistica = analise_estatistica.rename(columns={
    'mean': 'Média de Rodadas',
    'median': 'Mediana de Rodadas',
    'std': 'Desvio Padrão',
    'min': 'Mínimo',
    'max': 'Máximo'
})

analise_estatistica = analise_estatistica.round(1)

print("Análise Estatística da Duração das Partidas de War")
print("=" * 55)
print(analise_estatistica)