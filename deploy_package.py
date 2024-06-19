import sys
import shutil
import subprocess
import asyncio
import shutil

from simumatik_api_helper import UploadFile, GetRequestJson, GetSimumatikApiToken

PLATFORM = sys.platform
OS_EXECUTABLE_EXT = {"win32": "exe", "linux": "sh", "darwin": "sh"}

print("[+] Do you want to deploy the Gateway (Default) or the ControllerBridge (1) package?")
PACKAGE = 'ControllerBridge' if input() == '1' else 'Gateway'
PACKAGE_EXECUTABLE = f'{PACKAGE}.{OS_EXECUTABLE_EXT[PLATFORM]}'
    
print(f"Deploying {PACKAGE} package for platform {PLATFORM}...")

# WINDOWS
if PLATFORM=="win32":
    SIGNTOOLS_PATH = "\"C:/Program Files (x86)/Windows Kits/10/bin/10.0.22000.0/x86/signtool.exe\""
    TIMESTAMP_URL = "http://timestamp.comodoca.com"
    PACKAGE_PATH = 'C:/Git/'
    PACKAGE_SPEC_PATH = f'{PACKAGE_PATH}simumatik-gateway/{PACKAGE}_package.spec'
    PYTHON_PATH = 'C:/python312/python.exe'
    subprocess.call(f'{PYTHON_PATH} -m PyInstaller --noconfirm {PACKAGE_SPEC_PATH}', shell=True)
    subprocess.call(f"{SIGNTOOLS_PATH} sign /tr {TIMESTAMP_URL} /td sha256 /fd sha256 /a dist/{PACKAGE}/{PACKAGE_EXECUTABLE}", shell=True)

# LINUX
elif PLATFORM=="linux":
    pass
# MACOS
elif PLATFORM=="darwin":
    pass

TOKEN, AUDIENCE = GetSimumatikApiToken()
assert TOKEN is not None, "Error getting Simumatik API token!"

print("[+] Do you want to deploy a regular (Default) or experimental (1) package?")
experimental = input() == '1'

# TODO: Fix new paths for other platforms
if experimental:
    actual_version = asyncio.run(GetRequestJson(token=TOKEN, url=f'{AUDIENCE}/{PACKAGE}/experimental/version'))
else:
    actual_version = asyncio.run(GetRequestJson(token=TOKEN, url=f'{AUDIENCE}/{PACKAGE}/version'))

print(f"Actual {PACKAGE} package version is: {actual_version}")
print("[+] Introduce the new version number (i.e. '1.0.0'): ")
version = input()
filepath = 'Output/'

print("Ziping the package...")
shutil.make_archive(f'{filepath}{PACKAGE}-{version}', 'zip', f'dist/{PACKAGE}')
filename = f'{PACKAGE}-{version}.zip'
print('Uploading package...')
if experimental:
    asyncio.run(UploadFile(token=TOKEN, url=f'{AUDIENCE}/admin/{PACKAGE}/experimental', path=filepath, filename=filename))
else:
    asyncio.run(UploadFile(token=TOKEN, url=f'{AUDIENCE}/admin/{PACKAGE}', path=filepath, filename=filename))
print('Package uploaded!')
if experimental:
    version = asyncio.run(GetRequestJson(token=TOKEN, url=f'{AUDIENCE}/{PACKAGE}/experimental/version'))
else:
    version = asyncio.run(GetRequestJson(token=TOKEN, url=f'{AUDIENCE}/{PACKAGE}/version'))
print(f"Uploaded {PACKAGE} package version is: {version}")