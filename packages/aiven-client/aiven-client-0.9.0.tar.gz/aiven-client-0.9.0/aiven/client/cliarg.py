# Copyright 2015, Aiven, https://aiven.io/
#
# This file is under the Apache License, Version 2.0.
# See the file `LICENSE` for details.

from .argx import arg
import os

arg.card_id = arg("--card-id", help="Card ID")
arg.cloud = arg("--cloud", help="Cloud to use (see 'cloud list' command)")
arg.email = arg("email", help="User email address")
arg.force = arg("-f", "--force", help="Force action without interactive confirmation",
                action="store_true", default=False)
arg.json = arg("--json", help="Raw json output", action="store_true", default=False)
arg.project = arg("--project", help="Project name to use, default %(default)r",
                  default=os.environ.get("AIVEN_PROJECT"))
arg.service_type = arg("-t", "--service-type", help="Type of service (see 'service list-types')")
arg.timeout = arg("--timeout", type=int, help="Wait for up to N seconds (default: infinite)")
arg.user_config = arg("-c", dest="user_config", action="append", default=[],
                      help="User configuration: KEY=JSON_VALUE")
arg.verbose = arg("-v", "--verbose", help="Verbose output", action="store_true", default=False)
