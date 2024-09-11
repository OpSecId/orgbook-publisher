# from config import settings
# import oracledb

# DB_VIEWS = {
#     # shows all the titles that are flagged as public
#     "titles": "IPS_DIGITRUST_TITLE_VW",
#     # shows the owners of the public titles
#     "title_holders": "IPS_DIGITRUST_TITLE_CLIENT_OWNER_VW",
#     # shows the caveats of the public titles and non-deleted caveats
#     "caveats": "IPS_DIGITRUST_TITLE_CAVEAT_VW",
#     # shows the title tract of the public titles and non-deleted tracts
#     "tracts": "IPS_DIGITRUST_TITLE_TRACT_VW",
#     # show the title tract description of the public titles and non deleted tracts
#     "tracts_descriptions": "IPS_DIGITRUST_TITLE_TRACT_DESC_VW",
#     # shows the title tract notes of the public titles and non deleted tracts
#     "tracts_notes": "IPS_DIGITRUST_TITLE_TRACT_NOTE_VW",
#     # shows the title tract right of the public titles and non deleted tracts
#     "tracts_rights": "IPS_DIGITRUST_TITLE_TRACT_RIGHT_VW",
#     #
#     "wells": "IPS_DIGITRUST_TITLE_WELL_VW",
#     #
#     "wells_info": "IPS_DIGITRUST_TITLE_WELL_UWI_VW",
# }

# class IPSView:
#     def __init__(self):
#         self.user = settings.IPS_DB_USERNAME
#         self.password = settings.IPS_DB_PASSWORD
#         self.host = settings.IPS_DB_HOSTNAME
#         self.port = settings.IPS_DB_PORT
#         self.db = settings.IPS_DB_NAME
#         self.service = settings.IPS_DB_SERVICE_NAME

#     async def get_title_info(self, entity, title_no):
#         connection = oracledb.connect(
#             user=self.user,
#             password=self.password,
#             host=self.host,
#             port=self.port,
#             service_name=self.service,
#         )
#         self.cursor = connection.cursor()
#         title = await self.get_title(title_no)
#         title["holder"] = await self.get_holder(title_no, entity['name'])
#         title["caveats"] = await self.get_caveats(title_no)
#         title["tracts"] = await self.get_tracts(title_no)
#         title["wells"] = await self.get_wells(title_no)

#         return title

#     async def get_title(self, title_no):
#         self.cursor.execute(
#             f"select * from {DB_VIEWS['titles']} WHERE TITLE_NUMBER_ID='{title_no}'"
#         )
#         title_record = self.cursor.fetchall()[0]
#         title_record = {
#             "identifier": title_record[0],
#             "titleStatusCode": title_record[1],
#             "titleTypeCode": title_record[2],
#             "originTypeCode": title_record[3],
#             "originIdentifier": title_record[4],
#             "issueDate": title_record[5].isoformat() + "Z" if title_record[5] else None,
#             "term": title_record[6],
#             "effectiveDate": (
#                 title_record[7].isoformat() + "Z" if title_record[7] else None
#             ),
#             "areaInHectares": title_record[8],
#             "paidToDate": (
#                 title_record[9].isoformat() + "Z" if title_record[9] else None
#             ),
#             "expiryDate": (
#                 title_record[10].isoformat() + "Z" if title_record[10] else None
#             ),
#             "cancellationDate": (
#                 title_record[11].isoformat() + "Z" if title_record[11] else None
#             ),
#             "bonusPaid": title_record[12],
#             "dollarPerHa": title_record[13],
#             "feePaid": title_record[14],
#             "rentPaid": title_record[15],
#         }
#         return title_record

#     async def get_holder(self, title_no, holder_name):

#         self.cursor.execute(
#             f"select * from {DB_VIEWS['title_holders']} WHERE TITLE_NUMBER_ID='{title_no}' AND POPULATED_NAME='{holder_name}'"
#         )
#         holder_record = self.cursor.fetchall()[0]
#         holder = {
#             "identifier": holder_record[1],
#             "clientSupcd": holder_record[2],
#             "clientStatusInd": holder_record[3],
#             "populatedName": holder_record[4],
#             "percentageOwnership": holder_record[5],
#             "transferRecordedDate": (
#                 holder_record[6].isoformat() + "Z" if holder_record[6] else None
#             ),
#         }
#         return holder

#     async def get_caveats(self, title_no):
#         caveats = []

#         self.cursor.execute(
#             f"select * from {DB_VIEWS['caveats']} WHERE TITLE_NUMBER_ID='{title_no}'"
#         )
#         caveats_records = self.cursor.fetchall()
#         for caveat_record in caveats_records:
#             caveats.append(caveat_record[3])
#         return caveats

#     async def get_tracts(self, title_no):
#         tracts = []

#         self.cursor.execute(
#             f"select * from {DB_VIEWS['tracts']} WHERE TITLE_NUMBER_ID='{title_no}'"
#         )
#         tracts_records = self.cursor.fetchall()
#         for tract_record in tracts_records:
#             tract = {
#                 "identifier": tract_record[0],
#                 "gridUnits": tract_record[3],
#                 "tractDescriptions": [],
#                 "tractRights": [],
#             }

#             self.cursor.execute(
#                 f"select * from {DB_VIEWS['tracts_descriptions']} WHERE TITLE_TRACT_ID='{tract_record[0]}'"
#             )
#             tract_description_records = self.cursor.fetchall()
#             for tract_description_record in tract_description_records:
#                 tract_description = {
#                     "tractDescriptionOrder": tract_description_record[1],
#                     "landSys": tract_description_record[2],
#                     "lowLevelDesc": tract_description_record[3],
#                     "highLevelDesc": tract_description_record[4],
#                     "sortKey": tract_description_record[5],
#                 }
#                 tract["tractDescriptions"].append(tract_description)

#             self.cursor.execute(
#                 f"select * from {DB_VIEWS['tracts_rights']} WHERE TITLE_TRACT_ID='{tract_record[0]}'"
#             )
#             tract_rights_records = self.cursor.fetchall()
#             for tract_right_record in tract_rights_records:
#                 tract_right = {
#                     "tractRightOrder": tract_right_record[1],
#                     "geologicalFormationCode": tract_right_record[2],
#                     "standardZoneCode": tract_right_record[3],
#                     "strataZoneCode": tract_right_record[4],
#                     "tractRightCode": tract_right_record[5],
#                     "includeExcludeInd": tract_right_record[6],
#                     "description": tract_right_record[7],
#                     "nstdZoneLongDescription": tract_right_record[8],
#                 }
#                 tract["tractRights"].append(tract_right)

#             tracts.append(tract)
#         return tracts

#     async def get_wells(self, title_no):
#         wells = []

#         self.cursor.execute(
#             f"select * from {DB_VIEWS['wells']} WHERE TITLE_NUMBER_ID='{title_no}'"
#         )
#         wells_records = self.cursor.fetchall()
#         for well_record in wells_records:
#             well = {
#                 "identifier": well_record[0],
#                 "waNumber": well_record[2],
#                 "earningWell": well_record[3],
#                 "uwi": [],
#             }

#             self.cursor.execute(
#                 f"select * from {DB_VIEWS['wells_info']} WHERE TITLE_WELL_ID='{well_record[0]}'"
#             )
#             well_uwi_records = self.cursor.fetchall()
#             for well_uwi_record in well_uwi_records:
#                 uwi = {
#                     "uwi": well_uwi_record[0],
#                     "notInLocInd": well_uwi_record[2],
#                 }
#                 well["uwi"].append(uwi)
#             wells.append(well)
#         return wells