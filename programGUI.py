import socket
import threading
from tkinter import (
    Tk,
    Label,
    Button,
    Entry,
    StringVar,
    Listbox,
    Scrollbar,
    Frame,
    filedialog,
    Toplevel,
    DoubleVar,
)
from tkinter.messagebox import showinfo, showerror, askyesno
from tkinter.ttk import Combobox, Progressbar
from configuration import Configuration
from announcer import Announcer
from Modules.PeerConnection.torrent_manager import TorrentManager
from Modules.TorrentCreator.torrent_creator import TorrentCreator
from log import announcer_logger, download_logger, seeding_logger
import os

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Try to connect to an external host to get the LAN IP
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        try:
            # If that fails, use gethostbyname to get the IP
            IP = socket.gethostbyname(socket.gethostname())
        except Exception:
            # If all methods fail, default to localhost
            IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class ProgramGUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("TorrentApplication - PhucVanKhoa - TN01")
        self.root.geometry("800x500")
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        self.ip = get_lan_ip()
        self.configs = Configuration()
        self.port = self.configs.port
        self.announcer = Announcer(self.configs, self.ip, self)
        self.torrent_manager = TorrentManager(self.configs.download_dir, self)

        self.torrent_list = []
        self.selected_torrent = StringVar()

        self.create_widgets()
        self.announcer.start()
        self.loop_refresh_torrents()

    def loop_refresh_torrents(self):
        self.refresh_torrents()
        self.root.after(500, self.loop_refresh_torrents)

    def create_widgets(self):
        Label(
            self.root,
            text="TorrentApplication - PhucVanKhoa - TN01",
            font=("Arial", 16),
        ).pack(pady=10)

        # Torrent List
        frame = Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = Scrollbar(frame, orient="vertical")
        self.listbox = Listbox(frame, yscrollcommand=scrollbar.set, selectmode="single")
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        button_frame = Frame(self.root)
        button_frame.pack(pady=10)

        Button(
            button_frame, text="Create Torrent", command=self.create_torrent_window
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        Button(button_frame, text="Add Torrent", command=self.add_torrent_window).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )
        Button(button_frame, text="Resume Torrent", command=self.resume_torrent).grid(
            row=0, column=2, padx=5, pady=5, sticky="ew"
        )
        Button(
            button_frame, text="Reveal Downloaded File", command=self.reveal_torrent
        ).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        Button(button_frame, text="Pause Torrent", command=self.pause_torrent).grid(
            row=1, column=0, padx=5, pady=5, sticky="ew"
        )
        Button(button_frame, text="Remove Torrent", command=self.remove_torrent).grid(
            row=1, column=1, padx=5, pady=5, sticky="ew"
        )
        Button(
            button_frame, text="Refresh Torrents", command=self.refresh_torrents
        ).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        Button(
            button_frame, text="Open Log Terminal", command=self.open_log_terminal
        ).grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Adjust column weights for better distribution
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)

    def create_torrent_window(self):
        window = Toplevel(self.root)
        window.title("Create Torrent")
        window.transient(self.root)
        window.grab_set()

        selected_files = []  # To store selected file paths
        self.creator = None  # Initialize creator

        Label(window, text="Piece Size:").grid(row=0, column=0, padx=10, pady=5)

        # Dropdown for piece size options
        piece_size_var = StringVar()
        piece_size_options = [
            "256 KB",
            "512 KB",
            "1 MB",
            "2 MB",
            "4 MB",
            "8 MB",
            "16 MB",
            "32 MB",
        ]
        piece_size_dropdown = Combobox(
            window,
            textvariable=piece_size_var,
            values=piece_size_options,
            state="readonly",
        )
        piece_size_dropdown.grid(row=0, column=1, padx=10, pady=5)
        piece_size_dropdown.current(0)  # Set default to "256 KB"

        Label(window, text="Torrent Name:").grid(row=1, column=0, padx=10, pady=5)
        torrent_name = Entry(window)
        torrent_name.grid(row=1, column=1, padx=10, pady=5)

        def browse_files():
            nonlocal selected_files
            files = filedialog.askopenfilenames(
                title="Select Files for Torrent",
                filetypes=[("All Files", "*.*")],  # Allow all file types
            )
            if files:
                selected_files = list(files)
                file_list_label.config(text=f"Selected {len(selected_files)} files.")

        Button(window, text="Browse Files", command=browse_files).grid(
            row=2, column=0, columnspan=2, pady=5
        )

        file_list_label = Label(window, text="No files selected.")
        file_list_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        progress_var = DoubleVar()
        progress_bar = Progressbar(window, variable=progress_var, maximum=100)
        progress_bar.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        progress_label = Label(window, text="Progress: 0%")
        progress_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        def update_progress():
            if self.creator:
                progress = self.creator.progress
                progress_var.set(progress)
                progress_label.config(text=f"Progress: {progress:.2f}%")
                if progress < 100:
                    window.after(100, update_progress)

        def create():
            if not selected_files:
                showerror("Error", "No files selected.")
                return
            piece_size_text = piece_size_var.get()
            if not piece_size_text:
                showerror("Error", "Please select a piece size.")
                return
            name = torrent_name.get()
            if not name.strip():
                showerror("Error", "Torrent name cannot be empty.")
                return

            # Convert piece size text to bytes
            size_mapping = {
                "256 KB": 256 * 1024,
                "512 KB": 512 * 1024,
                "1 MB": 1 * 1024 * 1024,
                "2 MB": 2 * 1024 * 1024,
                "4 MB": 4 * 1024 * 1024,
                "8 MB": 8 * 1024 * 1024,
                "16 MB": 16 * 1024 * 1024,
                "32 MB": 32 * 1024 * 1024,
            }
            piece = size_mapping[piece_size_text]

            # Start the torrent creation in a new thread
            def torrent_creation_thread():
                try:
                    self.creator = TorrentCreator(
                        selected_files, self.configs.tracker_url, piece
                    )
                    window.after(100, update_progress)
                    self.creator.create(f"torrents/{name}.torrent")
                    if self.creator._stop:
                        return  # Torrent creation was stopped
                    showinfo("Success", "Torrent created successfully!")
                    if_add = askyesno("Add Torrent", "Add torrent to seeding list?")
                    if if_add:
                        self.torrent_manager.addTorrent(
                            file_path=f"torrents/{name}.torrent",
                            downloaded_path=selected_files,
                        )
                    self.refresh_torrents()
                    # Open folder containing the created torrent file

                    if os.name == "nt":
                        os.system(f'explorer /select,"torrents\\{name}.torrent"')
                    elif os.name == "posix":
                        os.system(f'xdg-open "torrents/{name}.torrent"')
                    elif os.name == "mac":
                        os.system(f'open "torrents/{name}.torrent"')
                    window.destroy()
                except Exception as e:
                    showerror("Error", f"Error creating torrent: {e}")

            self.creation_thread = threading.Thread(target=torrent_creation_thread)
            self.creation_thread.start()
            update_progress()  # Start updating the progress

        def stop_creation():
            if self.creator:
                self.creator.stop()
                showinfo("Stopped", "Torrent creation has been stopped.")
            window.destroy()

        def on_window_close():
            stop_creation()

        window.protocol("WM_DELETE_WINDOW", on_window_close)

        Button(window, text="Create Torrent", command=create).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        window.mainloop()

    def add_torrent_window(self):
        window = Toplevel(self.root)  # Use Toplevel instead of Tk
        window.title("Add Torrent")
        window.transient(self.root)  # Link the window to the main application
        window.grab_set()  # Focus on this window until closed

        Label(window, text="File Path:").grid(row=0, column=0, padx=10, pady=5)

        file_path_var = StringVar()  # Variable to hold the selected file path
        file_path_entry = Entry(
            window, textvariable=file_path_var, state="readonly"
        )  # Read-only
        file_path_entry.grid(row=0, column=1, padx=10, pady=5)

        def browse_file():
            selected_file = filedialog.askopenfilename(
                title="Select Torrent File",
                filetypes=[("Torrent Files", "*.torrent"), ("All Files", "*.*")],
            )
            if selected_file:
                file_path_var.set(selected_file)  # Update the entry with the file path

        def add():
            try:
                path = file_path_var.get()
                if not path:
                    showerror("Error", "No file selected!")
                    return
                self.torrent_manager.addTorrent(
                    file_path=path, is_called_by_gui=True, downloaded_path=[]
                )
                showinfo("Success", "Torrent added successfully!")
                self.refresh_torrents()
                window.destroy()
            except Exception as e:
                showerror("Error", f"Error adding torrent: {e}")

        Button(window, text="Browse", command=browse_file).grid(
            row=0, column=2, padx=10, pady=5
        )
        Button(window, text="Add", command=add).grid(
            row=1, column=0, columnspan=3, pady=10
        )

        window.mainloop()

    def refresh_torrents(self):
        try:
            # Save current selection
            selection = self.listbox.curselection()
            self.torrent_list = self.torrent_manager.getTorrentList_StringType()
            self.listbox.delete(0, "end")
            for torrent in self.torrent_list:
                self.listbox.insert("end", torrent)
            # Restore selection
            if selection:
                self.listbox.selection_set(selection[0])
        except Exception as e:
            showerror("Error", f"Error refreshing torrents: {e}")

    def remove_torrent(self):
        try:
            selection = self.listbox.curselection()
            if not selection:
                showerror("Error", "No torrent selected!")
                return
            torrent = self.torrent_list[selection[0]]
            torrent_id = torrent.split(",")[0].split(":")[1].strip()
            self.torrent_manager.removeTorrent(torrent_id)
            self.refresh_torrents()
        except Exception as e:
            showerror("Error", f"Error removing torrent: {e}")

    def resume_torrent(self):
        try:
            selection = self.listbox.curselection()
            if not selection:
                showerror("Error", "No torrent selected!")
                return
            torrent = self.torrent_list[selection[0]]
            torrent_id = torrent.split(",")[0].split(":")[1].strip()
            self.torrent_manager.resumeDownload(torrent_id)
        except Exception as e:
            showerror("Error", f"Error resuming torrent: {e}")

    def pause_torrent(self):
        try:
            selection = self.listbox.curselection()
            if not selection:
                showerror("Error", "No torrent selected!")
                return
            torrent = self.torrent_list[selection[0]]
            torrent_id = torrent.split(",")[0].split(":")[1].strip()
            self.torrent_manager.pauseDownload(torrent_id)
        except Exception as e:
            showerror("Error", f"Error pausing torrent: {e}")

    def reveal_torrent(self):
        try:
            selection = self.listbox.curselection()
            if not selection:
                showerror("Error", "No torrent selected!")
                return
            torrent = self.torrent_list[selection[0]]
            torrent_id = torrent.split(",")[0].split(":")[1].strip()
            self.torrent_manager.revealDownloadedFile(torrent_id)
        except Exception as e:
            showerror("Error", f"Error revealing torrent: {e}")

    def open_log_terminal(self):
        announcer_logger.open_terminal()
        download_logger.open_terminal()
        seeding_logger.open_terminal()

    def shutdown(self):
        if askyesno("Exit", "Are you sure you want to exit?"):
            self.announcer.stop()
            self.torrent_manager.stop()
            announcer_logger.clear()
            download_logger.clear()
            seeding_logger.clear()
            self.root.destroy()


def start_program():
    try:
        root = Tk()
        app = ProgramGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        app.shutdown()


if __name__ == "__main__":
    start_program()
