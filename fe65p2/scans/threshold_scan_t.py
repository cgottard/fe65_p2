
from fe65p2.scan_base import ScanBase
import fe65p2.plotting as  plotting
import fe65p2.analysis as analysis
import time
import numpy as np
import bitarray
import tables as tb
from bokeh.charts import output_file, show, vplot, hplot, save
from progressbar import ProgressBar
from basil.dut import Dut
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")

local_configuration = {
    "mask_steps": 1,
    "repeat_command": 101,
    "scan_range": [0.05, 1.5, 0.05],
    "vthin1Dac": 60,
    "preCompVbnDac" : 115,
    "columns" : [True] * 2 + [True] * 14,
    "mask_filename": ''
}



class ThresholdScan(ScanBase):
    scan_id = "threshold_scan"

    def scan(self, mask_steps=4, repeat_command=100, columns = [True] * 16, scan_range = [0, 1.2, 0.1], vthin1Dac = 80, preCompVbnDac = 50, mask_filename='', **kwargs):
        '''Scan loop
        Parameters
        ----------
        mask : int
            Number of mask steps.
        repeat : int
            Number of injections.
        '''

        INJ_LO = 0.0
        dut = Dut('/home/carlo/basil/examples/lab_devices/agilent33250a_pyserial.yaml')
        dut.init()
        logging.info('Connected to '+str(dut['Pulser'].get_info()))

        self.dut['global_conf']['PrmpVbpDac'] = 80
        self.dut['global_conf']['vthin1Dac'] = 255
        self.dut['global_conf']['vthin2Dac'] = 0
        self.dut['global_conf']['vffDac'] = 24
        self.dut['global_conf']['PrmpVbnFolDac'] = 51
        self.dut['global_conf']['vbnLccDac'] = 1
        self.dut['global_conf']['compVbnDac'] = 25
        self.dut['global_conf']['preCompVbnDac'] = 50
        
        self.dut.write_global() 
        self.dut['control']['RESET'] = 0b01
        self.dut['control']['DISABLE_LD'] = 0
        self.dut['control']['PIX_D_CONF'] = 0
        self.dut['control'].write()
        
        self.dut['control']['CLK_OUT_GATE'] = 1
        self.dut['control']['CLK_BX_GATE'] = 1
        self.dut['control'].write()
        time.sleep(0.1)
        
        self.dut['control']['RESET'] = 0b11
        self.dut['control'].write()

        self.dut['global_conf']['OneSr'] = 1  
        
        self.dut['global_conf']['TestHit'] = 0
        self.dut['global_conf']['SignLd'] = 0
        self.dut['global_conf']['InjEnLd'] = 0
        self.dut['global_conf']['TDacLd'] = 0
        self.dut['global_conf']['PixConfLd'] = 0
        self.dut.write_global()

        self.dut['global_conf']['ColEn'][:] = bitarray.bitarray([True] * 16) #(columns)
        self.dut['global_conf']['ColSrEn'][:] = bitarray.bitarray([True] * 16)     
        self.dut.write_global()

        self.dut['pixel_conf'].setall(False)
        self.dut.write_pixel()
        self.dut['global_conf']['InjEnLd'] = 1
        self.dut.write_global()
        self.dut['global_conf']['InjEnLd'] = 0

        mask_en = np.full([64,64], False, dtype = np.bool)
        mask_tdac = np.full([64,64], 16, dtype = np.uint8)
        
        for inx, col in enumerate(columns):
           if col:
                mask_en[inx*4:(inx+1)*4,:]  = True
        
        if mask_filename:
            logging.info('Using pixel mask from file: %s', mask_filename)
        
            with tb.open_file(mask_filename, 'r') as in_file_h5:
                mask_tdac = in_file_h5.root.scan_results.tdac_mask[:]
                mask_en = in_file_h5.root.scan_results.en_mask[:]
        
        self.dut.write_en_mask(mask_en)
        self.dut.write_tune_mask(mask_tdac)
        
        self.dut['global_conf']['OneSr'] = 1
        self.dut.write_global()

        self.dut['inj'].set_delay(100000)
        self.dut['inj'].set_width(1000)
        self.dut['inj'].set_repeat(repeat_command)
        self.dut['inj'].set_en(False)

        self.dut['trigger'].set_delay(400-4)
        self.dut['trigger'].set_width(16)
        self.dut['trigger'].set_repeat(1)
        self.dut['trigger'].set_en(False)
        pixel = [128]
        lmask = [0]*(64*64)
        lmask[pixel[0]] = 1

        scan_range = np.arange(scan_range[0], scan_range[1], scan_range[2])
        self.pixel_list = np.repeat(pixel, scan_range.shape[0])
        logging.debug('Enable TDC')
        self.dut['tdc']['RESET'] = True
        self.dut['tdc']['EN_TRIGGER_DIST'] = True
        self.dut['tdc']['ENABLE_EXTERN'] = False
        self.dut['tdc']['EN_ARMING'] = False
        self.dut['tdc']['EN_INVERT_TRIGGER'] = False
        self.dut['tdc']['EN_INVERT_TDC'] = False
        self.dut['tdc']['EN_WRITE_TIMESTAMP'] = True
        self.inj_charge = []
        for idx, k in enumerate(scan_range):
            dut['Pulser'].set_voltage(INJ_LO, float(INJ_LO + k), unit='V')
            self.inj_charge.append(float(k)*1000.0*ScanBase.cap_fac(self))

            time.sleep(0.5)
            
            bv_mask = bitarray.bitarray(lmask)
        
            with self.readout(scan_param_id = idx):
                logging.info('Scan Parameter: %f (%d of %d)', k, idx+1, len(scan_range))
                self.dut['tdc']['ENABLE'] = True
