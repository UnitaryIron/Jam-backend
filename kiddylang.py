def jam_to_js(jam_code: str) -> str:
    lines = jam_code.strip().split('\n')
    js_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        tokens = line.split()

        if not tokens:
            i += 1
            continue

        if tokens[0] == "print":
            content = ' '.join(tokens[1:])
            js_lines.append(f'console.log({content});')

        elif tokens[0] == "set":
           var_name = tokens[1]
           value = ' '.join(tokens[3:])
           js_lines.append(f'let {var_name} = {value};')

        elif tokens[0] == "otherwise":
          condition = ' '.join(tokens[1:]).split('{')[0].strip()
          i += 1
          block = []
          while i < len(lines) and lines[i].strip() != "}":
            block.append(lines[i].strip())
            i += 1
          js_lines.append(f'else if ({condition}) {{')
          js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
          js_lines.append('}')

        elif tokens[0] == "if":
    # Parse condition with explicit block structure
          condition = ' '.join(tokens[1:]).split('{')[0].strip()
          i += 1
          block = []
          while i < len(lines) and lines[i].strip() != "}":
           block.append(lines[i].strip())
           i += 1
          js_lines.append(f'if ({condition}) {{')
          js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
          js_lines.append('}')

            # Check for else/elif
        if i + 1 < len(lines) and lines[i+1].strip().startswith("else"):
                i += 1
                line = lines[i].strip()
                if line.startswith("else if"):
                    # Handle else if
                    condition = line[7:].split('{')[0].strip()
                    i += 1
                    block = []
                    while i < len(lines) and lines[i].strip() != "}":
                        block.append(lines[i].strip())
                        i += 1
                    js_lines.append(f'else if ({condition}) {{')
                    js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
                    js_lines.append('}')
                else:
                    # Handle plain else
                    i += 1
                    block = []
                    while i < len(lines) and lines[i].strip() != "}":
                        block.append(lines[i].strip())
                        i += 1
                    js_lines.append('else {')
                    js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
                    js_lines.append('}')

        elif tokens[0] == "function":
            # Named functions
            if tokens[1] == "anonymous":
                # Lambda support
                params = ' '.join(tokens[2:]).split('{')[0].strip()
                i += 1
                block = []
                while i < len(lines) and lines[i].strip() != "}":
                    block.append(lines[i].strip())
                    i += 1
                js_lines.append(f'({params}) => {{')
                js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
                js_lines.append('}')
            else:
                # Regular named function
                name = tokens[1]
                params = ' '.join(tokens[2:]).split('{')[0].strip()
                i += 1
                block = []
                while i < len(lines) and lines[i].strip() != "}":
                    block.append(lines[i].strip())
                    i += 1
                js_lines.append(f'function {name}({params}) {{')
                js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
                js_lines.append('}')

        elif tokens[0] == "map":
            # Higher-order function support
            func = tokens[1]
            data = ' '.join(tokens[3:])
            js_lines.append(f'{data}.map({func})')

        elif tokens[0] == "repeat":
            count = tokens[1]
            i += 1
            block = []
            while i < len(lines) and lines[i].strip() != "}":
                block.append(lines[i].strip())
                i += 1

            js_lines.append(f'for (let i = 0; i < {count}; i++) {{')
            js_lines += ['  ' + line for line in jam_to_js('\n'.join(block)).split('\n')]
            js_lines.append('}')

        else:
            js_lines.append(f'// Unknown Jam command: {line}')

        i += 1

    return '\n'.join(js_lines)
