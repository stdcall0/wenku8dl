import logging, copy, logging.handlers, os.path, os

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color=True):
  if use_color:
    message = message.replace(
      "$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
  else:
    message = message.replace("$RESET", "").replace("$BOLD", "")
  return message

COLORS = {
  'WARNING': YELLOW,
  'INFO': WHITE,
  'DEBUG': BLUE,
  'CRITICAL': YELLOW,
  'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
  def __init__(self, msg, use_color=True):
    logging.Formatter.__init__(self, msg, datefmt='%d-%I:%M:%S %p')
    self.use_color = use_color

  def format(self, rec):
    record = copy.copy(rec)
    levelname = record.levelname
    if self.use_color and levelname in COLORS:
      levelname_color = COLOR_SEQ % (
        30 + COLORS[levelname]) + levelname + RESET_SEQ
      record.levelname = levelname_color
    return logging.Formatter.format(self, record)

class NoServerFilter(logging.Filter):
  def filter(self, record):
    return record.name != 'SERVER'

class ColoredLogger(logging.Logger):
  FORMAT = "%(asctime)s %(name)s $BOLD%(levelname)s$RESET %(message)s"
  COLOR_FORMAT = formatter_message(FORMAT, True)

  def __init__(self, name):
    logging.Logger.__init__(self, name, logging.DEBUG)

    color_formatter = ColoredFormatter(self.COLOR_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(color_formatter)

    self.addHandler(console)
    
    """
    # also log to file
    filename = os.path.join(os.getcwd(), 'logs/mcdr.log').replace('\\','/')
    fhlr = logging.handlers.TimedRotatingFileHandler(filename, 'D', 1, 30)
    fhlr.setFormatter(color_formatter)
    fhlr.addFilter(NoServerFilter())

    self.addHandler(fhlr)
    """
    return

def enable():
  logging.setLoggerClass(ColoredLogger)
