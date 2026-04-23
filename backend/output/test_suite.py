import pytest
import tkinter as tk
from tkinter import messagebox
from unittest.mock import MagicMock

class Calculator:
    """
    A simple calculator using tkinter module.
    """

    def __init__(self, master: tk.Tk) -> None:
        """
        Initializes the calculator.

        Args:
            master (tk.Tk): The main window.
        """
        self.master = master
        self.entry = tk.Entry(master, width=35, borderwidth=5)
        self.entry.grid(row=0, column=0, columnspan=4)
        self.create_buttons()

    def create_buttons(self) -> None:
        """
        Creates the buttons for the calculator.
        """
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row_val = 1
        col_val = 0

        for button in buttons:
            # Create a button and add it to the grid
            tk.Button(self.master, text=button, width=10, command=lambda button=button: self.click_button(button)).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

        # Create a clear button
        tk.Button(self.master, text="Clear", width=22, command=self.clear_entry).grid(row=row_val, column=0, columnspan=2)
        tk.Button(self.master, text="Delete", width=22, command=self.delete_char).grid(row=row_val, column=2, columnspan=2)

    def click_button(self, button: str) -> None:
        """
        Handles a button click.

        Args:
            button (str): The text of the button.
        """
        # Check if the button is a number or operator
        if button == '=':
            try:
                # Evaluate the expression in the entry field
                result = str(eval(self.entry.get()))
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, result)
            except Exception as e:
                # Handle any exceptions
                messagebox.showerror("Error", str(e))
        else:
            # Append the button text to the entry field
            self.entry.insert(tk.END, button)

    def clear_entry(self) -> None:
        """
        Clears the entry field.
        """
        self.entry.delete(0, tk.END)

    def delete_char(self) -> None:
        """
        Deletes the last character in the entry field.
        """
        current = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, current[:-1])

def test_calculator_init() -> None:
    """
    Tests the Calculator class initialization.
    """
    root = tk.Tk()
    calc = Calculator(root)
    assert calc.master == root
    assert calc.entry is not None

def test_create_buttons() -> None:
    """
    Tests the create_buttons method.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.create_buttons()
    assert len(root.winfo_children()) > 0

def test_click_button_number() -> None:
    """
    Tests the click_button method with a number.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.click_button('5')
    assert calc.entry.get() == '5'

def test_click_button_operator() -> None:
    """
    Tests the click_button method with an operator.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.click_button('+')
    assert calc.entry.get() == '+'

def test_click_button_equals() -> None:
    """
    Tests the click_button method with the equals button.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.entry.insert(0, '5+5')
    calc.click_button('=')
    assert calc.entry.get() == '10'

def test_click_button_equals_error() -> None:
    """
    Tests the click_button method with the equals button and an error.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.entry.insert(0, '5+')
    messagebox.showerror = MagicMock()
    calc.click_button('=')
    assert messagebox.showerror.called

def test_clear_entry() -> None:
    """
    Tests the clear_entry method.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.entry.insert(0, '5+5')
    calc.clear_entry()
    assert calc.entry.get() == ''

def test_delete_char() -> None:
    """
    Tests the delete_char method.
    """
    root = tk.Tk()
    calc = Calculator(root)
    calc.entry.insert(0, '5+5')
    calc.delete