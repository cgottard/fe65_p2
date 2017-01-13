from basil.dut import Dut
import logging
import time


try:
    pow = Dut('/home/topcoup/Applications/basil/examples/lab_devices/ttiql335tp_pyserial2.yaml')
    pow.init()
    logging.info('Connected to ' + str(pow['Power'].get_info()))
    logging.info('Powering off')
    pow['Power'].turn_off()
    time.sleep(10)
    logging.info('Powering on')
    pow['Power'].turn_on()

except RuntimeError:
    logging.info('Connection to power supply failed')

