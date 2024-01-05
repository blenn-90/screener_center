format_2decimal = "{:.2f}"
format_4decimal = "{:.4f}"

def fun_format_2decimal(value):
    return format_2decimal.format(value)

def fun_format_4decimal(value):
    return format_4decimal.format(value)

def get_change_perc(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')