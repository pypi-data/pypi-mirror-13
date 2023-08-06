from django.utils.translation import ugettext as _

def form_errors_output(form):
    error_list = []
    for e,v in form.errors.items():
        if e.startswith('__'):
            title = ""
        else:
            title = _(e.title()) + ": "
        if isinstance(v, list):
            error_list.append(title + "\n".join(v))
        else:
            error_list.append(title + "\n".join([v]))
    return "\n".join(error_list)
