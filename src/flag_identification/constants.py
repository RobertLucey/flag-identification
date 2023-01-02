import os

LOG_LOCATION = (
    "/var/log/flag_identification/flag_identification.log"
    if os.getenv("TEST_ENV", "False") == "False"
    else "/tmp/log/flag_identification/flag_identification.log"
)
