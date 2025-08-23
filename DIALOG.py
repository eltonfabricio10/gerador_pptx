#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import customtkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox as ctkbox
from pathlib import Path


class FileSelector(tk.CTkToplevel):
    def __init__(self, master=None, initialdir="."):
        super().__init__(master)
        self.title("Selecionar arquivos")
        self.geometry("500x400")

        # Caminho para o ícone
        icon_path = 'assets/folder.png'

        # Verifica se o arquivo existe
        if os.path.exists(icon_path):
            # Define o ícone da janela
            self.iconphoto(
                False,
                ImageTk.PhotoImage(Image.open(icon_path))
            )

        self.current_dir = os.path.abspath(initialdir)
        self.selected_files = []

        # Label com caminho atual
        self.path_label = tk.CTkLabel(self, text=self.current_dir, anchor="w")
        self.path_label.pack(fill="x", padx=5, pady=5)

        # Lista de arquivos/pastas
        self.tree = ttk.Treeview(
            self, columns=("path",),
            show="tree",
            selectmode="extended"
        )
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<ButtonRelease-1>", self.on_single_click)

        # Botões
        frame_buttons = tk.CTkFrame(self)
        frame_buttons.pack(fill="x", pady=5)

        self.action_btn = tk.CTkButton(
            frame_buttons, text="Selecionar",
            command=self.select_files_dialog
        )
        self.action_btn.pack(side="right", padx=5)

        tk.CTkButton(
            frame_buttons, text="Cancelar",
            command=self.cancel
        ).pack(side="right")

        self.load_directory(self.current_dir)

    def sorted_directory(self, directory_path):
        """
        Returns a list of directory contents (directories first, then files),
        sorted alphabetically within each group.
        """
        path = Path(directory_path)
        if not path.is_dir():
            raise ValueError(f"'{directory_path}' is not a valid directory.")

        items = list(path.iterdir())

        # Sort by whether it's a directory
        # (True for directories, False for files)
        # and then alphabetically by name.
        sorted_items = sorted(
            items,
            key=lambda item: (not item.is_dir(), item.name.lower())
        )

        return [str(item.name) for item in sorted_items]

    def load_directory(self, path):
        """Carregar os arquivos e diretórios (sem ocultos)"""
        self.tree.delete(*self.tree.get_children())
        self.current_dir = path
        self.path_label.configure(text=self.current_dir)

        # Adicionar opção de voltar
        self.tree.insert("", "end", text="[..]", values=("<UP>",))
        sorted_contents = self.sorted_directory(path)
        try:
            for item in sorted_contents:
                if item.startswith("."):
                    continue  # Ignora ocultos
                fullpath = os.path.join(path, item)
                if not item.endswith(".txt") and not os.path.isdir(fullpath):
                    continue
                if os.path.isdir(fullpath):
                    self.tree.insert(
                        "", "end", text=f"[{item}]",
                        values=(fullpath,)
                    )
                else:
                    self.tree.insert(
                        "", "end", text=item,
                        values=(fullpath,)
                    )
        except PermissionError as e:
            # Janela de diálogo
            ctkbox(
                master=self,
                title="Buscar Letras",
                message=str(e),
                icon="warning",
                justify="center",
                width=300,
                height=100
            )

    def on_single_click(self, event):
        """Detecta se é diretório ou arquivo e muda o texto do botão"""
        item_id = self.tree.focus()
        if not item_id:
            return
        path = self.tree.item(item_id, "values")[0]

        if path == "<UP>":
            self.action_btn.configure(text="Voltar")
        elif os.path.isdir(path):
            self.action_btn.configure(text="Abrir")
        elif os.path.isfile(path):
            self.action_btn.configure(text="Selecionar")

    def on_double_click(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
        path = self.tree.item(item_id, "values")[0]

        if path == "<UP>":
            parent_dir = os.path.dirname(self.current_dir)
            if parent_dir and os.path.exists(parent_dir):
                self.load_directory(parent_dir)
        elif os.path.isdir(path):
            self.load_directory(path)
        else:
            self.selected_files.append(path)
            self.destroy()

    def select_files_dialog(self):
        """Selecionar vários arquivos"""
        items = self.tree.selection()
        if not items:
            return
        files = []
        for item_id in items:
            path = self.tree.item(item_id, "values")[0]
            if path == "<UP>":
                parent_dir = os.path.dirname(self.current_dir)
                if parent_dir and os.path.exists(parent_dir):
                    self.load_directory(parent_dir)
                return
            if os.path.isdir(path):
                self.load_directory(path)
                return
            if os.path.isfile(path):
                files.append(path)
        self.selected_files = files
        self.destroy()

    def cancel(self):
        self.selected_files = []
        self.destroy()


# Exemplo de uso
if __name__ == "__main__":
    root = tk.CTk()
    root.withdraw()

    home = Path.home()
    selector = FileSelector(initialdir=home)
    root.wait_window(selector)
    for f in selector.selected_files:
        print(f)
