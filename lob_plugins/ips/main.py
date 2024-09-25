from . import IPSView

registration_number = ''
holder_name = ''
title_number = ''
title = IPSView().get_title_info(holder_name, title_number)
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