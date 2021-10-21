import os
import requests as rq


def _pre_vm():
    s = """sudo apt update -y
    sudo apt-get update -y
    sudo apt-get install wget -y
    """
    os.system(s)


def init_chrome_for_vm(path=os.getcwd()):
    _pre_vm()
    s = f"""wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_91.0.4472.106-1_amd64.deb
    sudo apt install /tmp/chrome.deb -y
    sudo rm /tmp/chrome.deb
    cd {path}
    wget --no-verbose -O d.zip https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip
    unzip d.zip
    rm d.zip
    """
    os.system(s)


def init_conda_for_vm():
    _pre_vm()
    s = """wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        && bash Miniconda3-latest-Linux-x86_64.sh -b \
        && rm -f Miniconda3-latest-Linux-x86_64.sh
    . $HOME/miniconda3/etc/profile.d/conda.sh
    conda init
    """
    os.system(s)


def dropbox_down(from_path, to_path="/tmp", key=os.getenv("DROPBOX_KEY")):
    if key is None:
        raise Exception("No keys provided")

    headers = {
        'Authorization': f'Bearer {key}',
        'Dropbox-API-Arg': '{"path": "' + from_path + '"}',
    }
    r = rq.post('https://content.dropboxapi.com/2/files/download', headers=headers)

    with open(f"{to_path}", "wb") as file:
        file.write(r.content)

    return r


def dropbox_up(obj_or_path, to_path="/tmp", key=os.getenv("DROPBOX_KEY")):
    if isinstance(obj_or_path, str):
        obj_or_path = open(obj_or_path, 'rb').read()

    headers = {
        'Authorization': f'Bearer {key}',
        'Dropbox-API-Arg': '{"path": "' + to_path + '"}',
        'Content-Type': 'application/octet-stream',
    }
    r = rq.post('https://content.dropboxapi.com/2/files/upload', headers=headers, data=obj_or_path)

    return r
