#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
import customtkinter as ctk
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from SAVE import salvar_letra, char_accents
from PIL import Image, ImageTk
import threading

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


def process_links(base_url):
    try:
        # Fazendo a requisição HTTP para pegar o conteúdo da página
        response = requests.get(base_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Encontrando todos os links
            links = soup.find_all('a', href=True)
            links_ok = []

            # Extraindo e resolvendo URLs relativas
            for link in links:
                absolute_url = urljoin(base_url, link['href'])

                if (absolute_url.startswith(
                    'https://musicasparamissa.com.br/musica/'
                ) or absolute_url.startswith(
                    'https://musica-liturgica.net/view.pl/'
                ) or absolute_url.startswith(
                    'https://www.letras.mus.br/catolicas/'
                )):
                    links_ok.append(absolute_url)

            title = soup.title.string.strip() if soup.title else "letra"
            title = char_accents(title)

            # Salva os links em um arquivo
            results = []
            for lnk in links_ok:
                ok, letter_saved = salvar_letra(
                    lnk,
                    folder=title,
                    get_text=False
                )
                results.append(letter_saved)

            result = "\n".join([
                f'{index+1} - {item}' for index, item in enumerate(results)
            ])

            if result:
                return f"Links encontrados e as letras a seguir foram salvas na pasta:\n{title}\n\n{result}"
            else:
                return f"Este site não é válido!\nPor favor, verifique!"

        else:
            return f"Erro ao acessar o site: {response.status_code}"

    except Exception as e:
        return f"Erro no processamento: {str(e)}"


class LinkProcessorApp(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title("Conversor de Links")
        self.geometry("600x350")
        self.minsize(500, 300)

        # Caminho para o ícone
        icon_path = 'assets/download_icon.png'

        # Verifica se o arquivo existe
        if os.path.exists(icon_path):
            # Define o ícone da janela
            self.iconphoto(
                False,
                ImageTk.PhotoImage(Image.open(icon_path))
            )

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de entrada
        self.entry_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.entry_frame.pack(fill="x", padx=10, pady=10)

        # Entrada de URL
        self.url_entry = ctk.CTkEntry(
            self.entry_frame,
            width=350
        )
        self.url_entry.pack(
            side="left", expand=True, fill="x", padx=(0, 10)
        )
        self.url_entry.focus()

        # Botão de limpar
        self.clear_button = ctk.CTkButton(
            self.entry_frame,
            text="",
            width=40,
            image=ctk.CTkImage(light_image=Image.open("assets/clear.png")),
            command=self.on_clear_button
        )
        self.clear_button.pack(side="right", padx=(5, 0))

        # Botão de processar
        self.process_button = ctk.CTkButton(
            self.entry_frame,
            text="Processar Link",
            image=ctk.CTkImage(light_image=Image.open("assets/exec.png")),
            command=self.on_process_button
        )
        self.process_button.pack(side="right", padx=(0, 5))

        # Label de resultado
        self.result_caption = ctk.CTkLabel(
            self.main_frame,
            text="◄  Mensagem  ►",
            font=("Arial", 14, "bold")
        )
        self.result_caption.pack(pady=(15, 5))

        self.text_var = tk.StringVar()

        # Área de resultado com rolagem
        self.result_box = ctk.CTkScrollableFrame(
            self.main_frame,
            height=200,
            width=500
        )
        self.result_box.pack()

        self.result_text = ctk.CTkLabel(
            self.result_box,
            textvariable=self.text_var,
            wraplength=480
        )
        self.result_text.pack()

    def on_clear_button(self):
        self.url_entry.delete(0, tk.END)
        self.text_var.set("")

    def on_process_button(self):
        base_url = self.url_entry.get()

        if base_url:
            # Usar threading para evitar congelar a interface
            threading.Thread(
                target=self.process_links_thread, args=(base_url,), daemon=True
            ).start()
        else:
            self.text_var.set("")
            self.text_var.set("Por favor, insira uma URL válida.")

    def process_links_thread(self, base_url):
        result_message = process_links(base_url)
        # Usar after para atualizar a interface de forma segura
        self.after(0, self.update_result_text, result_message)

    def update_result_text(self, message):
        self.text_var.set("")
        self.text_var.set(message)


def main():
    app = LinkProcessorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
