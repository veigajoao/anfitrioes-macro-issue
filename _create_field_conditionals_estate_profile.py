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

# query for finding all field codes
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDExMDcyODcsImVtYWlsIjoiai52ZWlnYUBhbmZpdHJpb2VzZGVhbHVndWVsLmNvbS5iciIsImFwcGxpY2F0aW9uIjozMDAwODczMTh9fQ.kaf7lQFeKhfWd2syG83WB6JQ_KJSXtWVvuzMtzykiVvdcbYkn66HN1SKfkkUSr5x7nv_z-pobAoTdx8-jSPNKA"

headers = {
    "Authorization": "Bearer {}".format(token),
    "Content-Type": "application/json"
          }

transport = RequestsHTTPTransport(
    url="https://api.pipefy.com/graphql", verify=True, retries=3,
    headers=headers
)

client = Client(transport=transport, fetch_schema_from_transport=True)

find_fields_query = GQL(
"""
query FindCodes($phaseCode: ID!){
  phase(id: $phaseCode){
    fields{
      label
      internal_id
    }
  }
}
"""
)

#declare phase code
phase_code = "310678120"

#get codes for all phase fields
params = {"phaseCode" : phase_code}

fields_data = client.execute(find_fields_query, variable_values=params)


def parse_phase_date(json_data):
    list_items = json_data["phase"]["fields"]
    code_dict = {}
    for item in list_items:
        code_dict[item["label"]] = item["internal_id"]

    return code_dict

code_dict = parse_phase_date(fields_data)

