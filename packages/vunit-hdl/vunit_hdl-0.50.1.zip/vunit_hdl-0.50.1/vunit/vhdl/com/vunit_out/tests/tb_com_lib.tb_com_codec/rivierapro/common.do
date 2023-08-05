
proc vunit_help {} {
    echo {List of VUnit commands:}
    echo {vunit_help}
    echo {  - Prints this help}
    echo {vunit_load}
    echo {  - Load design with correct generics for the test}
    echo {  - Optional first argument are passed as extra flags to vsim}
    echo {vunit_run}
    echo {  - Run test, must do vunit_load first}
}

proc vunit_load {} {
    set vsim_failed [catch {
        vsim  -g/tb_com_codec/runner_cfg="enabled_test_cases : Test that integer can be encoded and decoded,,Test that real can be encoded and decoded,,Test that time can be encoded and decoded,,Test that boolean can be encoded and decoded,,Test that bit can be encoded and decoded,,Test that std_ulogic can be encoded and decoded,,Test that severity_level can be encoded and decoded,,Test that file_open_status can be encoded and decoded,,Test that file_open_kind can be encoded and decoded,,Test that character can be encoded and decoded,,Test that string can be encoded and decoded,,Test that boolean_vector can be encoded and decoded,,Test that bit_vector can be encoded and decoded,,Test that integer_vector can be encoded and decoded,,Test that real_vector can be encoded and decoded,,Test that time_vector can be encoded and decoded,,Test that std_ulogic_vector can be encoded and decoded,,Test that complex can be encoded and decoded,,Test that complex_polar can be encoded and decoded,,Test that unsigned from numeric_bit can be encoded and decoded,,Test that signed from numeric_bit can be encoded and decoded,,Test that unsigned from numeric_std can be encoded and decoded,,Test that signed from numeric_std can be encoded and decoded,,Test that ufixed can be encoded and decoded,,Test that sfixed can be encoded and decoded,,Test that float can be encoded and decoded,,Test that custom enumeration type can be encoded and decoded,,Test that custom record type can be encoded and decoded,,Test that custom array can be encoded and decoded,,Test that all provided codecs can be used within a composite,,Test that the values of different enumeration types used for msg_type record elements get different encodings,,Test that records with different msg_type enumeration types can classified with a single get_msg_type function,,Test that records containing arrays can be encoded and decoded,output path : d::/Programming/github/vunit/vunit/vhdl/com/vunit_out/tests/tb_com_lib.tb_com_codec/,active python runner : true" -lib tb_com_lib tb_com_codec test_fixture
    }]
    if {${vsim_failed}} {
        return 1
    }

    set no_vhdl_test_runner_exit [catch {examine /vunit_lib.run_base_pkg/runner.exit_simulation}]
    set no_verilog_test_runner_exit [catch {examine /\\package vunit_lib.vunit_pkg\\/__runner__}]
    if {${no_vhdl_test_runner_exit} && ${no_verilog_test_runner_exit}}  {
        echo {Error: No vunit test runner package used}
        return 1
    }
    return 0
}

proc vunit_run {} {
    vhdlassert.break error
    vhdlassert.break -builtin error

    proc on_break {} {
        resume
    }
    onbreak {on_break}

    set has_vhdl_runner [expr ![catch {examine /vunit_lib.run_base_pkg/runner}]]
    set has_verilog_runner [expr ![catch {examine /\\package vunit_lib.vunit_pkg\\/__runner__}]]

    if {${has_vhdl_runner}} {
        set status_boolean "/vunit_lib.run_base_pkg/runner.exit_without_errors"
        set true_value true
    } elseif {${has_verilog_runner}} {
        set status_boolean "/\\package vunit_lib.vunit_pkg\\/__runner__.exit_without_errors"
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
