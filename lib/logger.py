import logging, copy, logging.handlers, os.path, os
from lib.constants import *

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
BOLD_SEQ = "\033[1m"
COLOR_SEQ = "\033[1;%dm"
COLORS = {
  'WARNING': YELLOW,
  'INFO': WHITE,
  'DEBUG': BLUE,
  'CRITICAL': YELLOW,
  'ERROR': RED
}
COLORS_BG = {
  'WARNING': BLACK,
  'INFO': BLACK,
  'DEBUG': BLACK,
  'CRITICAL': RED,
  'ERROR': WHITE
}

class CustomFormatter(logging.Formatter):
  def __init__(self, msg, col):
    logging.Formatter.__init__(self, msg, datefmt='%I:%M:%S')
    self.col = col

  def format(self, rec):
    if not self.col:
      return logging.Formatter.format(self, record)
    record = copy.copy(rec)
    levelname = record.levelname.upper()
    if levelname in COLORS:
      record.levelname = COLOR_SEQ % (30 + COLORS[levelname]) + COLOR_SEQ % (40 + COLORS_BG[levelname]) + levelname + RESET_SEQ
    return logging.Formatter.format(self, record)

class CustomLogger(logging.Logger):
  def __init__(self, name):
    logging.Logger.__init__(self, name, logging.DEBUG if OPT["debug"] else logging.INFO)
    if LOGGER_COLORED:
      fmt = LOGGER_TEXT.replace("$BOLD", BOLD_SEQ).replace("$RESET", RESET_SEQ)
    else:
      fmt = LOGGER_TEXT.replace("$BOLD", "").replace("$RESET", "")
    formatter = CustomFormatter(fmt, LOGGER_COLORED)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    self.addHandler(console)

f = True
def getLogger(name):
  global f
  if f:
    logging.setLoggerClass(CustomLogger)
    f = False
  return logging.getLogger(name)
