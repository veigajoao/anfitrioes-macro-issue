import requests
import json

def query_location_api(countryRegion, adminDistrict, locality, postalCode, addressLine):
    BingMapsKey = "AglwJHxkLUadHQ3l5i9B1vjUz9pujSEi8DSfeiiZN6u7uyzfKdiJFF1ZGEiSj1iN"

    query_url = "https://dev.virtualearth.net/REST/v1/Locations"

    params = {"countryRegion" : countryRegion,
              "adminDistrict" : adminDistrict,
              "locality" : locality,
              "postalCode" : postalCode,
              "addressLine" : addressLine,
              "Key" : BingMapsKey,}

    response = requests.get(query_url, params=params)

    return response

#get location data for prospect
countryRegion = input("País (ISO 3166-1 alpha-2 - para brasil, escrever BR)")
adminDistrict = input("Estado - sigla de 2 dígitos")
locality = input("cidade")
postalCode = input("cep")
addressLine = input("Rua e número")

prospect_location = query_location_api(countryRegion=countryRegion, adminDistrict=adminDistrict, locality=locality, postalCode=postalCode, addressLine=addressLine)

prospect_json = prospect_location.json()['resourceSets'][0]['resources'][0]["geocodePoints"][0]["coordinates"]
wp1 = ",".join([str(item) for item in prospect_json])

print(wp1)

####
#dados do anfitrião
countryRegion = "BR"
adminDistrict = "SC"
locality = "florianopolis"
postalCode = "88080160"
addressLine = "355 avenida almirante tamandare"

host_location = query_location_api(countryRegion=countryRegion, adminDistrict=adminDistrict, locality=locality, postalCode=postalCode, addressLine=addressLine)

host_json = host_location.json()['resourceSets'][0]['resources'][0]["geocodePoints"][0]["coordinates"]
wp2 = ",".join([str(item) for item in host_json])
####

#evaluate distance
def calculate_dist(wp1, wp2):
    BingMapsKey = "AglwJHxkLUadHQ3l5i9B1vjUz9pujSEi8DSfeiiZN6u7uyzfKdiJFF1ZGEiSj1iN"
    query_url = "http://dev.virtualearth.net/REST/v1/Routes/Driving"

    params = {"wayPoint.1" : wp1,
              "waypoint.2" : wp2,
              "distanceUnit" : "Kilometer",
              "key" : BingMapsKey,}

    response = requests.get(query_url, params=params).json()

    distance = response["resourceSets"][0]['resources'][0]["travelDistance"]

    return distance

distance_response = calculate_dist(wp1=wp1, wp2=wp2)

print(distance_response)
print(type(distance_response))

#find closest affiliate - load db build new column with distance from prospect - select smallest distance
affiliates_db = pd.read_excel(config.AFFILIATESDB_LOCATION)

affiliates_db["distance_km"] = affiliates_db.apply(lambda row : calculate_dist(wp1=wp1, wp2=row["Coordenada central"]), axis=1)

index_min = affiliates_db[["distance_km"]].idxmin()

print(affiliates_db["Chave primária"].values[index_min])
print(affiliates_db["Nome Completo"].values[index_min])
print(affiliates_db["Endereço completo"].values[index_min])
print(affiliates_db["Razão social MEI ou PJ"].values[index_min])
