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


#pull pipesDB
def getPipePhasesIds(affiliatesDBDF):

    def processJsonDB(data_blob):
        listItems = data_blob["pipe"]["phases"]
        func_df = pd.DataFrame()
        _buildDict = {}
        _buildDict["pipe_id"] = data_blob["pipe"]["id"]
        for phase in listItems:
            _buildDict[phase["name"]] = phase["id"]

        _df = pd.DataFrame(_buildDict, index=[0])
        return func_df.append(_df)

    phasesQuery = """
    query($paramPipeId: ID!){
        pipe(id: $paramPipeId) {
            id
            phases {
                id
                name
                    }
                }
            }
    """
    

    requestsToProcess = []
    for index, row in affiliatesDBDF.iterrows():
        params = {"paramPipeId" : row["ID pipe recepção"]}
        dictToProcess = {"params" : params, "api_key" : row["Chave pipefy"]}
        requestsToProcess.append(dictToProcess)

    responses = makeAsyncApiCalls(requestsToProcess, phasesQuery)

    pipePhasesDF = pd.DataFrame()
    for response in responses:
        pipePhasesDF = pipePhasesDF.append(processJsonDB(response[0]))

    pipePhasesDF.to_excel("files/bdPipePhases.xlsx")


#pull propertiesDB
def getAffiliatesPropertiesDB(affiliatesDBDF):
    affiliatePropertiesDB = pd.DataFrame()
    DBsToSearch = affiliatesDBDF[affiliatesDBDF["Chave pipefy"].notna()]
    DBsToSearch = DBsToSearch[DBsToSearch["ID BD propriedades"].notna()]
    DBsToSearchList = []
    for index, row in DBsToSearch.iterrows():
        DBsToSearchList.append({"id" : row["id"],
                                "api_key" : row["Chave pipefy"],
                                "db_key" : row["ID BD propriedades"]})

    #converto to IO async code
    def processJsonDB(data_blob, affiliateId):
        listItems = data_blob["table_records"]["edges"]
        func_df = pd.DataFrame()
        for edge in listItems:
            _buildDict = {}
            _buildDict["id"] = edge["node"]["id"]
            for field in edge["node"]["record_fields"]:
                _buildDict[field["name"]] = field["value"]

            _df = pd.DataFrame(_buildDict, index=[0])
            func_df = func_df.append(_df)
        func_df["AffiliateId"] = affiliateId
        return func_df


    for item in DBsToSearchList:

        headers = {
                "Authorization": "Bearer {}".format(item["api_key"]),
                "Content-Type": "application/json"
                      }

        hasNextPage = 0
        endCursor = 0

        while True:

            if endCursor == 0:
                params = {"paramTable" : item["db_key"]}
                data_base_query = """
                    query ($paramTable: ID!){
                      table_records(table_id: $paramTable,first:50) {
                        pageInfo {
                          hasNextPage
                          endCursor
                        }
                        edges {
                          node {
                            id
                            record_fields {
                              indexName
                              name
                              value
                            }
                          }
                        }
                      }
                    }
                    """
                    
            else:
                params = {"paramTable" : item["db_key"],
                              "paramAfter" : endCursor}
                data_base_query = """
                    query ($paramTable: ID!, $paramAfter: String!){
                      table_records(table_id: $paramTable,first:50, after: $paramAfter) {
                        pageInfo {
                          hasNextPage
                          endCursor
                        }
                        edges {
                          node {
                            id
                            record_fields {
                              indexName
                              name
                              value
                            }
                          }
                        }
                      }
                    }
                    """
                    

            
            db_data = requests.request("POST", "https://api.pipefy.com/graphql", json={"query": data_base_query, "variables": params}, headers=headers)
            db_data = json.loads(db_data.text)["data"]
            db_dataDF = processJsonDB(data_blob=db_data, affiliateId=item["id"])
            affiliatePropertiesDB = affiliatePropertiesDB.append(db_dataDF)

            hasNextPage = db_data["table_records"]["pageInfo"]["hasNextPage"]
            endCursor = db_data["table_records"]["pageInfo"]["endCursor"]

            if hasNextPage != True:
                break


    affiliatePropertiesDB.to_excel("files/bdPropriedadesAfiliados.xlsx")


