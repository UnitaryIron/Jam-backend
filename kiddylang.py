def run_jam_code(code: str) -> str:
    import io
    import sys
    import random
    import math
    import time
    import pyttsx3

    global output_buffer
    output_buffer = ""
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
        if expr in variables:
            return variables[expr]
        elif expr.startswith('"') and expr.endswith('"'):
            return expr.strip('"')
        elif expr == "true":
            return True
        elif expr == "false":
            return False
        elif expr.startswith("[") and expr.endswith("]"):
            return eval(expr)
        else:
            try:
                return int(expr)
            except:
                try:
                    return float(expr)
                except:
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
                parts = line[4:].split(" = ", 1)
                if len(parts) == 2:
                    variables[parts[0].strip()] = eval_expr(parts[1].strip())

            elif line.startswith("print "):
                to_print = line[6:].strip()
                print(eval_expr(to_print))

            elif line.startswith("say "):
                to_say = line[4:].strip()
                say(eval_expr(to_say))

            elif line.startswith("ask "):
                print("ask is not supported in web version")

            elif line.startswith("add "):
                parts = line[4:].split(" and ", 1)
                if len(parts) == 2:
                    a = eval_expr(parts[0].strip())
                    subparts = parts[1].split(" into ", 1)
                    if len(subparts) == 2:
                        b = eval_expr(subparts[0].strip())
                        variables[subparts[1].strip()] = a + b

            elif line.startswith("multiply "):
                parts = line[9:].split(" and ", 1)
                if len(parts) == 2:
                    a = eval_expr(parts[0].strip())
                    subparts = parts[1].split(" into ", 1)
                    if len(subparts) == 2:
                        b = eval_expr(subparts[0].strip())
                        variables[subparts[1].strip()] = a * b

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
                parts = line[len("random between "):].split(" and ", 1)
                if len(parts) == 2:
                    a = int(eval_expr(parts[0]))
                    b = int(eval_expr(parts[1]))
                    print(random.randint(a, b))

            elif line.startswith("wait "):
                pass  # skip wait for browser safety

            elif line.startswith("choose from "):
                parts = line[len("choose from "):].split(" into ", 1)
                if len(parts) == 2:
                    items = [s.strip('"\' ') for s in parts[0].split(",")]
                    chosen = random.choice(items)
                    variables[parts[1].strip()] = chosen

            elif line.startswith("function "):
                name = line.split()[1]
                i += 1
                body = []
                while i < len(lines) and not lines[i].strip() == "}":
                    body.append(lines[i])
                    i += 1
                functions[name] = body

            elif line.startswith("call "):
                name = line.split()[1]
                if name in functions:
                    run_program(functions[name])
                    variables["last_return"] = last_return

            elif line.startswith("repeat "):
                parts = line.split()
                if len(parts) >= 2:
                    count = int(eval_expr(parts[1]))
                    i += 1
                    block = []
                    while i < len(lines) and not lines[i].strip() == "}":
                        block.append(lines[i])
                        i += 1
                    for _ in range(count):
                        run_program(block)

            elif line.startswith("if "):
                condition = line[3:].split("{")[0].strip()
                i += 1
                block = []
                while i < len(lines) and not lines[i].strip() == "}":
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

    try:
        lines = code.strip().split("\n")
        run_program(lines)
        sys.stdout = sys.__stdout__
        return output.getvalue()
    except Exception as e:
        sys.stdout = sys.__stdout__
        return f"Error: {str(e)}"

    lines = code.strip().splitlines()
    run_program(lines)

    sys.stdout = sys.__stdout__
    return output.getvalue()
