# modules/report_generator.py 

import pandas as pd
import logging

# --- FUNÇÕES DE ESTILO E FORMATAÇÃO  ---

def highlight_first_row_styler(df: pd.DataFrame):
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    first_row_style = 'background-color: #b9d3f5; color: #000000;'
    style_df.iloc[0] = first_row_style
    return style_df

# --- Função de  formatação de valores brasileiros R$ ---
def format_brazilian_currency(val):
    if pd.isna(val): return ''
    formatted_val = f'{val:,.0f}'
    brazilian_format_string = formatted_val.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"R$ {brazilian_format_string}"

# --- Funções de formatação de números brasileiros ---
def format_brazilian_number(val):
    if pd.isna(val): return ''
    formatted_val = f'{val:,.1f}'
    brazilian_format_string = formatted_val.replace(',', 'X').replace('.', ',').replace('X', '.')
    return brazilian_format_string

# --- Funções de estilo para células específicas (Alcance meta)---
def style_alcance_cells(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    if val < 0.97: color = '#C10000'
    elif val < 1.0: color = '#F07B0C'
    else: color = '#04861A'
    return f'background-color: {color}; color: white;'

# --- Funções de estilo para células de crescimento (positivo e negativo) ---
def style_cresc_font(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    if val < 0: color = '#C10000'
    else: color = '#04861A'
    return f'background-color: {color}; color: white;'

# --- Função de estilo para células de crescimento inverso (positivo = Vermelho e negativo = Verde) ---
def style_cresc_inverso_font(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    if val > 0: color = '#C10000'
    else: color = '#04861A'
    return f'background-color: {color}; color: white;'

# --- Função de formatação de porcentagem brasileira ---
def format_brazilian_percentage(val):
    if pd.isna(val): return '-'
    standard_percentage = "{:.1%}".format(val)
    return standard_percentage.replace('.', ',')

# --- Função auxiliar para parsear listas de colunas ---
def _parse_column_list(config_str: str) -> list:
    if not config_str: return []
    return [col.strip() for col in config_str.split(',') if col.strip()]

# --- FUNÇÃO PRINCIPAL ---
# Em modules/report_generator.py

def create_component_html(data_df: pd.DataFrame, component_config: dict) -> str:
    """
    Gera um componente HTML (título + tabela) a partir de um DataFrame e das regras de estilo do config.
    Versão final com método de renomeação de cabeçalho compatível com TODAS as versões do Pandas.
    """
    component_title = component_config.get('title', 'Relatório')
    if data_df.empty:
        return f"<h2>{component_title}</h2><p>Não há dados para exibir.</p>"

    # 1. Parsear TODAS as configurações no início.
    date_cols = _parse_column_list(component_config.get('date_cols', ''))
    currency_cols = _parse_column_list(component_config.get('currency_cols', ''))
    percentage_cols = _parse_column_list(component_config.get('percentage_cols', ''))
    numeric_cols = _parse_column_list(component_config.get('numeric_cols_1decimal', ''))
    alcance_cols = _parse_column_list(component_config.get('alcance_cols', ''))
    crescimento_cols = _parse_column_list(component_config.get('crescimento_cols', ''))
    crescimento_inverso_cols = _parse_column_list(component_config.get('crescimento_cols_inverso', ''))
    highlight_row1 = component_config.get('highlight_first_row', 'no').lower() in ['yes', 'true', '1']
    should_clean_headers = component_config.get('clean_headers', 'no').lower() in ['yes', 'true', '1']

    try:
        styler = data_df.style

        # 2. APLICAR TODA A FORMATAÇÃO E ESTILO USANDO OS NOMES ORIGINAIS
        if date_cols: styler = styler.format("{:%d/%m/%Y}", subset=date_cols, na_rep="-")
        if currency_cols: styler = styler.format(format_brazilian_currency, subset=currency_cols)
        if numeric_cols: styler = styler.format(format_brazilian_number, subset=numeric_cols)
        if alcance_cols:
            styler = styler.apply(lambda s: [style_alcance_cells(v) for v in s], subset=alcance_cols)
            styler = styler.format(format_brazilian_percentage, subset=alcance_cols)
        if crescimento_cols:
            styler = styler.apply(lambda s: [style_cresc_font(v) for v in s], subset=crescimento_cols)
            styler = styler.format(format_brazilian_number, subset=crescimento_cols)
        if crescimento_inverso_cols:
            styler = styler.apply(lambda s: [style_cresc_inverso_font(v) for v in s], subset=crescimento_inverso_cols)
            styler = styler.format(format_brazilian_number, subset=crescimento_inverso_cols)
        if percentage_cols: styler = styler.format(format_brazilian_percentage, subset=percentage_cols)
        if highlight_row1 and not data_df.empty:
            styler = styler.apply(highlight_first_row_styler, axis=None)

        # 3. RENDERIZAR O HTML e configurações finais
        styler = styler.set_table_attributes('class="table table-striped"').hide(axis="index")
        table_html = styler.to_html(escape=False)
        
        if should_clean_headers:
            new_labels = {col: col.replace('_', ' ').title() for col in data_df.columns}
            for original_name, new_name in new_labels.items():
                # Substitui o cabeçalho antigo pelo novo no texto do HTML
                # O padrão ">original_name</th>" é específico para garantir que só cabeçalhos sejam trocados
                table_html = table_html.replace(f">{original_name}</th>", f">{new_name}</th>")
                
    except KeyError as e:
        logging.error(f"Erro de Chave ao estilizar '{component_title}': a coluna '{e}' especificada no config.ini não foi encontrada no DataFrame. Verifique a query e o config.", exc_info=True)
        return f"<h2>{component_title}</h2><p>Erro ao gerar a tabela: Coluna não encontrada. Verifique os logs.</p>"
    except Exception as e:
        logging.error(f"Falha ao estilizar o DataFrame para '{component_title}': {e}", exc_info=True)
        return f"<h2>{component_title}</h2><p>Erro ao gerar a tabela. Verifique os logs.</p>"

    final_html = f"<h2>{component_title}</h2>\n{table_html}"
    return final_html