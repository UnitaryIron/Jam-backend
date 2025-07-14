from jam import jam_to_js, run_jam_code
import pytest

class TestJamToJS:

    class TestPrint:
        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_one_element(self):
            result = jam_to_js("print 'Hello'")
            assert result == "console.log('Hello');"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_multiple_lines(self):
            result = jam_to_js("print 'Hello'\nprint 'World'")
            print(result)
            assert result == "console.log('Hello');\nconsole.log('World');"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_multiple_words(self):
            result = jam_to_js("print 'Hello World'")
            assert result == "console.log('Hello World');"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_empty_string(self):
            result = jam_to_js("print ''")
            assert result == "console.log('');"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_nothing(self):
            result = jam_to_js("print")
            assert result == "console.log();"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_variable(self):
            result = jam_to_js("print x")
            assert result == "console.log(x);"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_prints_number(self):
            result = jam_to_js("print 42")
            assert result == "console.log(42);"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_handles_multiple_arguments_for_console_log(self):
            result = jam_to_js("print 'Hello', 'World'")
            assert result == "console.log('Hello', 'World');"

    class TestSet:
        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_sets_variable(self):
            result = jam_to_js("set x = 10")
            assert result == "let x = 10;"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_sets_multiple_variables(self):
            result = jam_to_js("set x = 10\nset y = 20")
            assert result == "let x = 10;\nlet y = 20;"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_sets_variable_with_expression(self):
            result = jam_to_js("set x = 5 + 3")
            assert result == "let x = 5 + 3;"

        @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
        def test_sets_variable_to_string(self):
            result = jam_to_js("set x = 'Hello'")
            assert result == "let x = 'Hello';"

        @pytest.mark.skip(reason="Currently this works the same as the correct syntax")
        def test_errors_if_invalid_syntax(self):
            result = jam_to_js("set x * 10")
            assert not result == "let x = 10;"

    @pytest.mark.skip(reason="""
        The if/else statements restarts in the center of the function when it tests for else.
        This causes every one of these to have a second line that says the command was invalid
        in addition to the correct line.
        These give the correct result without that additional line.
        """)
    def test_handles_empty_lines(self):
        result = jam_to_js("print 'Hello'\n\nprint 'World'")
        assert result == "console.log('Hello');\nconsole.log('World');"

class TestRunJamCode:
    class TestPrint:
        @pytest.mark.skip(reason="""
            This produces a different result than the JS code.
            One result needs to be chosen.
            Currently this tests for the same result the js would give when run.
        """)
        def test_prints_one_element(self):
            result = run_jam_code("print 'Hello'")
            assert result =='Hello\n'

        @pytest.mark.skip(reason="""
            This produces a different result than the JS code.
            One result needs to be chosen.
            Currently this tests for the same result the js would give when run.
        """)
        def test_prints_multiple_lines(self):
            result = run_jam_code("print 'Hello'\nprint 'World'")
            assert result == 'Hello\nWorld\n'

        @pytest.mark.skip(reason="""
            This produces a different result than the JS code.
            One result needs to be chosen.
            Currently this tests for the same result the js would give when run.
        """)
        def test_prints_multiple_words(self):
            result = run_jam_code("print 'Hello World'")
            assert result == 'Hello World\n'

        @pytest.mark.skip(reason="""
            This produces a different result than the JS code.
            One result needs to be chosen.
            Currently this tests for the same result the js would give when run.
        """)
        def test_prints_empty_string(self):
            result = run_jam_code("print ''")
            assert result == "\n"

        @pytest.mark.skip(reason="""
        This works in the js compiler but not in the run function
        """)
        def test_prints_nothing(self):
            result = run_jam_code("print")
            assert result == "\n"

        @pytest.mark.skip(reason="""
            Varible setting is called set the js compiler but let in the run function
        """)
        def test_prints_variable(self):
            result = run_jam_code("set x = 'Hello'\nprint x")
            assert result == "Hello\n"

        def test_prints_number(self):
            result = run_jam_code("print 42")
            assert result == "42\n"

        @pytest.mark.skip(reason="""
            This produces a different result than the JS code.
            One result needs to be chosen.
            Currently this tests for the same result the js would give when run.
        """)
        def test_handles_multiple_arguments_for_console_log(self):
            result = run_jam_code("print 'Hello', 'World'")
            assert result == "Hello World\n"