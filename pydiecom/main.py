import logging
import os
import sys
import tempfile
import textwrap

import boto3
from pydicom.filewriter import write_file_meta_info
from pynetdicom import AE, AllStoragePresentationContexts, debug_logger
from pynetdicom.events import EVT_C_ECHO, EVT_C_STORE

s3 = boto3.client("s3")


def c_echo_handle(_event):
    return 0x0000


def c_store_handle_gen(bucket_name: str):
    # Implement a handler for evt.EVT_C_STORE
    def c_store_handle(event):
        tmp_file = tempfile.NamedTemporaryFile("wb", dir=tempfile.gettempdir())
        instance_uid = event.request.AffectedSOPInstanceUID

        with tmp_file as tf:
            print(tmp_file)
            # Write the preamble and prefix
            tf.write(b"\x00" * 128)
            tf.write(b"DICM")

            # Encode and write the File Meta Information
            write_file_meta_info(tf, event.file_meta)

            # Write the encoded dataset
            tf.write(event.request.DataSet.getvalue())

            print("flush")
            tf.flush()
            print(bucket_name)
            print("upload")

            s3.upload_file(tf.name, bucket_name, f"{instance_uid}.dcm")
            print("complete")

        # Return a 'Success' status
        return 0x0000

    return c_store_handle


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    address = os.getenv("PYDIECOM_LISTEN_ADDRESS", "0.0.0.0")
    bucket_name = os.getenv("PYDIECOM_BUCKET_NAME", "mclark-dicom-staging")
    hostname = os.getenv("HOSTNAME", "development")
    port = os.getenv("PYDIECOM_LISTEN_PORT", "2761")

    # debug_logger()

    server = AE(textwrap.shorten(hostname, width=16))
    server.supported_contexts = AllStoragePresentationContexts

    logger.info("%s:%s", address, port)
    server.start_server(
        address=(address, int(port)),
        evt_handlers=[
            (EVT_C_ECHO, c_echo_handle),
            (EVT_C_STORE, c_store_handle_gen(bucket_name)),
        ],
    )


if __name__ == "__main__":
    sys.exit(main())
