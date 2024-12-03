import customtkinter as ctk
import requests
import csv
import unicodedata
import re
import random
from io import StringIO

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Artemis")
        master.geometry("600x500")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")  # "light" ou "dark"
        ctk.set_default_color_theme("dark-blue")  # Temas disponíveis: "blue", "green", "dark-blue"

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Artemis, sua assistente virtual. Me informe de qual ano você deseja saber informações?\n")
        self.text_area.configure(state="disabled")  # Apenas leitura na área de texto

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite a sua solicitação...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

        # Dicionário de sinônimos
        self.synonyms = {
            "nome": ["nome", "designação", "título"],
            "modalidade": ["modalidade", "tipo de atividade", "classificação"],
            "tipo_sede": ["tipo de sede", "localização", "instalação"],
            "data_fundacao": ["data de fundação", "data de criação", "data de estabelecimento"],
            "cnpj": ["CNPJ", "número de registro", "identificação tributária"],
            "bairro": ["bairro", "região", "local"],
            "cidade": ["cidade", "município", "localidade"],
            "rpa": ["RPA", "Registro de Prestação de Serviço"],
            "uf": ["UF", "unidade federativa", "estado"]
        }

        # Exemplo de frases para respostas aleatórias
        self.responses = [
            "Encontrei informações:\n",
            "Aqui estão os dados que encontrei:\n",
            "Informações disponíveis:\n",
            "Os detalhes que consegui são:\n"
        ]

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        # Processar a entrada do usuário
        response = self.get_response(user_input)

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Artemis: " + response + "\n")
        self.text_area.configure(state="disabled")

        self.entry.delete(0, ctk.END)

    def normalize_string(self, s):
        # Remover acentos e converter para minúsculas
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower()

    def build_response(self, row):
        chosen_response = random.choice(self.responses)
        return (f"{chosen_response}"
                f"{random.choice(self.synonyms['nome'])}: {row['nome']}\n"
                f"{random.choice(self.synonyms['modalidade'])}: {row['modalidade']}\n"
                f"{random.choice(self.synonyms['tipo_sede'])}: {row['tipo_sede']}\n"
                f"{random.choice(self.synonyms['data_fundacao'])}: {row['data_fundacao']}\n"
                f"{random.choice(self.synonyms['cnpj'])}: {row['cnpj']}\n"
                f"{random.choice(self.synonyms['bairro'])}: {row['bairro']}\n"
                f"{random.choice(self.synonyms['cidade'])}: {row['cidade']}\n"
                f"{random.choice(self.synonyms['rpa'])}: {row['rpa']}\n"
                f"{random.choice(self.synonyms['uf'])}: {row['uf']}")

    def get_response(self, user_input):
        # Normalizar a entrada do usuário
        user_input_normalized = self.normalize_string(user_input)

        # Novo link para o CSV exportado
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTHI0cSRrbVOlh7aPLITwFFFouwSyYxOgyLQLNkqIbGyNvFmqIxvrBvteUYouH9-xU-zTgFQoi9kT2R/pub?output=csv"

        # Tentar obter os dados do CSV
        try:
            response = requests.get(csv_url)
            response.raise_for_status()  # Verifica se o download foi bem-sucedido

            # Ler o conteúdo do CSV
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)

            # Variáveis para armazenar filtros de busca
            ano, sigla_uf = None, None

            # Tentativa de extrair ano e sigla de UF do input do usuário
            ano_match = re.search(r'\b(20\d{2})\b', user_input_normalized)
            if ano_match:
                ano = ano_match.group(1)
            uf_match = re.search(r'\b(?:ac|al|ap|am|ba|ce|df|es|go|ma|mt|ms|mg|pa|pb|pr|pe|pi|rj|rn|rs|ro|rr|sc|sp|se|to)\b', user_input_normalized)
            if uf_match:
                sigla_uf = uf_match.group(0).upper()

            # Verificar se ao menos o ano ou a UF foi informado
            if not ano and not sigla_uf:
                return "Por favor, especifique pelo menos o ano ou a sigla de UF para obter informações mais precisas."

            # Procurar pela linha correspondente no CSV
            for row in reader:
                ano_cell = row['data_fundacao'][:4]  # Extrair ano da coluna 'data_fundacao'
                uf_cell = row['uf'].strip().upper()

                if (ano == ano_cell if ano else True) and (sigla_uf == uf_cell if sigla_uf else True):
                    # Construir uma resposta com as informações da linha encontrada
                    return self.build_response(row)

            return "Não encontrei dados correspondentes para os parâmetros especificados."

        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a tabela: {e}"

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()