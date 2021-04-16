from typing import List
import logging
import os

from azure.common import AzureConflictHttpError

import azure.functions
import azure.functions as func
from azure.storage.queue import QueueService

from ..shared_code import SensorDataPoint


def main(events: List[func.EventHubEvent], msg: func.Out[str], context: azure.functions.Context):
    if len(events) == 0:
        logging.info("No events?")
    else:
        logging.info("RECEIVED {} events for {}".format(len(events), context.invocation_id))
    #
    connection_string = os.environ["AzureStorageQueuesConnectionString"]
    queue_name = os.environ["AzureStorageQueueName"]
    qs = QueueService(connection_string=connection_string, is_emulated=True)
    logging.info("Conn String: {} \n Queue Name: {}".format(connection_string, queue_name))
    # if not qs.exists(queue_name=queue_name):
    try:
        qs.create_queue(queue_name=queue_name, fail_on_exist=True)
    except AzureConflictHttpError:
        logging.info("EXISTS")
    except KeyError as k:
        logging.info("Key does not exist, {}".format(str(k)))

    # else:
    #     logging.info("QUEUE EXISTS")

    for i in range(len(events)):
        # Decode IoT Hub message for entry into the Queue Storage
        event = events[i]
        decoded_message = event.get_body().decode('utf-8')

        # Add raw JSON to Queue Storage
        msg.set(decoded_message)

        # Log results to console
        logging.info("Event #{}: {}".format(i + 1, decoded_message))
