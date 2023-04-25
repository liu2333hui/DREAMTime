
import re

def drawMacro(gui, 角1, 角2, 可动 = True):

    if(not 可动):
        color = 0xFF0000
    else:
        color = 0x00FF00
    
    gui.triangle([角1[0],角1[1]], [角1[0], 角2[1]],[角2[0], 角1[1]], color=color)
    gui.triangle([角2[0],角2[1]], [角1[0], 角2[1]],[角2[0], 角1[1]], color=color)
    gui.rect(角1, 角2, radius=2)





def readDEF(def_file, verbose = True):
    state = 0

    components = 0
    cells = []
    可动s = []
    locs = []
    unit = 1
    area = []
    
    with open(def_file) as f:
        lines = f.readlines()
        i = 0
        while(i < len(lines)):
            l = lines[i]


            if("UNITS" in l):
                unit = float(l.split()[3])
            elif("DIEAREA" in l):
                area = [float(l.split()[6])/unit , float(l.split()[7])/unit]
            elif (state == 0):
                if "COMPONENTS" in l:
                    components = int(l.split()[1])
                    state = 1
            elif (state == 1):


                if "END COMPONENT" in l:
                    state = 2
                    continue
                #e.sub(r"", "", lines)
                cells.append(l.strip().split()[2])

                
                l = lines[i+1]
                ll = l.strip().split()
                if(ll[1] == "PLACED"):
                    可动 = True
                else:
                    可动 = False
                    
                可动s.append(可动)
                locs.append([int(ll[3]) / unit, int(ll[4])/ unit])
                
                i+=1
                

            elif (state == 2):
                break

            i+=1

    if verbose:    
        print(cells)
        print(locs)
        print(可动s)
        print(area)

    return cells, locs , 可动s , area


def readLEF(lef_file, verbose = True):
    state = 0
    macros = {}
    
    components = ""
    with open(lef_file) as f:
        lines = f.readlines()
        i = 0
        while(i < len(lines)):
            l = lines[i]
            #print(state, l)
            if (state == 0):
                if "MACRO" in l:
                    components = (l.split()[1])
                    macros[components] = []
                    state = 1

                if("END LIBRARY" in l):
                    state = 2
            elif (state == 1):

                if "SIZE" in l:
                    ll = l.strip().split()
                    macros[components].append(float(ll[1]))
                    macros[components].append(float(ll[3]))
                    
                if "END "+components in l:
                    state = 0
                    
            elif (state == 2):
                break

            i+=1

    if verbose:
        print(macros)
    return macros

#results\simple
#simple.def
cells, locs , 可动s , area = readDEF("results/simple/simple.gp.def", verbose = False)

macros = readLEF("simple.lef", verbose = False)

for idx, cell in enumerate(cells):

    x1 = locs[idx][0]
    y1 = locs[idx][1]

    x2 = x1 + macros[cell][0]
    y2 = y1 + macros[cell][1]

    x1 /= area[0]
    x2 /= area[0]
    y1 /= area[1]
    y2 /= area[1]

    print(cell, [x1,y1], [x2,y2])

area[0] = area[0]*1.5
area[1] = area[1]*1.5
        
import taichi as ti

gui = ti.GUI('Hello World!', (640, 640))
while gui.running:

    for idx, cell in enumerate(cells):

        x1 = locs[idx][0]# - macros[cell][0]/2
        y1 = locs[idx][1]# - macros[cell][1]/2

        x2 = x1 + macros[cell][0]
        y2 = y1 + macros[cell][1]


        x1 /= area[0]
        x2 /= area[0]
        y1 /= area[1]
        y2 /= area[1]

        #print(cell, [x1,y1], [x2,y2])
        
        drawMacro(gui, [x1,y1], [x2, y2], 可动 = 可动s[idx])


    #drawMacro(gui, [0.1,0.1], [0.8,0.8], 可动 = True)
    
    #g#ui.rect([0.1,0.1], [0.8,0.8])
    #gui.rect([0.2,0.2], [0.1,0.1])
    gui.show()
