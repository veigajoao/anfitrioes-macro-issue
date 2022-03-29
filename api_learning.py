import requests
import json
import config
import datetime
import asyncio
import aiohttp

import gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.aiohttp import AIOHTTPTransport
from gql import Client
from gql import gql as GQL

headers = {
        "Authorization": "Bearer {}".format(config.token_main),
        "Content-Type": "application/json"
              }
params = {"paramPipeId" : 301576419}
dictToProcess = {"params" : params, "api_key" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDExOTExMDMsImVtYWlsIjoiYm9yZ2VzbGF1cmFzaWx2YUBnbWFpbC5jb20iLCJhcHBsaWNhdGlvbiI6MzAwMDkxNjMzfX0.wvbgoodWt7kVRujFgbyCi6eMS6XVEZo2yoNhUEBa6VOTvBvYrSmUxMK2Kv3OI67mo7RbpOcxtD7nT5q7-lxNPw"}
        
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
    
lista_aux = [dictToProcess]
responses = config.makeAsyncApiCalls(lista_aux, phasesQuery)

print(responses)