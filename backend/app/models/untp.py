from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl
# from .codes import EncryptionMethod, HashMethod

class BaseModel(BaseModel):
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

class IdentifierScheme(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#identifierscheme
    type: str = "IdentifierScheme"

    id: AnyUrl  # from vocabulary.uncefact.org/identifierSchemes
    name: str


class Entity(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#entity
    type: str = "Entity"

    id: str
    name: str
    registeredId: Optional[str] = None
    idScheme: Optional[IdentifierScheme] = None


class BinaryFile(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#binaryfile
    type: str = "BinaryFile"

    fileName: str
    fileType: str  # https://mimetype.io/all-types
    file: str  #Base64


class Link(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#link
    type: str = "Link"

    linkURL: AnyUrl
    linkName: str
    linkType: str  # drawn from a controlled vocabulary


class SecureLink(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#securelink
    type: str = "SecureLink"

    linkUrl: AnyUrl
    linkName: str
    linkType: str
    hashDigest: str
    # hashMethod: HashMethod
    # encryptionMethod: EncryptionMethod


class Measure(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#measure
    type: str = "Measure"

    value: float
    unit: str = Field(
        max_length="3")  # from https://vocabulary.uncefact.org/UnitMeasureCode


class Endorsement(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#endorsement
    type: str = "Endorsement"

    id: AnyUrl
    name: str
    trustmark: Optional[BinaryFile] = None
    issuingAuthority: Entity
    accreditationCertification: Optional[Link] = None
    

class Standard(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#standard
    type: str = "Standard"

    id: AnyUrl
    name: str
    issuingParty: Entity
    issueDate: str  #iso8601 datetime string


class Regulation(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#regulation
    type: str = "Regulation"

    id: AnyUrl
    name: str
    jurisdictionCountry: str  #countryCode from https://vocabulary.uncefact.org/CountryId
    administeredBy: Entity
    effectiveDate: str  #iso8601 datetime string


class Metric(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#metric
    type: str = "Metric"

    metricName: str
    metricValue: Measure
    accuracy: float


class Criterion(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#criterion
    type: str = "Criterion"

    id: AnyUrl
    name: str
    thresholdValues: Metric


class Facility(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#facility
    type: str = "Facility"

    # this looks wrongs
    id: AnyUrl  # The globally unique ID of the entity as a resolvable URL according to ISO 18975.
    name: str
    registeredId: Optional[str] = None
    idScheme: Optional[IdentifierScheme] = None
    IDverifiedByCAB: bool


class Product(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#product
    type: str = "Product"

    id: AnyUrl  # The globally unique ID of the entity as a resolvable URL according to ISO 18975.
    name: str
    registeredId: Optional[str] = None
    idScheme: Optional[IdentifierScheme] = None
    IDverifiedByCAB: bool


class ConformityAssessment(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#conformityassessment
    type: str = "ConformityAssessment"

    id: AnyUrl
    referenceStandard: Optional[Standard] = None  #defines the specification
    referenceRegulation: Optional[Regulation] = None  #defines the regulation
    assessmentCriterion: Optional[Criterion] = None  #defines the criteria
    declaredValues: Optional[List[Metric]] = None
    compliance: Optional[bool] = False
    # conformityTopic: ConformityTopicCode

    assessedProducts: Optional[List[Product]] = None
    assessedFacilities: Optional[List[Facility]] = None


class ConformityAssessmentScheme(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#conformityassessmentscheme
    type: str = "ConformityAssessmentScheme"

    id: str
    name: str
    issuingParty: Optional[Entity] = None
    issueDate: Optional[str] = None  #ISO8601 datetime string
    trustmark: Optional[BinaryFile] = None


class ConformityAttestation(BaseModel):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#ConformityAttestation
    type: list = ["ConformityAttestation"]
    # id: str
    # assessorLevel: Optional[AssessorLevelCode] = None
    # assessmentLevel: AssessmentLevelCode
    # attestationType: AttestationType
    attestationDescription: Optional[str] = None  #missing from context file
    issuedToParty: Entity
    authorisations: Optional[Endorsement] = None
    conformityCertificate: Optional[SecureLink] = None
    auditableEvidence: Optional[SecureLink] = None
    # scope: ConformityAssessmentScheme
    assessments: List[ConformityAssessment] = None
    

class AssessorLevelCode(str, Enum):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#assessorLevelCode
    Self = "Self"
    Commercial = "Commercial"
    Buyer = "Buyer"
    Membership = "Membership"
    Unspecified = "Unspecified"
    ThirdParty = "3rdParty"


class AssessmentLevelCode(str, Enum):
    #https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#assessmentlevelcode
    GovtApproval = "GovtApproval"
    GlobalMLA = "GlobalMLA"
    Accredited = "Accredited"
    Verified = "Verified"
    Validated = "Validated"
    Unspecified = "Unspecified"


class AttestationType(str, Enum):
    # https://uncefact.github.io/spec-untp/docs/specification/ConformityCredential/#attestationtype
    Certification = "Certification"
    Declaration = "Declaration"
    Inspection = "Inspection"
    Testing = "Testing"
    Verification = "Verification"
    Validation = "Validation"
    Calibration = "Calibration"


class HashMethod(str, Enum):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#hashmethodcode
    SHA256 = "SHA-256"
    SHA1 = "SHA-1"


class EncryptionMethod(str, Enum):
    NONE = "None"
    AES = "AES"


class ConformityTopicCode(str, Enum):
    # https://jargon.sh/user/unece/ConformityCredential/v/0.3.10/artefacts/readme/render#conformityTopicCode
    Environment_Energy = "Environment.Energy"
    Environment_Emissions = "Environment.Emissions"
    Environment_Water = "Environment.Water"
    Environment_Waste = "Environment.Waste"
    Environment_Deforestation = "Environment.Deforestation"
    Environment_Biodiversity = "Environment.Biodiversity"
    Cirularity_Content = "Circularity.Content"
    Cirularity_Design = "Circularity.Design"
    Social_Labour = "Social.Labour"
    Social_Rights = "Social.Rights"
    Social_Safety = "Social.Safety"
    Social_Community = "Social.Community"
    Governance_Ethics = "Governance.Ethics"
    Governance_Compliance = "Governance.Compliance"
    Governance_Transparency = "Governance.Transparency"