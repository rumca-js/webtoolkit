"""
TODO
these scripts will not work in case of multithreaded app
"""

import os
import psutil
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from .utils.logger import PrintLogger
from .webtools import WebLogger


class WebConfig(object):
    """
    API to configure webtools
    """

    script_operating_dir = None
    script_responses_directory = Path("storage")
    display = None
    browser_mapping = {}

    def init():
        pass

    def get_script_path(script_relative):
        """
        script_relative example crawleebeautifulsoup.py
        """
        import os

        poetry_path = ""
        if "POETRY_ENV" in os.environ:
            poetry_path = os.environ["POETRY_ENV"] + "/bin/"

        script_relative = poetry_path + "poetry run python {}".format(script_relative)

        return script_relative

    def use_logger(Logger):
        WebLogger.web_logger = Logger

    def use_print_logging():
        WebLogger.web_logger = PrintLogger()

    def disable_ssl_warnings():
        disable_warnings(InsecureRequestWarning)

    def kill_chrom_processes():
        """Kill all processes whose names start with 'chrom'."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower().startswith("chrom"):
                    proc.kill()  # Kill the process
                    WebLogger.error(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                WebLogger.error(
                    f"Could not kill process {proc.info.get('name', 'unknown')}: {e}"
                )

    def kill_xvfb_processes():
        """Kill all processes whose names start with 'chrom'."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower().startswith("xvfb"):
                    proc.kill()  # Kill the process
                    WebLogger.error(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                WebLogger.error(
                    f"Could not kill process {proc.info.get('name', 'unknown')}: {e}"
                )

    def count_chrom_processes():
        """Count the number of running processes whose names start with 'chrom'."""
        count = 0
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower().startswith("chrom"):
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  # Skip processes we can't access
        return count

    def start_display():
        try:
            from pyvirtualdisplay import Display

            # Check if WebConfig.display is already initialized and active
            if (
                isinstance(getattr(WebConfig, "display", None), Display)
                and WebConfig.display.is_alive()
            ):
                return  # Do nothing if already initialized and active

            # Requires xvfb
            os.environ["DISPLAY"] = ":10.0"

            # Create and start the Display
            WebConfig.display = Display(visible=0, size=(800, 600))
            WebConfig.display.start()
        except Exception as E:
            WebLogger.error(f"Problems with creating display: {str(E)}")
            return

    def stop_display():
        try:
            WebConfig.display.stop()
            WebConfig.display = None
        except Exception as E:
            WebLogger.error(f"Problems with creating display")
            return

    def get_bytes_limit():
        return 5000000  # 5 MB. There are some RSS more than 1MB
