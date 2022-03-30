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

def pullAllDbsPipefy_main(token):

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
              }

    client = "not used - to do - remove"
    def processJsonDB(data_blob):
        listItems = data_blob["table_records"]["edges"]
        func_df = pd.DataFrame()
        for edge in listItems:
            _buildDict = {}
            _buildDict["id"] = edge["node"]["id"]
            for field in edge["node"]["record_fields"]:
                _buildDict[field["name"]] = field["value"]

            _df = pd.DataFrame(_buildDict, index=[0])
            func_df = func_df.append(_df)
        return func_df

    def requestForLoop(endCursor, tableId, client):
        if endCursor == 0:
            params = {"paramTable" : tableId}
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
            params = {"paramTable" : tableId,
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
        database_data = json.loads(db_data.text)["data"]
        return {"data" : processJsonDB(database_data),
                "hasNextPage" : database_data["table_records"]["pageInfo"]["hasNextPage"],
                "endCursor" : database_data["table_records"]["pageInfo"]["endCursor"],
                }



    #propertiesDB
    dbCode = "eGzzx0JC"
    endCursor = 0
    propertiesDBDF = pd.DataFrame()
    while True:
        propertiesDBResult = requestForLoop(endCursor=endCursor, tableId=dbCode, client=client)
        endCursor = propertiesDBResult["endCursor"]
        propertiesDBDF = propertiesDBDF.append(propertiesDBResult["data"])
        if propertiesDBResult["hasNextPage"] == False:
            break

    propertiesDBDF.to_excel("files/bdPropriedades.xlsx")


    #propertiesDB
    dbCode = "D0gBzxEW"
    endCursor = 0
    ownersDBDF = pd.DataFrame()
    while True:
        ownersDBResult = requestForLoop(endCursor=endCursor, tableId=dbCode, client=client)
        endCursor = ownersDBResult["endCursor"]
        ownersDBDF = ownersDBDF.append(ownersDBResult["data"])
        if ownersDBResult["hasNextPage"] == False:
            break

    ownersDBDF.to_excel("files/bdProprietários.xlsx")

    #affiliatesDB
    dbCode = "cqd6OLsc"
    endCursor = 0
    affiliatesDBDF = pd.DataFrame()
    while True:
        affiliatesDBResult = requestForLoop(endCursor=endCursor, tableId=dbCode, client=client)
        endCursor = affiliatesDBResult["endCursor"]
        affiliatesDBDF = affiliatesDBDF.append(affiliatesDBResult["data"])
        if affiliatesDBResult["hasNextPage"] == False:
            break

    affiliatesDBDF.to_excel("files/bdAfiliados.xlsx")

    #indication affiliates DBDF
    dbCode = "WxIC2PJI"
    endCursor = 0
    indicationAffiliatesDBDF = pd.DataFrame()
    while True:
        indicationAffiliatesDBResult = requestForLoop(endCursor=endCursor, tableId=dbCode, client=client)
        endCursor = indicationAffiliatesDBResult["endCursor"]
        indicationAffiliatesDBDF = indicationAffiliatesDBDF.append(indicationAffiliatesDBResult["data"])
        if indicationAffiliatesDBResult["hasNextPage"] == False:
            break

    indicationAffiliatesDBDF.to_excel("files/bdAfiliadosIndicação.xlsx")

if __name__ == "__main__":
    pullAllDbsPipefy_main(config.token_main)