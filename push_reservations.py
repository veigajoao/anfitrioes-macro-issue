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


#push new reservations
def addNewReservations(ResDF, reservationCardsDB, affiliatesDBDF, propertiesDBDF, affiliatesIndicationsDB):

    affiliatesIndicationsDB["Código promocional para reservas"] = affiliatesIndicationsDB["Código promocional para reservas"].astype(str)

    def isNaN(num):
        return num != num

    def create_values_row(row):

        if row["Comissão portal/intermediário: comissão personalizada"] > 0:
            return row["Comissão portal/intermediário: comissão personalizada"]
        else:
            return row["Comissão portal/intermediário: comissão calculada"]


    ResDF["Valor_intermediario"] = ResDF.apply(create_values_row, axis=1)

    ResDF.to_excel("resDf.xlsx")

    affiliatesDBDF["id"] = affiliatesDBDF["id"].astype("str")
    if reservationCardsDB.empty:
        notYetLoadedResDF = ResDF
    else:
        notYetLoadedResDF = ResDF[~ResDF["Referência"].isin(list(reservationCardsDB["Código reserva"]))]
        notYetLoadedResDF = notYetLoadedResDF[~notYetLoadedResDF["Estado"].isin(["Indisponível", "Pedido informação", "Pré-reserva", "Cancelada", "Cancelada proprietário"])]

    reservationsToPass = []

    def date2APIFormat(date_val):
        return date_val[-4:] + "-" + date_val[3:5] + "-" + date_val[0:2]

    newResQuery = """
        mutation($paramResCode: [UndefinedInput], $paramPropCode: [UndefinedInput], $paramResDate: [UndefinedInput],
                 $paramInDate: [UndefinedInput], $paramOutDate: [UndefinedInput], $paramGuestName: [UndefinedInput],
                 $paramPhone: [UndefinedInput], $paramLanguage: [UndefinedInput], $paramGuestNumber: [UndefinedInput], $paramPortal: [UndefinedInput],
                 $paramNewResMes: [UndefinedInput], $paramIntructions: [UndefinedInput],
                 $paramWAWeb: [UndefinedInput], $paramOutMes: [UndefinedInput], $paramStatus: [UndefinedInput],
                 $paramRegLink: [UndefinedInput], $paramRegInst: [UndefinedInput], $paramValue: [UndefinedInput], $paramCleanValue: [UndefinedInput], $paramPipeCode: ID!, $paramDueDate: DateTime){
          createCard(input:{
            pipe_id: $paramPipeCode
            due_date: $paramDueDate
            fields_attributes:[
              {field_id:"c_digo_reserva", field_value: $paramResCode}
              {field_id:"c_digo_propriedade", field_value: $paramPropCode}
              {field_id:"data_da_reserva", field_value: $paramResDate}
              {field_id:"data_check_in", field_value: $paramInDate}
              {field_id:"data_check_out_1", field_value: $paramOutDate}
              {field_id:"nome_h_spede", field_value: $paramGuestName}
              {field_id:"telefone_de_contato", field_value: $paramPhone}
              {field_id:"idioma", field_value: $paramLanguage}
              {field_id:"quantidade_de_pessoas", field_value: $paramGuestNumber}
              {field_id:"portal_da_reserva", field_value: $paramPortal}
              {field_id:"mensagem_nova_reserva", field_value: $paramNewResMes}
              {field_id:"mensagem_instru_es_check_in", field_value: $paramIntructions}
              {field_id:"link_whatsapp_web", field_value: $paramWAWeb}
              {field_id:"mensagem_de_check_out", field_value: $paramOutMes}
              {field_id:"status_reserva", field_value: $paramStatus}
              {field_id:"link_formul_rio_de_cadastro", field_value: $paramRegLink}
              {field_id:"como_realizar_cadastro_no_condom_nio", field_value: $paramRegInst}
              {field_id:"valor_da_reserva", field_value: $paramValue}
              {field_id:"valor_taxa_de_limpeza", field_value: $paramCleanValue}
            ]
          })
            {
        clientMutationId
            }
        }
        """
    

    def nanHandling(val):
        if val != val:
            return ""
        else:
            return str(val)

    def nanHandlingb(val):
        if val != val:
            return 0
        else:
            return int(val)

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

        form_link = "https://conteudo.anfitrioesdealuguel.com.br/cadastro-de-hospedes?cod-reserva={resCode}".format(resCode=row["Referência"])
        #form_link = "https://anfitrioesdealuguel.com.br/registro/?reservation-code={resCode}".format(resCode=row["Referência"])

        affiliateId = getResponsibleAffiliate(propertiesDBDF=propertiesDBDF, row=row)

        print(affiliateId)
        print(str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["Mensagem inicial padrão"].values[0]))
        startMessage = str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["Mensagem inicial padrão"].values[0])
        startMessage = startMessage.format(guest_name=row["Cliente: Nome"],
                                           check_in_date=date2APIFormat(row["Data de check-in"]),
                                           link_register=form_link,)

        #handle nans
        params = {"paramPipeCode" : str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["ID pipe recepção"].values[0]),
                  "paramDueDate" : date2APIFormat(row["Data de check-in"]),
                  "paramResCode" : nanHandling(row["Referência"]),
                  "paramPropCode" : nanHandling(row["Nome alojamento"]),
                  "paramResDate" : date2APIFormat(row["Data"]),
                  "paramInDate" : date2APIFormat(row["Data de check-in"]),
                  "paramOutDate" : date2APIFormat(row["Data de check-out"]),
                  "paramGuestName" : nanHandling(row["Cliente: Nome"]) + " " + nanHandling(row["Cliente: Sobrenomes"]),
                  "paramPhone" : nanHandling(row["Cliente: Telefone"]),
                  "paramLanguage" : nanHandling(row["Hóspede: Idioma do cliente"]),
                  "paramGuestNumber" : nanHandling(row["Adultos"]),
                  "paramPortal" : nanHandling(row["Portal"]),
                  "paramNewResMes" : startMessage,
                  "paramIntructions" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Instruções do check-in"].values[0]),
                  "paramWAWeb" : "https://wa.me/" + re.sub("[^0-9]", "", nanHandling(row["Cliente: Telefone"])),
                  "paramOutMes" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Instruções do check-out"].values[0]),
                  "paramStatus" : nanHandling(row["Estado"]),
                  "paramRegLink" : str(form_link),
                  "paramRegInst" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Procedimento de cadastro no condomínio"].values[0]),
                  "paramValue" : "{:.2f}".format(nanHandlingb(row["Aluguer sem imposto"]) - nanHandlingb(row["Valor_intermediario"])),
                  "paramCleanValue" : "{:.2f}".format(nanHandlingb(row["Extras sem imposto"])),
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

        makeAsyncApiCalls(chunk, newResQuery)
        time.sleep(1)


