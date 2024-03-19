def is_integer_value(var):
    if isinstance(var, (int, float)):
        if isinstance(var, float):
            return var.is_integer()
        else:
            return True
    else:
        raise ValueError("Input must be of type int or float.")
