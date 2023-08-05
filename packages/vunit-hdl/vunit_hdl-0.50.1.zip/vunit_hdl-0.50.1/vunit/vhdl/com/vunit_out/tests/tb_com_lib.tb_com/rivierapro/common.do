
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
        vsim  -g/tb_com/runner_cfg="enabled_test_cases : Test that named actors can be created,,Test that no name actors can be created,,Test that two actors of the same name cannot be created,,Test that a created actor can be found,,Test that an actor not created is found and its creation is deferred,,Test that deferred creation can be suppressed when an actor is not found,,Test that a created actor get the correct inbox size,,Test that a created actor can be destroyed,,Test that a non-existing actor cannot be destroyed,,Test that all actors can be destroyed,,Test that an actor can send a message to another actor,,Test that an actor can send a message in response to another message from an a priori unknown actor,,Test that an actor can send a message to itself,,Test that an actor can poll for incoming messages,,Test that sending to a non-existing actor results in an error code,,Test that an actor can send to an actor with deferred creation,,Test that receiving from an actor with deferred creation results in an error code,,Test that empty messages can be sent,,Test that an actor can publish messages to multiple subscribers,,Test that a subscriber can unsubscribe,,Test that a destroyed subscriber is not addressed by the publisher,,Test that an actor can only subscribe once to the same publisher,,Test that each message gets an increasing message number,,Test that a client can wait for a specific request reply from a server even if it is not the first message to arrive,,Test that a synchronous request can be made,,Test that a receiver is protected from flooding by creating a bounded inbox,,Test that publish skip sending messages to subscribers with full inboxes,output path : d::/Programming/github/vunit/vunit/vhdl/com/vunit_out/tests/tb_com_lib.tb_com/,active python runner : true" -lib tb_com_lib tb_com test_fixture
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
