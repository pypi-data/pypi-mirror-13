import django


def get_empty_value_display(model_admin):
    if django.VERSION >= (1, 9):
        return model_admin.get_empty_value_display()
    else:
        from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
        return EMPTY_CHANGELIST_VALUE
