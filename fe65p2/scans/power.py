from basil.dut import Dut
	
pow = Dut('/home/user/Desktop/carlo/basil/basil/HL/tti_ql335tp.yaml')
pow.init()
pow['QL355TP']['channel 2']['OP2'] = 1
print 'Turned off' 
