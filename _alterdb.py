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

propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)

alterTableRecordQuery = GQL(
"""
mutation($paramId: ID!){
  setTableRecordFieldValue(input:{
    table_record_id: $paramId
    field_id: "afiliado_respons_vel"
    value: "406710545"
  }) {
    clientMutationId
  }
}
"""
)

alterationsToPass = []
for index, row in propertiesDBDF.iterrows():
    params = {"paramId" : row["id"]}
    api_key = config.token_main
    alterationsToPass.append({"params" : params, "api_key" : api_key})

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

for chunk in divide_chunks(alterationsToPass, 100):

    asyncio.run(makeAsyncApiCalls(chunk, alterTableRecordQuery))
    time.sleep(1)
