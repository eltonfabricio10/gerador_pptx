#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from SEARCH import search_google
from SAVE import salvar_letra
import customtkinter as ctk
import tkinter as tk
import os
import threading
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox as ctkbox

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class LyricSearchApp(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title("Buscar Letras")
        self.geometry("600x400")
        self.minsize(400, 200)

        # Caminho para o ícone
        icon_path = 'assets/search_icon.png'

        # Verifica se o arquivo existe
        if os.path.exists(icon_path):
            # Define o ícone da janela
            self.iconphoto(
                False,
                ImageTk.PhotoImage(Image.open(icon_path))
            )

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Frame de pesquisa
        self.search_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.search_frame.pack(fill="x", padx=10, pady=10)

        # Entrada de pesquisa
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            width=250
        )
        self.search_entry.pack(
            side="left", expand=True, fill="x", padx=(0, 10)
        )
        self.search_entry.focus()

        # Botão de limpar
        self.clear_button = ctk.CTkButton(
            self.search_frame,
            text="",
            width=40,
            image=ctk.CTkImage(
                light_image=Image.open("assets/clear.png")
            ),
            command=self.on_clear_button_clicked
        )
        self.clear_button.pack(side="right", padx=(5, 0))

        # Frame de resultados
        self.results_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_init()

        # Variável de controle para pesquisa
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_changed)

        # Configurar entrada para usar variável de controle
        self.search_entry.configure(textvariable=self.search_var)

    def text_init(self):
        init_text = "Pesquise a letra da música no campo acima."
        result_text = ctk.CTkLabel(
            self.results_frame,
            text=init_text,
            wraplength=480
        )
        result_text.pack()

    def on_clear_button_clicked(self):
        self.search_entry.delete(0, tk.END)

    def on_search_changed(self, *args):
        # Cancelar pesquisa anterior se existir
        if hasattr(self, '_search_job'):
            self.after_cancel(self._search_job)

        # Agendar nova pesquisa
        self._search_job = self.after(1000, self.perform_search)

    def perform_search(self):
        # Limpar resultados anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().lower()
        if not query:
            self.text_init()
            return

        # Executar busca em thread separada
        threading.Thread(
            target=self.search_thread,
            args=(query,),
            daemon=True
        ).start()

    def search_thread(self, query):
        try:
            results = search_google(query)
            self.after(0, self.update_results, results)
        except Exception as e:
            self.after(0, self.show_message, f"Erro na busca: {str(e)}")

    def update_results(self, results):
        if not results:
            self.show_message("Nenhum resultado encontrado!")
            return

        for result in results:
            self.create_result_item(result)

    def create_result_item(self, result):
        item_frame = ctk.CTkFrame(self.results_frame)
        item_frame.pack(fill="x", padx=5, pady=5)

        # Label do título
        title_label = ctk.CTkLabel(
            item_frame,
            text=result['title'],
            anchor="w",
            width=400
        )
        title_label.pack(side="left", padx=5, expand=True)

        # Botão de visualizar
        view_button = ctk.CTkButton(
            item_frame,
            text="",
            width=40,
            image=ctk.CTkImage(
                light_image=Image.open("assets/view.png")
            ),
            command=lambda link=result['link'], title=result['title']:
                self.on_view_button_clicked(link, title)
        )
        view_button.pack(side="right", padx=5)

        # Botão de salvar
        save_button = ctk.CTkButton(
            item_frame,
            text="",
            width=40,
            image=ctk.CTkImage(
                light_image=Image.open("assets/save.png")
            ),
            command=lambda link=result['link']:
                self.on_save_button_clicked(link)
        )
        save_button.pack(side="right", padx=5)

    def on_view_button_clicked(self, link, title):
        try:
            ok, lyrics = salvar_letra(link, get_text=True)
            if ok:
                self.open_lyrics_window(lyrics, title)
            else:
                self.show_message(lyrics)
        except Exception as e:
            self.show_message(f"Erro ao carregar letra: {str(e)}")

    def open_lyrics_window(self, lyrics, title):
        lyrics_window = ctk.CTkToplevel(self)
        lyrics_window.title(title)
        lyrics_window.geometry("600x400")

        text_area = ctk.CTkTextbox(
            lyrics_window,
            wrap=tk.WORD,
            width=70,
            height=20
        )
        text_area.insert(tk.INSERT, lyrics)
        text_area.configure(state='disabled')
        text_area.pack(padx=10, pady=10, fill="both", expand=True)

    def on_save_button_clicked(self, link):
        try:
            ok, msg = salvar_letra(link, folder=None, get_text=False)
            self.show_message(msg)
        except Exception as e:
            self.show_message(f"Erro ao salvar: {str(e)}")

    def show_message(self, msg):
        # Janela de diálogo
        ctkbox(
            master=self,
            title="Buscar Letras",
            message=msg,
            icon="warning",
            justify="center",
            width=300,
            height=100
        )


def main():
    app = LyricSearchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
