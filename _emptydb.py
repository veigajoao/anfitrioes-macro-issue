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

affiliatePropertiesDB = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)

deletetablerecordQuery = GQL(
"""
mutation($paramRecordId: ID!){
  deleteTableRecord(input: {id: $paramRecordId, clientMutationId: "xxx"}) {
    clientMutationId
    success
  }
}
"""
)

dataToDelete = []
for index, row in affiliatePropertiesDB.iterrows():
    api_key = config.token_main
    params = {"paramRecordId" : str(row["id"])}
    dataToDelete.append({"api_key" : api_key, "params" : params})

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

for chunk in divide_chunks(dataToDelete, 100):

    asyncio.run(makeAsyncApiCalls(chunk, deletetablerecordQuery))
    time.sleep(1)
