print_log = False

def set_print_log(should_print):
    global print_log
    print_log = should_print

def log(message):
    if print_log:
        print(message)