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
    def __init__(self, name):
        self.name = name
        self.logger = self.setup_logger()

    def setup_logger(self):
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers if logger is reused
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create file handler
        file_handler = logging.FileHandler(self.log_file, mode="a")  # Append mode
        file_handler.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

        return logger

    @property
    def log_file(self):
        return f"logs/{self.name}.log"

    def open_terminal(self):
        print(f"Opening terminal for {self.name}...")
        # Open terminal for log file
        if get_my_os() == "LINUX":
            os.system(f"gnome-terminal -- tail -f {self.log_file}")
        elif get_my_os() == "WINDOWS":
            # Using powershell to open a new terminal window
            os.system(
                f"start powershell.exe -NoExit -Command Get-Content {self.log_file} -Wait"
            )
        elif get_my_os() == "MACOS":
            os.system(f"open -a Terminal tail -f {self.log_file}")
        else:
            print("Unsupported OS. Cannot open terminal.")
            return

    def clear(self):
        with open(self.log_file, "w"):
            pass


announcer_logger = Log("Announcer")
download_logger = Log("Download")
seeding_logger = Log("Seeding")
