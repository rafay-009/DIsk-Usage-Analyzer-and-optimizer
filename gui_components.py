import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Callable, Dict, Optional
import os
from file_utils import format_size, get_file_type_icon
from disk_scanner import FileInfo

class FileTreeView(ttk.Frame):  # This is the corrected class name
    def __init__(self, parent, on_delete: Optional[Callable] = None):
        super().__init__(parent)
        self.on_delete = on_delete
        self.setup_ui()

    def setup_ui(self):
        # Create Treeview
        columns = ('icon', 'name', 'size', 'type', 'path')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        # Configure columns
        self.tree.heading('icon', text='')
        self.tree.heading('name', text='Name')
        self.tree.heading('size', text='Size')
        self.tree.heading('type', text='Type')
        self.tree.heading('path', text='Path')

        self.tree.column('icon', width=30, stretch=False)
        self.tree.column('name', width=200)
        self.tree.column('size', width=100)
        self.tree.column('type', width=50)
        self.tree.column('path', width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
        self.tree.bind("<Button-3>", self._show_context_menu)

    def update_files(self, files: Dict[str, FileInfo]):
        self.tree.delete(*self.tree.get_children())
        
        sorted_files = sorted(files.values(), key=lambda x: x.size, reverse=True)
        for file_info in sorted_files:
            name = os.path.basename(file_info.path)
            icon = get_file_type_icon(file_info.type)
            
            self.tree.insert('', 'end', values=(
                icon,
                name,
                format_size(file_info.size),
                file_info.type,
                file_info.path
            ))

    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _delete_selected(self):
        if self.on_delete:
            selected = self.tree.selection()
            if selected:
                item = selected[0]
                file_path = self.tree.item(item)['values'][4]
                self.on_delete(file_path)

class ChartPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Chart type selector
        self.chart_type = tk.StringVar(value="pie")
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X)
        ttk.Radiobutton(frame, text="Pie Chart", variable=self.chart_type,
                       value="pie", command=lambda: self.update_chart()).pack(side=tk.LEFT)
        ttk.Radiobutton(frame, text="Bar Chart", variable=self.chart_type,
                       value="bar", command=lambda: self.update_chart()).pack(side=tk.LEFT)

    def update_chart(self, files: Dict[str, FileInfo] = None):
        if not files:
            return

        self.ax.clear()
        
        # Get top 10 files
        top_files = sorted(files.values(), key=lambda x: x.size, reverse=True)[:10]
        labels = [os.path.basename(f.path) for f in top_files]
        sizes = [f.size for f in top_files]

        if self.chart_type.get() == "pie":
            self.ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            self.ax.set_title("Top 10 Largest Files")
        else:
            y_pos = range(len(labels))
            self.ax.barh(y_pos, sizes)
            self.ax.set_yticks(y_pos)
            self.ax.set_yticklabels(labels)
            self.ax.set_xlabel("Size (bytes)")
            self.ax.set_title("Top 10 Largest Files")

        self.canvas.draw()