from fe65p2.scans.noise_scan import NoiseScan
from fe65p2.scans.threshold_scan import ThresholdScan
from fe65p2.scans.tu_threshold_scan import ThresholdScanTuned
from fe65p2.scans.digital_scan import DigitalScan
from fe65p2.scans.digital_scan_freq import DigitalScanFreq
from fe65p2.scans.timewalk_scan import TimewalkScan
from fe65p2.scans.analog_scan import AnalogScan
from fe65p2.scans.proofread_scan import proofread_scan
from fe65p2.scan_base import ScanBase
import fe65p2.plotting as  plotting
import numpy as np
import os
import sys
import yaml
import time
from itertools import cycle
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")

fe65p2_path="/home/user/Desktop/carlo/fe65_p2"
storage_dir="/run/media/user/TB/"

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
    "preCompVbnDac" : 110
}

#parameter folder name
par_string = "Prmp"+str(par_conf['PrmpVbpDac']) +"_vthA"+str(par_conf['vthin1Dac'])+"_vthB"+str(par_conf['vthin2Dac'])\
             +"_PreCmp"+str(par_conf['preCompVbnDac'])


def noise_sc():
    logging.info("Starting Noise Scan")
    noise_sc = NoiseScan()
    noise_mask_file = str(noise_sc.output_filename)+'.h5'

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

def thresh_sc_unt(noise_mask_file=''):
    logging.info("Starting Threshold Scan")
    thrs_sc = ThresholdScan()
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_range": [0.2, 0.8, 0.01], #[0.0, 0.6, 0.01],
        "mask_filename": noise_mask_file,
        "TDAC" : 16
    }

    scan_conf = dict(par_conf, **custom_conf)
    thrs_sc.start(**scan_conf)
    thrs_sc.analyze()
    thrs_mask_file = str(thrs_sc.output_filename)+'.h5'
    thrs_sc.dut.close()
    return thrs_mask_file

def thresh_sc_tuned(noise_mask_file=''):
    logging.info("Starting Threshold Scan")
    thrs_sc = ThresholdScanTuned()
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_range": [0.005, 0.25, 0.005], #[0.0, 0.6, 0.01],
        "mask_filename": noise_mask_file,
        "TDAC" : 16
    }
    scan_conf = dict(par_conf, **custom_conf)
    thrs_sc.start(**scan_conf)
    thrs_sc.analyze()
    thrs_mask_file=str(thrs_sc.output_filename)+'.h5'
    thrs_sc.dut.close()
    return thrs_mask_file

def digi_sc():
    logging.info("Starting Digital Scan")
    digital_sc = DigitalScan()
    custom_conf = {
        "mask_steps": 4,
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

def timewalk_sc(noise_mask, th_mask, pix_list):
    time_sc = TimewalkScan()
    custom_conf = {
        "mask_steps" : 4,
        "repeat_command" : 101,
        "scan_range" : [0.005, 0.25, 0.005],
        "noise_mask" : noise_mask,
        "mask_filename":th_mask,
        "pix_list":pix_list
    }
    scan_conf = dict(par_conf, **custom_conf)
    scanrange=custom_conf["scan_range"]
    time_sc.start(**scan_conf)
    time_sc.tdc_table(len(np.arange(scanrange[0], scanrange[1], scanrange[2]))+3)
    time_sc.dut.close()



def digi_shmoo_sc_cmd():
    digi_shmoo = DigitalScanFreq(None)
    digi_shmoo.plots=False
    custom_conf = {

        "mask_steps": 4,
        "repeat_command": 100,
        "scan_type" : 'cmd'
    }
    scan_conf = dict(par_conf, **custom_conf)
    digi_shmoo.scan(**scan_conf)
    digi_shmoo.dut.close()


def digi_shmoo_sc_data():
    digi_shmoo = DigitalScanFreq(None)
    digi_shmoo.plots=False
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_type" : 'data'
    }
    scan_conf = dict(par_conf, **custom_conf)
    digi_shmoo.scan(**scan_conf)
    digi_shmoo.dut.close()

def pix_reg_sc():
    pix_reg = proofread_scan(fe65p2_path+"/fe65p2/fe65p2.yaml")
    pix_reg.scan(**par_conf)
    pix_reg.shmoo_plotting()
    pix_reg.dut.close()