normal_query = ""
yes_no_query = ""
water_query = ""
#condition hide all rooms, bathrooms, WC and suites
list_to_hide = (
                ("Suíte 1", "statement", normal_query),
                ("Quantidade camas casal (s1)", "number", normal_query),
                ("Descrição camas de casal (s1)", "long_text", normal_query),
                ("Quantidade camas solteiro (s1)", "number", normal_query),
                ("Descrição camas de solteiro (s1)", "long_text", normal_query),
                ("Possui ar-condicionado (s1)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s1)", "short_text", normal_query),
                ("Possui televisão (s1)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s1)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s1)", "short_text", normal_query),
                ("Possui chuveiro (s1)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s1)", "short_text", normal_query),
                ("Aquecimento água (s1)", "radio_vertical", water_query),
                ("Possui banheira (s1)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s1)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s1)", "attachment", normal_query),
                ("Outras observações da suíte 1 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 2", "statement", normal_query),
                ("Quantidade camas casal (s2)", "number", normal_query),
                ("Descrição camas de casal (s2)", "long_text", normal_query),
                ("Quantidade camas solteiro (s2)", "number", normal_query),
                ("Descrição camas de solteiro (s2)", "long_text", normal_query),
                ("Possui ar-condicionado (s2)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s2)", "short_text", normal_query),
                ("Possui televisão (s2)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s2)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s2)", "short_text", normal_query),
                ("Possui chuveiro (s2)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s2)", "short_text", normal_query),
                ("Aquecimento água (s2)", "radio_vertical", water_query),
                ("Possui banheira (s2)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s2)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s2)", "attachment", normal_query),
                ("Outras observações da suíte 2 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 3", "statement", normal_query),
                ("Quantidade camas casal (s3)", "number", normal_query),
                ("Descrição camas de casal (s3)", "long_text", normal_query),
                ("Quantidade camas solteiro (s3)", "number", normal_query),
                ("Descrição camas de solteiro (s3)", "long_text", normal_query),
                ("Possui ar-condicionado (s3)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s3)", "short_text", normal_query),
                ("Possui televisão (s3)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s3)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s3)", "short_text", normal_query),
                ("Possui chuveiro (s3)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s3)", "short_text", normal_query),
                ("Aquecimento água (s3)", "radio_vertical", water_query),
                ("Possui banheira (s3)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s3)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s3)", "attachment", normal_query),
                ("Outras observações da suíte 3 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 4", "statement", normal_query),
                ("Quantidade camas casal (s4)", "number", normal_query),
                ("Descrição camas de casal (s4)", "long_text", normal_query),
                ("Quantidade camas solteiro (s4)", "number", normal_query),
                ("Descrição camas de solteiro (s4)", "long_text", normal_query),
                ("Possui ar-condicionado (s4)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s4)", "short_text", normal_query),
                ("Possui televisão (s4)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s4)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s4)", "short_text", normal_query),
                ("Possui chuveiro (s4)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s4)", "short_text", normal_query),
                ("Aquecimento água (s4)", "radio_vertical", water_query),
                ("Possui banheira (s4)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s4)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s4)", "attachment", normal_query),
                ("Outras observações da suíte 4 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 5", "statement", normal_query),
                ("Quantidade camas casal (s5)", "number", normal_query),
                ("Descrição camas de casal (s5)", "long_text", normal_query),
                ("Quantidade camas solteiro (s5)", "number", normal_query),
                ("Descrição camas de solteiro (s5)", "long_text", normal_query),
                ("Possui ar-condicionado (s5)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s5)", "short_text", normal_query),
                ("Possui televisão (s5)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s5)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s5)", "short_text", normal_query),
                ("Possui chuveiro (s5)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s5)", "short_text", normal_query),
                ("Aquecimento água (s5)", "radio_vertical", water_query),
                ("Possui banheira (s5)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s5)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s5)", "attachment", normal_query),
                ("Outras observações da suíte 5 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 6", "statement", normal_query),
                ("Quantidade camas casal (s6)", "number", normal_query),
                ("Descrição camas de casal (s6)", "long_text", normal_query),
                ("Quantidade camas solteiro (s6)", "number", normal_query),
                ("Descrição camas de solteiro (s6)", "long_text", normal_query),
                ("Possui ar-condicionado (s6)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s6)", "short_text", normal_query),
                ("Possui televisão (s6)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s6)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s6)", "short_text", normal_query),
                ("Possui chuveiro (s6)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s6)", "short_text", normal_query),
                ("Aquecimento água (s6)", "radio_vertical", water_query),
                ("Possui banheira (s6)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s6)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s6)", "attachment", normal_query),
                ("Outras observações da suíte 6 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 7", "statement", normal_query),
                ("Quantidade camas casal (s7)", "number", normal_query),
                ("Descrição camas de casal (s7)", "long_text", normal_query),
                ("Quantidade camas solteiro (s7)", "number", normal_query),
                ("Descrição camas de solteiro (s7)", "long_text", normal_query),
                ("Possui ar-condicionado (s7)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s7)", "short_text", normal_query),
                ("Possui televisão (s7)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s7)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s7)", "short_text", normal_query),
                ("Possui chuveiro (s7)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s7)", "short_text", normal_query),
                ("Aquecimento água (s7)", "radio_vertical", water_query),
                ("Possui banheira (s7)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s7)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s7)", "attachment", normal_query),
                ("Outras observações da suíte 7 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 8", "statement", normal_query),
                ("Quantidade camas casal (s8)", "number", normal_query),
                ("Descrição camas de casal (s8)", "long_text", normal_query),
                ("Quantidade camas solteiro (s8)", "number", normal_query),
                ("Descrição camas de solteiro (s8)", "long_text", normal_query),
                ("Possui ar-condicionado (s8)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s8)", "short_text", normal_query),
                ("Possui televisão (s8)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s8)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s8)", "short_text", normal_query),
                ("Possui chuveiro (s8)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s8)", "short_text", normal_query),
                ("Aquecimento água (s8)", "radio_vertical", water_query),
                ("Possui banheira (s8)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s8)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s8)", "attachment", normal_query),
                ("Outras observações da suíte 8 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 9", "statement", normal_query),
                ("Quantidade camas casal (s9)", "number", normal_query),
                ("Descrição camas de casal (s9)", "long_text", normal_query),
                ("Quantidade camas solteiro (s9)", "number", normal_query),
                ("Descrição camas de solteiro (s9)", "long_text", normal_query),
                ("Possui ar-condicionado (s9)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s9)", "short_text", normal_query),
                ("Possui televisão (s9)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s9)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s9)", "short_text", normal_query),
                ("Possui chuveiro (s9)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s9)", "short_text", normal_query),
                ("Aquecimento água (s9)", "radio_vertical", water_query),
                ("Possui banheira (s9)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s9)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s9)", "attachment", normal_query),
                ("Outras observações da suíte 9 e requisições especiais do proprietário", "long_text", normal_query),

                ("Suíte 10", "statement", normal_query),
                ("Quantidade camas casal (s10)", "number", normal_query),
                ("Descrição camas de casal (s10)", "long_text", normal_query),
                ("Quantidade camas solteiro (s10)", "number", normal_query),
                ("Descrição camas de solteiro (s10)", "long_text", normal_query),
                ("Possui ar-condicionado (s10)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s10)", "short_text", normal_query),
                ("Possui televisão (s10)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s10)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s10)", "short_text", normal_query),
                ("Possui chuveiro (s10)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s10)", "short_text", normal_query),
                ("Aquecimento água (s10)", "radio_vertical", water_query),
                ("Possui banheira (s10)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s10)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s10)", "attachment", normal_query),
                ("Outras observações da suíte 10 e requisições especiais do proprietário", "long_text", normal_query),

                ("Quarto 1", "statement", normal_query),
                ("Quantidade de camas de casal (q1)", "number", normal_query),
                ("Descrição camas de casal (q1)", "long_text", normal_query),
                ("Quantidade camas solteiro (q1)", "number", normal_query),
                ("Descrição camas de solteiro (q1)", "long_text", normal_query),
                ("Possui ar-condicionado (q1)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q1)", "short_text", normal_query),
                ("Possui televisão (q1)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q1)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q1)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q1)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q1)", "long_text", normal_query),

                ("Quarto 2", "statement", normal_query),
                ("Quantidade de camas de casal (q2)", "number", normal_query),
                ("Descrição camas de casal (q2)", "long_text", normal_query),
                ("Quantidade camas solteiro (q2)", "number", normal_query),
                ("Descrição camas de solteiro (q2)", "long_text", normal_query),
                ("Possui ar-condicionado (q2)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q2)", "short_text", normal_query),
                ("Possui televisão (q2)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q2)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q2)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q2)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q2)", "long_text", normal_query),

                ("Quarto 3", "statement", normal_query),
                ("Quantidade de camas de casal (q3)", "number", normal_query),
                ("Descrição camas de casal (q3)", "long_text", normal_query),
                ("Quantidade camas solteiro (q3)", "number", normal_query),
                ("Descrição camas de solteiro (q3)", "long_text", normal_query),
                ("Possui ar-condicionado (q3)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q3)", "short_text", normal_query),
                ("Possui televisão (q3)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q3)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q3)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q3)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q3)", "long_text", normal_query),

                ("Quarto 4", "statement", normal_query),
                ("Quantidade de camas de casal (q4)", "number", normal_query),
                ("Descrição camas de casal (q4)", "long_text", normal_query),
                ("Quantidade camas solteiro (q4)", "number", normal_query),
                ("Descrição camas de solteiro (q4)", "long_text", normal_query),
                ("Possui ar-condicionado (q4)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q4)", "short_text", normal_query),
                ("Possui televisão (q4)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q4)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q4)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q4)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q4)", "long_text", normal_query),

                ("Quarto 5", "statement", normal_query),
                ("Quantidade de camas de casal (q5)", "number", normal_query),
                ("Descrição camas de casal (q5)", "long_text", normal_query),
                ("Quantidade camas solteiro (q5)", "number", normal_query),
                ("Descrição camas de solteiro (q5)", "long_text", normal_query),
                ("Possui ar-condicionado (q5)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q5)", "short_text", normal_query),
                ("Possui televisão (q5)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q5)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q5)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q5)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q5)", "long_text", normal_query),

                ("Quarto 6", "statement", normal_query),
                ("Quantidade de camas de casal (q6)", "number", normal_query),
                ("Descrição camas de casal (q6)", "long_text", normal_query),
                ("Quantidade camas solteiro (q6)", "number", normal_query),
                ("Descrição camas de solteiro (q6)", "long_text", normal_query),
                ("Possui ar-condicionado (q6)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q6)", "short_text", normal_query),
                ("Possui televisão (q6)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q6)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q6)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q6)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q6)", "long_text", normal_query),

                ("Quarto 7", "statement", normal_query),
                ("Quantidade de camas de casal (q7)", "number", normal_query),
                ("Descrição camas de casal (q7)", "long_text", normal_query),
                ("Quantidade camas solteiro (q7)", "number", normal_query),
                ("Descrição camas de solteiro (q7)", "long_text", normal_query),
                ("Possui ar-condicionado (q7)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q7)", "short_text", normal_query),
                ("Possui televisão (q7)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q7)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q7)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q7)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q7)", "long_text", normal_query),

                ("Quarto 8", "statement", normal_query),
                ("Quantidade de camas de casal (q8)", "number", normal_query),
                ("Descrição camas de casal (q8)", "long_text", normal_query),
                ("Quantidade camas solteiro (q8)", "number", normal_query),
                ("Descrição camas de solteiro (q8)", "long_text", normal_query),
                ("Possui ar-condicionado (q8)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q8)", "short_text", normal_query),
                ("Possui televisão (q8)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q8)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q8)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q8)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q8)", "long_text", normal_query),

                ("Quarto 9", "statement", normal_query),
                ("Quantidade de camas de casal (q9)", "number", normal_query),
                ("Descrição camas de casal (q9)", "long_text", normal_query),
                ("Quantidade camas solteiro (q9)", "number", normal_query),
                ("Descrição camas de solteiro (q9)", "long_text", normal_query),
                ("Possui ar-condicionado (q9)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q9)", "short_text", normal_query),
                ("Possui televisão (q9)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q9)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q9)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q9)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q9)", "long_text", normal_query),

                ("Quarto 10", "statement", normal_query),
                ("Quantidade de camas de casal (q10)", "number", normal_query),
                ("Descrição camas de casal (q10)", "long_text", normal_query),
                ("Quantidade camas solteiro (q10)", "number", normal_query),
                ("Descrição camas de solteiro (q10)", "long_text", normal_query),
                ("Possui ar-condicionado (q10)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q10)", "short_text", normal_query),
                ("Possui televisão (q10)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q10)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q10)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q10)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q10)", "long_text", normal_query),

                ("Banheiro 1", "statement", normal_query),
                ("Possui chuveiro (b1)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b1)", "short_text", normal_query),
                ("Possui banheira (b1)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b1)", "short_text", normal_query),
                ("Aquecimento água (b1)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b1)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b1)", "long_text", normal_query),

                ("Banheiro 2", "statement", normal_query),
                ("Possui chuveiro (b2)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b2)", "short_text", normal_query),
                ("Possui banheira (b2)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b2)", "short_text", normal_query),
                ("Aquecimento água (b2)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b2)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b2)", "long_text", normal_query),

                ("Banheiro 3", "statement", normal_query),
                ("Possui chuveiro (b3)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b3)", "short_text", normal_query),
                ("Possui banheira (b3)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b3)", "short_text", normal_query),
                ("Aquecimento água (b3)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b3)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b3)", "long_text", normal_query),

                ("Banheiro 4", "statement", normal_query),
                ("Possui chuveiro (b4)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b4)", "short_text", normal_query),
                ("Possui banheira (b4)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b4)", "short_text", normal_query),
                ("Aquecimento água (b4)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b4)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b4)", "long_text", normal_query),

                ("Banheiro 5", "statement", normal_query),
                ("Possui chuveiro (b5)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b5)", "short_text", normal_query),
                ("Possui banheira (b5)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b5)", "short_text", normal_query),
                ("Aquecimento água (b5)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b5)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b5)", "long_text", normal_query),

                ("Lavabo 1", "statement", normal_query),
                ("Fotos detalhadas lavabo 1", "attachment", normal_query),

                ("Lavabo 2", "statement", normal_query),
                ("Fotos detalhadas lavabo 2", "attachment", normal_query),

                ("Lavabo 3", "statement", normal_query),
                ("Fotos detalhadas lavabo 3", "attachment", normal_query),

                ("Lavabo 4", "statement", normal_query),
                ("Fotos detalhadas lavabo 4", "attachment", normal_query),

                ("Lavabo 5", "statement", normal_query),
                ("Fotos detalhadas lavabo 5", "attachment", normal_query),

                )

