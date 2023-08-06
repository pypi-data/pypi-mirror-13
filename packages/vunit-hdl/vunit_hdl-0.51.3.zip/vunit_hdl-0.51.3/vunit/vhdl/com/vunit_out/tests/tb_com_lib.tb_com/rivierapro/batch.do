onerror {quit -code 1}
source "d:/Programming/github/vunit/vunit/vhdl/com/vunit_out/tests/tb_com_lib.tb_com/rivierapro/common.do"
set failed [vunit_load]
if {$failed} {quit -code 1}
set failed [vunit_run]
if {$failed} {quit -code 1}
quit -code 0
