# main.py
# encoding: UTF-8

import configparser
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader
from modules.data_loader import fetch_data
from modules.report_generator import create_component_html
from modules.email_sender import read_recipients_from_file, send_email

# LOGGER PRA DEBBUG/APURACAO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

CONFIG_FILE = 'config/config.ini'

def run_report_pipeline():
    """
    Orquestra a geração e envio de relatórios, usando corretamente os templates.
    """
    logging.info("--- Iniciando pipeline de relatórios ---")

    # PUXAR O CONFIG.INI COM UTF-8
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
    except Exception as e:
        logging.error(f"Não foi possível ler o arquivo de configuração '{CONFIG_FILE}'. Erro: {e}")
        return

    # PREPARAR O TEMPLATE DO E-MAIL (O SEU report_template.html)
    try:
        env = Environment(loader=FileSystemLoader('templates/'))
        # CARREGA TEMPLATE PRINCIPAL
        master_template = env.get_template('report_template.html')
    except Exception as e:
        logging.error(f"Não foi possível carregar o template 'report_template.html'. Verifique o caminho. Erro: {e}")
        return

    # ENCONTRAR E PROCESSAR CADA E-MAIL(CADA RELATÓRIO) ATIVO
    active_email_reports = [s for s in config.sections() if s.startswith('EmailReport:') and config.getboolean(s, 'ativo')]
    if not active_email_reports:
        logging.warning("Nenhum relatório de e-mail ativo encontrado. Encerrando.")
        return

    for report_section in active_email_reports:
        logging.info(f"Processando e-mail: '{report_section}'")
        try:
            report_config = config[report_section]
            
            # Monta o conteúdo dinâmico (tabelas, títulos)
            component_names = [c.strip() for c in report_config.get('components', '').split(',') if c.strip()]
            email_html_parts = []
            for comp_name in component_names:
                component_section = f"Component:{comp_name}"
                if not config.has_section(component_section):
                    logging.error(f"Configuração para componente '{comp_name}' não encontrada. Pulando.")
                    continue
                
                comp_config = config[component_section]
                dados_df = fetch_data(query_filepath=comp_config['query_file'])

                if dados_df is None:
                    email_html_parts.append(f"<h2>{comp_config.get('title','Componente')}</h2><p>Falha ao carregar dados.</p>")
                else:
                    component_html = create_component_html(dados_df, dict(comp_config))
                    email_html_parts.append(component_html)

            # Junta os componentes gerados em uma única string
            dynamic_content = "<br>".join(email_html_parts)
            
            # 4. INJETAR O CONTEÚDO DINÂMICO DENTRO DO TEMPLATE MESTRE
            final_html_body = master_template.render(
                # Usa a variável 'content' que está no seu template!
                content=dynamic_content 
            )

            # 5. ENVIAR O E-MAIL COM O HTML COMPLETO E CORRETO
            data_hoje = datetime.now().strftime('%d/%m/%Y')
            subject = f"{report_config['email_subject']} - {data_hoje}"
            
            destinatarios = read_recipients_from_file(report_config['recipient_list_file'])
            if destinatarios:
                send_email(
                    subject=subject,
                    html_body=final_html_body,
                    recipients=destinatarios
                )
            else:
                logging.warning(f"Nenhum destinatário para '{report_section}'. E-mail não enviado.")

        except Exception as e:
            logging.error(f"Falha crítica ao processar o relatório '{report_section}': {e}", exc_info=True)

if __name__ == "__main__":
    run_report_pipeline()