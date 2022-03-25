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
files_dir = os.getcwd() + "\\files"
backups_dir = os.getcwd() + "\\backup files"

#async function make multiple independent calls
call_count = 0
async def makeAsyncApiCalls(key_paramsDict, query):

    async def one_query(api_key, query_var, params):

        response_date = []
        headers = {
                "Authorization": "Bearer {}".format(api_key),
                "Content-Type": "application/json"
                }

        transport = AIOHTTPTransport(url="https://api.pipefy.com/graphql", headers=headers)

        global call_count
        call_count = call_count + 1
        if call_count == 300:
            time.sleep(50)
            call_count = 0
            print("break")

        while True:
            try:
                async with Client(
                    transport=transport, fetch_schema_from_transport=True,
                ) as session:

                    result = await session.execute(query_var, variable_values=params)
                    response_date.append(result)
                    return response_date
                    break

            except asyncio.TimeoutError:
                print("asyncio.TimeoutError")
                return None
                break

            except aiohttp.client_exceptions.ServerDisconnectedError:
                print("aiohttp.client_exceptions.ServerDisconnectedError")
                continue

            except aiohttp.client_exceptions.ClientOSError:
                print("aiohttp.client_exceptions.ClientOSError")
                continue

            except gql.transport.exceptions.TransportServerError:
                print("gql.transport.exceptions.TransportServerError")
                continue

            except RuntimeError:
                print("RuntimeError")
                continue

            except:
                print(key_paramsDict)
                print(query)
                raise Exception("Erro \n\n {} \n\n {}".format(key_paramsDict, query))


    coros = [one_query(api_key=_["api_key"], query_var=query, params=_["params"]) for _ in  key_paramsDict]
    return await asyncio.gather(*coros)

#build async function for continuous calls pull dbs

#Main company dbs from AdA pipefy
MAIN_PROPERTIESDB_LOCATION = files_dir + "\\bdPropriedades.xlsx"
MAIN_OWNERSDB_LOCATION = files_dir + "\\bdProprietários.xlsx"
AFFILIATESDB_LOCATION = files_dir + "\\bdAfiliados.xlsx"
INDICATION_AFFILIATESDB_LOCATION = files_dir + "\\bdAfiliadosIndicação.xlsx"

#Agregator dbs from all Affiliates
PIPEPHASESDB_LOCATION = files_dir + "\\bdPipePhases.xlsx"
RESERVATIONCARDS_LOCATION = files_dir + "\\bdCardsReservas.xlsx"
AFFILIATES_PROPERTYDB_LOCATION = files_dir + "\\bdPropriedadesAfiliados.xlsx"

#inputData
RESERVATIONS_SHEET_LOCATION = data_sources.UPDATE_RESERVATIONS_FOLDER + "\\reservas.csv"
#FORMS_SHEET_LOCATION = data_sources.UPDATE_RESERVATIONS_FOLDER + "\\forms.csv"
FORMS_SHEET_LOCATION = files_dir + "\\forms.xlsx"

#backup files
MAIN_PROPERTIESDB_BACKUP_FOLDER = backups_dir + "\\bdPropriedades"
MAIN_OWNERSDB_BACKUP_FOLDER = backups_dir + "\\bdProprietários"
AFFILIATESDB_BACKUP_FOLDER = backups_dir + "\\bdAfiliados"
PIPEPHASESDB_BACKUP_FOLDER = backups_dir + "\\bdPipePhases"
RESERVATIONCARDS_BACKUP_FOLDER = backups_dir + "\\bdCardsReservas"
AFFILIATES_PROPERTYDB_BACKUP_FOLDER = backups_dir + "\\bdPropriedadesAfiliados"

#main token
token_main = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDExMDcyODcsImVtYWlsIjoiai52ZWlnYUBhbmZpdHJpb2VzZGVhbHVndWVsLmNvbS5iciIsImFwcGxpY2F0aW9uIjozMDAxNDg1ODR9fQ.RnCORWfGc7hFA9Lwv-A6gGFGDffFxmxU-KGpwJWC28sZJ-YxKeVuV28z0bp-IxAHcXIB97KoAYHNps9O4lHbCg"

