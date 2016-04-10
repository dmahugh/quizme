"""Module for widgets object.

The widgets object contains uniquely named references to widgets
that need to be accessed at runtime by other parts of the GUI.

Usage:

1) add "from widgetrefs import widgets"

2) when creating a widget that may need to be updated by other GUI elements
at runtime, save it as a property of the widgets object. For example:

    widgets.lblWeekday = ttk.Label(self, text="Monday")

3) When you need to refer to the widget later, use the widgets object.
For example:

    widgets.lblWeekday.configure(text="Tuesday")

"""
class widgets:
    pass
