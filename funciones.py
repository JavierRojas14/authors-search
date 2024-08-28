import re

import pandas as pd


def parse_article_data(article_string):
    # Remove leading and trailing whitespaces/newlines
    article_string = article_string.strip()

    # Extract the type of publication (search for the first meaningful word)
    publication_type_match = re.search(
        r"\b(Article|Review|Research|Case Study|Editorial|Open access)\b", article_string
    )
    publication_type = publication_type_match.group(1) if publication_type_match else "Unknown"

    # Extract the title of the article by skipping known irrelevant words
    title_match = re.search(
        r"\b(?:Review|Article|Research|Case Study|Editorial|Open access)\b\s*\n*([^\n]+)",
        article_string,
    )
    title = title_match.group(1) if title_match else "Unknown Title"

    # Extract the authors (between the title and the journal name)
    authors = re.findall(r"(\w+,\s*\w+\.\w*)", article_string)
    authors_str = ", ".join(authors) if authors else "Unknown Authors"

    # Extract the journal name (after the last author)
    journal_match = re.search(r"\n([^,\n]+), \d{4}", article_string)
    journal = journal_match.group(1) if journal_match else "Unknown Journal"

    return {
        "Type of Publication": publication_type,
        "Title": title,
        "Authors": authors_str,
        "Journal": journal,
    }


def split_string(string):
    """Splits a string containing names into individual names.

    Args:
      string: The input string.

    Returns:
      A list of individual names.
    """

    # Split the string by commas, but only between 2 commas
    names = string.split(",")

    # Combine the split names back into pairs
    paired_names = [names[i] + names[i + 1] for i in range(0, len(names), 2)]
    paired_names = [name.strip() for name in paired_names if "pp" not in name]

    return paired_names


def obtener_resumen_de_articulos(string_articulos):
    separador = (
        "\n\nShow abstract\nThis link is disabled.\nRelated documents\nThis link is disabled.\n "
    )
    articulos_separados = string_articulos.split(separador)
    articulos_parseados = list(map(parse_article_data, articulos_separados))
    resumen_articulos = pd.DataFrame(articulos_parseados).iloc[:-1]

    resumen_articulos["Authors"] = resumen_articulos["Authors"].apply(split_string)
    resumen_articulos = resumen_articulos.explode("Authors")

    return resumen_articulos


def resumir_cantidad_de_autores(resumen_articulos):
    # Obtiene el conteo de autores con los que ha trabajado
    conteo_autores = resumen_articulos["Authors"].value_counts()

    # Obtiene la cantidad de autores con los que ha trabajado en total
    numero_autores_distintos = conteo_autores.shape[0] - 1

    # Obtiene la cantidad de autores con los que ha trabajado mas de 1 vez
    autores_repetidos = conteo_autores[conteo_autores > 1]
    numero_autores_repetidos = autores_repetidos.shape[0] - 1

    # Obtiene la cantidad de autores con los que ha trabajado solo 1 vez
    autores_que_ha_trabajado_una_vez = conteo_autores[conteo_autores == 1]
    numero_autores_que_ha_trabajado_una_vez = autores_que_ha_trabajado_una_vez.shape[0]

    # print(
    #     f"> Autores distintos con los que ha trabajado: {numero_autores_distintos}\n"
    #     f"> Autores repetidos: {numero_autores_repetidos}\n"
    #     f"> Autores con los que ha trabajado una vez: {numero_autores_que_ha_trabajado_una_vez}"
    # )

    return (
        numero_autores_distintos,
        numero_autores_repetidos,
        numero_autores_que_ha_trabajado_una_vez,
    )
