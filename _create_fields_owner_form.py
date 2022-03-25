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

import data_sources

import os



def pullAllDbsPipefy_main(token):

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
              }

    transport = RequestsHTTPTransport(
        url="https://api.pipefy.com/graphql", verify=True, retries=3,
        headers=headers
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    normal_query = GQL("""
    mutation($paramTextName: String!, $paramType: ID!, $paramPhase: ID!){
      createPhaseField(input:{
        phase_id: $paramPhase,
        type: $paramType,
        label: $paramTextName,
      }){
    	clientMutationId
      }
    }
    """)

    yes_no_query = GQL("""
    mutation($paramTextName: String!, $paramType: ID!, $paramPhase: ID!){
      createPhaseField(input:{
        phase_id: $paramPhase,
        type: $paramType,
        label: $paramTextName,
        options: ["Sim", "Não"]
      }){
    	clientMutationId
      }
    }
    """)

    water_query = GQL("""
    mutation($paramTextName: String!, $paramType: ID!, $paramPhase: ID!){
      createPhaseField(input:{
        phase_id: $paramPhase,
        type: $paramType,
        label: $paramTextName,
        options: ["Gás", "Elétrico", "Sem aquecimento"]
      }){
    	clientMutationId
      }
    }
    """)

    uf_query = GQL("""
    mutation($paramTextName: String!, $paramType: ID!, $paramPhase: ID!){
      createPhaseField(input:{
        phase_id: $paramPhase,
        type: $paramType,
        label: $paramTextName,
        options: ["RO", "AC", "AM", "RR", "PA", "AP", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MG", "ES", "RJ", "SP", "PR", "SC", "RS", "MS", "MT", "GO", "DF"]
      }){
    	clientMutationId
      }
    }
    """)

    entries_list = [
    ("Imóvel 2", "statement", normal_query),
    ("Logradouro", "short_text", normal_query),
    ("Número", "short_text", normal_query),
    ("Andar", "short_text", normal_query),
    ("Complemento", "short_text", normal_query),
    ("CEP", "short_text", normal_query),
    ("Bairro", "short_text", normal_query),
    ("Cidade", "short_text", normal_query),


    ("Código da acomodação", "short_text", normal_query),
    ("Endereço", "statement", normal_query),
    ("Logradouro", "short_text", normal_query),
    ("Número", "short_text", normal_query),
    ("Andar", "short_text", normal_query),
    ("Complemento", "short_text", normal_query),
    ("CEP", "short_text", normal_query),
    ("Bairro", "short_text", normal_query),
    ("Cidade", "short_text", normal_query),
    ("Estado", "select", uf_query),
    ("Metragem quadrada da área privativa", "number", normal_query),

    ("Cômodos", "statement", normal_query),


    ]

    for item in entries_list:
        params = {"paramTextName" : item[0],
                  "paramType" : item[1],
                  "paramPhase" : "310644065"}

        database_data = client.execute(item[2], variable_values=params)
        print(item[0] + " done")

pullAllDbsPipefy_main(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDExMDcyODcsImVtYWlsIjoiai52ZWlnYUBhbmZpdHJpb2VzZGVhbHVndWVsLmNvbS5iciIsImFwcGxpY2F0aW9uIjozMDAwODczMTh9fQ.kaf7lQFeKhfWd2syG83WB6JQ_KJSXtWVvuzMtzykiVvdcbYkn66HN1SKfkkUSr5x7nv_z-pobAoTdx8-jSPNKA")
