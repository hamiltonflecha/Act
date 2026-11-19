with open("app-v100.py", "r", encoding="utf-8") as f:
    src = f.read()

# Atualizar versão para V101
src = src.replace('VERSAO_APP = "Act!   V100"', 'VERSAO_APP = "Act!   V101"')
src = src.replace('Act! Versão V100', 'Act! Versão V101')

# Na medição do print (e no layout do app):
# As distâncias maiores que 20px eram:
# - Barra superior até linha divisória: 35 px -> reduzido pela metade: ~17-18 px (ex: margem/espaço reduzido)
# - Linha divisória até rótulo 'Nome': 31 px -> reduzido pela metade: ~15-16 px
# - Linha divisória até topo da caixa 'Nome': 44 px -> reduzido pela metade: ~22 px
# - Distância topo a topo entre caixas (30 px) -> reduzido pela metade: ~15 px (com caixas de 18px + rótulo ~11px)

# Vamos compactar o CSS das margens, paddings, .act-hr e espaçamentos verticais entre linhas/faixas
old_css_block = """    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main .block-container,
    section.main > div.block-container,
    div.block-container {{
        max-width: 990px !important;
        width: 990px !important;
        padding-top: 4px !important;
        padding-bottom: 2px !important;
        padding-left: 6px !important;
        padding-right: 6px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stVerticalBlock"] {{ gap: 0px !important; margin: 0 !important; padding: 0 !important; }}
    [data-testid="stElementContainer"] {{ margin: 0 !important; padding: 0 !important; overflow: visible !important; }}
    [data-testid="stHorizontalBlock"] {{
        gap: 4px !important;
        align-items: flex-end !important;
        margin: 0 0 1px 0 !important;
        padding: 0 !important;
    }}"""

new_css_block = """    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main .block-container,
    section.main > div.block-container,
    div.block-container {{
        max-width: 990px !important;
        width: 990px !important;
        padding-top: 2px !important;
        padding-bottom: 2px !important;
        padding-left: 6px !important;
        padding-right: 6px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stVerticalBlock"] {{ gap: 0px !important; margin: 0 !important; padding: 0 !important; }}
    [data-testid="stElementContainer"] {{ margin: 0 !important; padding: 0 !important; overflow: visible !important; line-height: 1 !important; }}
    [data-testid="stHorizontalBlock"] {{
        gap: 4px !important;
        align-items: flex-end !important;
        margin: 0 !important;
        padding: 0 !important;
    }}"""

assert old_css_block in src, "old_css_block not found"
src = src.replace(old_css_block, new_css_block)

# Ajustar .act-hr e margens da barra superior e linhas
src = src.replace(
    ".act-hr {{ border: none; border-top: 1px solid #6E6659; margin: 3px 0 1px 0; height: 1px; }}",
    ".act-hr {{ border: none; border-top: 1px solid #6E6659; margin: 2px 0 1px 0; height: 1px; }}"
)

# Reduzir espaçamentos extras do Streamlit entre blocos (ex: blocos vazios/markdown/colunas)
extra_compact = """
    [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {{
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }}
    [data-testid="stHorizontalBlock"]:has(input[aria-label="cnt_box"]) {{
        margin-bottom: 1px !important;
    }}
    """

src = src.replace("</style>", extra_compact + "    </style>")

compile(src, "app-v101.py", "exec")

with open("app-v101.py", "w", encoding="utf-8") as f:
    f.write(src)

print("app-v101.py gerado e compilado com sucesso!")