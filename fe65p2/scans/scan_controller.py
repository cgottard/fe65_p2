from fe65p2.scans.noise_scan import NoiseScan
from fe65p2.scans.threshold_scan import ThresholdScan
from fe65p2.scans.digital_scan import DigitalScan
from fe65p2.scans.digital_scan_freq import DigitalScanFreq
from fe65p2.scans.timewalk_scan import TimewalkScan
from fe65p2.scans.analog_scan import AnalogScan
from fe65p2.scans.proofread_scan import proofread_scan
from fe65p2.scan_base import ScanBase
import os
import sys
import yaml
import time
from itertools import cycle
import logging

par_conf = {
    "columns": [True] * 16,
    #DAC parameters
    "PrmpVbpDac": 36,
    "vthin1Dac": 255,
    "vthin2Dac": 0,
    "vffDac" : 42,          #not subject to change
    "PrmpVbnFolDac" : 51,   #not subject to change
    "vbnLccDac" : 1,        #not subject to change
    "compVbnDac":25,        #not subject to change
    "preCompVbnDac" : 50,
}

#parameter folder name
par_string = "Prmp"+str(par_conf['PrmpVbpDac']) +"_vthA"+str(par_conf['vthin1Dac'])+"_vthB"+str(par_conf['vthin2Dac'])\
             +"_PreCmp"+str(par_conf['preCompVbnDac'])


def noise_sc():
    logging.info("Starting Noise Scan")
    noise_sc = NoiseScan()
    noise_mask_file = str(noise_sc.output_filename)+".h5"

    custom_conf = {
        "stop_pixel_count": 4,
        "repeats" : 100 #100000
    }

    scan_conf = dict(par_conf, **custom_conf)
    noise_sc.start(**scan_conf)
    noise_sc.analyze()


    print noise_sc.vth1Dac
    noise_sc.dut.close()
    return noise_mask_file

def thresh_sc(noise_mask_file=''):
    logging.info("Starting Threshold Scan")
    thrs_sc = ThresholdScan()
    thrs_mask_file = thrs_sc.output_filename

    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_range": [0.6, 0.7, 0.1], #[0.0, 0.6, 0.01],
        "mask_filename": noise_mask_file,
        "TDAC" : 16
    }

    scan_conf = dict(par_conf, **custom_conf)
    thrs_sc.start(**scan_conf)
    #thrs_sc.analyze()
    thrs_sc.dut.close()
    return thrs_mask_file

def digi_sc():
    logging.info("Starting Digital Scan")
    digital_sc = DigitalScan()
    custom_conf = {
        "mask_steps": 4*64,
        "repeat_command": 100
    }

    scan_conf = dict(par_conf, **custom_conf)
    digital_sc.start(**scan_conf)
    digital_sc.analyze()
    digital_sc.dut.close()

def analog_sc():
    logging.info("Starting Analog Scan")
    ana_sc = AnalogScan()
    custom_conf = {
        "mask_steps": 4*64,
        "repeat_command": 100
    }

    scan_conf = dict(par_conf, **custom_conf)
    ana_sc.start(**scan_conf)
    ana_sc.analyze()
    ana_sc.dut.close()

def timewalk_sc(mask):
    time_sc = TimewalkScan()
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_range": [0.6, 0.7, 0.1], #[0.0, 0.6, 0.01],
        "mask_filename": mask,   #from noise or threshold?
        "TDAC" : 16
    }
    scan_conf = dict(par_conf, **custom_conf)
    time_sc.start(**scan_conf)
    time_sc.analyze()
    time_sc.dut.close()



def digi_shmoo_sc_cmd():
    digi_shmoo = DigitalScanFreq(None)
    custom_conf = {

        "mask_steps": 4,
        "repeat_command": 100,
        "scan_type" : 'cmd'
    }
    scan_conf = dict(par_conf, **custom_conf)
    digi_shmoo.scan(**custom_conf)
    digi_shmoo.dut.close()

def digi_shmoo_sc_data():
    digi_shmoo = DigitalScanFreq(None)
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_type" : 'data'
    }
    scan_conf = dict(par_conf, **custom_conf)
    digi_shmoo.scan(**custom_conf)
    digi_shmoo.dut.close()

def pix_reg_sc():
    scan_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    yaml_path = scan_path.replace('scans','fe65p2.yaml')
    pix_reg = proofread_scan()
    pix_reg.scan(**par_conf)
    pix_reg.dut.close()



class status_sc(ScanBase):
    scan_id = "digital_scan"

    def print_status(self, **kwargs):
        self.dut['global_conf']['PrmpVbpDac'] = kwargs['PrmpVbpDac']
        self.dut['global_conf']['vthin1Dac'] = kwargs['vthin1Dac']
        self.dut['global_conf']['vthin2Dac'] = kwargs['vthin2Dac']
        self.dut['global_conf']['vffDac'] = kwargs['vffDac']
        self.dut['global_conf']['PrmpVbnFolDac'] = kwargs['PrmpVbnFolDac']
        self.dut['global_conf']['vbnLccDac'] = kwargs['vbnLccDac']
        self.dut['global_conf']['compVbnDac'] = kwargs['compVbnDac']
        self.dut['global_conf']['preCompVbnDac'] = kwargs['preCompVbnDac']
        self.dut['VDDA'].set_current_limit(200, unit='mA')
        self.dut['VDDA'].set_voltage(1.2, unit='V')
        self.dut['VDDA'].set_enable(True)
        self.dut['VDDD'].set_voltage(1.2, unit='V')
        self.dut['VDDD'].set_enable(True)
        self.dut['VAUX'].set_voltage(1.5, unit='V')
        self.dut['VAUX'].set_enable(True)
        logging.info('Power Status: %s', str(self.dut.power_status()))
        logging.info('DAC Status: %s', str(self.dut.dac_status()))
        self.dut['ntc'].get_temperature('C')
        self.dut.close()




if __name__ == "__main__":

    #logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    for keys,values in par_conf.items():
        print(keys)
        print(values)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
    os.chdir('/media/carlo/1 TB/')

    working_dir = os.path.join(os.getcwd(), par_string)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    os.chdir(working_dir)

    for c in cycle(range(0,2)): #goes on forever

        #for just 1 iteration
        if c==1: break
        #column independent scans
        print '*** CMD SCAN ***'
        digi_shmoo_sc_cmd()
        print '*** DATA SCAN ***'
        digi_shmoo_sc_data()
        print '*** PIX REG SCAN ***'
        pix_reg_sc()

        for i in cycle(range(1,9)):
            print 'col ', i
            cols = [False]*16
            j=2*i-1
            cols[j-1]=True
            cols[j]=True
            par_conf['columns'] = cols
            col_dir = os.path.join(os.getcwd(), "col"+str(i))
            if not os.path.exists(col_dir):
                os.makedirs(col_dir)
            os.chdir(col_dir)

            digi_sc()
            thrs_mask = thresh_sc('')
            time.sleep(1)
            #here print vth1 and other thresholds, also to .log file
            noise_masks = noise_sc()

            time.sleep(1)
            # here print vth1 and other thresholds, also to .log file
            thrs_mask = thresh_sc(noise_masks)
            os.chdir('..')



