import config
from config import makeAsyncApiCalls

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

affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)

def pushNewPropertiesToAffiliatesPropertiesDB(affiliatePropertiesDBDF, propertiesDBDF, affiliatesDBDF, ownersDBDF):

    def nanHandling(val):
        if val != val:
            return ""
        else:
            return str(val)

    #all record where affiliate db overrides main db
    affiliateToAdA = ("o_que_o_condom_nio_oferece", "regras_do_condom_nio_para_h_spedes", "procedimento_de_cadastro_no_condom_nio", "elevador", "nome_e_senha_wi_fi",
                      "dados_contrato_wifi", "instru_es_do_check_in", "instru_es_do_check_out", "descri_o_chaves_da_propriedade")

    #identify all properties that haven't been added to their correct owner
    createTableRecordQuery = """
    mutation($paramCode: [UndefinedInput], $paramActive: [UndefinedInput], $paramStreet: [UndefinedInput],
             $paramBuild: [UndefinedInput], $paramFloor: [UndefinedInput], $paramApto: [UndefinedInput],
             $paramCep: [UndefinedInput], $paramNeigh: [UndefinedInput], $paramCity: [UndefinedInput],
             $paramUf: [UndefinedInput], $paramPercent: [UndefinedInput], $paramBuildName: [UndefinedInput],
             $paramBuildAmen: [UndefinedInput], $paramBuildRules: [UndefinedInput], $paramGuestReg: [UndefinedInput],
             $paramLinkReg: [UndefinedInput], $paramElev: [UndefinedInput], $paramWifi: [UndefinedInput], $paramWifiData: [UndefinedInput],
             $paramInInst: [UndefinedInput], $paramOutInst: [UndefinedInput], $paramKeys: [UndefinedInput],
             $paramFile: [UndefinedInput], $paramPJ: [UndefinedInput], $paramCnpj: [UndefinedInput],
             $paramPf: [UndefinedInput], $paramCpf: [UndefinedInput], $paramCel: [UndefinedInput],
             $paramOthers: [UndefinedInput], $paramTable: ID!){
      createTableRecord(input:{
        table_id: $paramTable,
        fields_attributes:[
          {field_id: "c_digo_da_propriedade", field_value: $paramCode}
          {field_id: "propriedade_ativa", field_value: $paramActive}
          {field_id: "logradouro", field_value: $paramStreet}
          {field_id: "n_mero_do_edif_cio", field_value: $paramBuild}
          {field_id: "andar", field_value: $paramFloor}
          {field_id: "complemento", field_value: $paramApto}
          {field_id: "cep", field_value: $paramCep}
          {field_id: "bairro", field_value: $paramNeigh}
          {field_id: "cidade", field_value: $paramCity}
          {field_id: "uf", field_value: $paramUf}
          {field_id: "porcentagem_cobrada_anfitri_o", field_value: $paramPercent}
          {field_id: "nome_do_condom_nio", field_value: $paramBuildName}
          {field_id: "o_que_o_condom_nio_oferece", field_value: $paramBuildAmen}
          {field_id: "regras_do_condom_nio_para_h_spedes", field_value: $paramBuildRules}
          {field_id: "procedimento_de_cadastro_no_condom_nio", field_value: $paramGuestReg}
          {field_id: "link_ficha_de_cadastro_padr_o_do_condom_nio", field_value: $paramLinkReg}
          {field_id: "elevador", field_value: $paramElev}
          {field_id: "nome_e_senha_wi_fi", field_value: $paramWifi}
          {field_id: "dados_contrato_wifi", field_value: $paramWifiData}
          {field_id: "instru_es_do_check_in", field_value: $paramInInst}
          {field_id: "instru_es_do_check_out", field_value: $paramOutInst}
          {field_id: "descri_o_chaves_da_propriedade", field_value: $paramKeys}
          {field_id: "link_ficha_t_cnica_da_propriedade", field_value: $paramFile}
          {field_id: "nome_propriet_rio_pj", field_value: $paramPJ}
          {field_id: "cnpj_da_pj_titular", field_value: $paramCnpj}
          {field_id: "nome_propriet_rio_pf", field_value: $paramPf}
          {field_id: "cpf_da_pf_titular", field_value: $paramCpf}
          {field_id: "celular_whatsapp_de_contato", field_value: $paramCel}
          {field_id: "terceiros_autorizados_a_lidar_em_nome_do_propriet_rio", field_value: $paramOthers}
        ]

      }) {
        clientMutationId
      }
    }
    """
    

    alterTableRecordQuery = """
    mutation($paramId: ID!, $paramFieldId: ID!, $paramValue: [UndefinedInput]){
      setTableRecordFieldValue(input:{
        table_record_id: $paramId
        field_id: $paramFieldId
        value: $paramValue
      }) {
        clientMutationId
      }
    }
    """
    

    recordsToBuild = []
    alterationsToPass = []

    ownersDBDF["id"] = ownersDBDF["id"].astype("str")
    affiliatesDBDF["id"] = affiliatesDBDF["id"].astype("str")
    affiliatePropertiesDBDF["AffiliateId"] = affiliatePropertiesDBDF["AffiliateId"].astype("str")

    for index, row in propertiesDBDF.iterrows():

        _affiliateRow = affiliatePropertiesDBDF[affiliatePropertiesDBDF["Código da propriedade"]==row["Código da propriedade"]]
        _affiliateRow = _affiliateRow[_affiliateRow["AffiliateId"]==re.sub("[^0-9]", "", str(row["Afiliado responsável"]))]


        if _affiliateRow.empty:
            #add to create pipeline
            #falta adicionar table_id
            params = {"paramTable" : nanHandling(affiliatesDBDF[affiliatesDBDF["id"]==re.sub("[^0-9]", "", str(row["Afiliado responsável"]))]["ID BD propriedades"].values[0]),
                    "paramCode" : nanHandling(row["Código da propriedade"]),
                    "paramActive" : nanHandling(row["Propriedade ativa?"]),
                    "paramStreet" : nanHandling(row["Logradouro"]),
                    "paramBuild" : nanHandling(row["Número do edifício"]),
                    "paramFloor" : nanHandling(row["Andar"]),
                    "paramApto" : nanHandling(row["Complemento"]),
                    "paramCep" : nanHandling(row["CEP"]),
                    "paramNeigh" : nanHandling(row["Bairro"]),
                    "paramCity" : nanHandling(row["Cidade"]),
                    "paramUf" : nanHandling(row["UF"]),
                    "paramPercent" : nanHandling(row["Porcentagem cobrada Anfitrião"]),
                    "paramBuildName" : nanHandling(row["Nome do condomínio"]),
                    "paramBuildAmen" : nanHandling(row["(*) O que o condomínio oferece?"]),
                    "paramBuildRules" : nanHandling(row["(*) Regras do condomínio para hóspedes"]),
                    "paramGuestReg" : nanHandling(row["(*) Procedimento de cadastro no condomínio"]),
                    "paramLinkReg" : nanHandling(row["Link ficha de cadastro padrão do condomínio"]),
                    "paramElev" : nanHandling(row["(*) Elevador"]),
                    "paramWifi" : nanHandling(row["(*) Nome e senha wi-fi"]),
                    "paramWifiData" : nanHandling(row["(*) Dados contrato wifi"]),
                    "paramInInst" : nanHandling(row["(*) Instruções do check-in"]),
                    "paramOutInst" : nanHandling(row["(*) Instruções do check-out"]),
                    "paramKeys" : nanHandling(row["(*) Descrição chaves da propriedade"]),
                    "paramFile" : nanHandling(row["Link ficha técnica da propriedade"]),
                    "paramPJ" : nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Razão social PJ titular"].values[0]),
                    "paramCnpj" : nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["CNPJ"].values[0]),
                    "paramPf" : nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Nome Completo da Pessoa Física titular"].values[0]),
                    "paramCpf" : nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["CPF da PF titular"].values[0]),
                    "paramCel" : nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Celular (whatsapp) de contato"].values[0]),
                    "paramOthers" : nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Terceiros autorizados a lidar em nome do proprietário"].values[0]),
                    }

            api_key = affiliatesDBDF[affiliatesDBDF["id"]==re.sub("[^0-9]", "", str(row["Afiliado responsável"]))]["Chave pipefy"].values[0]

            recordsToBuild.append({"params" : params, "api_key" : api_key})

        else:
            #falta código do row no bd pipefy
            compareList = [(nanHandling(_affiliateRow["Código da propriedade"].values[0]), nanHandling(row["Código da propriedade"]), "c_digo_da_propriedade"),
            (nanHandling(_affiliateRow["Propriedade ativa?"].values[0]), nanHandling(row["Propriedade ativa?"]), "propriedade_ativa"),
            (nanHandling(_affiliateRow["Logradouro"].values[0]), nanHandling(row["Logradouro"]), "logradouro"),
            (nanHandling(_affiliateRow["Número do edifício"].values[0]), nanHandling(row["Número do edifício"]), "n_mero_do_edif_cio"),
            (nanHandling(_affiliateRow["Andar"].values[0]), nanHandling(row["Andar"]), "andar"),
            (nanHandling(_affiliateRow["Complemento"].values[0]), nanHandling(row["Complemento"]), "complemento"),
            (nanHandling(_affiliateRow["CEP"].values[0]), nanHandling(row["CEP"]), "cep"),
            (nanHandling(_affiliateRow["Bairro"].values[0]), nanHandling(row["Bairro"]), "bairro"),
            (nanHandling(_affiliateRow["Cidade"].values[0]), nanHandling(row["Cidade"]), "cidade"),
            (nanHandling(_affiliateRow["UF"].values[0]), nanHandling(row["UF"]), "uf"),
            (nanHandling(_affiliateRow["Porcentagem cobrada Anfitrião"].values[0]), nanHandling(row["Porcentagem cobrada Anfitrião"]), "porcentagem_cobrada_anfitri_o"),
            (nanHandling(_affiliateRow["Nome do condomínio"].values[0]), nanHandling(row["Nome do condomínio"]), "nome_do_condom_nio"),
            (nanHandling(_affiliateRow["(*) O que o condomínio oferece?"].values[0]), nanHandling(row["(*) O que o condomínio oferece?"]), "o_que_o_condom_nio_oferece"),
            (nanHandling(_affiliateRow["(*) Regras do condomínio para hóspedes"].values[0]), nanHandling(row["(*) Regras do condomínio para hóspedes"]), "regras_do_condom_nio_para_h_spedes"),
            (nanHandling(_affiliateRow["(*) Procedimento de cadastro no condomínio"].values[0]), nanHandling(row["(*) Procedimento de cadastro no condomínio"]), "procedimento_de_cadastro_no_condom_nio"),
            (nanHandling(_affiliateRow["Link ficha de cadastro padrão do condomínio"].values[0]), nanHandling(row["Link ficha de cadastro padrão do condomínio"]), "link_ficha_de_cadastro_padr_o_do_condom_nio"),
            (nanHandling(_affiliateRow["(*) Elevador"].values[0]), nanHandling(row["(*) Elevador"]), "elevador"),
            (nanHandling(_affiliateRow["(*) Nome e senha wi-fi"].values[0]), nanHandling(row["(*) Nome e senha wi-fi"]), "nome_e_senha_wi_fi"),
            (nanHandling(_affiliateRow["(*) Dados contrato wifi"].values[0]), nanHandling(row["(*) Dados contrato wifi"]), "dados_contrato_wifi"),
            (nanHandling(_affiliateRow["(*) Instruções do check-in"].values[0]), nanHandling(row["(*) Instruções do check-in"]), "instru_es_do_check_in"),
            (nanHandling(_affiliateRow["(*) Instruções do check-out"].values[0]), nanHandling(row["(*) Instruções do check-out"]), "instru_es_do_check_out"),
            (nanHandling(_affiliateRow["(*) Descrição chaves da propriedade"].values[0]), nanHandling(row["(*) Descrição chaves da propriedade"]), "descri_o_chaves_da_propriedade"),
            (nanHandling(_affiliateRow["Link ficha técnica da propriedade"].values[0]), nanHandling(row["Link ficha técnica da propriedade"]), "link_ficha_t_cnica_da_propriedade"),
            (nanHandling(_affiliateRow["Nome proprietário PJ"].values[0]), nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Razão social PJ titular"].values[0]), "nome_propriet_rio_pj"),
            (nanHandling(_affiliateRow["CNPJ da PJ titular"].values[0]), nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["CNPJ"].values[0]), "cnpj_da_pj_titular"),
            (nanHandling(_affiliateRow["Nome proprietário PF"].values[0]), nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Nome Completo da Pessoa Física titular"].values[0]), "nome_propriet_rio_pf"),
            (nanHandling(_affiliateRow["CPF da PF titular"].values[0]), nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["CPF da PF titular"].values[0]), "cpf_da_pf_titular"),
            (nanHandling(_affiliateRow["Celular/whatsapp de contato"].values[0]), nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Celular (whatsapp) de contato"].values[0]), "celular_whatsapp_de_contato"),
            (nanHandling(_affiliateRow["Terceiros autorizados a lidar em nome do proprietário"].values[0]), nanHandling(ownersDBDF[ownersDBDF["id"]==re.sub("[^0-9]", "", str(row["Proprietário"]))]["Terceiros autorizados a lidar em nome do proprietário"].values[0]), "terceiros_autorizados_a_lidar_em_nome_do_propriet_rio"),
            ]


            for item in compareList:
                if item[0]!=item[1]:

                    if item[2] in affiliateToAdA:
                        new_val = str(item[0])
                        record_id = str(row["id"])

                        api_key = config.token_main

                    else:
                        new_val = str(item[1])
                        record_id = str(_affiliateRow["id"].values[0])

                        api_key = affiliatesDBDF[affiliatesDBDF["id"]==re.sub("[^0-9]", "", row["Afiliado responsável"])]["Chave pipefy"].values[0]

                    params = {"paramId" : record_id,
                              "paramFieldId": str(item[2]),
                              "paramValue": new_val,
                              }

                    alterationsToPass.append({"params" : params, "api_key" : api_key})


            #criar diversos ifs pareando os campos. para cada divergência, criar ordem de alteração

    def divide_chunks(l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    for chunk in divide_chunks(recordsToBuild, 100):

        makeAsyncApiCalls(chunk, createTableRecordQuery)
        time.sleep(1)

    for chunk in divide_chunks(alterationsToPass, 100):

        makeAsyncApiCalls(chunk, alterTableRecordQuery)
        time.sleep(1)


if __name__ == "__main__":
    affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
    propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
    pushNewPropertiesToAffiliatesPropertiesDB(affiliatePropertiesDBDF = affiliatePropertiesDBDF, propertiesDBDF = propertiesDBDF, affiliatesDBDF = affiliatesDBDF, ownersDBDF = ownersDBDF)
