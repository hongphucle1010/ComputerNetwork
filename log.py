import os
import logging


def get_my_os():
    # If Linux, return LINUX, if Windows, return WINDOWS, if MacOS, return MACOS, otherwise, return OTHER
    if os.name == "posix":
        return "LINUX"
    elif os.name == "nt":
        return "WINDOWS"
    elif os.name == "mac":
        return "MACOS"
    else:
        return "OTHER"


class Log:
    def __init__(self, name, enable_terminal=False):
        self.name = name
        self.enable_terminal = enable_terminal  # Add option to open terminal or not
        self.logger = self.setup_logger()

    def setup_logger(self):
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers if logger is reused
        if logger.hasHandlers():
            logger.handlers.clear()

        # Ensure the logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Create file handler with utf-8 encoding
        file_handler = logging.FileHandler(
            self.log_file, mode="a", encoding="utf-8"
        )  # Set encoding to utf-8
        file_handler.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

        # If terminal output is enabled, open terminal
        if self.enable_terminal:
            self.open_terminal()

        return logger

    @property
    def log_file(self):
        return f"logs/{self.name}.log"

    def open_terminal(self):
        print(f"Opening terminal for {self.name}...")
        if get_my_os() == "LINUX":
            # Try to open with available terminal emulators
            if os.system(f"command -v qterminal") == 0:
                os.system(f"qterminal -e tail -f {self.log_file}")
            if os.system(f"command -v gnome-terminal") == 0:
                os.system(f"gnome-terminal -- tail -f {self.log_file}")
            elif os.system(f"command -v lxterminal") == 0:
                os.system(f"lxterminal -e tail -f {self.log_file}")
            elif os.system(f"command -v xterm") == 0:
                os.system(f"xterm -e tail -f {self.log_file}")
            else:
                print("No supported terminal emulator found.")
        elif get_my_os() == "WINDOWS":
            # Using PowerShell to open a new terminal window
            os.system(
                f"start powershell.exe -NoExit -Command Get-Content {self.log_file} -Wait"
            )
        elif get_my_os() == "MACOS":
            os.system(f"open -a Terminal tail -f {self.log_file}")
        else:
            print("Unsupported OS. Cannot open terminal.")

    def clear(self):
        with open(self.log_file, "w"):
            pass


# Create logger instances with the option to open terminal if needed
announcer_logger = Log("Announcer", enable_terminal=False)
download_logger = Log("Download", enable_terminal=False)
seeding_logger = Log("Seeding", enable_terminal=False)
