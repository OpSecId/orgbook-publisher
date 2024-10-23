from jsonpath_ng import jsonpath, parse
from fastapi.templating import Jinja2Templates
import pystache
import segno

PNG_BUNDLE = {
    "capture_base": {
        "type": "",
        "attributes": {
            "titleType": "Text",
            "titleNumber": "Number",
            "originType": "Text",
            "originNumber": "Number",
            "caveats": "List[Text]",
        },
    },
    "overlays": [
        {
            "type": "vc/overlays/paths/1.0",
            "attribute_paths": {
                "titleType": "$.credentialSubject.titleType",
                "titleNumber": "$.credentialSubject.titleNumber",
                "originType": "$.credentialSubject.originType",
                "originNumber": "$.credentialSubject.originNumber",
                "caveats": "$.credentialSubject.caveats",
            },
        },
        {
            "type": "vc/overlays/render/1.0",
            "media_type": "text/html",
            "attribute_groupings": {
                "title": [
                    "titleType",
                    "titleNumber",
                    "originType",
                    "originNumber",
                    "caveats",
                ]
            },
            "render_template": "urn:bcgov:template:vc-card",
        },
        {
            "type": "aries/overlays/branding/1.0",
            "primary_attribute": "titleType",
            "secondary_attribute": "titleNumber",
            "image": "https://avatars.githubusercontent.com/u/916280",
            "name": "BC Petroleum and Natural Gas Title",
            "issuer": "Director of Petroleum Lands",
        },
    ],
}


class OCAReader:
    def __init__(self):
        self.templates = Jinja2Templates(directory="app/templates")

    def load_template(self, name):
        with open(f"app/static/templates/{name}.html", "r") as f:
            template = f.read()
        return template

    def render(self, document, bundle):
        bundle = PNG_BUNDLE
        values = {}
        paths_overlay = next(
            (
                overlay
                for overlay in bundle["overlays"]
                if overlay["type"] == "vc/overlays/paths/1.0"
            ),
            None,
        )
        for attribute in paths_overlay["attribute_paths"]:
            jsonpath_expr = parse(paths_overlay["attribute_paths"][attribute])
            values[attribute] = [match.value for match in jsonpath_expr.find(document)][
                0
            ]

        render_overlay = next(
            (
                overlay
                for overlay in bundle["overlays"]
                if overlay["type"] == "vc/overlays/render/1.0"
            ),
            None,
        )
        groupings = {}
        for grouping in render_overlay["attribute_groupings"]:
            groupings[grouping] = {}
            for attribute in values:
                if attribute in render_overlay["attribute_groupings"][grouping]:
                    groupings[grouping][attribute] = values[attribute]

        branding_overlay = next(
            (
                overlay
                for overlay in bundle["overlays"]
                if overlay["type"] == "vc/overlays/branding/1.0"
            ),
            None,
        )

        credential = {"name": branding_overlay["name"]}
        issuer = {
            "id": document["issuer"]["id"],
            "name": branding_overlay["issuer"],
            "image": branding_overlay["image"],
        }
        verified = True
        status = True
        qr_code = segno.make(document["id"])
        template = self.load_template(render_overlay["render_template"])
        context = {
            "groupings": groupings,
            "issuer": issuer,
            "credential": credential,
            "qrcode": qr_code,
            "verified": verified,
            "status": status,
        }
        # rendered = pystache.render(template, context)
        return pystache.render(template, context)
        return self.templates.TemplateResponse(
            request=request,
            name="base.jinja",
            context={
                "groupings": groupings,
                "issuer": issuer,
                "credential": credential,
                "qrcode": qr_code,
                "verified": verified,
                "status": status,
            },
        )
