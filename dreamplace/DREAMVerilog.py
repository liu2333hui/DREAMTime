import numpy as np
import os
#from tqdm import tqdm

class VerilogAnalyzer():
    def __init__(self, verilog_input):
        self.verilog_input = verilog_input
        self.wire2port = {}
        #use idx mapping
        self.wire2port_map = {}

        self.port_type = {}

        self.wire2port2pin = {}

        self.mod2idx = {}

        self.analyzeVerilog()

    def analyzeVerilog(self):
        with open(self.verilog_input) as f:
            for l_idx, l in enumerate(f.readlines()):
                ll = l.split()
                if (len(ll) < 1):
                    continue
                if( ll[0] == "wire" or ll[0] == "input" or ll[0] == "output"):
                    wire = ll[1][:-1]
                    if (wire not in self.wire2port):
                        self.wire2port[wire] = []
                        self.wire2port2pin[wire] = {}
                        #self.port_type[wire] = "I"

                        self.wire2port_map[wire] = []
                        self.mod2idx[wire] = len(self.mod2idx)+1
 
 

                if(ll[0] == "input" or ll[0] == "output"):
                    self.wire2port[wire].append(wire)

                    self.wire2port2pin[wire][wire] = wire
                    self.port_type[wire] = "P"

                    self.wire2port_map[wire].append("*" + str(self.mod2idx[wire]))
 
                   
                #print(l_idx, self.wire2port)

                if(len(ll) > 4):
                    module = ll[1]
                    for i in range(3, len(ll) - 1):
                        lll = ll[i].split(")")[0]
                        llll = lll[1:].split("(")
                        pin = module + ":" + llll[0] 
                        net = llll[1]
                        self.wire2port[net].append(pin)
                        self.wire2port2pin[net][module] = pin  #llll[0]
                        self.port_type[module] = "I"
                

 
                        if(module not in self.mod2idx):
                            self.mod2idx[module] = len(self.mod2idx)+1

                        self.wire2port_map[net].append("*" + str(self.mod2idx[module]) + ":" + llll[0])
 
 

    def pin_direct(self,p):
        if(p in ["o", "q"]):
            return "O"
        else:
            return "I"

    def createSPEF(self,params, spef_file, placedb):
        #get r/c per length
        r_per_u = params.r_per_u
        c_per_u = params.c_per_u

        #generate SPEF file
        g = open(spef_file, "w")
    
        g.write("*SPEF \"IEEE 1481-1998\"\n")
        g.write("*DESIGN \"simple\"\n")
        g.write('*DATE "Datetodo"\n')
        g.write('*VENDOR "DREAMVerilog"\n')
        g.write('*PROGRAM "DREAMVerilog analyzer"\n')
        g.write('*VERSION "0.0"\n')
        g.write('*DESIGN_FLOW "NAME_SCOPE LOCAL" "PIN_CAP NONE"\n')
        g.write('*DIVIDER /\n')
        g.write('*DELIMITER :\n')
        g.write("*BUS_DELIMITER [ ]\n")
        g.write('*T_UNIT 1 PS\n')
        g.write('*C_UNIT 1 FF\n')
        g.write('*R_UNIT 1 KOHM\n')
        g.write('*L_UNIT 1 UH\n\n')
    
        
        #create the name map
        g.write("*NAME_MAP\n")
        g.write("\n")
        for mod, idx in self.mod2idx.items():
            g.write("*"+str(idx)+" " + mod + "\n")
        g.write("\n")




        #write net parasitics
        for net_idx, name in enumerate(placedb.net_names):
            if(net_idx % 10000 == 0):
                print("Writing parasitic for " + str(net_idx) + " nets out of " + str(len(placedb.net_names)))
                #break
            net = str(name)[2:-1] 
            #if it is 2, dont need to run flute
            #print(net_idx, name, placedb.net2pin_map[net_idx])
            if(len(placedb.net2pin_map[net_idx]) == 2):
                #print("LEN == 2")
                pins = placedb.net2pin_map[net_idx]
                pin1 = pins[0]
                pin1_x = placedb.pin_offset_x[pin1] + placedb.node_x[placedb.pin2node_map[pin1]] 
                pin1_y = placedb.pin_offset_y[pin1] + placedb.node_y[placedb.pin2node_map[pin1]]
                pin2 = pins[1]
                pin2_x = placedb.pin_offset_x[pin2] + placedb.node_x[placedb.pin2node_map[pin2]] 
                pin2_y = placedb.pin_offset_y[pin2] + placedb.node_y[placedb.pin2node_map[pin2]]
                wl = abs(pin1_x - pin2_x) + abs(pin1_y - pin2_y)
                R = wl*r_per_u /1000
                C = wl*c_per_u / 1e-15
                #need to use self.net2pin_map sorted order, then use pin_direct, pin2node and name to index into the correct location...
                pin1 = placedb.net2pin_map[net_idx][0]
                pin2 = placedb.net2pin_map[net_idx][1]
                module1 = str(placedb.node_names[placedb.pin2node_map[pin1]])[2:-1].split(".")[0]

                module2 = str(placedb.node_names[placedb.pin2node_map[pin2]])[2:-1].split(".")[0]

                #print(self.wire2port2pin)
                #print(self.wire2port)

                #port1 = self.wire2port2pin[net][module1]
                #port2 = self.wire2port2pin[net][module2]

                port1 = str(self.wire2port_map[net][0])
                port2 = str(self.wire2port_map[net][1])
                #print(placedb.net2pin_map)
                #print(pin1,port1)
                #print(pin2,port2)


                direct1 = self.pin_direct(port1.split(":")[-1][0])
                direct2 = self.pin_direct(port2.split(":")[-1][0])
 
                #print(direct1)
                #print(direct2)
                #print(placedb.pin_direct[pin1])
                #print(placedb.pin_direct[pin2])
                #print( placedb.pin_direct  )
                #import sys
                #sys.exit()
                
                if net in self.mod2idx:
                    g.write("*D_NET *" + str(self.mod2idx[net]) + " " + str(C) + "\n")  
                else:
                    g.write("*D_NET " + net + " " + str(C) + "\n")  

                g.write("*CONN\n")
                g.write("*" + self.port_type[module1]  + " " + port1 + " " + direct1  + "\n")
                g.write("*" + self.port_type[module2]  + " " + port2 + " " + direct2  + "\n")

                g.write("*CAP\n")
                g.write("1 " + port1 + " " + str(C/2)  + "\n")
                g.write("2 " + port2 + " " + str(C/2)  + "\n")

                g.write("*RES\n")
                g.write("1 " + port1 + " " + port2 + " " +  str(R) + "\n")

                g.write("*END\n")
                g.write("\n")
 
                    
            else:
                continue
                #star model
                center_x = 0
                center_y = 0
                node_x = []
                node_y = []
                nodes_cap = []
                res = []
                for idx,pin in enumerate(placedb.net2pin_map[net_idx]):
                    x = placedb.pin_offset_x[pin] + placedb.node_x[placedb.pin2node_map[pin]]
                    y = placedb.pin_offset_y[pin] + placedb.node_y[placedb.pin2node_map[pin]] 

                    node_x.append(x)
                    node_y.append(y)
                    nodes_cap.append(0.0)
                    res.append(0.0)
                    
                caps = len(nodes_cap) 
                nodes_cap.append(0.0)
                node_x = np.array(node_x)
                node_y = np.array(node_y)
                nodes_cap = np.array(nodes_cap)
                res = np.array(res)
                ctr_x = np.mean(node_x)
                ctr_y = np.mean(node_y) 
                
                wl = np.abs(node_x - ctr_x) + np.abs(node_y - ctr_y)
                wl /= 1000.0
                R = wl*r_per_u /1000
                C = wl*c_per_u / 1e-15
                 
                total_cap = np.sum(C)
                res = R
                nodes_cap[-1] = total_cap/2.0
                
                #g.write('*D_NET ' + net + ' ' + str(total_cap) + '\n')

                if net in self.mod2idx:
                    g.write("*D_NET *" + str(self.mod2idx[net]) + " " + str(total_cap) + "\n")  
                else:
                    g.write("*D_NET " + net + " " + str(total_cap) + "\n")  



                g.write("*CONN\n")
                ports = []
                for idx,pin in enumerate(placedb.net2pin_map[net_idx]) :
                    module1 = str(placedb.node_names[placedb.pin2node_map[pin]])[2:-1].split(".")[0]
                    #port1 = self.wire2port2pin[net][module1]
                    port1 = self.wire2port_map[net][idx]
                    ports.append(port1)
                    direct1 = self.pin_direct(port1.split(":")[-1][0])
                    g.write("*" + self.port_type[module1]  + " " + port1 + " " + direct1  + "\n")

                g.write("*CAP\n")
                for idx in range(len(nodes_cap)):
                    if(idx < len(ports)):
                        port1 = ports[idx]
                        g.write(str(idx+1) + " " + port1 + " " + str(nodes_cap[idx]) + "\n")
                    else:
                        port1 = net+":"+str(idx+1)
                        ports.append(port1)
                        g.write(str(idx+1) + " " + port1 + " " + str(nodes_cap[idx]) + "\n")                 

                g.write("*RES\n")
                for idx, R in enumerate(res):
                    port1 = ports[idx]
                    port2 = ports[-1]
                    g.write(str(idx+1) +" " + port1 + " " + port2 + " " +  str(R) + "\n")

                g.write("*END\n")
                g.write("\n")


                continue
                #---------------------
                #major todos
                ######
                #用Flute给出的点做
                #边
                ######
                #wireload model
                pins = ""
                for idx,pin in enumerate(placedb.net2pin_map[net_idx]):
                    if(idx > 8):
                        break
                    pins += str(int(placedb.pin_offset_x[pin] + placedb.node_x[placedb.pin2node_map[pin]]*1000))
                    pins += " "
                    pins += str(int(placedb.pin_offset_y[pin] + placedb.node_y[placedb.pin2node_map[pin]]*1000))
                    pins += "\t" 
                with open("pin.tmp", "w") as tmp:
                    tmp.write(pins)
                #print(pins)
                os.system('cat pin.tmp | ~/DREAMPlace/thirdparty/flute-3.1/build/flute-tree > flute.tmp')
                #os.system('~/DREAMPlace/thirdparty/flute-3.1/build/flute-tree ' +   + ' > flute.tmp') 

                #分析flute.tmp
                nodes_x = []
                nodes_y = []
                nodes_n = []
                nodes_cap = {}  
                res = []

                with open("flute.tmp") as f:
                    for idx,l in enumerate(f.readlines()):
                        x, y, n = l.strip().split('\t')
                        nodes_x.append(float(x))
                        nodes_y.append(float(y))
                        nodes_n.append(int(n))
                        nodes_cap[idx] = 0.0
                        #print(x,y,n)

                #print(nodes_x)
                #print(nodes_y)
                #print(nodes_n)

                #todo convert into the SPEF format todos
                for idx in range(len(nodes_x)):
                    x = nodes_x[idx]
                    y = nodes_y[idx]
                    n = nodes_n[idx]
                    x2 = nodes_x[n]
                    y2 = nodes_y[n]
                    wl = abs(x - x2) + abs(y - y2)
                    wl /= 1000.0
                    R = wl*r_per_u /1000
                    C = wl*c_per_u / 1e-15
                    nodes_cap[idx] += C/2
                    nodes_cap[n] += C/2

                    res.append(R)
                    #print(wl) 
                #print(nodes_cap)
                total_cap = sum(nodes_cap.values()) 
                g.write('*D_NET ' + net + ' ' + str(total_cap) + '\n')
                g.write("*CONN\n")
                ports = []
                for pin in placedb.net2pin_map[net_idx]: 
                    module1 = str(placedb.node_names[placedb.pin2node_map[pin]])[2:-1]
                    port1 = self.wire2port2pin[net][module1]
                    ports.append(port1)
                    direct1 = self.pin_direct(port1.split(":")[-1][0])
                    g.write("*" + self.port_type[module1]  + " " + port1 + " " + direct1  + "\n")

                g.write("*CAP\n")
                for idx in range(len(res)):
                    if(idx < len(ports)):
                        port1 = ports[idx]
                        g.write(str(idx+1) + " " + port1 + " " + str(nodes_cap[idx]) + "\n")
                    else:
                        port1 = net+":"+str(idx+1)
                        ports.append(port1)
                        g.write(str(idx+1) + " " + port1 + " " + str(nodes_cap[idx]) + "\n")
 


                 

                g.write("*RES\n")
                for idx, R in enumerate(res):
                    port1 = ports[idx]
                    port2 = ports[nodes_n[idx]]
                g.write(str(idx+1) +" " + port1 + " " + port2 + " " +  str(R) + "\n")

                g.write("*END\n")
                g.write("\n")
 
        #end per-net spef
    
        g.close()
            
    def createSPEFfromDEF(self, spef_file, def_file, lef_file):
        #todos
        return

if __name__ == "__main__":
    import sys
    a = VerilogAnalyzer(sys.argv[1]) 
    print(a.wire2port)
