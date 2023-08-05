def series_to_gtk_form(series, title=''):
    '''
    Generate an editable GTK form based on a pandas Series. Returns
    a flag specifying whether or not the form responses are valid and a
    dictionary containing the updated values.
    
    Note that this function requires the flatland and wheeler.pygtkhelpers
    packages.
    '''
    from flatland import Boolean, Form, String, Integer, Float
    from pygtkhelpers.ui.extra_dialogs import FormViewDialog
     
    schema_entries = []
    settings = {}
    for k, v in series.iteritems():
        settings[k] = v
        if type(v) == int:
            schema_entries.append(
                Integer.named(k).using(
                    default=settings[k], optional=True),
            )
        elif type(v) == float:
            schema_entries.append(
                Float.named(k).using(
                    default=settings[k], optional=True),
            )
        elif type(v) == bool:
            schema_entries.append(
                Boolean.named(k).using(
                    default=settings[k], optional=True),
            )
        elif type(v) == str:
            schema_entries.append(
                String.named(k).using(
                    default=settings[k], optional=True),
            )
            
    form = Form.of(*schema_entries)
    dialog = FormViewDialog(title)
    valid, response = dialog.run(form)
    return valid, response