
proc vunit_load {} {
    set vunit_generic_runner_cfg {active python runner : true,enabled_test_cases : Test strip,,Test rstrip,,Test lstrip,,Test count,,Test find,,Test image,,Test hex_image,,Test replace,,Test title,,Test upper,,Test lower,,Test split,,Test to_integer_string,,Test to_nibble_string,output path : d::/Programming/github/vunit/vunit/vhdl/string_ops/vunit_out/tests/lib.tb_string_ops/}
    set vsim_failed [catch {
        vsim  -g/tb_string_ops/runner_cfg=${vunit_generic_runner_cfg} -lib lib tb_string_ops test_fixture
    }]
    if {${vsim_failed}} {
        return 1
    }

    global breakassertlevel
    set breakassertlevel 2

    global builtinbreakassertlevel
    set builtinbreakassertlevel $breakassertlevel

    set no_vhdl_test_runner_exit [catch {examine /run_base_pkg/runner.exit_simulation}]
    if {${no_vhdl_test_runner_exit}}  {
        echo {Error: No vunit test runner package used}
        return 1
    }
    return 0
}

proc vunit_run {} {
    set has_vhdl_runner [expr ![catch {examine /run_base_pkg/runner}]]

    if {${has_vhdl_runner}} {
        set status_boolean "/run_base_pkg/runner.exit_without_errors"
        set true_value 1
    } else {
        echo "No finish mechanism detected"
        return 1;
    }

    run -all
    set failed [expr [examine ${status_boolean}]!=${true_value}]
    if {$failed} {
        catch {
            # tb command can fail when error comes from pli
            echo ""
            echo "Stack trace result from 'bt' command"
            bt
        }
    }
    return $failed
}