#pull cardsDB
def CollectAllReservationCards(affiliatesDBDF):
    reservationCardsDB = pd.DataFrame()
    pipesToSearch = affiliatesDBDF[affiliatesDBDF["Chave pipefy"].notna()]
    pipesToSearch = pipesToSearch[pipesToSearch["ID pipe recepção"].notna()]
    pipesToSearchList = []
    for index, row in pipesToSearch.iterrows():
        pipesToSearchList.append({"id" : row["id"],
                                  "api_key" : row["Chave pipefy"],
                                  "pipe_key" : row["ID pipe recepção"]})

    #converto to IO async code
    def processJsonPipe(data_blob, affiliateId):
            listItems = data_blob["allCards"]["edges"]
            func_df = pd.DataFrame()
            for edge in listItems:
                _buildDict = {}
                _buildDict["id"] = edge["node"]["id"]
                _buildDict["due_date"]= edge["node"]["due_date"]
                _buildDict["current_phase_id"]= edge["node"]["current_phase"]["id"]
                for field in edge["node"]["fields"]:
                    _buildDict[field["name"]] = field["value"]

                _df = pd.DataFrame(_buildDict, index=[0])
                func_df = func_df.append(_df)
            func_df["AffiliateId"] = affiliateId
            return func_df

    for item in pipesToSearchList:

        headers = {
                "Authorization": "Bearer {}".format(item["api_key"]),
                "Content-Type": "application/json"
                      }

        hasNextPage = 0
        endCursor = 0

        while True:
            if endCursor == 0:
                params = {"paramPipe" : item["pipe_key"]}
                data_base_query = """
                    query ($paramPipe: ID!){
                      allCards(pipeId: $paramPipe, first:50){
                        pageInfo {
                          hasNextPage
                          endCursor
                        }
                        edges {
                          node {
                          due_date
                            id
                            fields {
                              indexName
                              name
                              value
                            }
                            current_phase{
                              id
                              name
                            }
                          }
                        }
                      }
                    }
                    """
                    
            else:
                params = {"paramPipe" : item["pipe_key"],
                              "paramAfter" : endCursor}
                data_base_query = """
                    query ($paramPipe: ID!, $paramAfter: String!){
                      allCards(pipeId: $paramPipe, first:50, after: $paramAfter){
                        pageInfo {
                          hasNextPage
                          endCursor
                        }
                        edges {
                          node {
                            due_date
                            id
                            fields {
                              indexName
                              name
                              value
                            }
                            current_phase{
                              id
                              name
                            }
                          }
                        }
                      }
                    }
                    """
                    

            pipe_data = requests.request("POST", "https://api.pipefy.com/graphql", json={"query": data_base_query, "variables": params}, headers=headers)
            pipe_data = json.loads(pipe_data.text)["data"]
            pipe_dataDF = processJsonPipe(data_blob=pipe_data, affiliateId=item["id"])

            reservationCardsDB = reservationCardsDB.append(pipe_dataDF)

            hasNextPage = pipe_data["allCards"]["pageInfo"]["hasNextPage"]
            endCursor = pipe_data["allCards"]["pageInfo"]["endCursor"]

            if hasNextPage != True:
                break

    reservationCardsDB.to_excel("files/bdCardsReservas.xlsx")

if __name__ == "__main__":
    affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
    getPipePhasesIds(affiliatesDBDF=affiliatesDBDF)
    print("Pipephases Done")
    getAffiliatesPropertiesDB(affiliatesDBDF=affiliatesDBDF)
    print("Affiliates DBs Done")
    CollectAllReservationCards(affiliatesDBDF=affiliatesDBDF)
    print("ReservationCards Done")