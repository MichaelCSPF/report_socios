import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def read_query_from_file(filepath: str) -> str:
    """
    Lê uma query SQL de um arquivo de texto.
    """
    print(f"Lendo a query do arquivo: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo de query '{filepath}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo de query: {e}")
        return None

def get_sql_server_engine():
    """
    Cria e retorna uma engine de conexão do SQLAlchemy para o SQL Server,
    usando autenticação do Windows (Trusted Connection).
    As credenciais são carregadas do arquivo .env.
    """
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv(dotenv_path='config/.env')

    server_name = os.getenv('SERVER')
    db_name = os.getenv('DATABASE')

    if not server_name or not db_name:
        raise ValueError("As variáveis de ambiente SERVER e DATABASE não foram definidas no arquivo .env")

    # String de conexão para SQL Server com Trusted Connection
    # O driver ODBC precisa estar instalado na máquina
    conn_str = (
        f"mssql+pyodbc://{server_name}/{db_name}?"
        "driver=ODBC+Driver+17+for+SQL+Server&"
        "Trusted_Connection=yes"
    )

    try:
        print(f"Conectando ao banco de dados '{db_name}' no servidor '{server_name}'...")
        engine = create_engine(conn_str)
        # Testa a conexão
        with engine.connect() as connection:
            print("Conexão com o banco de dados estabelecida com sucesso!")
        return engine
    except Exception as e:
        print(f"Falha ao conectar ao banco de dados: {e}")
        return None

def fetch_data(query_filepath: str) -> pd.DataFrame:
    """
    Função principal que orquestra a leitura da query e a busca dos dados.
    Retorna um DataFrame do Pandas com os resultados.
    """
    engine = get_sql_server_engine()
    if not engine:
        return None

    query = read_query_from_file(query_filepath)
    if not query:
        return None

    print("Executando a query no banco de dados...")
    try:
        df = pd.read_sql(text(query), engine)
        print("Dados buscados com sucesso!")
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao executar a query: {e}")
        return None