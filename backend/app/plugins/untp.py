

class DigitalConformityCredential:
    
    def __init__(self):
        self.context = 'https://test.uncefact.org/vocabulary/untp/dcc/0/untp-dcc-context-0.3.9.jsonld'
        self.type = 'DigitalConformityCredential'
        
    def vc_to_dcc(self, credential, entity):
        credential['@context'].append(self.context)
        credential['type'].append(self.type)
        credential['credentialSubject'] = {
            'type': ['ConformityAttestation'],
            'issuedTo': entity
        }
        return credential
        
    def add_subject_party(self, entity_id):
        self.credential['credentialSubject']['issuedTo'] = {'id': entity_id}
        
    def add_assessment(self, credential, assessment):
        credential['credentialSubject']['assessments'] = [assessment]
        return credential