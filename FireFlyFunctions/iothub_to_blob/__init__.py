from typing import List
import logging

import azure.functions
import azure.functions as func


def main(events: List[func.EventHubEvent], context: azure.functions.Context) -> func.HttpResponse:
    logging.info("RECEIVED {} events for {}".format(len(events), context.invocation_id))
    for i in range(len(events)):
        event = events[i]
        logging.info("Event #{}: {}".format(i+1, event.get_body().__str__()))
    if len(events) > 0:
        return func.HttpResponse("SUCCESS", status_code=200)
    return func.HttpResponse("FAILURE", status_code=400)
