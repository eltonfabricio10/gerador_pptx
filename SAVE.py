# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from subprocess import check_output
import re
import os
import unicodedata
from DIRECTORY import documents


def char_accents(text):
    # Função para remover acentuação e caracteres especiais,
    # substituindo por '_'
    # Remover acentuação e til (convertendo para letras sem acento)

    # Decompor os caracteres acentuados
    text = unicodedata.normalize('NFD', text)
    # Remove acentuação
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    # Substituir espaços e caracteres especiais por "_"
    text = re.sub(r'[^a-zA-Z0-9]', '_', text)
    # Substituir múltiplos underscores por um único underscore
    text = re.sub(r'_+', '_', text)
    text = re.sub(r'_', ' ', text)

    return text


def limpar_arquivo(_file_):
    try:
        # Abrir o arquivo e ler o conteúdo
        with open(_file_, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = []
        content_started = False

        for line in lines:
            stripped_line = line.strip()

            if not content_started:
                if stripped_line:
                    content_started = True
                    cleaned_lines.append(line.lstrip(" "))
            else:
                cleaned_lines.append(line.lstrip(" "))

        # Gravar o conteúdo limpo de volta no arquivo
        with open(_file_, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

    except Exception as e:
        print(f"Erro ao limpar o arquivo {_file_}: {e}")


def salvar_letra(url, folder=None, get_text=False):
    try:
        # Verifica se a URL foi fornecida corretamente
        if not url:
            return False, "Por favor, insira uma URL válida."

        resp = requests.get(url, timeout=30)
        resp.encoding = 'utf-8'
        resp.raise_for_status()

        letra_div = letra_all_div = ""
        soup = BeautifulSoup(resp.text, "html.parser")

        if url.startswith("https://musicasparamissa.com.br"):
            letra_div = soup.find(id="div-letra")

        if url.startswith("https://www.vagalume.com.br"):
            letra_div = soup.find(id="lyrics")

        if url.startswith("https://www.letras.mus.br"):
            letra_div = soup.find("div", class_="lyric-original")

        if url.startswith("https://musicocatolico.org"):
            letra_all = soup.find_all("div", class_="form-group")
            letra_div = letra_all[1]

        if url.startswith("https://www.letrasliturgicas.com.br"):
            letra_div = soup.find("div", class_="post-body entry-content")

        if url.startswith("https://musica-liturgica.net/"):
            letra_all_div = soup.find_all("div", class_="letra")

        if not letra_div and not letra_all_div:
            letra_all_div = soup.find_all("div", class_="MsoNormal")
            if not letra_all_div:
                return False, "Não foi possível encontrar a letra da música."

        lyrics = ""
        if letra_div:
            for tag in letra_div.find_all():
                if tag.name == "p":
                    tag.append("\n\n")
                elif tag.name == "br":
                    tag.replace_with("\n")
                elif tag.name == "div":
                    tag.unwrap()

            lyrics = letra_div.get_text()

        elif letra_all_div:
            lyrics = "".join([div.get_text() for div in letra_all_div])

        if not get_text:
            # Gera nome do arquivo a partir do título da página
            title = soup.title.string.strip() if soup.title else "letra"
            title = char_accents(title)
            path = os.path.expanduser(f'{documents}/LETRAS_PROJETOR')

            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

            if folder is not None:
                if not os.path.exists(folder):
                    os.makedirs(f"{path}/{folder}", exist_ok=True)

                filename = f"{path}/{folder}/{title}.txt"
                msg = f"{title}.txt"
            else:
                filename = f"{path}/{title}.txt"
                msg = f"Letra salva em:\n{path}/{title}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(lyrics.upper())
                f.close()

            # Chama a função para limpar o arquivo após salvar
            limpar_arquivo(filename)

            return True, msg
        else:
            return True, lyrics.upper().lstrip(" ")

    except requests.exceptions.RequestException as e:
        return False, f"Erro de requisição: {e}"
    except Exception as e:
        return False, f"Erro inesperado: {e}"
