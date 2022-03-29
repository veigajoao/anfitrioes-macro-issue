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

def backupAllDbFiles(reservationCardsDB, affiliatesDBDF, propertiesDBDF, ownersDBDF, affiliatePropertiesDBDF, pipePhasesDF):
    reservationCardsDB.to_excel(config.RESERVATIONCARDS_BACKUP_FOLDER + "/bdCardsReservas" + "-" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".xlsx")
    affiliatesDBDF.to_excel(config.AFFILIATESDB_BACKUP_FOLDER + "/bdAfiliados" + "-" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".xlsx")
    propertiesDBDF.to_excel(config.MAIN_PROPERTIESDB_BACKUP_FOLDER + "/bdPropriedades" + "-" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".xlsx")
    ownersDBDF.to_excel(config.MAIN_OWNERSDB_BACKUP_FOLDER + "/bdProprietários" + "-" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".xlsx")
    affiliatePropertiesDBDF.to_excel(config.AFFILIATES_PROPERTYDB_BACKUP_FOLDER + "/bdPropriedadesAfiliados" + "-" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".xlsx")
    pipePhasesDF.to_excel(config.PIPEPHASESDB_BACKUP_FOLDER + "/bdPipePhases" + "-" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".xlsx")


if __name__ == "__main__":
    ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
    reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
    ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
    affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
    pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
    backupAllDbFiles(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, ownersDBDF=ownersDBDF, affiliatePropertiesDBDF=affiliatePropertiesDBDF, pipePhasesDF=pipePhasesDF)
