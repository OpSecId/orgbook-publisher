import app.models.untp as untp

UNTP_CONTEXTS = {
    'DigitalConformityCredential': 'https://test.uncefact.org/vocabulary/untp/dcc/0/untp-dcc-context-0.3.10.jsonld'
}

class DigitalConformityCredential:
    
    def __init__(self):
        self.context = 'https://test.uncefact.org/vocabulary/untp/dcc/0/untp-dcc-context-0.3.10.jsonld'
        self.type = 'DigitalConformityCredential'
        
    def vc_to_dcc(self, credential, credential_registration, entity):
        credential['@context'].append(self.context)
        credential['type'].append(self.type)
        # credential['credentialSubject'] = {
        #     'type': ['ConformityAttestation'],
        #     'issuedToParty': untp.Entity(
        #         id=entity['id'],
        #         name=entity['name'],
        #         registeredId=entity['registrationNumber']
        #     ).model_dump(),
        # }
        credential['credentialSubject'] = untp.ConformityAttestation(
            issuedToParty=untp.Entity(
                id=entity['id'],
                name=entity['name'],
                registeredId=entity['registrationNumber']
            )
        ).model_dump()
        return credential
        
    def add_subject_party(self, entity_id):
        self.credential['credentialSubject']['issuedTo'] = {'id': entity_id}
        
    def add_assessment(self, credential, assessment):
        credential['credentialSubject']['assessments'] = [assessment]
        return credential