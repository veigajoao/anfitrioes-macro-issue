import config
from config import makeAsyncApiCalls

import pull_main_dbs
import pull_agg_dbs
import push_form_data
import push_reservations
import push_affiliate_dbs
import push_reservation_moves
import delete_old_reservations
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

###
#update affiliates DBs
#pull main dbs

pull_main_dbs.pullAllDbsPipefy_main(config.token_main)
print("push main done")

#pull agg dbs
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
pull_agg_dbs.getPipePhasesIds(affiliatesDBDF=affiliatesDBDF)
print("Pipephases Done")
#pull_agg_dbs.getAffiliatesPropertiesDB(affiliatesDBDF=affiliatesDBDF)
print("Affiliates DBs Done")

#update afiliate dbs
affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
push_affiliate_dbs.pushNewPropertiesToAffiliatesPropertiesDB(affiliatePropertiesDBDF = affiliatePropertiesDBDF, propertiesDBDF = propertiesDBDF, affiliatesDBDF = affiliatesDBDF, ownersDBDF = ownersDBDF)
print("push dbs done")

'''
#backup
ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
save_dbs_backups.backupAllDbFiles(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, ownersDBDF=ownersDBDF, affiliatePropertiesDBDF=affiliatePropertiesDBDF, pipePhasesDF=pipePhasesDF)
'''
###

#pull main dbs
pull_main_dbs.pullAllDbsPipefy_main(config.token_main)
print("Main DBs Done")

#pull agg dbs
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
pull_agg_dbs.getPipePhasesIds(affiliatesDBDF=affiliatesDBDF)
print("Pipephases Done")
pull_agg_dbs.getAffiliatesPropertiesDB(affiliatesDBDF=affiliatesDBDF)
print("Affiliates DBs Done")
pull_agg_dbs.CollectAllReservationCards(affiliatesDBDF=affiliatesDBDF)
print("ReservationCards Done")

#push reservations
pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
ResDF.to_excel("teste-row.xlsx")
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
affiliatesIndicationsDB = pd.read_excel(config.INDICATION_AFFILIATESDB_LOCATION)
push_reservations.addNewReservations(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, affiliatesIndicationsDB=affiliatesIndicationsDB)
print("New Reservations Done")
push_reservations.modifyReservationsWithChanges(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, pipePhasesDF=pipePhasesDF, affiliatesIndicationsDB=affiliatesIndicationsDB)
print("Alter Reservations Done")
pull_agg_dbs.CollectAllReservationCards(affiliatesDBDF)
print("Update Reservation Cards DB Done")


#make reservation moves
ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
push_reservation_moves.moveCardsBetweenPhases(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, pipePhasesDF=pipePhasesDF)
print("Move cards Done")


#push form data
ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
#guestRegistrationDF = pd.read_csv(config.FORMS_SHEET_LOCATION)
guestRegistrationDF = pd.read_excel(config.FORMS_SHEET_LOCATION)
push_form_data.addGuestRegistrationInfo(ResDF=ResDF, reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, guestRegistrationDF=guestRegistrationDF)
print("Registration Data Done")

#delete old reservations
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
delete_old_reservations.deleteOldReservations(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF)
print("Cancel old reservations Done")

'''
#backup
ResDF = pd.read_csv(config.RESERVATIONS_SHEET_LOCATION, header=1)
reservationCardsDB = pd.read_excel(config.RESERVATIONCARDS_LOCATION)
affiliatesDBDF = pd.read_excel(config.AFFILIATESDB_LOCATION)
propertiesDBDF = pd.read_excel(config.MAIN_PROPERTIESDB_LOCATION)
ownersDBDF = pd.read_excel(config.MAIN_OWNERSDB_LOCATION)
affiliatePropertiesDBDF = pd.read_excel(config.AFFILIATES_PROPERTYDB_LOCATION)
pipePhasesDF = pd.read_excel(config.PIPEPHASESDB_LOCATION)
save_dbs_backups.backupAllDbFiles(reservationCardsDB=reservationCardsDB, affiliatesDBDF=affiliatesDBDF, propertiesDBDF=propertiesDBDF, ownersDBDF=ownersDBDF, affiliatePropertiesDBDF=affiliatePropertiesDBDF, pipePhasesDF=pipePhasesDF)
print("backup Done")
'''