import pandas as pd
import tarfile
import json
import os

# Extraindo os arquivos JSON do tar.gz
with tarfile.open('input.tar.gz', 'r:gz') as tar:
    tar.extractall(path='input_data')


# Função para ler JSONs em um DataFrame, lidando com subpastas
def read_json_files(directory):
    data_frames = []
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        # Verificar a estrutura dos dados
                        if isinstance(data, list):
                            if all(isinstance(item, dict) for item in data):
                                df = pd.DataFrame(data)
                                data_frames.append(df)
                            else:
                                print(
                                    f"Estrutura de dados inválida no arquivo (não todos os itens são dicionários): {file_path}")
                        elif isinstance(data, dict):
                            df = pd.DataFrame([data])  # Converter dicionário único em uma linha do DataFrame
                            data_frames.append(df)
                        else:
                            print(
                                f"Estrutura de dados inválida no arquivo (não é uma lista ou dicionário): {file_path}")
                            print(f"Conteúdo do arquivo {file_path}: {data}")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Erro ao ler o arquivo JSON: {file_path} - {str(e)}")

    if not data_frames:
        raise ValueError(
            "Nenhum dado foi lido dos arquivos JSON. Verifique se os arquivos JSON estão formatados corretamente.")

    return pd.concat(data_frames, ignore_index=True)


# Listando os arquivos no diretório para depuração
print("Arquivos na pasta 'input_data':", os.listdir('input_data/input'))

# Ler os arquivos JSON
df = read_json_files('input_data')

# Verificação dos dados lidos
print("Colunas no DataFrame:", df.columns)
print("Primeiras linhas do DataFrame:", df.head())

# Selecione as colunas relevantes (ajuste conforme necessário)
relevant_columns = ['artist', 'grossUSD', 'numTicketsSold', 'ticketPriceFrom',
                    'ticketPriceTo']  # substitua pelos nomes das colunas relevantes
df = df[relevant_columns]

# Extrair informações do campo 'artist'
df['artist_id'] = df['artist'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
df['artist_name'] = df['artist'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
df['artist_url'] = df['artist'].apply(lambda x: x.get('url') if isinstance(x, dict) else None)

# Remover a coluna original 'artist' agora que extraímos os dados relevantes
df = df.drop(columns=['artist'])

# Identificação e marcação de outliers
# Aqui usamos o método do IQR para identificar outliers
Q1 = df['grossUSD'].quantile(0.25)
Q3 = df['grossUSD'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df['outlier_yn'] = (df['grossUSD'] < lower_bound) | (df['grossUSD'] > upper_bound)

# Salvar o DataFrame resultante (opcional)
df.to_csv('output_data.csv', index=False)

# Explique suas escolhas de algoritmo
explanation = """
I used the Interquartile Range (IQR) method to identify outliers because it's a robust technique that isn't influenced by anomalous distributions. This method is suitable for outlier detection in revenue data (grossUSD).

This algorithm would scale well in a production pipeline because it's simple and efficient. 
However, if the amount of data significantly increases, other techniques such as model-based outlier detection could be considered, although the complexity and computational cost may increase.
"""

print(explanation)

# Envie o código de volta para o repositório para PR e revisão
# git commands (comentado porque depende do ambiente)
# git add output_data.csv
# git commit -m "Add processed data and outlier detection"
# git push origin branch_name
