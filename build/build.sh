pyinstaller --additional-hooks-dir=hooks \
			--hidden-import missionbio.mosaic \
			--hidden-import missionbio.h5 \
			--hidden-import plotly \
			--clean run.py

cp ../*.py ./dist/run/
cp -r ../tasks ./dist/run/
