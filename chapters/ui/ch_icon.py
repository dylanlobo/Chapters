import tkinter as tk
from chapters.logger_config import logger


icondata = """
R0lGODlhQABAAIUAAAAAALe3t6ioqMfHx9XV1QQEBAAAAObm5pqamgAAAJeXl8bGxqenp7i4uNfX
1wcHB3Nzc7a2thgYGElJSYeHh8nJydnZ2eXl5ScnJzMzM6Ojo9bW1vT09CgoKEdHR19fX2hoaIiI
iIWFhcrKyh8fHzo6Ol1dXWNjY2FhYXNzc3t7e4mJibOzs729vcrKyunp6QAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAAALAAAAABAAEAAQAj/AAEI
HEiwoMGDCBMqXMiwocOHEBMWWHCg4gEOFyJE3MgRwEQCIEOKHAmyogUNHVMWYBCgpcuXMGPKDDBg
QIMVKREWUCCgp8+fQHsimJAgQQEDOSPuRMCUwoQHRg0gTUq1qtWrWK16cJG168CPJEOa1OgVYoEG
NdOqXctWLciTZQWunElX5tCiR8vuDMq0p1OoR6fGVSg18ODDiBMrXsy48UMDDjgc2KDCsVmKIy1u
AGFZ54KwYStW4Gz5LIG2qN0eIFDBQ+KzA+rKdpmWgIMWJLrOnc07gAAIEqJmnRu0OFDfwI3mHbzX
ONDkBZYz3su0LwIIGJQL7ixXAXbt3MOLux9Pvrz58+jTq19vtcOFFyzYD4RcEWOFDusnri5pEuV5
/aEdcEEF5YEFGn8bhBCegQeKdIADZDVmWmqoEbDaCAoqBhuFHFoIIWIbcijiACCNkIJeaPXGG4m2
RWjVbirOJsAJ0r3IUox0iZBddNvZ6JtzzrUkgAmASRXXSkA6J0IGePWoF09J+oTAB0U6yRyUQFLA
pHCl8VRddQJMWaV4S32pZZPmFYBAmCgEZxh6BpSApnx01mnnnXjaGRAAOw==
"""


def apply_icon(w):
    try:
        icon = tk.PhotoImage(data=icondata)
        w.iconphoto(True, icon)
    except Exception as e:
        logger().warning("Could not load icon due to:\n  ", e)
