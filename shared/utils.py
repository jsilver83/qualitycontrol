def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def remove_bullet_numbering(string_value, delimiter='-'):
    string_value = str(string_value)
    if string_value and len(string_value.split(delimiter)) > 1:
        return string_value.split(delimiter)[1].strip()
    else:
        return string_value
