import logging
import os
import sys
import textwrap

from pydicom.filewriter import write_file_meta_info
from pynetdicom import AE, AllStoragePresentationContexts, debug_logger
from pynetdicom.events import EVT_C_STORE


# Implement a handler for evt.EVT_C_STORE
def c_store_handle(event):
    with open(event.request.AffectedSOPInstanceUID, "wb") as f:
        # Write the preamble and prefix
        f.write(b"\x00" * 128)
        f.write(b"DICM")
        # Encode and write the File Meta Information
        write_file_meta_info(f, event.file_meta)
        # Write the encoded dataset
        f.write(event.request.DataSet.getvalue())

    # Return a 'Success' status
    return 0x0000


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    hostname = os.getenv("HOSTNAME", "development")
    address = os.getenv("PYDIECOM_LISTEN_ADDRESS", "0.0.0.0")
    port = os.getenv("PYDIECOM_LISTEN_PORT", "2761")

    debug_logger()

    server = AE(textwrap.shorten(hostname, width=16))
    server.supported_contexts = AllStoragePresentationContexts

    logger.info("%s:%s", address, port)
    server.start_server(
        address=(address, int(port)),
        evt_handlers=[
            (EVT_C_STORE, c_store_handle),
        ],
    )


if __name__ == "__main__":
    sys.exit(main())
