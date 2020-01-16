# Generic Verilog 2 DIMACS Converter

These python functions will convert a verilog circuit into a DIMACS format
compatible with a wide variety of SAT solvers. The conversion uses the [Tseytin transformation](https://en.wikipedia.org/wiki/Tseytin_transformation)

The verilog netlist must be in the generic gate format `<gate_type> <gate_name> (<output> <in0> [<in1> ...]);`

Example:
```verilog
nand NAND2_1 (N10, N1, N3,N6);
nor NAND2_2 (N11, N3, N6, N1);
or NAND2_3 (N16, N2, N11);
and NAND2_4 (N19, N11, N7);
```

To convert verilog, use `verilog2dimacs(path)`. This will return a list of DIMACS clauses and a dictionary mapping original net names to the DIMACS encoding and a dictionary mapping original net names to the DIMACS encodingg 

Constraints can be added to the encoding using `constrain(constraints,net_map,clauses)`

The clauses and mapping can be exported to a file through `write(top,net_map,clauses)`

The functions have been verified through simulation. The simulation exercises every possible input value to a circuit and checks that the DIMACS encoding is consistent.
The test requires cadical and Cadence xrun to be in `$PATH`

The test is run with `python verilogTseytin.py c17.v`
