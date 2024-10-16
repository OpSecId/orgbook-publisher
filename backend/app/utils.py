import uuid
import base64
from datetime import datetime, timezone, timedelta
import validators
import re
from fastapi import HTTPException

def valid_datetime_string(datetime_string):
    try:
        datetime.fromisoformat(datetime_string)
        return True
    except:
        return False
    
def valid_uri(value):
    DID_REGEX = re.compile("did:([a-z0-9]+):((?:[a-zA-Z0-9._%-]*:)*[a-zA-Z0-9._%-]+)")
    if DID_REGEX.match(value) or validators.url(value):
        return True
    return False
    
def check_validity_period(credential):
    if 'validFrom' in credential and 'validUntil' in credential:
        start = datetime.fromisoformat(credential['validFrom'])
        end = datetime.fromisoformat(credential['validUntil'])
        if start > end:
            raise HTTPException(status_code=400, detail="Bad validity period.")
    return False
    

def id_from_string(string):
    return f'urn:uuid:{str(uuid.uuid5(uuid.NAMESPACE_DNS, string))}'

def b64_encode(message):
    return base64.urlsafe_b64encode(message).decode().rstrip("=")

def datetime_range(days=None, minutes=None):
    start = datetime.now(timezone.utc).isoformat('T', 'seconds')
    if days:
        end = (datetime.now(timezone.utc)+ timedelta(days=days)).isoformat('T', 'seconds')
    elif minutes:
        end = (datetime.now(timezone.utc)+ timedelta(minutes=minutes)).isoformat('T', 'seconds')
    return start, end