class status_sc(ScanBase):
    scan_id = "status_scan"

    def load_bit(self):
        self.dut['intf']._sidev.DownloadXilinx(fe65p2_path+"/firmware/ise/fe65p2_mio.bit")
        self.dut['VDDA'].set_current_limit(200, unit='mA')
        self.dut['VDDA'].set_voltage(1.2, unit='V')
        self.dut['VDDA'].set_enable(True)
        self.dut['VDDD'].set_voltage(1.2, unit='V')
        self.dut['VDDD'].set_enable(True)
        self.dut['VAUX'].set_voltage(1.2, unit='V')
        self.dut['VAUX'].set_enable(True)
        self.dut['global_conf']['PrmpVbpDac'] = 36
        self.dut['global_conf']['vthin1Dac'] = 255
        self.dut['global_conf']['vthin2Dac'] = 0
        self.dut['global_conf']['vffDac'] = 24
        self.dut['global_conf']['PrmpVbnFolDac'] = 51
        self.dut['global_conf']['vbnLccDac'] = 1
        self.dut['global_conf']['compVbnDac'] = 25
        self.dut['global_conf']['preCompVbnDac'] = 50
        logging.info('Power Status: %s', str(self.dut.power_status()))
        logging.info('DAC Status: %s', str(self.dut.dac_status()))
        self.dut['ntc'].get_temperature('C')
        self.dut.close()

def time_pixels(col):
    lp = []
    if col==1: lp=[(2,6), (3,3)]
    if col==2: lp=[(6,20),(14,10)]
    if col==3: lp=[(20,20),(22,18)]
    if col==4: lp=[(28,28),(30,31)]
    if col==5: lp=[(36,36),(38,34)]
    if col==6: lp=[(44,44),(44,42)]
    if col==7: lp=[(49,49),(50,48)]
    if col==8: lp=[(56,56),(58,58)]
    return lp





if __name__ == "__main__":

    #logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    for keys,values in par_conf.items():
        print keys, values

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
    os.chdir(storage_dir)

    working_dir = os.path.join(os.getcwd(), par_string)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    os.chdir(working_dir)

    for c in cycle(range(0,2)): #goes on forever
        #for just 1 iteration
        if c==1: break
        #column independent scans
        '''
        time.sleep(1)
        
        print '*** CMD SCAN ***'
        dir = os.path.join(os.getcwd(), "CMD_shmoo")
        if not os.path.exists(dir):
            os.makedirs(dir)
        os.chdir(dir)
        digi_shmoo_sc_cmd()
        os.chdir('..')

        time.sleep(1)
        print '*** DATA SCAN ***'
        dir = os.path.join(os.getcwd(), "DATA_shmoo")
        if not os.path.exists(dir):
            os.makedirs(dir)
        os.chdir(dir)
        digi_shmoo_sc_data()
        os.chdir('..')
        
        time.sleep(1)
        print '*** PIX REG SCAN ***'
        dir = os.path.join(os.getcwd(), "PIX_shmoo")
        if not os.path.exists(dir):
            os.makedirs(dir)
        os.chdir(dir)
        pix_reg_sc()
        os.chdir('..')
        
        time.sleep(1)
        print '*** DIGI SCAN ***'
        loadbit = status_sc()
        loadbit.load_bit()
        
        dir = os.path.join(os.getcwd(), "DIGI_scan")
        if not os.path.exists(dir):
            os.makedirs(dir)
        os.chdir(dir)
        digi_sc()
        os.chdir('..')
        '''
        time.sleep(1)
        for i in range(8,9):
            cols = [False]*16
            j=2*i-1
            cols[j-1]=True
            cols[j]=True
            par_conf['columns'] = cols
            col_dir = os.path.join(os.getcwd(), "col"+str(i))
            if not os.path.exists(col_dir):
                os.makedirs(col_dir)
            os.chdir(col_dir)
            
            #unt_thrs_mask = thresh_sc_unt('')
            #time.sleep(2.0)
            noise_masks = noise_sc()
            time.sleep(2.0)
            thrs_mask = thresh_sc_tuned(noise_masks)
            time.sleep(2.0)
            
            if i==1:
                pixels = time_pixels(i)
                timewalk_sc(noise_masks, thrs_mask, pixels)
            
            os.chdir('..')
        


