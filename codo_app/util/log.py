import logging
import datetime

logging.basicConfig(
    filename=f"codo_log{datetime.date.today()}.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

D = "debug"
I = "info"
W = "warning"
E = "error"


def l(file: str, message: str, type=I, error=None):
    if type == W:
        logging.warning(f"{file}: {message} {datetime.datetime.now()}")
    elif type == E:
        logging.error(f"{file}: {message} {datetime.datetime.now()} - Error: {error}")
    elif type == I:
        logging.info(f"{file}: {message} {datetime.datetime.now()}")
    else:
        logging.debug(f"{file}: {message} {datetime.datetime.now()}")
