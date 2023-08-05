do d:/Programming/github/vunit/vunit/vhdl/logging/vunit_out/tests/lib.tb_logging/modelsim/common.do
quietly set failed [vunit_load]
if {$failed} {quit -f -code 1}
quietly set failed [vunit_run]
if {$failed} {quit -f -code 1}
quit -f -code 0
