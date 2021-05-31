from decimal import getcontext, ROUND_HALF_UP

from pa.common.common import validate_settings
from pa.cli.cli import CLI

if __name__ == "__main__":
    getcontext().rounding = ROUND_HALF_UP
    validate_settings()
    cli = CLI()
    cli.run()
