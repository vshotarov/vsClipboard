import vsClipboard
import logging


doLog = False

if doLog:
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    logging.info("Imported module. Starting...")

vsClipboard.start()

if doLog:
    logging.info("Finished.")
