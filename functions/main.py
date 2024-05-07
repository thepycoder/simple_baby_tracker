# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
from deona import read_from_deona

initialize_app()


@https_fn.on_request(region="europe-west1")
def update_from_deona(req: https_fn.Request) -> https_fn.Response:
    try:
        read_from_deona()
        return https_fn.Response("Done!")
    except Exception as e:
        return https_fn.Response(f"Error! {e}", status=400)
