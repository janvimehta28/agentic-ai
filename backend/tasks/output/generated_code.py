 
```python
import tkinter as tk
from tkinter import messagebox

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

def main() -> None:
    """
    Creates and starts the calculator.
    """
    root = tk.Tk()
    root.title("Calculator")
    calc = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```