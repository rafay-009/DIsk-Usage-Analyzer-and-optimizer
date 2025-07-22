import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from disk_scanner import DiskScanner  # This line is correct as is
from file_utils import delete_file
from gui_components import FileTreeView, ChartPanel

class DiskAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Usage Analyzer and Optimizer")
        self.root.geometry("1000x700")

        self.scanner = DiskScanner(progress_callback=self._on_scan_progress)
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Path selection
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))

        self.path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse", command=self._browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="Analyze", command=self._start_analysis).pack(side=tk.LEFT)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # Paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # File tree
        self.file_tree = FileTreeView(paned, on_delete=self._delete_file)
        paned.add(self.file_tree, weight=3)

        # Chart panel
        self.chart_panel = ChartPanel(paned)
        paned.add(self.chart_panel, weight=1)

    def _browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)

    def _start_analysis(self):
        path = self.path_var.get()
        if not path:
            messagebox.showerror("Error", "Please select a directory")
            return

        self.progress_var.set(0)
        self.scanner.scan_directory(path)

    def _on_scan_progress(self, progress, files):
        self.progress_var.set(progress)
        self.file_tree.update_files(files)
        self.chart_panel.update_chart(files)

    def _delete_file(self, file_path):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{file_path}"):
            success, error = delete_file(file_path)
            if success:
                messagebox.showinfo("Success", "File deleted successfully")
                self._start_analysis()  # Refresh
            else:
                messagebox.showerror("Error", f"Could not delete file: {error}")

def main():
    root = tk.Tk()
    app = DiskAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()