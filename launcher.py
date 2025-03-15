import os
import sys
import streamlit.web.cli as stcli


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def launch_streamlit():
    streamlit_script = resource_path(os.path.join('src', 'app.py'))

    # Start the Streamlit process
    sys.argv = [
        "streamlit",
        "run",
        streamlit_script,
        "--global.developmentMode=false",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    try:
        launch_streamlit()
    except KeyboardInterrupt:
        pass