#               pbar = ProgressBar(maxval=mask_steps).start()
#               for i in range(mask_steps):

                self.dut['global_conf']['vthin1Dac'] = 255
                self.dut['global_conf']['preCompVbnDac'] = 50
                self.dut.write_global()
                time.sleep(0.1)

                self.dut['pixel_conf'][:]  = bv_mask
                self.dut.write_pixel()
                self.dut['global_conf']['InjEnLd'] = 1
                #self.dut['global_conf']['PixConfLd'] = 0b11
                self.dut.write_global()

                #bv_mask[1:] = bv_mask[0:-1]
                #bv_mask[0] = 0

                self.dut['global_conf']['vthin1Dac'] = vthin1Dac
                self.dut['global_conf']['preCompVbnDac'] = preCompVbnDac
                self.dut.write_global()
                time.sleep(0.1)

                self.dut['inj'].start()

              #  pbar.update(i)

                while not self.dut['inj'].is_done():
                    pass

                while not self.dut['trigger'].is_done():
                    pass

                self.dut['tdc'].ENABLE = 0


                    
        scan_results = self.h5_file.create_group("/", 'scan_masks', 'Scan Masks')
        self.h5_file.createCArray(scan_results, 'tdac_mask', obj=mask_tdac)
        self.h5_file.createCArray(scan_results, 'en_mask', obj=mask_en)
        
        
    def analyze(self):
        h5_filename = self.output_filename +'.h5'
        with tb.open_file(h5_filename, 'r+') as in_file_h5:
            raw_data = in_file_h5.root.raw_data[:]
            meta_data = in_file_h5.root.meta_data[:]

            hit_data = self.dut.interpret_raw_data(raw_data, meta_data)
            in_file_h5.createTable(in_file_h5.root, 'hit_data', hit_data, filters=self.filter_tables)

        analysis.analyze_threshold_scan(h5_filename)
        status_plot = plotting.plot_status(h5_filename)
        occ_plot, H = plotting.plot_occupancy(h5_filename)
        tot_plot,_ = plotting.plot_tot_dist(h5_filename)
        lv1id_plot, _ = plotting.plot_lv1id_dist(h5_filename)
        scan_pix_hist, _ = plotting.scan_pix_hist(h5_filename)
        t_dac = plotting.t_dac_plot(h5_filename)

        output_file(self.output_filename + '.html', title=self.run_name)
        save(vplot(hplot(occ_plot, tot_plot, lv1id_plot), scan_pix_hist, t_dac, status_plot))



    def tdc_table(self):
        h5_filename = self.output_filename +'.h5'
        with tb.open_file(h5_filename, 'r+') as in_file_h5:
            raw_data = in_file_h5.root.raw_data[:]
            meta_data = in_file_h5.root.meta_data[:]
            if (meta_data.shape[0]==0): return
            param, index = np.unique(meta_data['scan_param_id'], return_index=True)
            index = index[1:]
            index = np.append(index, meta_data.shape[0])
            index = index - 1
            stops = meta_data['index_stop'][index]
            split = np.split(raw_data, stops)
            avg_tdc = []
            avg_tdc_err = []
            avg_del = []
            avg_del_err = []
            for i in range(len(split[:-1])):
                rwa_data_param  = split[i]
                tdc_data = rwa_data_param & 0xFFF  # take last 12 bit
                tdc_delay = (rwa_data_param & 0x0FF00000) >> 20
                counter = 0.0
                TOT_sum = 0.0
                DEL_sum = 0.0
                if (tdc_data.shape[0]==0): counter = 1.0
                for j in range(tdc_data.shape[0]):
                    if (j>0):
                       # print  j, hex(raw_data[j]), tdc_data[j], tdc_delay[j]
                        counter += 1
                        TOT_sum += tdc_data[j]
                        DEL_sum += tdc_delay[j]
                avg_tdc.append((float(TOT_sum)/float(counter))*1.5625)
                avg_tdc_err.append(1.5625/(np.sqrt(12.0*counter)))
                avg_del.append((float(DEL_sum)/float(counter))*1.5625)
                avg_del_err.append(1.5625/(np.sqrt(12.0*counter)))
            '''
            If the collected injections are less than the actual ones it's because I injected below threshold.
            In case the lenght of arrays does not match I discard the proper amount of inj_charge entries.
            '''
            if (len(self.inj_charge)-len(avg_tdc) > 0):
                n = len(self.inj_charge)-len(avg_tdc)
                self.inj_charge = self.inj_charge[n:]
                self.pixel_list = self.pixel_list[n:]

            avg_tab = np.rec.fromarrays([self.inj_charge, self.pixel_list, avg_tdc, avg_tdc_err, avg_del, avg_del_err],
                                        dtype =[('charge', float), ('pixel_no', int), ('tot_ns', float),('err_tot_ns', float), ('delay_ns', float), ('err_delay_ns', float)])
            in_file_h5.createTable(in_file_h5.root, 'tdc_data', avg_tab, filters=self.filter_tables)

        p1, p2 = plotting.plot_timewalk(h5_filename)
        output_file(self.output_filename + '.html', title=self.run_name)
        save(vplot(p1,p2))



if __name__ == "__main__":

    scan = ThresholdScan()
    scan.start(**local_configuration)
    scan.tdc_table()