#push reservation alterations
def modifyReservationsWithChanges(ResDF, reservationCardsDB, affiliatesDBDF, propertiesDBDF, pipePhasesDF, affiliatesIndicationsDB):

    def date2APIFormat(date_val):
        return date_val[-4:] + "-" + date_val[3:5] + "-" + date_val[0:2]

    def nanHandling(val):
        if val != val:
            return ""
        else:
            return str(val)

    def nanHandlingb(val):
        if val != val:
            return 0
        else:
            if re.search('[a-zA-Z]', str(val)):
                return 0
            else:
                return int(float(val))

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

    affiliatesDBDF["id"] = affiliatesDBDF["id"].astype("str")
    reservationCardsDB["AffiliateId"] = reservationCardsDB["AffiliateId"].astype("str")

    affiliatesIndicationsDB["Código promocional para reservas"] = affiliatesIndicationsDB["Código promocional para reservas"].astype(str)

    def isNaN(num):
        return num != num

    def create_values_row(row):
        if isNaN(row["Código promocional"]):
            if row["Comissão portal/intermediário: comissão personalizada"] > 0:
                return row["Comissão portal/intermediário: comissão personalizada"]
            else:
                return row["Comissão portal/intermediário: comissão calculada"]
        else:
            #multiplica aluguekl pela porcentagem acordada com o afiliado de venda
            try:
                return row["Aluguer sem imposto"] * affiliatesIndicationsDB[affiliatesIndicationsDB["Código promocional para reservas"]==str(row["Código promocional"]).split('.')[0]]["Porcentagem recebida por reserva indicada"].values[0]
            except IndexError:
                return 0

    ResDF["Valor_intermediario"] = ResDF.apply(create_values_row, axis=1)

    alreadyLoadedResDF = ResDF[ResDF["Referência"].isin(list(reservationCardsDB["Código reserva"]))]


    alterationsToPass = []
    newResToPass = []
    deleteResToPass = []

    newResQuery = """
        mutation($paramResCode: [UndefinedInput], $paramPropCode: [UndefinedInput], $paramResDate: [UndefinedInput],
                 $paramInDate: [UndefinedInput], $paramOutDate: [UndefinedInput], $paramGuestName: [UndefinedInput],
                 $paramPhone: [UndefinedInput], $paramLanguage: [UndefinedInput], $paramGuestNumber: [UndefinedInput], $paramPortal: [UndefinedInput],
                 $paramNewResMes: [UndefinedInput], $paramIntructions: [UndefinedInput],
                 $paramWAWeb: [UndefinedInput], $paramOutMes: [UndefinedInput], $paramStatus: [UndefinedInput],
                 $paramRegLink: [UndefinedInput], $paramRegInst: [UndefinedInput], $paramValue: [UndefinedInput], $paramCleanValue: [UndefinedInput], $paramPipeCode: ID!, $paramDueDate: DateTime){
          createCard(input:{
            pipe_id: $paramPipeCode
            due_date: $paramDueDate
            fields_attributes:[
              {field_id:"c_digo_reserva", field_value: $paramResCode}
              {field_id:"c_digo_propriedade", field_value: $paramPropCode}
              {field_id:"data_da_reserva", field_value: $paramResDate}
              {field_id:"data_check_in", field_value: $paramInDate}
              {field_id:"data_check_out_1", field_value: $paramOutDate}
              {field_id:"nome_h_spede", field_value: $paramGuestName}
              {field_id:"telefone_de_contato", field_value: $paramPhone}
              {field_id:"idioma", field_value: $paramLanguage}
              {field_id:"quantidade_de_pessoas", field_value: $paramGuestNumber}
              {field_id:"portal_da_reserva", field_value: $paramPortal}
              {field_id:"mensagem_nova_reserva", field_value: $paramNewResMes}
              {field_id:"mensagem_instru_es_check_in", field_value: $paramIntructions}
              {field_id:"link_whatsapp_web", field_value: $paramWAWeb}
              {field_id:"mensagem_de_check_out", field_value: $paramOutMes}
              {field_id:"status_reserva", field_value: $paramStatus}
              {field_id:"link_formul_rio_de_cadastro", field_value: $paramRegLink}
              {field_id:"como_realizar_cadastro_no_condom_nio", field_value: $paramRegInst}
              {field_id:"valor_da_reserva", field_value: $paramValue}
              {field_id:"valor_taxa_de_limpeza", field_value: $paramCleanValue}
            ]
          })
            {
        clientMutationId
            }
        }
        """
    

    alterResQuery = """
    mutation($paramResCode: [UndefinedInput], $paramPropCode: [UndefinedInput], $paramResDate: [UndefinedInput],
             $paramInDate: [UndefinedInput], $paramOutDate: [UndefinedInput], $paramGuestName: [UndefinedInput],
             $paramPhone: [UndefinedInput], $paramLanguage: [UndefinedInput], $paramGuestNumber: [UndefinedInput], $paramPortal: [UndefinedInput],
             $paramNewResMes: [UndefinedInput], $paramIntructions: [UndefinedInput],
             $paramWAWeb: [UndefinedInput], $paramOutMes: [UndefinedInput], $paramStatus: [UndefinedInput],
             $paramRegLink: [UndefinedInput], $paramRegInst: [UndefinedInput], $paramValue: [UndefinedInput], $paramCleanValue: [UndefinedInput], $paramCardCode: ID!, $paramDueDate: DateTime){
      A1: updateFieldsValues(input:{
        nodeId:$paramCardCode
        values: [
          {fieldId:"c_digo_reserva", value: $paramResCode, operation: REPLACE}
          {fieldId:"c_digo_propriedade", value: $paramPropCode, operation: REPLACE}
          {fieldId:"data_da_reserva", value: $paramResDate, operation: REPLACE}
          {fieldId:"data_check_in", value: $paramInDate, operation: REPLACE}
          {fieldId:"data_check_out_1", value: $paramOutDate, operation: REPLACE}
          {fieldId:"nome_h_spede", value: $paramGuestName, operation: REPLACE}
          {fieldId:"telefone_de_contato", value: $paramPhone, operation: REPLACE}
          {fieldId:"idioma", value: $paramLanguage, operation: REPLACE}
          {fieldId:"quantidade_de_pessoas", value: $paramGuestNumber, operation: REPLACE}
          {fieldId:"portal_da_reserva", value: $paramPortal, operation: REPLACE}
          {fieldId:"mensagem_nova_reserva", value: $paramNewResMes, operation: REPLACE}
          {fieldId:"mensagem_instru_es_check_in", value:$paramIntructions, operation: REPLACE}
          {fieldId:"link_whatsapp_web", value: $paramWAWeb, operation: REPLACE}
          {fieldId:"mensagem_de_check_out", value: $paramOutMes, operation: REPLACE}
          {fieldId:"status_reserva", value: $paramStatus, operation: REPLACE}
          {fieldId:"link_formul_rio_de_cadastro", value: $paramRegLink, operation: REPLACE}
          {fieldId:"como_realizar_cadastro_no_condom_nio", value: $paramRegInst, operation: REPLACE}
          {fieldId:"valor_da_reserva", value: $paramValue, operation: REPLACE}
          {fieldId:"valor_taxa_de_limpeza", value: $paramCleanValue, operation: REPLACE}
        ]
      }) {
        clientMutationId
      }
     A2: updateCard(input:{
       id: $paramCardCode
       due_date: $paramDueDate
     }) {
       clientMutationId
     }
    }
    """
    

    deleteCardQuery = """
    mutation($paramCardCode: ID!){
      deleteCard(input:{id: $paramCardCode}){
        clientMutationId
        success
      }
    }
    """
    

    for index, row in alreadyLoadedResDF.iterrows():

        print("++++++++++++++++++++++++++++++++++++++++++")
        print(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Valor taxa de limpeza"].values[0])
        print("++++++++++++++++++++++++++++++++++++++++++")

        form_link = "https://conteudo.anfitrioesdealuguel.com.br/cadastro-de-hospedes?cod-reserva={resCode}".format(resCode=row["Referência"])
        #form_link = "https://anfitrioesdealuguel.com.br/registro/?reservation-code={resCode}&property-code={propCode}".format(resCode=row["Referência"], propCode=row["Nome alojamento"])

        affiliateId = getResponsibleAffiliate(propertiesDBDF=propertiesDBDF, row=row)

        startMessage = str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["Mensagem inicial padrão"].values[0])
        startMessage = startMessage.format(guest_name=row["Cliente: Nome"],
                                           check_in_date=date2APIFormat(row["Data de check-in"]),
                                           link_register=form_link,)

        new_params = {"paramPipeCode" : str(affiliatesDBDF[affiliatesDBDF["id"]==affiliateId]["ID pipe recepção"].values[0]),
                  "paramDueDate" : date2APIFormat(str(row["Data de check-in"])) + "T15:00:00-03:00" if datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) <= datetime.datetime.strptime(date2APIFormat(str(row["Data de check-in"])), "%Y-%m-%d") else date2APIFormat(str(row["Data de check-out"])) + "T15:00:00-03:00",
                  "paramResCode" : nanHandling(row["Referência"]),
                  "paramPropCode" : nanHandling(row["Nome alojamento"]),
                  "paramResDate" : date2APIFormat(str(row["Data"])),
                  "paramInDate" : date2APIFormat(str(row["Data de check-in"])),
                  "paramOutDate" : date2APIFormat(str(row["Data de check-out"])),
                  "paramGuestName" : nanHandling(row["Cliente: Nome"]) + " " + nanHandling(row["Cliente: Sobrenomes"]),
                  "paramPhone" : nanHandling(row["Cliente: Telefone"]),
                  "paramLanguage" : nanHandling(row["Hóspede: Idioma do cliente"]),
                  "paramGuestNumber" : "{:.1f}".format(nanHandlingb(row["Adultos"])),
                  "paramPortal" : nanHandling(row["Portal"]),
                  "paramNewResMes" : startMessage,
                  "paramIntructions" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Instruções do check-in"].values[0]),
                  "paramWAWeb" : "https://wa.me/" + re.sub("[^0-9]", "", nanHandling(row["Cliente: Telefone"])),
                  "paramOutMes" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Instruções do check-out"].values[0]),
                  "paramStatus" : nanHandling(row["Estado"]),
                  "paramRegLink" : str(form_link),
                  "paramCardCode" : str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["id"].values[0]),
                  "paramRegInst" : nanHandling(propertiesDBDF[propertiesDBDF["Código da propriedade"]==row["Nome alojamento"]]["(*) Procedimento de cadastro no condomínio"].values[0]),
                  "paramValue" : "{:.2f}".format(nanHandlingb(row["Aluguer sem imposto"]) - nanHandlingb(row["Valor_intermediario"])),
                  "paramCleanValue" : "{:.2f}".format(nanHandlingb(row["Extras sem imposto"])),
                  }


        old_params = {"paramPipeCode" : nanHandling(pipePhasesDF[pipePhasesDF.isin([reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["current_phase_id"].values[0]]).any(axis=1)]["pipe_id"].values[0]),
                  "paramDueDate" : datetime.datetime.strptime(nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["due_date"].values[0].split("T")[0]), "%Y-%m-%d").strftime("%Y-%m-%d") + "T15:00:00-03:00" if not isNaN(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["due_date"].values[0]) else "",
                  "paramResCode" : nanHandling(row["Referência"]),
                  "paramPropCode" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Código propriedade"].values[0]),
                  "paramResDate" : date2APIFormat(str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Data da reserva"].values[0])),
                  "paramInDate" : date2APIFormat(str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Data Check-In"].values[0])),
                  "paramOutDate" : date2APIFormat(str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Data Check-out"].values[0])),
                  "paramGuestName" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Nome hóspede"].values[0]),
                  "paramPhone" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Telefone de contato"].values[0]),
                  "paramLanguage" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Idioma"].values[0]),
                  "paramGuestNumber" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Quantidade de pessoas"].values[0]),
                  "paramPortal" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Portal da reserva"].values[0]),
                  "paramNewResMes" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Mensagem nova reserva"].values[0]),
                  "paramIntructions" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Mensagem instruções check-in"].values[0]),
                  "paramWAWeb" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Link whatsapp web"].values[0]),
                  "paramOutMes" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Mensagem de check-out"].values[0]),
                  "paramStatus" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Status reserva"].values[0]),
                  "paramRegLink" : str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Link formulário de cadastro"].values[0]),
                  "paramCardCode" : str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["id"].values[0]),
                  "paramRegInst" : nanHandling(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Como realizar cadastro no condomínio?"].values[0]),
                  "paramValue" : "{:.2f}".format(nanHandlingb(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Valor da reserva"].values[0])),
                  "paramCleanValue" : "{:.2f}".format(nanHandlingb(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["Valor taxa de limpeza"].values[0])),
                  }

        for key in list(new_params.keys()):
            if old_params[key] != new_params[key]:

                if key == "paramPipeCode":
                    print(new_params["paramResCode"])
                    print(key)

                    if old_params[key]=="":
                        print("VAZIO")
                    else:
                        print(old_params[key])

                    print(new_params[key])
                    print("---")
                    deleteResToPass.append({"api_key" : affiliatesDBDF[affiliatesDBDF["id"]==reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["AffiliateId"].values[0]]["Chave pipefy"].values[0],
                                                  "params" : old_params})
                    break

                print(new_params["paramResCode"])
                print(key)

                if old_params[key]=="":
                    print("VAZIO")
                else:
                    print(old_params[key])

                print(new_params[key])
                print("---")
                alterationsToPass.append({"api_key" : affiliatesDBDF[affiliatesDBDF["id"]==reservationCardsDB[reservationCardsDB["Código reserva"]==row["Referência"]]["AffiliateId"].values[0]]["Chave pipefy"].values[0],
                                              "params" : new_params})

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    for chunk in divide_chunks(alterationsToPass, 200):

        makeAsyncApiCalls(chunk, alterResQuery)
        time.sleep(1)

    for chunk in divide_chunks(newResToPass, 200):

        makeAsyncApiCalls(chunk, newResQuery)
        time.sleep(1)

    for chunk in divide_chunks(deleteResToPass, 200):

        makeAsyncApiCalls(chunk, deleteCardQuery)
        time.sleep(1)


if __name__ == "__main__":
    pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
    ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
    reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
    affiliatesIndicationsDB = pd.read_excel(config.INDICATION_AFFILIATESDB_LOCATION)
    addNewReservations(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, affiliatesIndicationsDB=affiliatesIndicationsDB)
    print("New Reservations Done")
    modifyReservationsWithChanges(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, pipePhasesDF=pipePhasesDF, affiliatesIndicationsDB=affiliatesIndicationsDB)
    print("Alter Reservations Done")
    CollectAllReservationCards(affiliatesDBDF)
    print("Update Reservation Cards DB Done")
