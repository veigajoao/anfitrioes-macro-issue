import requests
import json
import pandas as pd
import re
import time

import datetime
import asyncio
import aiohttp

import gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.aiohttp import AIOHTTPTransport
from gql import Client
from gql import gql as GQL

token = input("token do afiliado")

organization_id = input("organization_id do afiliado")

def createTable(token, organization_id):

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
              }

    transport = RequestsHTTPTransport(
        url="https://api.pipefy.com/graphql", verify=True, retries=3,
        headers=headers
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    createTableQuery = GQL(
    """
    mutation($paramOrg: ID!){
      createTable(input:{
        name: "Suas propriedades"
        organization_id: $paramOrg
        authorization: write
      }) {
        table{
          id
        }
      }
    }
    """
    )

    params = {"paramOrg" : organization_id}

    table_data = client.execute(createTableQuery, variable_values=params)

    table_id = table_data["createTable"]["table"]["id"]

    print("Table created")
    print(table_id)

    fields_to_build = [
    ("Código da propriedade", "short_text"),
    ("Propriedade ativa?", "short_text"),
    ("Dados de localização", "statement"),
    ("Logradouro", "short_text"),
    ("Número do edifício", "short_text"),
    ("Andar", "short_text"),
    ("Complemento", "short_text"),
    ("CEP", "short_text"),
    ("Bairro", "short_text"),
    ("Cidade", "short_text"),
    ("UF", "short_text"),
    ("Dados do contrato", "statement"),
    ("Porcentagem cobrada Anfitrião", "short_text"),
    ("Dados do condomínio", "statement"),
    ("Nome do condomínio", "short_text"),
    ("(*) O que o condomínio oferece?", "long_text"),
    ("(*) Regras do condomínio para hóspedes", "long_text"),
    ("(*) Procedimento de cadastro no condomínio", "long_text"),
    ("Link ficha de cadastro padrão do condomínio", "long_text"),
    ("(*) Elevador", "long_text"),
    ("Dados da operação", "statement"),
    ("(*) Nome e senha wi-fi", "long_text"),
    ("(*) Dados contrato wifi", "long_text"),
    ("(*) Instruções do check-in", "long_text"),
    ("(*) Instruções do check-out", "long_text"),
    ("(*) Descrição chaves da propriedade", "long_text"),
    ("Link ficha técnica da propriedade", "long_text"),
    ("Dados do proprietário", "statement"),
    ("Nome proprietário PJ", "short_text"),
    ("CNPJ da PJ titular", "short_text"),
    ("Nome proprietário PF", "short_text"),
    ("CPF da PF titular", "short_text"),
    ("Celular/whatsapp de contato", "short_text"),
    ("Terceiros autorizados a lidar em nome do proprietário", "short_text"),
    ("Vídeos e fotos", "attachment")
    ]

    createFieldQuery = GQL(
    """
    mutation($paramTable: ID!, $paramLabel: String!, $paramType: ID!){
      createTableField(input:{
        table_id: $paramTable
        label: $paramLabel
        type: $paramType
      }){
      clientMutationId
      }
    }
    """
    )

    for item in fields_to_build:
        params = {"paramTable" : table_id,
                  "paramLabel" : item[0],
                  "paramType" : item[1]}
        _field_date = client.execute(createFieldQuery, variable_values=params)
        print(item[0] + " Done")

#func create reception pipe

#func create maintenance pipe

#func create automations

createTable(token=token, organization_id=organization_id)