list_suite_1 = (
                ("Suíte 1", "statement", normal_query),
                ("Quantidade camas casal (s1)", "number", normal_query),
                ("Descrição camas de casal (s1)", "long_text", normal_query),
                ("Quantidade camas solteiro (s1)", "number", normal_query),
                ("Descrição camas de solteiro (s1)", "long_text", normal_query),
                ("Possui ar-condicionado (s1)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s1)", "short_text", normal_query),
                ("Possui televisão (s1)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s1)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s1)", "short_text", normal_query),
                ("Possui chuveiro (s1)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s1)", "short_text", normal_query),
                ("Aquecimento água (s1)", "radio_vertical", water_query),
                ("Possui banheira (s1)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s1)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s1)", "attachment", normal_query),
                ("Outras observações da suíte 1 e requisições especiais do proprietário", "long_text", normal_query),
)
list_suite_2 =(
                ("Suíte 2", "statement", normal_query),
                ("Quantidade camas casal (s2)", "number", normal_query),
                ("Descrição camas de casal (s2)", "long_text", normal_query),
                ("Quantidade camas solteiro (s2)", "number", normal_query),
                ("Descrição camas de solteiro (s2)", "long_text", normal_query),
                ("Possui ar-condicionado (s2)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s2)", "short_text", normal_query),
                ("Possui televisão (s2)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s2)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s2)", "short_text", normal_query),
                ("Possui chuveiro (s2)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s2)", "short_text", normal_query),
                ("Aquecimento água (s2)", "radio_vertical", water_query),
                ("Possui banheira (s2)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s2)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s2)", "attachment", normal_query),
                ("Outras observações da suíte 2 e requisições especiais do proprietário", "long_text", normal_query),
)


