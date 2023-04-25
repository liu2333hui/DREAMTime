# DREAMTime

Timing-Driven Placement , similar to work done by [1]P. Liao, S. Liu, Z. Chen, W. Lv, Y. Lin and B. Yu, "DREAMPlace 4.0: Timing-driven Global Placement with Momentum-based Net Weighting," 2022 Design, Automation & Test in Europe Conference & Exhibition (DATE), Antwerp, Belgium, 2022, pp. 939-944.

To use-it, OpenTimer should be installed (the static timing analyzer tool).
https://github.com/OpenTimer/OpenTimer/tree/master/example
Furthermore, DREAMPlace should be compiled according to the original work.
https://github.com/limbo018/DREAMPlace

Flute is included in the thirdparty folder as well as the detailed placer.
Sample json hyper-parameters are in benchmarks.

Benchmarks were downloaded from the open-source ICCAD15 timing-driven placement circuits:
http://iccad-contest.org/2015/problem_C/default.html#BENCHMARKS

The main added python scripts for timing-driven placement are :
DREAMTimer.py and DREAMVerilog.py , both under dreamplace.
The Placer.py is also modified slightly and PlaceDB.py (which has the main calls and flow for optimization).

DREAMTimer.py interfaces with the OpenTimer STA tool, and also "cleans" the sdc files. Outputs are also read and converted into appropriate weights here.

DREAMVerilog.py interfaces with the Flute tool, and also has an internal Star-based generator for RC parasitics. 
This script is mainly for generating the SPEF parasitic file, reading the verilog to get net2pin detailed mappings.

The PlaceDB.py "__call__" function is also modified to load in the weights from the timing analysis. 
