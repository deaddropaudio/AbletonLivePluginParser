import gzip
import shutil
from lxml import etree
from pathlib import Path
import yaml
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            return {"threshold": 5, "project_dir": "./projects", "show_processed_projects": True, "cleanup_temp": True}
        with open(self.config_path, 'r') as config_file:
            return yaml.safe_load(config_file)

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            yaml.safe_dump(self.config, config_file, default_flow_style=False)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

class ALSFileCollectorApp:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.setup_ui()
        self.selected_items = []

    def setup_ui(self):
        self.root.title("Ableton Live Projects - Plugin statistics")

        # Configuration Frame
        self.config_frame = tk.LabelFrame(self.root, text="Configuration", padx=10, pady=10)
        self.config_frame.pack(padx=10, pady=5, fill=tk.X)

        # Threshold Configuration
        tk.Label(self.config_frame, text="Threshold for 'often used':").pack(side=tk.LEFT)
        self.threshold_entry = tk.Entry(self.config_frame, width=5)
        self.threshold_entry.pack(side=tk.LEFT, padx=5)
        self.threshold_entry.insert(0, str(self.config_manager.get("threshold", 5)))

        # Cleanup Temp Checkbox
        self.cleanup_temp_var = tk.BooleanVar(value=self.config_manager.get("cleanup_temp", False))
        self.cleanup_temp_check = tk.Checkbutton(self.config_frame, text="Cleanup Tempfolder", variable=self.cleanup_temp_var)
        self.cleanup_temp_check.pack(side=tk.LEFT, padx=10)

        # Save Configuration Button
        self.btn_save_config = tk.Button(self.config_frame, text="Save Config", command=self.save_config)
        self.btn_save_config.pack(side=tk.RIGHT, padx=5)

        # File and Folder Selection Frame
        self.selection_frame = tk.Frame(self.root)
        self.selection_frame.pack(padx=10, pady=5, fill=tk.X)

        self.btn_add_file = tk.Button(self.selection_frame, text="Add Files", command=self.add_files)
        self.btn_add_file.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_add_folder = tk.Button(self.selection_frame, text="Add Folder", command=self.add_folder_and_search_als)
        self.btn_add_folder.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_process = tk.Button(self.selection_frame, text="Generate Report", command=self.process_files)
        self.btn_process.pack(side=tk.RIGHT, padx=5, pady=5)

        # Listbox for Selected Files and Folders
        self.listbox = tk.Listbox(self.root, width=60, height=10)
        self.listbox.pack(padx=10, pady=5, fill=tk.X)

        self.removal_frame = tk.Frame(self.root)
        self.removal_frame.pack(padx=10, pady=5, fill=tk.X)

        self.btn_remove = tk.Button(self.removal_frame, text="Remove Selected", command=self.remove_selected)
        self.btn_remove.pack(side=tk.LEFT,padx=5, pady=5)

        self.btn_remove_all = tk.Button(self.removal_frame, text="Remove All", command=self.remove_all)
        self.btn_remove_all.pack(side=tk.LEFT,padx=5, pady=5)

    def add_files(self):
        file_paths = filedialog.askopenfilenames(multiple=True, title="Select Files",
                                             filetypes=[("Ableton Live Sets", "*.als")])

        if file_paths:
            for file_path in file_paths:
                self.selected_items.append(file_path)
                self.listbox.insert(tk.END, file_path)

    def add_folder_and_search_als(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            folder = Path(folder_path)
            for als_file in folder.rglob('*.als'):            
                if "Backup" not in als_file.parts:
                    self.selected_items.append(str(als_file))
                    self.listbox.insert(tk.END, als_file)

    def remove_selected(self):
        selected_indices = self.listbox.curselection()
        for index in selected_indices[::-1]:
            del self.selected_items[index]
            self.listbox.delete(index)

    def remove_all(self):
        # Clear the listbox
        self.listbox.delete(0, tk.END)
        # Clear the list of selected items
        self.selected_items.clear()

    def save_config(self):
        threshold = self.threshold_entry.get()
        cleanup_temp = self.cleanup_temp_var.get()
        try:
            threshold_val = int(threshold)
            self.config_manager.set("threshold", threshold_val)
            self.config_manager.set("cleanup_temp", cleanup_temp)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid threshold value. Please enter a valid number.")

    def process_files(self):     
        project_dir = Path(self.config_manager.get("project_dir", "./projects"))
        temp_dir = project_dir / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for item in self.selected_items:
            path = Path(item)
            if path.is_dir():
                for als_file in path.glob("*.als"):
                    shutil.copy(als_file, project_dir)
            else:
                shutil.copy(path, project_dir)

        processing_logic(temp_dir)

        messagebox.showinfo("Success", "Files have been processed.")

        if self.config_manager.get("cleanup_temp", False):
            clear_temp_folder(temp_dir)
            clear_temp_folder(project_dir)
            messagebox.showinfo("Cleanup", "Temporary files have been cleaned up.")

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config

def locate_projects(directory: Path) -> tuple[list[Path], int]:
    als_files = [file for file in directory.rglob("*.als") if "Backup" not in file.parts]
    return als_files, len(als_files)
                
def copy_projects_to_temp(projects: list[Path], temp_dir: Path):
    for project in projects:
        shutil.copy(project, temp_dir / project.name)

def clear_temp_folder(temp_folder_path: Path):
    for item in temp_folder_path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def rename_projects(temp_dir: Path):
    for file in temp_dir.glob("*.als"):
        file.rename(file.with_suffix(".gzip"))

def unzip_projects(temp_dir: Path):
    for file in temp_dir.glob("*.gzip"):
        with gzip.open(file, 'rb') as f_in, (file.with_suffix(".xml")).open('wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def parse_projects(temp_dir: Path) -> dict[str, int]:
    plugins = {}
    parser = etree.XMLParser(huge_tree=True)
    for file in temp_dir.glob("*.xml"):
        tree = etree.parse(file, parser)
        root = tree.getroot()
        for elem in root.findall('.//PluginDesc/AuPluginInfo/Name'):
            plugin_name = elem.get("Value")
            plugins[plugin_name] = plugins.get(plugin_name, 0) + 1
    return plugins

def create_report(plugins: dict[str, int], threshold: int, projects: list[Path] = None, show_processed_projects: bool = False) -> str:
    md_content = "# Plugins Report\n\n"
    md_content += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"  
    
    # Sort plugins based on count (descending) and then alphabetically
    used_often = sorted([plugin for plugin, count in plugins.items() if count > threshold], key=lambda x: (-plugins[x], x))
    used_less_often = sorted([plugin for plugin, count in plugins.items() if count <= threshold], key=lambda x: (-plugins[x], x))

    if used_often:
        md_content += "## Used Often\n" + "\n".join(f"- {plugin}: {plugins[plugin]} times" for plugin in used_often)
    if used_less_often:
        md_content += "\n## Used Less Often\n" + "\n".join(f"- {plugin}: {plugins[plugin]} times" for plugin in used_less_often)

    if show_processed_projects and projects:
        md_content += "## Processed Projects\n" + "\n".join(f"- {project}" for project in projects) + "\n\n"

    return md_content


def processing_logic(temp_dir: Path):
    print("Process started")  # Debug print
    config = load_config("config.yaml")
    threshold = config["threshold"]
    project_dir = Path(config["project_dir"])
    show_processed_projects = config.get("show_processed_projects", False)
    
    temp_dir.mkdir(exist_ok=True)
    
    all_projects, number_of_projects = locate_projects(project_dir)
    copy_projects_to_temp(all_projects, temp_dir)
    rename_projects(temp_dir)
    unzip_projects(temp_dir)
    plugins = parse_projects(temp_dir)
    report_content = create_report(plugins, threshold, all_projects if show_processed_projects else None, show_processed_projects)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"plugins_report_{timestamp}.md"
    with open(report_filename, "w") as file:
        file.write(report_content)
    


def main():
    root = tk.Tk()
    config_manager = ConfigManager()
    app = ALSFileCollectorApp(root, config_manager)
    root.mainloop()

if __name__ == "__main__":
    main()