import re
from datetime import datetime

MESES = {
    "jan": 1, "janeiro": 1,
    "fev": 2, "fevereiro": 2,
    "mar": 3, "março": 3, "marco": 3,
    "abr": 4, "abril": 4,
    "mai": 5, "maio": 5,
    "jun": 6, "junho": 6,
    "jul": 7, "julho": 7,
    "ago": 8, "agosto": 8,
    "set": 9, "setembro": 9,
    "out": 10, "outubro": 10,
    "nov": 11, "novembro": 11,
    "dez": 12, "dezembro": 12,
}

def _normalizar(texto: str) -> str:
    return (
        texto.lower()
        .replace("–", "-")
        .replace("—", "-")
        .replace(" até ", " - ")
        .replace(" a ", " - ")
    )

def _data_para_meses(mes, ano):
    ano = int(ano)
    mes = mes.lower().strip(".") if mes else "jan"
    mes_num = MESES.get(mes, 1)
    return ano * 12 + mes_num

def _extrair_intervalos(texto: str):
    texto = _normalizar(texto)
    atual = datetime.now()
    fim_atual = atual.year * 12 + atual.month

    padroes = [
        # jan/2020 - mar/2024
        r"(?:(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez|janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\.?\s*/?\s*)?(20\d{2})\s*-\s*(?:(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez|janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\.?\s*/?\s*)?(20\d{2}|atual|presente|hoje)",
    ]

    intervalos = []

    for padrao in padroes:
        for m in re.findall(padrao, texto):
            mes_ini, ano_ini, mes_fim, ano_fim = m

            inicio = _data_para_meses(mes_ini, ano_ini)

            if ano_fim in ["atual", "presente", "hoje"]:
                fim = fim_atual
            else:
                fim = _data_para_meses(mes_fim, ano_fim)

            if fim >= inicio:
                intervalos.append((inicio, fim))

    return intervalos

def extrair_secao_experiencia(cv_text: str) -> str:
    texto = cv_text

    inicio_markers = [
        "experiência profissional",
        "experiencia profissional",
        "experiências profissionais",
        "historico profissional",
        "histórico profissional",
        "experiência",
        "experiencia",
    ]

    fim_markers = [
        "formação",
        "formacao",
        "educação",
        "educacao",
        "cursos",
        "certificações",
        "certificacoes",
        "habilidades",
        "competências",
        "competencias",
        "projetos",
        "idiomas",
    ]

    lower = texto.lower()

    inicio = None
    for marker in inicio_markers:
        pos = lower.find(marker)
        if pos != -1:
            inicio = pos
            break

    if inicio is None:
        return texto

    fim = len(texto)
    for marker in fim_markers:
        pos = lower.find(marker, inicio + 20)
        if pos != -1:
            fim = min(fim, pos)

    return texto[inicio:fim]

def _unir_intervalos(intervalos):
    if not intervalos:
        return []

    intervalos = sorted(intervalos)
    unidos = [list(intervalos[0])]

    for inicio, fim in intervalos[1:]:
        ultimo = unidos[-1]

        if inicio <= ultimo[1]:
            ultimo[1] = max(ultimo[1], fim)
        else:
            unidos.append([inicio, fim])

    return unidos

def calcular_experiencia_total(cv_text: str):
    secao_exp = extrair_secao_experiencia(cv_text)
    intervalos = _extrair_intervalos(secao_exp)
    unidos = _unir_intervalos(intervalos)

    if not unidos:
        return {
            "anos": None,
            "confianca": "Baixa",
            "motivo": "Nenhum período profissional claro foi identificado no currículo.",
            "intervalos_detectados": []
        }

    meses_total = sum(fim - inicio for inicio, fim in unidos)
    anos = round(meses_total / 12, 1)

    return {
        "anos": anos,
        "confianca": "Alta",
        "motivo": "Experiência calculada com base nos períodos profissionais detectados no currículo, removendo sobreposições.",
        "intervalos_detectados": unidos
    }