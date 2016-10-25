from fe65p2.scans.noise_scan import NoiseScan
from fe65p2.scans.threshold_scan import ThresholdScan
from fe65p2.scans.digital_scan import DigitalScan
from fe65p2.scans.digital_scan_freq import DigitalScanFreq
from fe65p2.scans.analog_scan import AnalogScan
from fe65p2.scans.proofread_scan import proofread_scan
import os
import yaml

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
    noise_sc = NoiseScan()
    noise_mask_file = noise_sc.output_filename

    noise_conf = {
        "columns": [True] * 2 + [False] * 14,
        "stop_pixel_count": 4,
    }

    scan_conf = dict(par_conf, **noise_conf)
    noise_sc.start(**scan_conf)
    noise_sc.analyze()
    return noise_mask_file

def thresh_sc(noise_mask_file=''):
    thrs_sc = ThresholdScan()
    thrs_mask_file = thrs_sc.output_filename

    thrs_conf = {
        "columns": [True] * 2 + [False] * 14,
        "mask_steps": 4,
        "repeat_command": 100,
        "scan_range": [0.0, 0.6, 0.01],
        "mask_filename": noise_mask_file,
        "TDAC" : 16
    }

    scan_conf = dict(par_conf, **thrs_conf)
    thrs_sc.start( **scan_conf)
    thrs_sc.analyze()
    return thrs_mask_file

def digi_sc():
    digital_sc = DigitalScan()

    digi_conf = {
        "mask_steps": 4*64,
        "repeat_command": 100
    }

    scan_conf = dict(par_conf, **digi_conf)
    digital_sc.start(**scan_conf)
    digital_sc.analyze()

def digi_shmoo_sc():
    digi_shmoo = DigitalScanFreq()
    digi_shmoo.scan(**par_conf)


def pix_reg_sc():
    pix_reg = proofread_scan()
    pix_reg.scan(**par_conf)



if __name__ == "__main__":
    noise_sc()
