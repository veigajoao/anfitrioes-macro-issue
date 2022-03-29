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



def deleteOldReservations(reservationCardsDB, affiliatesDBDF):
    deleteDates = ((datetime.date.today() - datetime.timedelta(days=x)).strftime("%d/%m/%Y") for x in range(30, 1800))
    reservationsToCancel = reservationCardsDB[reservationCardsDB["Data Check-out"].isin(deleteDates)]
    reservationsToCancel = reservationsToCancel[reservationsToCancel["Status reserva"].isin(["Confirmada", "De proprietário", "Cancelada"])]


    reservationsToCancel2 = reservationCardsDB[~reservationCardsDB["Status reserva"].isin(["Confirmada", "De proprietário", "Cancelada"])]

    reservationsToCancel = reservationsToCancel.append(reservationsToCancel2)

    deleteCardQuery = """
    mutation($paramCardId: ID!){
      deleteCard(input:{id: $paramCardId}){
        clientMutationId
        success
      }
    }
    """

    cardsToCancel = []
    for index, row in reservationsToCancel.iterrows():
        params = {"paramCardId" : str(row["id"])}
        api_key = str(affiliatesDBDF[affiliatesDBDF["id"]==row["AffiliateId"]]["Chave pipefy"].values[0])
        cardsToCancel.append({"params" : params, "api_key" : api_key})

    def divide_chunks(l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    for chunk in divide_chunks(cardsToCancel, 200):

        makeAsyncApiCalls(chunk, deleteCardQuery)
        time.sleep(1)




if __name__ == "__main__":
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
    deleteOldReservations(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF)
