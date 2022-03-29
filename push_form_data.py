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



def addGuestRegistrationInfo(ResDF, reservationCardsDB, affiliatesDBDF, propertiesDBDF, guestRegistrationDF):

    AlterResDF = reservationCardsDB[reservationCardsDB["Nome hóspede"].isna()]

    guestRegistrationDF = guestRegistrationDF[guestRegistrationDF["Código reserva"].isin(AlterResDF["Código reserva"])]

    def date2APIFormat(date_val):
        return date_val[-4:] + "-" + date_val[3:5] + "-" + date_val[0:2]

    def nanHandling(val):
        if val != val:
            return ""
        else:
            return str(val)

    formsToAdd = []

    for index, row in guestRegistrationDF.iterrows():

        print(row["Código reserva"])
        try:
            if datetime.datetime.strptime(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Código reserva"]]["Data Check-In"].values[0], "%d/%m/%Y") < datetime.datetime.now() - datetime.timedelta(days=30):
                continue
        except IndexError:
            continue


        api_key = str(affiliatesDBDF[affiliatesDBDF["id"]==reservationCardsDB[reservationCardsDB["Código reserva"]==row["Código reserva"]]["AffiliateId"].values[0]]["Chave pipefy"].values[0])
        # params = {"paramName" : nanHandling(row["Name"]) + " " + nanHandling(row["Surname"]),
        #               "paramPhone": nanHandling(row["Telefone"]),
        #       		  "paramAdress" : nanHandling(row["Address"]),
        #               "paramUF" : nanHandling(row["State"]),
        #       		  "paramCountry" : nanHandling(row["Country"]),
        #               "paramCEP" : nanHandling(row["Zip"]),
        #       		  "paramCPF" : nanHandling(row["Cpf"]),
        #               "paramDocument" : nanHandling(row["Rg"]),
        #       		  "paramProfession" : nanHandling(row["Job"]),
        #               "paramCar" : nanHandling(row["Car"]),
        #       		  "paramG1" : nanHandling(row["Guest1"]),
        #               "paramGD1" : nanHandling(row["Guestdata1"]),
        #         	  "paramG2" : nanHandling(row["Guest2"]),
        #               "paramGD2" : nanHandling(row["Guestdata2"]),
        #         	  "paramG3": nanHandling(row["Guest3"]),
        #               "paramGD3" : nanHandling(row["Guestdata3"]),
        #         	  "paramG4" : nanHandling(row["Guest4"]),
        #               "paramGD4" : nanHandling(row["Guestdata4"]),
        #         	  "paramG5" : nanHandling(row["Guest5"]),
        #               "paramGD5" : nanHandling(row["Guestdata5"]),
        #         	  "paramG6": nanHandling(row["Guest6"]),
        #               "paramGD6" : nanHandling(row["Guestdata6"]),
        #         	  "paramG7": nanHandling(row["Guest7"]),
        #               "paramGD7": nanHandling(row["Guestdata7"]),
        #         	  "paramG8": nanHandling(row["Guest8"]),
        #               "paramGD8": nanHandling(row["Guestdata8"]),
        #         	  "paramG9": nanHandling(row["Guest9"]),
        #               "paramGD9": nanHandling(row["Guestdata9"]),
        #         	  "paramG10": "",
        #               "paramGD10" : "",
        #       		  "paramCardCode" : str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Reservation Code"]]["id"].values[0]),
        #               }


        params = {"paramName" : nanHandling(row["Nome hóspede"]) + " " + nanHandling(row["Sobrenome hóspede"]),
                      "paramPhone": nanHandling(row["Celular"]),
              		  "paramAdress" : nanHandling(row["Endereço"]),
                      "paramUF" : nanHandling(row["Endereço"]), ##
              		  "paramCountry" : nanHandling(row["Endereço"]), ##
                      "paramCEP" : nanHandling(row["Endereço"]), ##
              		  "paramCPF" : nanHandling(row["CPF"]),
                      "paramDocument" : nanHandling(row["RG"]),
              		  "paramProfession" : nanHandling(row["Profissão"]),
                      "paramBirthDate" : nanHandling(row["Data nascimento"]),
                      "paramCar" : nanHandling(row["Modelo carros"]), ##
                      "paramCarPlate" : nanHandling(row["Placa carros"]), ##
              		  "paramG1" : nanHandling(row["Nome hóspede 1"]),
                      "paramGD1" : nanHandling(row["Documento hóspede 1"]),
                	  "paramG2" : nanHandling(row["Nome hóspede 2"]),
                      "paramGD2" : nanHandling(row["Documento hóspede 2"]),
                	  "paramG3": nanHandling(row["Nome hóspede 3"]),
                      "paramGD3" : nanHandling(row["Documento hóspede 3"]),
                	  "paramG4" : nanHandling(row["Nome hóspede 4"]),
                      "paramGD4" : nanHandling(row["Documento hóspede 4"]),
                	  "paramG5" : nanHandling(row["Nome hóspede 5"]),
                      "paramGD5" : nanHandling(row["Documento hóspede 5"]),
                	  "paramG6": nanHandling(row["Nome hóspede 6"]),
                      "paramGD6" : nanHandling(row["Documento hóspede 6"]),
                	  "paramG7": nanHandling(row["Nome hóspede 7"]),
                      "paramGD7": nanHandling(row["Documento hóspede 7"]),
                	  "paramG8": nanHandling(row["Nome hóspede 8"]),
                      "paramGD8": nanHandling(row["Documento hóspede 8"]),
                	  "paramG9": nanHandling(row["Nome hóspede 9"]),
                      "paramGD9": nanHandling(row["Documento hóspede 9"]),
                	  "paramG10": nanHandling(row["Nome hóspede 10"]),
                      "paramGD10" : nanHandling(row["Documento hóspede 10"]),
              		  "paramCardCode" : str(reservationCardsDB[reservationCardsDB["Código reserva"]==row["Código reserva"]]["id"].values[0]),
                      }

        formsToAdd.append({"api_key" : api_key,
                           "params" : params})

    updateRegFormQuery = """
    mutation($paramName: [UndefinedInput], $paramPhone: [UndefinedInput],
      			$paramAdress: [UndefinedInput],$paramUF: [UndefinedInput],
      			$paramCountry: [UndefinedInput],$paramCEP: [UndefinedInput],
      			$paramCPF: [UndefinedInput],$paramDocument: [UndefinedInput],
      			$paramProfession: [UndefinedInput],$paramCar: [UndefinedInput],
      			$paramG1: [UndefinedInput],$paramGD1: [UndefinedInput],
        		$paramG2: [UndefinedInput],$paramGD2: [UndefinedInput],
        		$paramG3: [UndefinedInput],$paramGD3: [UndefinedInput],
        		$paramG4: [UndefinedInput],$paramGD4: [UndefinedInput],
        		$paramG5: [UndefinedInput],$paramGD5: [UndefinedInput],
        		$paramG6: [UndefinedInput],$paramGD6: [UndefinedInput],
        		$paramG7: [UndefinedInput],$paramGD7: [UndefinedInput],
        		$paramG8: [UndefinedInput],$paramGD8: [UndefinedInput],
        		$paramG9: [UndefinedInput],$paramGD9: [UndefinedInput],
        		$paramG10: [UndefinedInput],$paramGD10: [UndefinedInput],
      			$paramCardCode: ID!){
      updateFieldsValues(input:{
        nodeId:$paramCardCode
        values: [
          {fieldId:"nome_completo_titular", value: $paramName, operation: REPLACE}
          {fieldId:"telefone_celular_titular", value: $paramPhone, operation: REPLACE}
          {fieldId:"endere_o_residencial", value: $paramAdress, operation: REPLACE}
          {fieldId:"estado_uf", value: $paramUF, operation: REPLACE}
          {fieldId:"pa_s", value: $paramCountry, operation: REPLACE}
          {fieldId:"cep", value: $paramCEP, operation: REPLACE}
          {fieldId:"cpf", value: $paramCPF, operation: REPLACE}
          {fieldId:"rg_ou_passaporte", value: $paramDocument, operation: REPLACE}
          {fieldId:"profiss_o", value: $paramProfession, operation: REPLACE}
          {fieldId:"modelo_e_placa_dos_carros", value: $paramCar, operation: REPLACE}
          {fieldId:"nome_acompanhante_1", value: $paramG1, operation: REPLACE}
          {fieldId:"cpf_acompanhante_1", value:$paramGD1, operation: REPLACE}
          {fieldId:"nome_acompanhante_2", value: $paramG2, operation: REPLACE}
          {fieldId:"cpf_acompanhante_2", value:$paramGD2, operation: REPLACE}
          {fieldId:"nome_acompanhante_3", value: $paramG3, operation: REPLACE}
          {fieldId:"cpf_acompanhante_3", value:$paramGD3, operation: REPLACE}
          {fieldId:"nome_acompanhante_4", value: $paramG4, operation: REPLACE}
          {fieldId:"cpf_acompanhante_4", value:$paramGD4, operation: REPLACE}
          {fieldId:"nome_acompanhante_5", value: $paramG5, operation: REPLACE}
          {fieldId:"cpf_acompanhante_5", value:$paramGD5, operation: REPLACE}
          {fieldId:"nome_acompanhante_6", value: $paramG6, operation: REPLACE}
          {fieldId:"cpf_acompanhante_6", value:$paramGD6, operation: REPLACE}
          {fieldId:"nome_acompanhante_7", value: $paramG7, operation: REPLACE}
          {fieldId:"cpf_acompanhante_7", value:$paramGD7, operation: REPLACE}
          {fieldId:"nome_acompanhante_8", value: $paramG8, operation: REPLACE}
          {fieldId:"cpf_acompanhante_8", value:$paramGD8, operation: REPLACE}
          {fieldId:"nome_acompanhante_9", value: $paramG9, operation: REPLACE}
          {fieldId:"cpf_acompanhante_9", value:$paramGD9, operation: REPLACE}
          {fieldId:"nome_acompanhante_10", value: $paramG10, operation: REPLACE}
          {fieldId:"cpf_acompanhante_10", value:$paramGD10, operation: REPLACE}

        ]
      }) {
        clientMutationId
      }
    }
    """
    

    def divide_chunks(l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    for chunk in divide_chunks(formsToAdd, 100):

        makeAsyncApiCalls(chunk, updateRegFormQuery)
        time.sleep(1)

if __name__ == "__main__":
    ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION)
    reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
    # guestRegistrationDF = pd.read_csv(config.FORMS_SHEET_LOCATION)
    guestRegistrationDF = pd.read_excel(config.FORMS_SHEET_LOCATION)
    addGuestRegistrationInfo(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, guestRegistrationDF=guestRegistrationDF)
    print("Registration Data Done")
    CollectAllReservationCards(affiliatesDBDF)