def run_jam_code(code: str) -> str:
    import io
    import sys
    import random
    import math
    import time
    import pyttsx3

    variables = {}
    lists = {}
    functions = {}
    timer_start = None
    last_return = None

    output = io.StringIO()
    sys.stdout = output

    def say(text):
        print(f"(say): {text}")

    def eval_expr(expr):
        expr = expr.strip()

        # Boolean values
        if expr == "true":
            return True
        if expr == "false":
            return False

        # Quoted string
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        # Check if it's a list
        if expr.startswith("[") and expr.endswith("]"):
            expr = expr[1:-1]
            items = [eval_expr(item.strip()) for item in expr.split(",")]
            return items

        # Integer
        if expr.isdigit() or (expr.startswith("-") and expr[1:].isdigit()):
            return int(expr)

        # Float
        if "." in expr:
            parts = expr.split(".")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return float(expr)

        # Variable reference
        if expr in variables:
            return variables[expr]

        # Fallback: treat as plain string
        return expr

    def eval_condition(condition):
        try:
            for var in variables:
                condition = condition.replace(var, repr(variables[var]))
            condition = condition.replace("true", "True").replace("false", "False")
            return eval(condition)
        except:
            return False

    def run_program(lines):
        nonlocal timer_start, last_return
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line == "" or line.startswith("#"):
                i += 1
                continue

            if line.startswith("let "):
                parts = line[4:].split(" = ")
                variables[parts[0].strip()] = eval_expr(parts[1].strip())

            elif line.startswith("print "):
               to_print = line[6:].strip()
               val = eval_expr(to_print)
               print(val)

            elif line.startswith("say "):
                to_say = line[4:].strip()
                say(eval_expr(to_say))

            elif line.startswith("ask "):
                print("ask is not supported in web version")

            elif line.startswith("add "):
                parts = line[4:].split(" and ")
                a = eval_expr(parts[0].strip())
                b, var = parts[1].split(" into ")
                b = eval_expr(b.strip())
                variables[var.strip()] = a + b

            elif line.startswith("multiply "):
                parts = line[9:].split(" and ")
                a = eval_expr(parts[0].strip())
                b, var = parts[1].split(" into ")
                b = eval_expr(b.strip())
                variables[var.strip()] = a * b

            elif line.startswith("length of "):
                name = line[len("length of "):].strip()
                print(len(str(eval_expr(name))))

            elif line.startswith("uppercase "):
                name = line[len("uppercase "):].strip()
                print(str(eval_expr(name)).upper())

            elif line.startswith("lowercase "):
                name = line[len("lowercase "):].strip()
                print(str(eval_expr(name)).lower())

            elif line.startswith("reverse "):
                name = line[len("reverse "):].strip()
                print(str(eval_expr(name))[::-1])

            elif line.startswith("square of "):
                num = eval_expr(line[len("square of "):].strip())
                print(num ** 2)

            elif line.startswith("sqrt of "):
                num = eval_expr(line[len("sqrt of "):].strip())
                print(math.sqrt(num))

            elif line.startswith("random between "):
                parts = line[len("random between "):].split(" and ")
                a = int(eval_expr(parts[0]))
                b = int(eval_expr(parts[1]))
                print(random.randint(a, b))

            elif line.startswith("wait "):
                pass  # skip wait for browser safety

            elif line.startswith("choose from "):
                list_part, var_part = line.split("into")
                items = [s.strip('" ') for s in list_part.split("from")[1].strip().split(",")]
                chosen = random.choice(items)
                variables[var_part.strip()] = chosen

            elif line.startswith("function "):
                name = line.split(" ")[1]
                i += 1
                body = []
                while not lines[i].strip() == "}":
                    body.append(lines[i])
                    i += 1
                functions[name] = body

            elif line.startswith("call "):
                name = line.split(" ")[1]
                run_program(functions[name])
                variables["last_return"] = last_return

            elif line.startswith("repeat "):
                count = int(eval_expr(line.split(" ")[1]))
                i += 1
                block = []
                while not lines[i].strip() == "}":
                    block.append(lines[i])
                    i += 1
                for _ in range(count):
                    run_program(block)

            elif line.startswith("if "):
                condition = line[3:].split("{")[0].strip()
                i += 1
                block = []
                while not lines[i].strip() == "}":
                    block.append(lines[i])
                    i += 1
                if eval_condition(condition):
                    run_program(block)

            elif line.startswith("timer start"):
                timer_start = time.time()

            elif line.startswith("timer stop"):
                if timer_start:
                    elapsed = time.time() - timer_start
                    print(f"Time elapsed: {elapsed:.2f} seconds")

            else:
                print(f"Unknown command: {line}")
            i += 1

    lines = code.strip().splitlines()
    run_program(lines)

    sys.stdout = sys.__stdout__
    return output.getvalue()

if __name__ == "__main__":
    jam_code = """
    set x = 5
    if x > 3 {
        print "Hello"
    } else if x < 2 {
        print "Small"
    } else {
        print "Medium"
    }
    
    function anonymous (n) {
        return n * 2
    }
    
    set numbers = [1, 2, 3]
    set doubled = map (n) => n * 2 over numbers
    print doubled
    """
    
    js_code = jam_to_js(jam_code)
    print("Generated JavaScript:\n")
    print(js_code)
