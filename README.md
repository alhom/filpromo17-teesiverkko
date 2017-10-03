MIT License (see LICENSE.md), (c) 2017 Markku Alho & Anton Saressalo

If you happen meet the authors of the Teesiverkko project some day, feel free to buy us some sparkling wine, if you think this stuff is worth it.

Verkkopohjaista visualisointia opinnäytteistä - Graph-based visualization of dissertations and Master's theses

There are two main components here:
1) The python harvester & data miner for HELDA OAI database, used to extract metadata and mine entire theses, where available.

Requires additional sickle package https://pypi.python.org/pypi/Sickle
as well as the pdfminer script in the same folder https://pypi.python.org/pypi/pdfminer/

Functions in file functions.py.
The main program in file graduminer.py.

Run with command:
python graduminer.py

2) Mathematica notebook for the remainder of text processing and graph creation, instructions included. Handles both plain metadata and mined thesis data from the python miner.

The notebook exports graphs to .graphml and additional data to TSV (Mathematica compresses large .graphml fields) to be used in dedicated graph software. We used Gephi and gexfjs for the final touches, including deployment to the Internet.
