from dotenv import load_dotenv
load_dotenv()
import os
import requests
from langgraph.prebuilt import create_react_agent

SF_INSTANCE_URL = os.getenv("SF_INSTANCE_URL")
SF_ACCESS_TOKEN = os.getenv("SF_ACCESS_TOKEN")


def run_soql(soql: str) -> dict:
    """Executa uma query SOQL no Salesforce e retorna os registros"""
    url = f"{SF_INSTANCE_URL}/services/data/v59.0/query"
    headers = {
        "Authorization": f"Bearer {SF_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {"q": soql}

    print("\n===== DEBUG SOQL =====")
    print("SOQL:", soql)
    print("======================")

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        print('Resultado da consulta: ',resp.json())
        return resp.json()
    else:
        return {"error": resp.status_code, "message": resp.text}


def query_nf(nf_name: str) -> dict:
    """Consulta uma Nota Fiscal (Nota_Fiscal__c) pelo Name.
    Exemplo: NF-0000109259"""
    soql = f"""
        SELECT Id, Name, Itens_Relacionados__c, Status__c, Status_Processo_NF__c,
               Status_Cobranca__c, Observacoes__c, Total_antes_do_Desconto__c,
               Valor_Faturado__c, SOL__c, SOL_Pesquisa__c, Cotacao_de_Venda__c
        FROM Nota_Fiscal__c
        WHERE Name = '{nf_name}'
        LIMIT 1
    """
    return run_soql(soql)


def query_cv(id: str) -> dict:
    """Consulta uma CV(Cotação de venda) pelo ID."""
    soql = f"""
        SELECT Id, Name, Fase_cotacao_venda__c, Prioridade__c, 	Utilizacao__c, Informacao_adicionais__c
        FROM Cotacao_de_Venda__c
        WHERE Id = '{id}'
        LIMIT 3
    """
    return run_soql(soql)


def query_ivs(iv_names: list[str]) -> dict:
    """Consulta uma ou mais IVs Itens de Venda (Item_venda__c) pelo Name.
    Pode receber um ou mais nomes de IVs."""
    if not iv_names:
        return {"error": "Nenhum IV informado"}

    soql = f"""
        SELECT Id, Name, Status__c, Status_Logistica__c, Status_Processo_IV__c,
               Status_Estoque__c, Status_Deadline_Estatica__c,
               Valor_Total_apos_condicao_pagamento__c
        FROM Item_venda__c
        WHERE Name IN ({','.join([f"'{iv}'" for iv in iv_names])})
    """
    return run_soql(soql)



def query_op(name: str) -> dict:
    """Consulta uma Oportunidade (Solicitacao__c) pelo Name."""
    soql = f"""
        SELECT Id, Name, Status_da_OP__c, Total_da_Oportunidade_Valor_Estimado__c,
               Prioridade_da_Oportunidade__c
        FROM Solicitacao__c
        WHERE Name = '{name}'
        LIMIT 10
    """
    return run_soql(soql)


def query_contact(email: str) -> dict:
    """Consulta um Contato pelo email"""
    soql = f"""
        SELECT Id, FirstName, LastName, Email, Phone
        FROM Contact
        WHERE Email = '{email}'
        LIMIT 10
    """
    return run_soql(soql)



def get_saudacao() -> str:
    """Retorna uma mensagem a respeito do objetivo e de quem é o chatbot, para que ele foi feito, como pode ajudar e etc"""
    return f"Olá eu sou o Mbot, um  chatBot feito pela Mtec para a Mtec. Que contém o uso de inteligência artifical que realiza consultas as bases do Salesforce, SAP e a bases de conhecimento internas da empresa. Em que posso te ajudar hoje?"


agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[get_saudacao,query_ivs, query_nf, query_contact, query_op, query_cv],
    prompt="Você é um assistente especialista em Salesforce. "
           "Quando escolher as tools se atente ao padrão do salesforce para consulta como: "
           "OP-{Número da OP} (ex: OP-10000), "
           "NF-{Número da nota fiscal} (ex: NF-000000000) "
           "Name do IV(Item de Venda) (ex: IV-123456)."
           "ou CV(Cotação de venda) (ex: CV-123456)."
           "Quando o usuário solicitar uma informação completa se atente aos objeto que estão sendo referenciados na consulta e realiza consultas nesses objetos para retornar as informações completas."


)


if __name__ == "__main__":
    print(agent.invoke(
        {"messages": [{"role": "user", "content": "Quais informações vc tem da NF-0000109259"}]}
    ))
