from fe65p2.scans.noise_scan import NoiseScan
from fe65p2.scans.threshold_scan import ThresholdScan
from fe65p2.scans.digital_scan import DigitalScan
from fe65p2.scans.digital_scan_freq import DigitalScanFreq
from fe65p2.scans.timewalk_scan import TimewalkScan
from fe65p2.scans.analog_scan import AnalogScan
from fe65p2.scans.proofread_scan import proofread_scan
import os
import sys
import yaml
import time
import logging

par_conf = {
    #DAC parameters
    "PrmpVbpDac": 36,
    "vthin1Dac": 255,
    "vthin2Dac": 0,
    "vffDac" : 24,
    "PrmpVbnFolDac" : 51,
    "vbnLccDac" : 1,
    "compVbnDac":25,
    "preCompVbnDac" : 50,
}

def noise_sc():
    logging.info("Starting Noise Scan")
    noise_sc = NoiseScan()
    noise_mask_file = noise_sc.output_filename

    custom_conf = {
        "columns": [True] * 1 + [False] * 15,
        "stop_pixel_count": 4,
        "repeats" : 100 #100000
    }

    scan_conf = dict(par_conf, **custom_conf)
    noise_sc.start(**scan_conf)
    noise_sc.analyze()
    noise_sc.dut.close()
    return noise_mask_file

def thresh_sc(noise_mask_file=''):
    logging.info("Starting Threshold Scan")
    thrs_sc = ThresholdScan()
    thrs_mask_file = thrs_sc.output_filename

    custom_conf = {
        "columns": [True] * 1 + [False] * 15,
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

def timewalk_sc(mask):
    time_sc = TimewalkScan()
    custom_conf = {
        "columns": [True] * 1 + [False] * 15,
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_range": [0.6, 0.7, 0.1], #[0.0, 0.6, 0.01],
        "mask_filename": mask,   #from noise or threshold?
        "TDAC" : 16
    }
    scan_conf = dict(par_conf, **custom_conf)
    time_sc.start(**scan_conf)
    time_sc.analyze()


def digi_shmoo_sc_cmd():
    digi_shmoo = DigitalScanFreq(None, **par_conf)
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_type" : 'cmd'
    }
    scan_conf = dict(par_conf, **custom_conf)
    digi_shmoo.scan(**scan_conf)

def digi_shmoo_sc_data():
    digi_shmoo = DigitalScanFreq(None,**par_conf)
    custom_conf = {
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_type" : 'data'
    }
    scan_conf = dict(par_conf, **custom_conf)
    digi_shmoo.scan(**scan_conf)

def pix_reg_sc():
    scan_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    yaml_path = scan_path.replace('scans','fe65p2.yaml')
    pix_reg = proofread_scan()
    pix_reg.scan(**par_conf)



if __name__ == "__main__":
    #noise_masks = noise_sc()
    '''
    noise_masks = '/home/carlo/fe65_p2/fe65p2/scans/output_data/20161026_180908_noise_scan'
    print noise_masks
    time.sleep(3)
    thrs_mask = thresh_sc(str(noise_masks)+".h5")
    print thrs_mask
    digi_sc()
    '''
    digi_shmoo_sc_data()
    #digi_shmoo_sc_cmd()
