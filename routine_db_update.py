import config
from config import makeAsyncApiCalls

import pull_main_dbs
import pull_agg_dbs
import push_affiliate_dbs
import save_dbs_backups

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

#pull main dbs
pull_main_dbs.pullAllDbsPipefy_main(config.token_main)

#pull agg dbs
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
pull_agg_dbs.getPipePhasesIds(affiliatesDBDF=affiliatesDBDF)
print("Pipephases Done")
pull_agg_dbs.getAffiliatesPropertiesDB(affiliatesDBDF=affiliatesDBDF)
print("Affiliates DBs Done")

#update afiliate dbs
affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
push_affiliate_dbs.pushNewPropertiesToAffiliatesPropertiesDB(affiliatePropertiesDBDF = affiliatePropertiesDBDF, propertiesDBDF = propertiesDBDF, affiliatesDBDF = affiliatesDBDF, ownersDBDF = ownersDBDF)
print("push dbs done")

#backup
ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
save_dbs_backups.backupAllDbFiles(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, ownersDBDF=ownersDBDF, affiliatePropertiesDBDF=affiliatePropertiesDBDF, pipePhasesDF=pipePhasesDF)
