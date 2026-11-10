import pandas as pd
import numpy as np
from datetime import datetime
import re

def limpar_cpf(val):
    if not val or pd.isna(val):
        return ""
    digitos = ''.join(filter(str.isdigit, str(val)))
    if len(digitos) >= 11:
        return digitos[-11:]
    elif len(digitos) > 0:
        return digitos.zfill(11)
    return ""

def formatar_cpf(digitos):
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return digitos

def fundir_bases_dbf(caminho_dbf1, caminho_dbf2, caminho_saida_csv):
    print("Iniciando fusão dos DBFs 1 e 2...")
    
    # 1. Carregar os dois ficheiros
    df1 = pd.read_csv(caminho_dbf1, dtype=str).fillna("") if caminho_dbf1.endswith('.csv') else pd.read_excel(caminho_dbf1, dtype=str).fillna("")
    df2 = pd.read_csv(caminho_dbf2, dtype=str).fillna("") if caminho_dbf2.endswith('.csv') else pd.read_excel(caminho_dbf2, dtype=str).fillna("")
    
    # 2. Higienizar CPFs nas duas bases
    df1['CPF_LIMPO'] = df1['USR1000'].apply(limpar_cpf)
    df2['CPF_LIMPO'] = df2['USR1000'].apply(limpar_cpf)
    
    # 3. Concatenar as duas bases
    df_unificado = pd.concat([df1, df2], ignore_index=True)
    
    # 4. Agrupar por CPF_LIMPO (Chave Absoluta) e mesclar informações mais recentes
    # Registos com o mesmo CPF têm os seus campos consolidados (priorizando textos válidos/acentuados)
    registos_finais = []
    
    hoje = datetime.now()
    
    for cpf, group in df_unificado.groupby('CPF_LIMPO'):
        if cpf == "":
            continue
            
        # Pega a melhor versão do nome (a que tiver mais acentos/carateres válidos)
        nomes = group['NAME'].tolist()
        melhor_nome = max(nomes, key=lambda x: len(re.sub(r'[^a-zA-ZÀ-ÿ]', '', str(x))))
        
        # Junta observações de ambos os computadores
        obs_combinadas = " | ".join(filter(None, set(group['USER9'].tolist())))
        
        # Pega a melhor data de nascimento
        datas_nasc = filter(None, group['USR1003'].tolist())
        data_nasc_str = next(datas_nasc, "")
        
        # Recalcula idade real
        data_dt = pd.to_datetime(data_nasc_str, errors='coerce', dayfirst=True)
        if pd.notnull(data_dt):
            idade = hoje.year - data_dt.year - ((hoje.month, hoje.day) < (data_dt.month, data_dt.day))
            data_nasc_fmt = data_dt.strftime('%d/%m/%Y')
        else:
            idade = ""
            data_nasc_fmt = data_nasc_str
            
        idade_108 = (idade + 9) if isinstance(idade, int) else ""
        
        # Pega o primeiro registo como base e atualiza os campos unificados
        registo = group.iloc[-1].to_dict()
        registo['NAME'] = melhor_nome
        registo['CPF_LIMPO'] = cpf
        registo['CPF_FORMATADO'] = formatar_cpf(cpf)
        registo['USER9'] = obs_combinadas
        registo['DATA_NASC'] = data_nasc_fmt
        registo['IDADE'] = idade
        registo['IDADE_108_MESES'] = idade_108
        registo['RESUMO'] = f"{registo.get('USR1001', 'INSS')} {melhor_nome} {cpf} {idade}".strip()
        
        registos_finais.append(registo)
        
    df_final = pd.DataFrame(registos_finais)
    df_final.to_csv(caminho_saida_csv, index=False, encoding='utf-8-sig')
    print(f"Fusão concluída! Total de contatos únicos consolidados: {len(df_final)}")

if __name__ == "__main__":
    fundir_bases_dbf("DBF1_MaquinaLocal.csv", "DBF2_CopiaOutroPC.csv", "Base_Consolidada_ACT_UNIFICADA.csv")