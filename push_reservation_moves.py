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

def date2APIFormat(date_val):
    return date_val[-4:] + "-" + date_val[3:5] + "-" + date_val[0:2]


def moveCardsBetweenPhases(reservationCardsDB, affiliatesDBDF, propertiesDBDF, pipePhasesDF):

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    moveQuery = """
    mutation($paramCardId: ID!, $paramDestPhase: ID!){
        moveCardToPhase(input:{
            card_id: $paramCardId,
            destination_phase_id: $paramDestPhase
                }) {
            clientMutationId
                }
            }
    """
    


    #movereservations to check-in
    checkin_dates = list((datetime.date.today() - datetime.timedelta(days=x)).strftime("%d/%m/%Y") for x in range(2))
    CheckinDB = reservationCardsDB[reservationCardsDB["Data Check-In"].isin(checkin_dates)]
    CheckinDB = CheckinDB[~CheckinDB["current_phase_id"].isin(pipePhasesDF["Concluído"])]
    CheckinDB = CheckinDB[~CheckinDB["current_phase_id"].isin(pipePhasesDF["Reserva cancelada"])]
    CheckinDB = CheckinDB[~CheckinDB["current_phase_id"].isin(pipePhasesDF["Check-out"])]
    CheckinDB = CheckinDB[~CheckinDB["current_phase_id"].isin(pipePhasesDF["Hospedados"])]
    CheckinDB = CheckinDB[~CheckinDB["current_phase_id"].isin(pipePhasesDF["Check-in"])]

    CheckinDB = CheckinDB[CheckinDB["Status reserva"].isin(["Confirmada", "De proprietário"])]

    checkinMovesToMake = []
    for index, row in CheckinDB.iterrows():
        try:
            params = {"paramCardId" : str(row["id"]),
                    "paramDestPhase" : str(pipePhasesDF[pipePhasesDF["pipe_id"]==affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["ID pipe recepção"].values[0]]["Check-in"].values[0])}
            api_key = str(affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["Chave pipefy"].values[0])
            checkinMovesToMake.append({"params" : params, "api_key" : api_key})
        except Exception as E:
            print(E)
    for chunk in divide_chunks(checkinMovesToMake, 300):

        makeAsyncApiCalls(chunk, moveQuery)
        time.sleep(1)

    print("moves check-in OK")

    #reservations to precheckin
    precheckin_dates = list((datetime.date.today() + datetime.timedelta(days=x)).strftime("%d/%m/%Y") for x in range(1, 3))
    preCheckinDB = reservationCardsDB[reservationCardsDB["Data Check-In"].isin(precheckin_dates)]
    preCheckinDB = preCheckinDB[~preCheckinDB["current_phase_id"].isin(pipePhasesDF["Concluído"])]
    preCheckinDB = preCheckinDB[~preCheckinDB["current_phase_id"].isin(pipePhasesDF["Reserva cancelada"])]
    preCheckinDB = preCheckinDB[~preCheckinDB["current_phase_id"].isin(pipePhasesDF["Check-out"])]
    preCheckinDB = preCheckinDB[~preCheckinDB["current_phase_id"].isin(pipePhasesDF["Próximos check-ins (2 dias)"])]
    preCheckinDB = preCheckinDB[~preCheckinDB["current_phase_id"].isin(pipePhasesDF["Hospedados"])]
    preCheckinDB = preCheckinDB[~preCheckinDB["current_phase_id"].isin(pipePhasesDF["Check-in"])]

    preCheckinDB = preCheckinDB[preCheckinDB["Status reserva"].isin(["Confirmada", "De proprietário"])]

    preCheckinMovesToMake = []
    for index, row in preCheckinDB.iterrows():
        try:
            params = {"paramCardId" : str(row["id"]),
                    "paramDestPhase" : str(pipePhasesDF[pipePhasesDF["pipe_id"]==affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["ID pipe recepção"].values[0]]["Próximos check-ins (2 dias)"].values[0])}
            api_key = str(affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["Chave pipefy"].values[0])
            preCheckinMovesToMake.append({"params" : params, "api_key" : api_key})
        except Exception as E:
            print(E)

    for chunk in divide_chunks(preCheckinMovesToMake, 300):

        makeAsyncApiCalls(chunk, moveQuery)
        time.sleep(1)

    print("moves pre check-in OK")

    #reservations to checkout
    checkout_dates = list((datetime.date.today() + datetime.timedelta(days=x)).strftime("%d/%m/%Y") for x in range(1, 2))
    CheckoutDB = reservationCardsDB[reservationCardsDB["Data Check-out"].isin(checkout_dates)]
    CheckoutDB = CheckoutDB[~CheckoutDB["current_phase_id"].isin(pipePhasesDF["Concluído"])]
    CheckoutDB = CheckoutDB[~CheckoutDB["current_phase_id"].isin(pipePhasesDF["Reserva cancelada"])]
    CheckoutDB = CheckoutDB[~CheckoutDB["current_phase_id"].isin(pipePhasesDF["Check-out"])]
    CheckoutDB = CheckoutDB[CheckoutDB["Status reserva"].isin(["Confirmada", "De proprietário"])]

    CheckoutMovesToMake = []
    for index, row in CheckoutDB.iterrows():
        try:
            params = {"paramCardId" : str(row["id"]),
                    "paramDestPhase" : str(pipePhasesDF[pipePhasesDF["pipe_id"]==affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["ID pipe recepção"].values[0]]["Check-out"].values[0]),
                    }
            api_key = str(affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["Chave pipefy"].values[0])
            CheckoutMovesToMake.append({"params" : params, "api_key" : api_key})
        except Exception as E:
            print(E)

    for chunk in divide_chunks(CheckoutMovesToMake, 300):

        makeAsyncApiCalls(chunk, moveQuery)
        time.sleep(1)

    print("moves check-out OK")

    #reservations to cancelled - substituted for label in pipefy automation
    #CancelDB = reservationCardsDB[~reservationCardsDB["current_phase_id"].isin(pipePhasesDF["Concluído"])]
    #CancelDB = CancelDB[~CancelDB["current_phase_id"].isin(pipePhasesDF["Reserva cancelada"])]
    #CancelDB = CancelDB[~CancelDB["Status reserva"].isin(["Confirmada", "De proprietário"])]

    #CancelMovesToMake = []
    #for index, row in CancelDB.iterrows():
    #    params = {"paramCardId" : str(row["id"]),
    #              "paramDestPhase" : str(pipePhasesDF[pipePhasesDF["pipe_id"]==affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["ID pipe recepção"].values[0]]["Reserva cancelada"].values[0])}
    #    api_key = str(affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["Chave pipefy"].values[0])
    #    CancelMovesToMake.append({"params" : params, "api_key" : api_key})

    #for chunk in divide_chunks(CancelMovesToMake, 300):

    #    asyncio.run(makeAsyncApiCalls(chunk, moveQuery))
    #    time.sleep(1)

    #print("moves cancel OK")

if __name__ == "__main__":
    ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
    reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
    pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
    moveCardsBetweenPhases(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, pipePhasesDF=pipePhasesDF)
