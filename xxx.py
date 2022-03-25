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

deleteCardQuery = GQL(
"""
mutation($paramCardId: ID!){
  deleteCard(input:{id: $paramCardId}){
    clientMutationId
    success
  }
}
"""
)

inputDF = pd.read_excel("xxx.xlsx")

cardsToCancel = []
for index, row in inputDF.iterrows():
    params = {"paramCardId" : str(row["Código"])}
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDExODg1NzcsImVtYWlsIjoiZ2FicmllbC5hbGJpbm9AZ21haWwuY29tIiwiYXBwbGljYXRpb24iOjMwMDA5MTI3OX19.P4ddMFdHGI1xk1QCAzBpECFPHSAZ5Ud51YH4OfYAymZ9UoCPeIafXOxndH0QBLh27-d85mdQXgx45RxXTlkRfw"
    cardsToCancel.append({"params" : params, "api_key" : api_key})

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

for chunk in divide_chunks(cardsToCancel, 200):

    asyncio.run(makeAsyncApiCalls(chunk, deleteCardQuery))
    time.sleep(1)
