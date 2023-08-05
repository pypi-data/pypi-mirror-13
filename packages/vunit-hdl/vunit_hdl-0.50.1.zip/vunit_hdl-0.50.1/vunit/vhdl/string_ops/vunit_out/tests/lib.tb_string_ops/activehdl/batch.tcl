source "d:/Programming/github/vunit/vunit/vhdl/string_ops/vunit_out/tests/lib.tb_string_ops/activehdl/common.tcl"
set failed [vunit_load]
if {$failed} {quit -code 1}
set failed [vunit_run]
if {$failed} {quit -code 1}
quit -code 0
