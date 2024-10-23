from pyld import jsonld
import json

CONTEXT_DIR = "app/contexts/"

CACHED_CONTEXTS = {
    "https://test.uncefact.org/vocabulary/untp/dcc/0.4.2/": "untp_dcc_0.4.2",
    "https://www.w3.org/ns/credentials/v2": "credentials_v2",
    "https://www.w3.org/ns/credentials/examples/v2": "credentials_examples_v2",
}


class LinkedData:
    def __init__(self):
        pass

    def load_cached_ctx(self, context_url):
        with open(f"{CONTEXT_DIR}{CACHED_CONTEXTS[context_url]}.jsonld", "r") as f:
            context = json.loads(f.read())
        return context

    def is_valid_context(self, context):
        if isinstance(context, list):
            for idx, ctx_entry in enumerate(context):
                if isinstance(ctx_entry, str):
                    if ctx_entry in CACHED_CONTEXTS:
                        context[idx] = self.load_cached_ctx(ctx_entry)
        elif isinstance(context, str):
            if context in CACHED_CONTEXTS:
                context = self.load_cached_ctx(context)
        jsonld.compact({}, context)
        try:
            jsonld.compact({}, context)
            return True
        except:
            return False
