"""
Handy utilities for working with Formsets
"""


def add_form_kwargs(formset_kwargs, **form_kwargs):
    """Add the form_kwargs to formset_kwargs['form_kwargs']"""
    kwargs = formset_kwargs.get("form_kwargs", {})
    kwargs.update(form_kwargs)
    formset_kwargs["form_kwargs"] = kwargs
    return formset_kwargs
