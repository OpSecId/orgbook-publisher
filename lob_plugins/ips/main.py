from viewer import IPSView
import asyncio




if __name__ == "__main__":

    registration_number = 'A0131571'
    holder_name = 'PACIFIC CANBRIAM ENERGY LIMITED'
    # title_number = '62715'
    title_number = '754'
    title = asyncio.run(IPSView().get_title_info(holder_name, title_number))
    # title = asyncio.run(IPSView().get_title_info(holder_name, title_number))
    # title = asyncio.run(IPSView().get_title_info(holder_name, title_number))
    # title = asyncio.run(IPSView().get_title_info(holder_name, title_number))
    # title = asyncio.run(IPSView().get_title_info(holder_name, title_number))
    print(title)
# IPSView().get_holders(holder_name, title_number)
# await IPSView().get_holders()
# try:
# title = IPSView().get_title_info(holder_name, title_number)
# except:
#     pass
# credential['credentialSubject']['type'].append()
# credential['credentialSubject']['titleNumber'] = claims['titleNumber']
# credential['credentialSubject']['originType'] = claims['titleNumber']
# credential['credentialSubject']['originNumber'] = claims['titleNumber']
# credential['credentialSubject']['issuedToParty']['type'].append('TitleHolder')
# credential['credentialSubject']['issuedToParty']['interest'] = 100.000
# assessment = {
#     'type': ['ConformityAssessment', 'Petroleum&NaturalGasTitle'],
#     'assessedFacilities': [],
#     'assessedProducts': [],
# }
# credential = DigitalConformityCredential().add_assessment(credential, assessment)