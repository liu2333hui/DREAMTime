import os
import time
from DREAMVerilog import VerilogAnalyzer

'''
wrapper around opentimer os-shell
'''
class Timer():
    """
    @brief Timer wrapper for OpenTimer and Flute
    """
    def __init__(self, placedb, params ):
        self.placedb = placedb
        self.params = params

        self.analyzer = VerilogAnalyzer(self.params.verilog_input)

        self.clean_sdc()
        self.gen_shell(parasitics=True)
        self.run_timer()

        self.convert_slack2weights()

    def gen_shell(self, parasitics=False):
        f = open("tmp.ot.shell", "w")
        f.write("set_num_threads " + str(self.params.num_threads)+"\n")
        f.write("read_celllib -early " + self.params.timer_libs[0]+"\n")
        f.write("read_celllib -late " + self.params.timer_libs[1]+"\n")
        f.write("read_verilog " + self.params.verilog_input + "\n")
        f.write("read_sdc " + self.params.timer_sdc + ".cleaned" + "\n")
        if(parasitics == True):
            self.analyzer.createSPEF(self.params,"tmp.spef", self.placedb)
            f.write("read_spef tmp.spef\n")
 
        #f.write("cppr -enable\n")
        #f.write("report_timing -num_paths 10\n")
        #f.write("echo analysis\n")
        f.write("report_tns\n")
        f.write("report_wns\n")
        #print(self.placedb.net_names)
        #print(self.placedb.net_weights)
        #print(self.analyzer.wire2port)
        for name in self.placedb.net_names:
            net = str(name)[2:-1]
            pin = self.analyzer.wire2port[net][0]
            f.write("report_slack -rise -max -pin " + pin + "\n")
 
        #f.write("dump_slack -o slack.log\n")
        #f.write("dump_at -o at.log\n")
        #f.write("dump_rat -o rat.log\n")
        f.close()

    def run_timer(self):
        tt = time.time()
        print("Start running STA")
        os.system("/lib64/bin/ot-shell -i tmp.ot.shell > ot.log")
        print("Run timer - " + str(time.time() - tt) + " s ")


    #Convert any set_driving_cell statements into set_transition_cell
    def clean_sdc(self):
        #todos
        f = open(self.params.timer_sdc)
        g = open(self.params.timer_sdc+".cleaned", "w")

        for l in f.readlines():
            if "create_clock" in l:
                clk_name = l.split()[2]
                clk_port = l.split()[5] + " " +l.split()[6]
                g.write(l)
                g.write("set_input_delay 10.0 " + clk_port  +  " -clock "+clk_name+"\n")
                delay = "10.0"
                g.write("set_input_transition " + delay + " " + clk_port + " -clock " + clk_name + "\n") 
 
            elif "set_driving_cell" in l:
                ll = l.split()
                port = ll[5] + " " + ll[6]
                delay = ll[8]
                g.write("set_input_transition " + delay + " " + port + " -clock " + clk_name + "\n") 
                #g.write("set_input_transition " + delay  + "-min -rise " + port + " -clock " + clk_name + "\n")

            else:
                g.write(l)

        f.close()
        g.close()

    def convert_slack2weights(self, ns_only = False):
        #todos
        #read in the results from timer
        #print(self.placedb.net_names)
        #print(self.placedb.net_weights)
        #print(self.analyzer.wire2port)
        self.weights = []

        with open("ot.log") as f:
            tns = float(f.readline().strip())
            wns = float(f.readline().strip())
            if(ns_only):
                return tns, wns
            for l in f.readlines():
                if(l.strip() == "nan"):
                    self.weights.append(1.0)
                else:
                    w = float(l.strip())
                    w /= wns
                    w += 1.0
                    self.weights.append(w)

        print("Time-driven weights")
        print("Tns, Wns")
        print(tns, wns)
        #print(self.weights)
        #print(self.placedb.net_weights)
        print("===================")

    def createSPEF(self):
        #todos
        return

    def getFinalTiming(self):
        #return
        self.createSPEF()
        self.clean_sdc()
        self.gen_shell(True)
        self.run_timer()
        self.convert_slack2weights()
