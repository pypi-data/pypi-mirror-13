do d:/Programming/github/vunit/vunit/vhdl/run/vunit_out/tests/tb_run_lib.tb_run/modelsim/common.do
quietly set failed [vunit_load]
if {$failed} {quit -f -code 1}
quietly set failed [vunit_run]
if {$failed} {quit -f -code 1}
quit -f -code 0
