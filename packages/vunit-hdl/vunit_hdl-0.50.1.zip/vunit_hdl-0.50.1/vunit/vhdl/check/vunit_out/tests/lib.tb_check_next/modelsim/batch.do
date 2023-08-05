do d:/Programming/github/vunit/vunit/vhdl/check/vunit_out/tests/lib.tb_check_next/modelsim/common.do
quietly set failed [vunit_load]
if {$failed} {quit -f -code 1}
quietly set failed [vunit_run]
if {$failed} {quit -f -code 1}
quit -f -code 0
