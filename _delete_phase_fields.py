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



def pullAllDbsPipefy_main(token):

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
              }

    transport = RequestsHTTPTransport(
        url="https://api.pipefy.com/graphql", verify=True, retries=3,
        headers=headers
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)


    query_get_phase_id
