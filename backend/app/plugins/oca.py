from jsonpath_ng import jsonpath, parse
from fastapi.templating import Jinja2Templates


class OCAReader:
    def __init__(self):
        self.templates = Jinja2Templates(directory="app/templates")

    def load_template(self, name):
        with open(f"app/static/templates/{name}.html", "r") as f:
            template = f.read()
        return template

    def get_overlay(self, bundle, overlay_type):
        return next(
            (
                overlay
                for overlay in bundle["overlays"]
                if overlay["type"] == overlay_type
            ),
            None,
        )

    def render(self, document, bundle):
        pass

    def create_context(self, document, bundle):
        information_overlay = self.get_overlay(bundle, "spec/overlays/information/1.0")
        labels_overlay = self.get_overlay(bundle, "spec/overlays/label/1.0")
        paths_overlay = self.get_overlay(bundle, "vc/overlays/paths/1.0")
        render_overlay = self.get_overlay(bundle, "vc/overlays/render/1.0")
        branding_overlay = self.get_overlay(bundle, "aries/overlays/branding/1.0")
        meta_overlay = self.get_overlay(bundle, "spec/overlays/meta/1.0")
        
        
        values = {}
        for attribute in paths_overlay["attribute_paths"]:
            jsonpath_expr = parse(paths_overlay["attribute_paths"][attribute])
            values[attribute] = [match.value for match in jsonpath_expr.find(document)][
                0
            ]

        return {
            "values": values,
            "labels": labels_overlay['attribute_labels'],
            "descriptions": information_overlay['attribute_information'],
            "groupings": render_overlay['attribute_groupings'],
            "meta": meta_overlay,
            "branding": branding_overlay,
        }
