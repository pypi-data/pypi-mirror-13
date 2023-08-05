
source "d:/Programming/github/vunit/vunit/vhdl/string_ops/vunit_out/tests/lib.tb_string_ops/activehdl/common.tcl"
workspace create workspace
design create -a design .
vmap vunit_lib d:/Programming/github/vunit/vunit/vhdl/string_ops/vunit_out/activehdl/libraries/vunit_lib
vmap lib d:/Programming/github/vunit/vunit/vhdl/string_ops/vunit_out/activehdl/libraries/lib

vunit_load
puts "VUnit help: Design already loaded. Use run -all to run the test."
