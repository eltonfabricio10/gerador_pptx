#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from subprocess import Popen
import platform
import sys
import customtkinter as ctk
from PIL import Image, ImageTk
from PPTX import gerar_pptx
from customtkinter import filedialog
from FIND import LyricSearchApp
from LINKS import LinkProcessorApp
from DIRECTORY import documents
from CTkMessagebox import CTkMessagebox as ctkbox


class MusicSlidesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.text_title = "Gerador de Slides"
        self.title(self.text_title)
        self.center(self, 400, 200)

        # Configuração do tema
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Definir ícone da janela
        icon_path = self.get_resource_path('assets/app_icon.png')

        # Verifica se o arquivo existe
        if os.path.exists(icon_path):
            # Define o ícone da janela
            self.iconphoto(
                False,
                ImageTk.PhotoImage(
                    Image.open(icon_path)
                )
            )

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            pady=20,
            padx=20,
            fill="both",
            expand=True
        )

        # Título
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="CRIAR SLIDES COM AS LETRAS DE MÚSICAS",
            font=("Roboto", 16, "bold")
        )
        self.label.pack(pady=15)

        # Frame de botões
        self.button_frame2 = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame2.pack(pady=5, fill="x")

        # Frame de botões
        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame.pack(pady=15, fill="x")

        # Carregar ícones
        pptx_icon = self.load_icon("assets/pptx_icon.png", (20, 20))
        cancel_icon = self.load_icon("assets/cancel_icon.png", (20, 20))
        download_icon = self.load_icon("assets/download_icon.png", (20, 20))
        search_icon = self.load_icon("assets/search_icon.png", (20, 20))

        # Botão Baixar Letra
        self.search_button = ctk.CTkButton(
            self.button_frame2,
            text="PESQUISAR LETRA",
            image=search_icon,
            compound="left",
            command=LyricSearchApp
        )
        self.search_button.pack(side="left", expand=True, padx=10)

        # Botão Baixar Letra
        self.download_button = ctk.CTkButton(
            self.button_frame2,
            text="BAIXAR LETRA",
            image=download_icon,
            compound="left",
            command=LinkProcessorApp
        )
        self.download_button.pack(side="right", expand=True, padx=10)

        # Botão Gerar PPTX
        self.select_button = ctk.CTkButton(
            self.button_frame,
            text="GERAR PPTX",
            image=pptx_icon,
            compound="left",
            command=self.show_open_dialog
        )
        self.select_button.pack(side="left", expand=True, padx=10)

        # Botão Cancelar
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="FECHAR",
            image=cancel_icon,
            compound="left",
            command=self.quit,
            fg_color="#f44336",
            hover_color="#da190b"
        )
        self.cancel_button.pack(side="right", expand=True, padx=10)

    def center(self, window, largura=400, altura=300):
        # Obtém largura e altura da tela
        largura_tela = window.winfo_screenwidth()
        altura_tela = window.winfo_screenheight()

        # Calcula posição x e y para centralizar
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)

        # Define geometria da window
        window.geometry(f"{largura}x{altura}+{x}+{y}")

    def load_icon(self, filename, size=(20, 20)):
        # Método para carregar ícones
        try:
            icon_path = self.get_resource_path(filename)
            return ctk.CTkImage(
                light_image=Image.open(icon_path),
                dark_image=Image.open(icon_path),
                size=size
            )
        except Exception as e:
            print(f"Erro ao carregar ícone {filename}: {e}")
            return None

    def get_resource_path(self, filename):
        # Método para encontrar caminho do ícone
        if getattr(sys, 'frozen', False):
            # Modo executável
            return os.path.join(sys._MEIPASS, filename)
        else:
            # Modo script
            return os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                filename
            )

    def show_open_dialog(self):
        try:
            # Abre diálogo de seleção de arquivos
            files = filedialog.askopenfilenames(
                title="Selecione os Arquivos",
                initialdir="~",
                filetypes=[("Arquivos de Texto", "*.txt")],
                multiple=True
            )

            if not files:
                return

            # Caminho padrão para salvar
            _path_ = f'{documents}/DATASHOW'

            if not os.path.exists(_path_):
                os.makedirs(_path_, exist_ok=True)

            # Chama função para gerar PPTX
            msg, namefile = gerar_pptx(_path_, files)

            # Mostra mensagem de sucesso
            self.show_success_message(msg, namefile)

        except Exception as e:
            self.show_error_message(str(e))

    def show_success_message(self, messag, file_path):
        # Janela de diálogo de sucesso
        success_window = ctkbox(
            master=self,
            title=self.text_title,
            message=f'{messag}{file_path}',
            icon="check",
            justify="center",
            width=300,
            height=150,
            option_1="Abrir",
            option_2="Cancelar"
        )
        resp = success_window.get()
        if resp == "Abrir":
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                Popen(["open", file_path])
            else:  # Linux/Unix-like
                try:
                    Popen(["xdg-open", file_path])
                except FileNotFoundError as e:
                    self.show_error_message(str(e))

    def show_error_message(self, error_text):
        # Janela de diálogo de erro
        ctkbox(
            master=self,
            title=self.text_title,
            message=error_text,
            icon="cancel",
            justify="center",
            width=300,
            height=100
        )


def main():
    app = MusicSlidesApp()
    app.mainloop()


if __name__ == "__main__":
    main()
