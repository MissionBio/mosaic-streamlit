import os
import sys
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

if __name__ == '__main__':

    launchdir = os.path.dirname(sys.argv[0])

    if launchdir == '':
        launchdir = '.'

    print('Launch dir ', launchdir)

    # Download latest code
    try:
        while True:
            val = input("\nCheck for updates?\n(This is in active development. Features that previously worked may no longer work. This is for research purposes only.)\nyes/[no] -  ")
            if val not in ['yes', 'no', '']:
                print("Invalid input. Enter one of 'yes' or 'no', or press enter to skip")
            else:
                break

        if val == 'yes':
            resp = urlopen("https://github.com/MissionBio/mosaic-streamlit/archive/master.zip")

            with ZipFile(BytesIO(resp.read())) as zipfile:
                for file in zipfile.namelist()[1:]:
                    local_file = f'{launchdir}/' + '/'.join(file.split('/')[1:])
                    print('Downloading', local_file)

                    if local_file[-1] == '/':
                        if not os.path.exists(local_file):
                            os.mkdir(local_file)
                    else:
                        with open(local_file, 'wb') as f:
                            f.write(zipfile.read(file))

            print('Succesfully downloaded all files')
        else:
            print('Skipping updates')
    except Exception as e:
        print(f'FAILED to download code. Running local version.\n{e}')

    # streamlit can take a while to import
    from streamlit import cli as stcli

    sys.argv = ["streamlit", "run", f"{launchdir}/app.py", "--server.port=10000", "--global.developmentMode=false"]
    sys.exit(stcli.main())