list_suite_3 =( ("Suíte 3", "statement", normal_query),
                ("Quantidade camas casal (s3)", "number", normal_query),
                ("Descrição camas de casal (s3)", "long_text", normal_query),
                ("Quantidade camas solteiro (s3)", "number", normal_query),
                ("Descrição camas de solteiro (s3)", "long_text", normal_query),
                ("Possui ar-condicionado (s3)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s3)", "short_text", normal_query),
                ("Possui televisão (s3)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s3)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s3)", "short_text", normal_query),
                ("Possui chuveiro (s3)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s3)", "short_text", normal_query),
                ("Aquecimento água (s3)", "radio_vertical", water_query),
                ("Possui banheira (s3)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s3)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s3)", "attachment", normal_query),
                ("Outras observações da suíte 3 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_4 = (
                ("Suíte 4", "statement", normal_query),
                ("Quantidade camas casal (s4)", "number", normal_query),
                ("Descrição camas de casal (s4)", "long_text", normal_query),
                ("Quantidade camas solteiro (s4)", "number", normal_query),
                ("Descrição camas de solteiro (s4)", "long_text", normal_query),
                ("Possui ar-condicionado (s4)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s4)", "short_text", normal_query),
                ("Possui televisão (s4)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s4)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s4)", "short_text", normal_query),
                ("Possui chuveiro (s4)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s4)", "short_text", normal_query),
                ("Aquecimento água (s4)", "radio_vertical", water_query),
                ("Possui banheira (s4)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s4)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s4)", "attachment", normal_query),
                ("Outras observações da suíte 4 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_5 = (
                ("Suíte 5", "statement", normal_query),
                ("Quantidade camas casal (s5)", "number", normal_query),
                ("Descrição camas de casal (s5)", "long_text", normal_query),
                ("Quantidade camas solteiro (s5)", "number", normal_query),
                ("Descrição camas de solteiro (s5)", "long_text", normal_query),
                ("Possui ar-condicionado (s5)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s5)", "short_text", normal_query),
                ("Possui televisão (s5)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s5)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s5)", "short_text", normal_query),
                ("Possui chuveiro (s5)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s5)", "short_text", normal_query),
                ("Aquecimento água (s5)", "radio_vertical", water_query),
                ("Possui banheira (s5)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s5)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s5)", "attachment", normal_query),
                ("Outras observações da suíte 5 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_6 =( ("Suíte 6", "statement", normal_query),
                ("Quantidade camas casal (s6)", "number", normal_query),
                ("Descrição camas de casal (s6)", "long_text", normal_query),
                ("Quantidade camas solteiro (s6)", "number", normal_query),
                ("Descrição camas de solteiro (s6)", "long_text", normal_query),
                ("Possui ar-condicionado (s6)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s6)", "short_text", normal_query),
                ("Possui televisão (s6)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s6)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s6)", "short_text", normal_query),
                ("Possui chuveiro (s6)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s6)", "short_text", normal_query),
                ("Aquecimento água (s6)", "radio_vertical", water_query),
                ("Possui banheira (s6)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s6)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s6)", "attachment", normal_query),
                ("Outras observações da suíte 6 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_7 = (
                ("Suíte 7", "statement", normal_query),
                ("Quantidade camas casal (s7)", "number", normal_query),
                ("Descrição camas de casal (s7)", "long_text", normal_query),
                ("Quantidade camas solteiro (s7)", "number", normal_query),
                ("Descrição camas de solteiro (s7)", "long_text", normal_query),
                ("Possui ar-condicionado (s7)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s7)", "short_text", normal_query),
                ("Possui televisão (s7)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s7)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s7)", "short_text", normal_query),
                ("Possui chuveiro (s7)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s7)", "short_text", normal_query),
                ("Aquecimento água (s7)", "radio_vertical", water_query),
                ("Possui banheira (s7)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s7)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s7)", "attachment", normal_query),
                ("Outras observações da suíte 7 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_8 = (
                ("Suíte 8", "statement", normal_query),
                ("Quantidade camas casal (s8)", "number", normal_query),
                ("Descrição camas de casal (s8)", "long_text", normal_query),
                ("Quantidade camas solteiro (s8)", "number", normal_query),
                ("Descrição camas de solteiro (s8)", "long_text", normal_query),
                ("Possui ar-condicionado (s8)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s8)", "short_text", normal_query),
                ("Possui televisão (s8)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s8)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s8)", "short_text", normal_query),
                ("Possui chuveiro (s8)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s8)", "short_text", normal_query),
                ("Aquecimento água (s8)", "radio_vertical", water_query),
                ("Possui banheira (s8)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s8)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s8)", "attachment", normal_query),
                ("Outras observações da suíte 8 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_9 = (
                ("Suíte 9", "statement", normal_query),
                ("Quantidade camas casal (s9)", "number", normal_query),
                ("Descrição camas de casal (s9)", "long_text", normal_query),
                ("Quantidade camas solteiro (s9)", "number", normal_query),
                ("Descrição camas de solteiro (s9)", "long_text", normal_query),
                ("Possui ar-condicionado (s9)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s9)", "short_text", normal_query),
                ("Possui televisão (s9)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s9)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s9)", "short_text", normal_query),
                ("Possui chuveiro (s9)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s9)", "short_text", normal_query),
                ("Aquecimento água (s9)", "radio_vertical", water_query),
                ("Possui banheira (s9)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s9)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s9)", "attachment", normal_query),
                ("Outras observações da suíte 9 e requisições especiais do proprietário", "long_text", normal_query),
)

list_suite_10 = (
                ("Suíte 10", "statement", normal_query),
                ("Quantidade camas casal (s10)", "number", normal_query),
                ("Descrição camas de casal (s10)", "long_text", normal_query),
                ("Quantidade camas solteiro (s10)", "number", normal_query),
                ("Descrição camas de solteiro (s10)", "long_text", normal_query),
                ("Possui ar-condicionado (s10)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (s10)", "short_text", normal_query),
                ("Possui televisão (s10)", "radio_vertical", yes_no_query),
                ("Modelo da TV (s10)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (s10)", "short_text", normal_query),
                ("Possui chuveiro (s10)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (s10)", "short_text", normal_query),
                ("Aquecimento água (s10)", "radio_vertical", water_query),
                ("Possui banheira (s10)", "radio_vertical", yes_no_query),
                ("Modelo banheira (s10)", "short_text", normal_query),
                ("Fotos detalhadas da suíte e banheiro (s10)", "attachment", normal_query),
                ("Outras observações da suíte 10 e requisições especiais do proprietário", "long_text", normal_query),
)

list_room_1 = (
                ("Quarto 1", "statement", normal_query),
                ("Quantidade de camas de casal (q1)", "number", normal_query),
                ("Descrição camas de casal (q1)", "long_text", normal_query),
                ("Quantidade camas solteiro (q1)", "number", normal_query),
                ("Descrição camas de solteiro (q1)", "long_text", normal_query),
                ("Possui ar-condicionado (q1)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q1)", "short_text", normal_query),
                ("Possui televisão (q1)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q1)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q1)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q1)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q1)", "long_text", normal_query),
)

list_room_2 = (
                ("Quarto 2", "statement", normal_query),
                ("Quantidade de camas de casal (q2)", "number", normal_query),
                ("Descrição camas de casal (q2)", "long_text", normal_query),
                ("Quantidade camas solteiro (q2)", "number", normal_query),
                ("Descrição camas de solteiro (q2)", "long_text", normal_query),
                ("Possui ar-condicionado (q2)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q2)", "short_text", normal_query),
                ("Possui televisão (q2)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q2)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q2)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q2)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q2)", "long_text", normal_query),
)

list_room_3 = (
                ("Quarto 3", "statement", normal_query),
                ("Quantidade de camas de casal (q3)", "number", normal_query),
                ("Descrição camas de casal (q3)", "long_text", normal_query),
                ("Quantidade camas solteiro (q3)", "number", normal_query),
                ("Descrição camas de solteiro (q3)", "long_text", normal_query),
                ("Possui ar-condicionado (q3)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q3)", "short_text", normal_query),
                ("Possui televisão (q3)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q3)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q3)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q3)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q3)", "long_text", normal_query),
)

list_room_4 = (
                ("Quarto 4", "statement", normal_query),
                ("Quantidade de camas de casal (q4)", "number", normal_query),
                ("Descrição camas de casal (q4)", "long_text", normal_query),
                ("Quantidade camas solteiro (q4)", "number", normal_query),
                ("Descrição camas de solteiro (q4)", "long_text", normal_query),
                ("Possui ar-condicionado (q4)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q4)", "short_text", normal_query),
                ("Possui televisão (q4)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q4)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q4)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q4)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q4)", "long_text", normal_query),
)

list_room_5 = (
                ("Quarto 5", "statement", normal_query),
                ("Quantidade de camas de casal (q5)", "number", normal_query),
                ("Descrição camas de casal (q5)", "long_text", normal_query),
                ("Quantidade camas solteiro (q5)", "number", normal_query),
                ("Descrição camas de solteiro (q5)", "long_text", normal_query),
                ("Possui ar-condicionado (q5)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q5)", "short_text", normal_query),
                ("Possui televisão (q5)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q5)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q5)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q5)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q5)", "long_text", normal_query),
)

list_room_6 = (
                ("Quarto 6", "statement", normal_query),
                ("Quantidade de camas de casal (q6)", "number", normal_query),
                ("Descrição camas de casal (q6)", "long_text", normal_query),
                ("Quantidade camas solteiro (q6)", "number", normal_query),
                ("Descrição camas de solteiro (q6)", "long_text", normal_query),
                ("Possui ar-condicionado (q6)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q6)", "short_text", normal_query),
                ("Possui televisão (q6)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q6)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q6)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q6)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q6)", "long_text", normal_query),
)

list_room_7 = (
                ("Quarto 7", "statement", normal_query),
                ("Quantidade de camas de casal (q7)", "number", normal_query),
                ("Descrição camas de casal (q7)", "long_text", normal_query),
                ("Quantidade camas solteiro (q7)", "number", normal_query),
                ("Descrição camas de solteiro (q7)", "long_text", normal_query),
                ("Possui ar-condicionado (q7)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q7)", "short_text", normal_query),
                ("Possui televisão (q7)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q7)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q7)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q7)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q7)", "long_text", normal_query),
)

list_room_8 = (
                ("Quarto 8", "statement", normal_query),
                ("Quantidade de camas de casal (q8)", "number", normal_query),
                ("Descrição camas de casal (q8)", "long_text", normal_query),
                ("Quantidade camas solteiro (q8)", "number", normal_query),
                ("Descrição camas de solteiro (q8)", "long_text", normal_query),
                ("Possui ar-condicionado (q8)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q8)", "short_text", normal_query),
                ("Possui televisão (q8)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q8)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q8)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q8)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q8)", "long_text", normal_query),
)

list_room_9 = (
                ("Quarto 9", "statement", normal_query),
                ("Quantidade de camas de casal (q9)", "number", normal_query),
                ("Descrição camas de casal (q9)", "long_text", normal_query),
                ("Quantidade camas solteiro (q9)", "number", normal_query),
                ("Descrição camas de solteiro (q9)", "long_text", normal_query),
                ("Possui ar-condicionado (q9)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q9)", "short_text", normal_query),
                ("Possui televisão (q9)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q9)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q9)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q9)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q9)", "long_text", normal_query),
)

list_room_10 = (
                ("Quarto 10", "statement", normal_query),
                ("Quantidade de camas de casal (q10)", "number", normal_query),
                ("Descrição camas de casal (q10)", "long_text", normal_query),
                ("Quantidade camas solteiro (q10)", "number", normal_query),
                ("Descrição camas de solteiro (q10)", "long_text", normal_query),
                ("Possui ar-condicionado (q10)", "radio_vertical", yes_no_query),
                ("Modelo ar-condicionado (q10)", "short_text", normal_query),
                ("Possui televisão (q10)", "radio_vertical", yes_no_query),
                ("Modelo da TV (q10)", "short_text", normal_query),
                ("Possui TV a cabo ou antena digital? Descrever (q10)", "short_text", normal_query),
                ("Fotos detalhadas do quarto (q10)", "attachment", normal_query),
                ("Outras observações do quarto e requisições especiais do proprietário (q10)", "long_text", normal_query),
)

list_bathroom_1 = (
                ("Banheiro 1", "statement", normal_query),
                ("Possui chuveiro (b1)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b1)", "short_text", normal_query),
                ("Possui banheira (b1)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b1)", "short_text", normal_query),
                ("Aquecimento água (b1)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b1)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b1)", "long_text", normal_query),
)

list_bathroom_2 = (
                ("Banheiro 2", "statement", normal_query),
                ("Possui chuveiro (b2)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b2)", "short_text", normal_query),
                ("Possui banheira (b2)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b2)", "short_text", normal_query),
                ("Aquecimento água (b2)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b2)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b2)", "long_text", normal_query),
)

list_bathroom_3 = (
                ("Banheiro 3", "statement", normal_query),
                ("Possui chuveiro (b3)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b3)", "short_text", normal_query),
                ("Possui banheira (b3)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b3)", "short_text", normal_query),
                ("Aquecimento água (b3)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b3)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b3)", "long_text", normal_query),
)

list_bathroom_4 = (

                ("Banheiro 4", "statement", normal_query),
                ("Possui chuveiro (b4)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b4)", "short_text", normal_query),
                ("Possui banheira (b4)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b4)", "short_text", normal_query),
                ("Aquecimento água (b4)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b4)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b4)", "long_text", normal_query),

)

list_bathroom_5 = (
                ("Banheiro 5", "statement", normal_query),
                ("Possui chuveiro (b5)", "radio_vertical", yes_no_query),
                ("Modelo chuveiro (b5)", "short_text", normal_query),
                ("Possui banheira (b5)", "radio_vertical", yes_no_query),
                ("Modelo banheira (b5)", "short_text", normal_query),
                ("Aquecimento água (b5)", "radio_vertical", water_query),
                ("Fotos detalhadas banheiro (b5)", "attachment", normal_query),
                ("Outras observações do banheiro e requisições especiais do proprietário (b5)", "long_text", normal_query),
)

list_wc_1 = (
                ("Lavabo 1", "statement", normal_query),
                ("Fotos detalhadas lavabo 1", "attachment", normal_query),
)

list_wc_2 = (
                ("Lavabo 2", "statement", normal_query),
                ("Fotos detalhadas lavabo 2", "attachment", normal_query),
)

list_wc_3 = (
                ("Lavabo 3", "statement", normal_query),
                ("Fotos detalhadas lavabo 3", "attachment", normal_query),

)

list_wc_4 = (

                ("Lavabo 4", "statement", normal_query),
                ("Fotos detalhadas lavabo 4", "attachment", normal_query),
)

list_wc_5 = (

                ("Lavabo 5", "statement", normal_query),
                ("Fotos detalhadas lavabo 5", "attachment", normal_query),

                )


_list_to_hide = [code_dict[item[0]] for item in list_to_hide]

_list_suite_1 = [code_dict[item[0]] for item in list_suite_1]
_list_suite_2 = [code_dict[item[0]] for item in list_suite_2]
_list_suite_3 = [code_dict[item[0]] for item in list_suite_3]
_list_suite_4 = [code_dict[item[0]] for item in list_suite_4]
_list_suite_5 = [code_dict[item[0]] for item in list_suite_5]
_list_suite_6 = [code_dict[item[0]] for item in list_suite_6]
_list_suite_7 = [code_dict[item[0]] for item in list_suite_7]
_list_suite_8 = [code_dict[item[0]] for item in list_suite_8]
_list_suite_9 = [code_dict[item[0]] for item in list_suite_9]
_list_suite_10 = [code_dict[item[0]] for item in list_suite_10]

_list_room_1 = [code_dict[item[0]] for item in list_room_1]
_list_room_2 = [code_dict[item[0]] for item in list_room_2]
_list_room_3 = [code_dict[item[0]] for item in list_room_3]
_list_room_4 = [code_dict[item[0]] for item in list_room_4]
_list_room_5 = [code_dict[item[0]] for item in list_room_5]
_list_room_6 = [code_dict[item[0]] for item in list_room_6]
_list_room_7 = [code_dict[item[0]] for item in list_room_7]
_list_room_8 = [code_dict[item[0]] for item in list_room_8]
_list_room_9 = [code_dict[item[0]] for item in list_room_9]
_list_room_10 = [code_dict[item[0]] for item in list_room_10]

_list_bathroom_1 = [code_dict[item[0]] for item in list_bathroom_1]
_list_bathroom_2 = [code_dict[item[0]] for item in list_bathroom_2]
_list_bathroom_3 = [code_dict[item[0]] for item in list_bathroom_3]
_list_bathroom_4 = [code_dict[item[0]] for item in list_bathroom_4]
_list_bathroom_5 = [code_dict[item[0]] for item in list_bathroom_5]

_list_wc_1 = [code_dict[item[0]] for item in list_wc_1]
_list_wc_2 = [code_dict[item[0]] for item in list_wc_2]
_list_wc_3 = [code_dict[item[0]] for item in list_wc_3]
_list_wc_4 = [code_dict[item[0]] for item in list_wc_4]
_list_wc_5 = [code_dict[item[0]] for item in list_wc_5]

#build queries for conditional fields

conditional_query = GQL(
"""
mutation createFieldCondition (
$name: String,
$phaseId: ID!,
$actions: [FieldConditionActionInput],
$condition: ConditionInput
){
createFieldCondition (
input: {
name: $name,
phaseId: $phaseId,
actions: $actions,
condition: $condition
}
)
{
fieldCondition {
id
condition {
expressions {
id
field_address
}
}
}
}
}

"""
)

params_hide_all = {
"name" : "hide_all",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "hide",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_to_hide
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "999",
            "operation": "number_less_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_1 = {
"name" : "params_suite_1",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_1
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "0",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_2 = {
"name" : "params_suite_2",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_2
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "1",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_3 = {
"name" : "params_suite_3",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_3
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "2",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_4 = {
"name" : "params_suite_4",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_4
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "3",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_5 = {
"name" : "params_suite_5",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_5
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "4",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_6 = {
"name" : "params_suite_6",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_6
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "5",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_7 = {
"name" : "params_suite_7",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_7
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "6",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_8 = {
"name" : "params_suite_8",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_8
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "7",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_9 = {
"name" : "params_suite_9",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_9
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "8",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_suite_10 = {
"name" : "params_suite_10",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_suite_10
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de suítes"],
            "value": "9",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}


params_room_1 = {
"name" : "params_room_1",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_1
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "0",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_2 = {
"name" : "params_room_2",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_2
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "1",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_3 = {
"name" : "params_room_3",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_3
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "2",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_4 = {
"name" : "params_room_4",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_4
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "3",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_5 = {
"name" : "params_room_5",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_5
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "4",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_6 = {
"name" : "params_room_6",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_6
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "5",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_7 = {
"name" : "params_room_7",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_7
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "6",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_8 = {
"name" : "params_room_8",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_8
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "7",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_9 = {
"name" : "params_room_9",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_9
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "8",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_room_10 = {
"name" : "params_room_10",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_room_10
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Quantidade de quartos regulares"],
            "value": "9",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}



params_bathroom_1 = {
"name" : "params_bathroom_1",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_bathroom_1
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número  de banheiros (exceto suítes)"],
            "value": "0",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_bathroom_2 = {
"name" : "params_bathroom_2",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_bathroom_2
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número  de banheiros (exceto suítes)"],
            "value": "1",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_bathroom_3 = {
"name" : "params_bathroom_3",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_bathroom_3
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número  de banheiros (exceto suítes)"],
            "value": "2",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_bathroom_4 = {
"name" : "params_bathroom_4",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_bathroom_4
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número  de banheiros (exceto suítes)"],
            "value": "3",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_bathroom_5 = {
"name" : "params_bathroom_5",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_bathroom_5
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número  de banheiros (exceto suítes)"],
            "value": "4",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}


params_wc_1 = {
"name" : "params_wc_1",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_wc_1
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número de lavabos"],
            "value": "0",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_wc_2 = {
"name" : "params_wc_2",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_wc_2
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número de lavabos"],
            "value": "1",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_wc_3 = {
"name" : "params_wc_3",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_wc_3
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número de lavabos"],
            "value": "2",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_wc_4 = {
"name" : "params_wc_4",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_wc_4
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número de lavabos"],
            "value": "3",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}

params_wc_5 = {
"name" : "params_wc_5",
"phaseId" : phase_code,
"actions" : [
                {
                "actionId": "show",
                "phaseFieldId": item,
                "whenEvaluator": True
                } for item in _list_wc_5
            ],
"condition" : {
    "expressions": [
            {
            "field_address": code_dict["Número de lavabos"],
            "value": "4",
            "operation": "number_greater_than",
            "structure_id": 0
            }
        ],
        "expressions_structure": [[0]]
    },
}



fields_data = client.execute(conditional_query, variable_values=params_hide_all)

fields_data = client.execute(conditional_query, variable_values=params_suite_1)
fields_data = client.execute(conditional_query, variable_values=params_suite_2)
fields_data = client.execute(conditional_query, variable_values=params_suite_3)
fields_data = client.execute(conditional_query, variable_values=params_suite_4)
fields_data = client.execute(conditional_query, variable_values=params_suite_5)
fields_data = client.execute(conditional_query, variable_values=params_suite_6)
fields_data = client.execute(conditional_query, variable_values=params_suite_7)
fields_data = client.execute(conditional_query, variable_values=params_suite_8)
fields_data = client.execute(conditional_query, variable_values=params_suite_9)
fields_data = client.execute(conditional_query, variable_values=params_suite_10)

fields_data = client.execute(conditional_query, variable_values=params_room_1)
fields_data = client.execute(conditional_query, variable_values=params_room_2)
fields_data = client.execute(conditional_query, variable_values=params_room_3)
fields_data = client.execute(conditional_query, variable_values=params_room_4)
fields_data = client.execute(conditional_query, variable_values=params_room_5)
fields_data = client.execute(conditional_query, variable_values=params_room_6)
fields_data = client.execute(conditional_query, variable_values=params_room_7)
fields_data = client.execute(conditional_query, variable_values=params_room_8)
fields_data = client.execute(conditional_query, variable_values=params_room_9)
fields_data = client.execute(conditional_query, variable_values=params_room_10)

fields_data = client.execute(conditional_query, variable_values=params_bathroom_1)
fields_data = client.execute(conditional_query, variable_values=params_bathroom_2)
fields_data = client.execute(conditional_query, variable_values=params_bathroom_3)
fields_data = client.execute(conditional_query, variable_values=params_bathroom_4)
fields_data = client.execute(conditional_query, variable_values=params_bathroom_5)

fields_data = client.execute(conditional_query, variable_values=params_wc_1)
fields_data = client.execute(conditional_query, variable_values=params_wc_2)
fields_data = client.execute(conditional_query, variable_values=params_wc_3)
fields_data = client.execute(conditional_query, variable_values=params_wc_4)
fields_data = client.execute(conditional_query, variable_values=params_wc_5)
