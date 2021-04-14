from typing import List
import logging

import azure.functions as func


def main(events: List[func.EventHubEvent]) -> func.HttpResponse:
    logging.info("RECEIVED")
    for event in events:
        logging.info('Python EventHub trigger processed an event: %s',
                     event.get_body().decode('utf-8'))
    if len(events) > 0:
        return func.HttpResponse("SUCCESS {}".format(events[0].get_body()), status_code=200)
    return func.HttpResponse("FAILURE", status_code=400)
