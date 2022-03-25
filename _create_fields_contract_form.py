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

    ("Sala de estar", "statement", normal_query),
    ("Possui ar-condicionado", "radio_vertical", yes_no_query),
    ("Modelo ar-condicionado", "short_text", normal_query),
    ("Possui TV", "radio_vertical", yes_no_query),
    ("Modelo TV", "short_text", normal_query),
    ("Possui antena digital?", "radio_vertical", yes_no_query),
    ("Possui TV a cabo", "radio_vertical", yes_no_query),
    ("Qual operadora/plano?", "short_text", normal_query),
    ("Possui internet wifi", "radio_vertical", yes_no_query),
    ("Qual o plano, operadora, usuário e senha e dados do titular do contrato?", "long_text", normal_query),
    ("Outras observações relevantes sobre a sala de estar e pedidos especiais do proprietário", "long_text", normal_query),
    ("Fotos detalhadas da sala de estar", "attachment", normal_query),

    ("Cozinha", "statement", normal_query),
    ("Possui fogão", "radio_vertical", yes_no_query),
    ("Modelo fogão", "short_text", normal_query),
    ("Possui forno", "radio_vertical", yes_no_query),
    ("Modelo forno", "short_text", normal_query),
    ("Possui Micro-ondas", "radio_vertical", yes_no_query),
    ("Modelo do micro-ondas", "short_text", normal_query),
    ("Possui geladeira", "radio_vertical", yes_no_query),
    ("Modelo geladeira", "short_text", normal_query),
    ("Possui freezer (separado da geladeira)", "radio_vertical", yes_no_query),
    ("Modelo freezer", "short_text", normal_query),
    ("Possui máquina de lavar louça", "radio_vertical", yes_no_query),
    ("Modelo máquina de lavar louça", "short_text", normal_query),
    ("Possui chaleira elétrica", "radio_vertical", yes_no_query),
    ("Modelo chaleira elétrica", "short_text", normal_query),
    ("Possui cafeteira elétrica", "radio_vertical", yes_no_query),
    ("Modelo cafeteira elétrica", "short_text", normal_query),
    ("Possui liquidificador", "radio_vertical", yes_no_query),
    ("Modelo liquidificador", "short_text", normal_query),
    ("Possui sanduicheira", "radio_vertical", yes_no_query),
    ("Modelo sanduicheira", "short_text", normal_query),
    ("Utensílios de cozinha autorizados", "long_text", normal_query),
    ("Fotos detalhadas da cozinha", "attachment", normal_query),
    ("Outras informações relevantes e pedidos do proprietário acerca da cozinha", "long_text", normal_query),

    ("Área de serviço", "statement", normal_query),
    ("Possui máquina de lavar roupas", "radio_vertical", yes_no_query),
    ("Modelo da máquina de lavar roupas", "short_text", normal_query),
    ("Possui máquina de secar roupas", "radio_vertical", yes_no_query),
    ("Modelo da máquina de secar roupas", "short_text", normal_query),
    ("Possui ferro de passar", "radio_vertical", yes_no_query),
    ("Modelo do ferro de passar", "short_text", normal_query),
    ("Possui mesa para passar roupas", "radio_vertical", yes_no_query),
    ("Fotos detalhadas da área de serviço", "attachment", normal_query),
    ("Outras informações relevantes e pedidos do proprietário acerca da área de serviço", "long_text", normal_query),

    ("Sacada/área externa privativa", "statement", normal_query),
    ("Possui sacada/área externa privativa", "radio_vertical", yes_no_query),
    ("Possui jardim privativo", "radio_vertical", yes_no_query),
    ("Possui churrasqueira privativa", "radio_vertical", yes_no_query),
    ("Possui piscina privativa", "radio_vertical", yes_no_query),
    ("Possui jacuzzi (banheira) privativa", "radio_vertical", yes_no_query),
    ("Fotos detalhadas de áreas externas e churrasqueira", "attachment", normal_query),
    ("Outras observações e pedidos do proprietário acerca de áreas externas", "long_text", normal_query),

    ("Capacidade de pessoas", "short_text", normal_query),
    ("Quantidade total de camas de casal", "number", normal_query),
    ("Quantidade total de camas de solteiro", "number", normal_query),

    ("Suítes", "statement", normal_query),
    ("Quantidade de suítes", "number", normal_query),

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

    ("Quartos", "statement", normal_query),
    ("Quantidade de quartos regulares", "number", normal_query),

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

    ("Banheiros e lavabos", "statement", normal_query),
    ("Número  de banheiros (exceto suítes)", "number", normal_query),

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

    ("Número de lavabos", "number", normal_query),

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

    ("Estacionamento", "statement", normal_query),
    ("Número de vagas", "number", normal_query),
    ("Descrição das vagas (número de vagas, são cobertas? Onde ficam?)", "long_text", normal_query),
    ("Foto vagas de garagem", "attachment", normal_query),

    ("Condomínio", "statement", normal_query),
    ("Como funciona a acessibilidade? Há Elevador e/ou escadas?", "long_text", normal_query),
    ("Unidade fica em condomínio residencial?", "radio_vertical", yes_no_query),
    ("Nome do condomínio", "short_text", normal_query),
    ("Condomínio possui portaria", "radio_vertical", yes_no_query),
    ("Como funciona a portaria do condomínio? Horários de funcionamento, acesso, etc.", "short_text", normal_query),
    ("O que o condomínio oferece aos hóspedes de temporada?", "long_text", normal_query),
    ("Fotos de instalações do condomínio (apenas locais disponíveis para uso pelos hóspedes de temporada)", "attachment", normal_query),
    ("Regras do condomínio para hóspedes", "long_text", normal_query),
    ("Contatos do condomínio (síndicos, zeladores, etc.)", "long_text", normal_query),
    ("Como deve ser realizado o cadastro de hóspedes no condomínio?", "long_text", normal_query),
    ("Fichas padrão do condomínio para preenchimento (se houver)", "attachment", normal_query),

    ("Dados de emergência", "statement", normal_query),
    ("Localização quadro de disjuntores", "short_text", normal_query),
    ("Foto quadro de disjuntores", "attachment", normal_query),
    ("Localização registro geral de água", "short_text", normal_query),
    ("Foto registro geral de água", "attachment", normal_query),
    ("Local registro gás/botijão", "short_text", normal_query),
    ("Foto local registro gás/botijão", "attachment", normal_query),

    ("Outros dados da propriedade", "statement", normal_query),
    ("Possui secador de cabelo", "radio_vertical", yes_no_query),
    ("Modelo secador de cabelo", "short_text", normal_query),
    ("Dados coleta do lixo", "long_text", normal_query),

    ("Outras informações para onboarding", "statement", normal_query),
    ("Data/hora para marcar fotografia", "datetime", normal_query),
    ]

    for item in entries_list:
        params = {"paramTextName" : item[0],
                  "paramType" : item[1],
                  "paramPhase" : "310644065"}

        database_data = client.execute(item[2], variable_values=params)
        print(item[0] + " done")

pullAllDbsPipefy_main(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDExMDcyODcsImVtYWlsIjoiai52ZWlnYUBhbmZpdHJpb2VzZGVhbHVndWVsLmNvbS5iciIsImFwcGxpY2F0aW9uIjozMDAwODczMTh9fQ.kaf7lQFeKhfWd2syG83WB6JQ_KJSXtWVvuzMtzykiVvdcbYkn66HN1SKfkkUSr5x7nv_z-pobAoTdx8-jSPNKA")
