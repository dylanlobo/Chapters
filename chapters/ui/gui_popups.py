""" Module containing generic/reusable GUI popups """

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from tkhtmlview import HTMLLabel
from typing import List, Dict


class EntryFieldsPopup:
    """class EntryFieldsPopup is a popup window that allows the user to enter values
    into one or more input fields"""

    def __init__(
        self,
        master: tk.Tk,
        popup_title: str = "",
        input_fields_parameters: List[List[str]] = [],
    ):
        self._master: tk.Tk = master
        self._popup_title = popup_title
        self._input_fields_parameters = input_fields_parameters
        self._input_fields_values = [
            tk.StringVar(value=field_param[1])
            for field_param in input_fields_parameters
        ]
        self._input_field_entries: List[ttk.Entry] = []
        self._input_fields_entry_values: Dict[ttk.Entry, tk.StringVar] = {}
        self._input_field_panels: List[ttk.LabelFrame] = []
        self._input_fields_return: List[str] = []
        self._construct_popup()

    def _create_input_panel(self):
        for i, field_param in enumerate(self._input_fields_parameters):
            self._input_field_panels.append(
                ttk.LabelFrame(master=self._popup, text=field_param[0], width=50)
            )
            self._input_field_entries.append(
                ttk.Entry(
                    master=self._input_field_panels[-1],
                    textvariable=self._input_fields_values[i],
                )
            )
            self._input_field_entries[-1].bind(
                "<Button-3>", self._handle_right_click_pressed
            )
            self._input_field_entries[-1].grid(padx=5, pady=5)
            self._input_field_panels[-1].grid(padx=5, pady=5)
        # Create a dictionary to lookup StringVars by their Entry widget
        self._input_fields_entry_values = dict(
            zip(self._input_field_entries, self._input_fields_values)
        )

    def _construct_popup(self):
        self._popup = tk.Toplevel(self._master)
        self._popup.title(self._popup_title)
        self._create_input_panel()
        self._create_button_panel()
        self._popup.resizable(width=False, height=False)
        self._popup.grid()
        # set to be on top of the main window
        self._popup.transient(self._master)
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()

    def get_response(self) -> str:
        self._master.wait_window(
            self._popup
        )  # pause anything on the main window until this one closes
        return self._input_fields_return

    def _create_button_panel(self):
        button_panel = ttk.Frame(master=self._popup)
        ok_button = ttk.Button(
            master=button_panel, text="OK", command=self._handle_ok_command
        )
        cancel_button = ttk.Button(
            master=button_panel, text="Cancel", command=self._handle_cancel_command
        )
        ok_button.grid(row=0, column=1, padx=10)
        cancel_button.grid(row=0, column=2, padx=10)
        self._input_field_entries[0].focus()
        button_panel.grid_columnconfigure(0, weight=1)
        button_panel.grid_rowconfigure(0, weight=1)
        button_panel.grid(padx=5, pady=5)
        self._popup.bind("<Return>", self._handle_ok_command)
        self._popup.bind("<Escape>", self._handle_cancel_command)

    def _handle_cancel_command(self, event=None):
        self._input_fields_return = None
        self._popup.destroy()

    def _handle_ok_command(self, event=None):
        self._input_fields_return = [
            input_field_value.get() for input_field_value in self._input_fields_values
        ]
        self._popup.destroy()

    def _handle_right_click_pressed(self, event):
        paste_text: str = self._master.clipboard_get()
        if paste_text:
            self._input_fields_entry_values[event.widget].set(paste_text)


class ListSelectionPopup:
    """The ListSelectionPopup class represents a popup window for selecting an item
    from a list."""

    def __init__(
        self,
        master: tk.Tk,
        popup_title: str,
        listbox_title: str,
        listbox_items: List[str],
    ):
        self._master: tk.Tk = master
        self._popup_title: str = popup_title
        self._listbox_title: str = listbox_title
        self._listbox_items: List[str] = listbox_items
        self._selected_item: str = None
        self._construct_popup()

    def _create_listbox_panel(self):
        listbox_panel = ttk.LabelFrame(master=self._popup, text=self._listbox_title)
        lb_height = 5
        self._listbox = tk.Listbox(
            master=listbox_panel,
            listvariable=tk.StringVar(value=self._listbox_items),
            width=20,
            height=lb_height,
        )
        self._listbox.grid(column=0, row=0, sticky="NWES")
        self._listbox.select_set(0)
        sv = ttk.Scrollbar(
            listbox_panel, orient=tk.VERTICAL, command=self._listbox.yview
        )
        sv.grid(column=1, row=0, sticky="NS")
        self._listbox["yscrollcommand"] = sv.set
        sh = ttk.Scrollbar(
            listbox_panel, orient=tk.HORIZONTAL, command=self._listbox.xview
        )
        sh.grid(column=0, row=1, sticky="EW")
        self._listbox["xscrollcommand"] = sh.set
        listbox_panel.grid_columnconfigure(0, weight=1)
        listbox_panel.grid_rowconfigure(0, weight=1)
        listbox_panel.grid(padx=0, pady=5)

    def _construct_popup(self):
        self._popup = tk.Toplevel(self._master)
        self._popup.title(self._popup_title)
        self._create_listbox_panel()
        self._create_button_panel()
        self._popup.resizable(width=False, height=False)
        self._popup.grid()
        # set to be on top of the main window
        self._popup.transient(self._master)
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()

    def get_response(self) -> str:
        self._master.wait_window(
            self._popup
        )  # pause anything on the main window until this one closes
        return self._selected_item

    def _create_button_panel(self):
        button_panel = ttk.Frame(master=self._popup)
        ok_button = ttk.Button(
            master=button_panel, text="Select", command=self._handle_select_command
        )
        cancel_button = ttk.Button(
            master=button_panel, text="Cancel", command=self._handle_cancel_command
        )
        ok_button.grid(row=0, column=1, padx=10)
        cancel_button.grid(row=0, column=2, padx=10)
        self._listbox.focus()
        button_panel.grid_columnconfigure(0, weight=1)
        button_panel.grid_rowconfigure(0, weight=1)
        button_panel.grid(padx=5, pady=5)
        self._popup.bind("<Return>", self._handle_select_command)
        self._popup.bind("<Escape>", self._handle_cancel_command)

    def _handle_cancel_command(self, event=None):
        self._selected_item = None
        self._popup.destroy()

    def _handle_select_command(self, event=None):
        self._selected_item = self._listbox.get(tk.ACTIVE)
        self._popup.destroy()


