import config
from config import makeAsyncApiCalls
from pull_agg_dbs import CollectAllReservationCards

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


def addNewAffiliateCards(ResDF, reservationCardsDB, affiliatesDBDF, propertiesDBDF, pipePhasesDF, propertyOnly, affiliateCode, propertyCode):

    affiliatesDBDF["id"] = affiliatesDBDF["id"].astype("str")
    notYetLoadedResDF = ResDF[~ResDF["Estado"].isin(["Indisponível", "Pedido informação", "Pré-reserva"])]

    reservationsToPass = []

    def date2APIFormat(date_val):
        return date_val[-4:] + "-" + date_val[3:5] + "-" + date_val[0:2]

    newResQuery = GQL(
        """
        mutation($paramResCode: [UndefinedInput], $paramPropCode: [UndefinedInput], $paramResDate: [UndefinedInput],
                 $paramInDate: [UndefinedInput], $paramOutDate: [UndefinedInput], $paramGuestName: [UndefinedInput],
                 $paramPhone: [UndefinedInput], $paramLanguage: [UndefinedInput], $paramPortal: [UndefinedInput],
                 $paramNewResMes: [UndefinedInput], $paramIntructions: [UndefinedInput],
                 $paramWAWeb: [UndefinedInput], $paramOutMes: [UndefinedInput], $paramStatus: [UndefinedInput],
                 $paramRegLink: [UndefinedInput], $paramRegInst: [UndefinedInput], $paramPipeCode: ID!){
          createCard(input:{
            pipe_id: $paramPipeCode
            fields_attributes:[
              {field_id:"c_digo_reserva", field_value: $paramResCode}
              {field_id:"c_digo_propriedade", field_value: $paramPropCode}
              {field_id:"data_da_reserva", field_value: $paramResDate}
              {field_id:"data_check_in", field_value: $paramInDate}
              {field_id:"data_check_out_1", field_value: $paramOutDate}
              {field_id:"nome_h_spede", field_value: $paramGuestName}
              {field_id:"telefone_de_contato", field_value: $paramPhone}
              {field_id:"idioma", field_value: $paramLanguage}
              {field_id:"portal_da_reserva", field_value: $paramPortal}
              {field_id:"mensagem_nova_reserva", field_value: $paramNewResMes}
              {field_id:"mensagem_instru_es_check_in", field_value: $paramIntructions}
              {field_id:"link_whatsapp_web", field_value: $paramWAWeb}
              {field_id:"mensagem_de_check_out", field_value: $paramOutMes}
              {field_id:"status_reserva", field_value: $paramStatus}
              {field_id:"link_formul_rio_de_cadastro", field_value: $paramRegLink}
              {field_id:"como_realizar_cadastro_no_condom_nio", field_value: $paramRegInst}
            ]
          })
            {
        clientMutationId
            }
        }
        """
    )

    def nanHandling(val):
        if val != val:
            return ""
        else:
            return str(val)

    def getResponsibleAffiliate(propertiesDBDF, row):
        def isNaN(num):
            return num != num
        _ = propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["Afiliado responsável"].values[0]
        if isNaN(_):
            affiliateId = "406710545"
        else:
            affiliateId = str(_)
            #affiliateId = propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["Afiliado responsável"].values[0]
        return re.sub("[^0-9]", "", affiliateId)


    for index, row in notYetLoadedResDF.iterrows():
        if propertyOnly:
            if row["Nome alojamento"] != propertyCode:
                continue
        else:
            if re.sub("[^0-9]", "", str(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["Afiliado responsável"].values[0])) != affiliateCode:
                continue

        form_link = "https://anfitrioesdealuguel.com.br/registro/?reservation-code={resCode}".format(resCode=row["Referência"])

        affiliateId = getResponsibleAffiliate(propertiesDBDF=propertiesDBDF, row=row)

        startMessage = str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["Mensagem inicial padrão"].values[0])
        startMessage = startMessage.format(guest_name=row["Cliente: Nome"],
                                           check_in_date=date2APIFormat(row["Data de check-in"]),
                                           link_register=form_link,)

        #handle nans
        params = {"paramPipeCode" : str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["ID pipe recepção"].values[0]),
                  "paramResCode" : nanHandling(row["Referência"]),
                  "paramPropCode" : nanHandling(row["Nome alojamento"]),
                  "paramResDate" : date2APIFormat(row["Data"]),
                  "paramInDate" : date2APIFormat(row["Data de check-in"]),
                  "paramOutDate" : date2APIFormat(row["Data de check-out"]),
                  "paramGuestName" : nanHandling(row["Cliente: Nome"]) + " " + nanHandling(row["Cliente: Sobrenomes"]),
                  "paramPhone" : nanHandling(row["Cliente: Telefone"]),
                  "paramLanguage" : nanHandling(row["Hóspede: Idioma do cliente"]),
                  "paramPortal" : nanHandling(row["Portal"]),
                  "paramNewResMes" : startMessage,
                  "paramIntructions" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Instruções do check-in"].values[0]),
                  "paramWAWeb" : "https://wa.me/" + re.sub("[^0-9]", "", nanHandling(row["Cliente: Telefone"])),
                  "paramOutMes" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Instruções do check-out"].values[0]),
                  "paramStatus" : nanHandling(row["Estado"]),
                  "paramRegLink" : str(form_link),
                  "paramRegInst" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Procedimento de cadastro no condomínio"].values[0]),
                  }

        #don't add reservation if checkout has already been
        checkoutDatesToIgnore = ((datetime.date.today() - datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in range(1, 1800))
        if params["paramOutDate"] in checkoutDatesToIgnore:
            continue

        api_key = affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["Chave pipefy"].values[0]

        reservationsToPass.append({"params" : params,
                                   "api_key" : api_key})

    def divide_chunks(l, n):
    # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    for chunk in divide_chunks(reservationsToPass, 200):

        asyncio.run(makeAsyncApiCalls(chunk, newResQuery))
        time.sleep(1)

if __name__ == "__main__":
    newAfiliate = str(input("Você deseja registrar um novo afiliado (digite 1) ou a troca de acomodação para um afiliado diferente (digite 2)?"))

    if newAfiliate == "1":
        propertyOnly = False
        affiliateCode = str(input("Qual o código do afiliado?"))
        propertyCode = ""
    elif newAfiliate == "2":
        propertyOnly = True
        propertyCode = str(input("Qual o código da propriedade?"))
        affiliateCode = ""
    else:
        print("Valor inválido")

    ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
    reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
    pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
    addNewAffiliateCards(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, pipePhasesDF=pipePhasesDF, propertyOnly=propertyOnly, affiliateCode=affiliateCode, propertyCode=propertyCode)
