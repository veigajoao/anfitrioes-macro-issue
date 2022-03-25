#This files creates variables with string directions for all spreadsheet databases utilised by the sistem
import os
from pathlib import Path

#company Information
GENERAL_MANAGER = "Marcos Rodrigues Schmidt"
GENERAL_MANAGER_PHONE = "(48) 99118-5939"

#Information for accessing email host
#email server info
SMTP_SSL_HOST = 'smtp.zoho.com'
SMTP_SSL_PORT = 465
#login info
EMAIL_USERNAME = 'contato@anfitrioesdealuguel.com.br'
EMAIL_PASSWORD = '20Airbnb18'

#folder in company's Dropbox
_parent_folder = Path(os.getcwd()).parent

main_folder = str(_parent_folder.parent)
financials_folder = str(_parent_folder.parent) + "\\0. Back Office\\1. Financeiro"
hospitality_folder = str(_parent_folder.parent) + "\\1. Hospitalidade"
cleaning_folder = str(_parent_folder.parent) + "\\2. Limpeza"
maintenance_folder = str(_parent_folder.parent) + "\\3. Manutenção"
sistem_folder = str(_parent_folder.parent) + "\\4. Sistemas"


#Spreadsheet files that will be used in the application
#These variables will be utilized in other python files

#sitem folder files/subfolders
LOCATION_CHROME_DRIVER = sistem_folder + "\\infrastructure_apps\\chromedriver.exe"
LOCATION_STATIC_GUEST_AUTOMESSAGING = sistem_folder + "\\static\\guest_automessaging"
LOCATION_STATIC_FINANCIALS = sistem_folder + "\\static\\financials"
LOCATION_STATIC_CLEANING = sistem_folder + "\\static\\cleaning_template"
LOCATION_STATIC_MAINTENANCE = sistem_folder + "\\static\\maintenance_tasks"
LOCATION_STATIC_CICADA = sistem_folder + "\\static\\cicada"

#other files/folders
LOCATION_MAIN_DB = hospitality_folder + "\\BD-central-propriedades.xlsx"
PROPERTIES_FOLDER = hospitality_folder + "\\1. Informações das Propriedades"
PROPERTIES_FINANCIALS_FOLDER = financials_folder + "\\3. Faturamento e Fiscal\\1. Faturamento Repasse de Aluguéis"
PROPERTIES_FINANCIALS = financials_folder + "\\3. Faturamento e Fiscal\\1. Faturamento Repasse de Aluguéis\\Controle de Repasses.xlsx"
PROPERTIES_FINANCIALS_RES_DATA = financials_folder + "\\3. Faturamento e Fiscal\\1. Faturamento Repasse de Aluguéis\\1. Arquivos para gerar relatórios\\Lista de reservas.csv"
PROPERTIES_FINANCIALS_EXP_DATA = financials_folder + "\\3. Faturamento e Fiscal\\1. Faturamento Repasse de Aluguéis\\1. Arquivos para gerar relatórios\\Lista despesas a proprietario.csv"
PROPERTIES_FINANCIALS_PAY_DATA = financials_folder + "\\3. Faturamento e Fiscal\\1. Faturamento Repasse de Aluguéis\\1. Arquivos para gerar relatórios\\x.csv"
PROPERTY_FINANCIALS_NF_DATA = financials_folder + "\\1. Notas Fiscais\\2. Notas Despesas de Imóveis"
UPDATE_RESERVATIONS_FOLDER = hospitality_folder + "\\Atualizar reservas"


LOCATION_RECEPTION_CONTROL_SHEET = hospitality_folder + "\\Planilha de Controle - Reservas.xlsm"
LOCATION_REGISTRATION_CONTROL_SHEET = hospitality_folder + "\\4. Procedimentos de Recepção\\6. Controle Cadastros.xlsm"
LOCATION_CLEANING_CONTROL_SHEET = cleaning_folder + "\\Planilha - Agendamentos de Limpezas.xlsm"
LOCATION_MAINTENANCE_SHEET = maintenance_folder + "\\Planilha controle de manutenções.xlsm"

LOCATION_MAINTENANCE_OS_FOLDER = maintenance_folder + "\\1. OS para imprimir"
LOCATION_CLEANING_OS_FOLDER = cleaning_folder + "\\1. Fichas para imprimir"