class HelpPopup:
    """
    The HelpPopup class represents a popup window for displaying application help .
    """

    def __init__(
        self,
        master: tk.Tk,
        title="Help",
        help_content="",
    ):
        self._master: tk.Tk = master
        self._content = tk.StringVar()
        self._help_title = title
        self._help_content = help_content

    def _create_message_box(self):
        self._popup = tk.Toplevel(self._master)
        self._popup.geometry("500x400")
        self._popup.grid_rowconfigure(0, weight=19)
        self._popup.grid_rowconfigure(1, weight=1)
        self._popup.grid_columnconfigure(0, weight=1)
        self._popup.title(self._help_title)
        self._create_message_panel()
        self._popup.bind("<Return>", self._handle_enter_pressed)
        self._popup.bind("<Escape>", self._handle_escape_pressed)
        self._popup.resizable(width=False, height=False)
        # set to be on top of the main window
        self._popup.transient(self._master)

    def _create_message_panel(self):
        self._help_input_panel = ScrolledFrame(master=self._popup, autohide=False)
        self._help_input_panel.grid(row=0, column=0, sticky="NWES")
        self._help_input_panel.grid_rowconfigure(0, weight=1)
        self._help_input_panel.grid_columnconfigure(0, weight=1)
        self._help_message_label = HTMLLabel(
            master=self._help_input_panel, html=self._help_content
        )
        self._help_message_label.grid(row=0, column=0, sticky="NWES")
        self._help_message_label.fit_height()

        button_panel = ttk.Frame(master=self._popup)
        button_panel.grid(row=1, column=0, sticky="NWES", pady=10)
        ok_button = ttk.Button(
            master=button_panel, text="OK", command=self._handle_ok_command
        )
        ok_button.pack()
        ok_button.focus()

    def _handle_ok_command(self):
        self._popup.destroy()

    def _handle_enter_pressed(self, event):
        self._handle_ok_command()

    def _handle_escape_pressed(self, event):
        self._handle_ok_command()

    def show_help(self) -> None:
        self._create_message_box()
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()
        self._master.wait_window(
            self._popup
        )  # pause anything on the main window until this one closes
        return None


class MessagePopup:
    """The MessagePopup class represents a popup window for displaying a message.
    The MessagePopup class is a simple way to display a message to the user in a
    popup window. It can be used to display error messages, confirmation messages,
    or any other type of message that requires user interaction.
    """

    def __init__(
        self,
        master: tk.Tk,
        title="Message",
        message_content_description="Message Details",
        message_content="",
    ):
        self._master: tk.Tk = master
        self._message = tk.StringVar()
        self._message_content_descrition = message_content_description
        self._message_title = title
        self._message_content = message_content

    def _create_message_box(self):
        self._popup = tk.Toplevel(self._master)
        self._popup.title(self._message_title)
        self._create_message_panel()
        self._popup.bind("<Return>", self._handle_enter_pressed)
        self._popup.bind("<Escape>", self._handle_escape_pressed)
        self._popup.resizable(width=False, height=False)
        self._popup.grid()
        # set to be on top of the main window
        self._popup.transient(self._master)

    def _create_message_panel(self):
        self._message_input_panel = ttk.LabelFrame(
            master=self._popup, text=self._message_content_descrition, width=70
        )
        self._error_message_label = ttk.Label(
            master=self._message_input_panel, textvariable=self._message
        )
        self._error_message_label.grid(padx=5, pady=5)
        self._message_input_panel.grid(padx=5, pady=5)

        button_panel = ttk.Frame(master=self._popup)
        ok_button = ttk.Button(
            master=button_panel, text="OK", command=self._handle_ok_command
        )
        ok_button.grid(row=0, column=1, padx=10)
        ok_button.focus()
        button_panel.grid_columnconfigure(0, weight=1)
        button_panel.grid_rowconfigure(0, weight=1)
        button_panel.grid(padx=5, pady=5)

    def _handle_ok_command(self):
        self._popup.destroy()

    def _handle_enter_pressed(self, event):
        self._handle_ok_command()

    def _handle_escape_pressed(self, event):
        self._handle_ok_command()

    def show_message(self, message: str | None = None) -> None:
        self._create_message_box()
        if message:
            self._message.set(message)
        else:
            self._message.set(self._message_content)
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()
        self._master.wait_window(
            self._popup
        )  # pause anything on the main window until this one closes
        return None


class ErrorMessagePopup:
    def __init__(
        self,
        master: tk.Tk,
    ):
        self._popup = MessagePopup(
            master=master,
            title="Error Message!",
            message_content_description="Error Details",
        )

    def show_message(self, message: str | None = None) -> None:
        self._popup.show_message(message=message)


class InfoMessagePopup:
    def __init__(
        self,
        master: tk.Tk,
    ):
        self._popup = MessagePopup(
            master=master,
            title="Information",
            message_content_description="Details",
        )

    def show_message(self, message: str | None = None) -> None:
        self._popup.show_message(message=message)
