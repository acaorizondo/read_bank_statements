# Read TDBank pdf statements
In online banking, sometimes, export in csv format doesn't work properly. This function offer an alternative to convert TDBank pdf statements to csv format.

A function in Python was developed to let import TDBank statements in pdf format
and return the respective transactions in csv format to ease processing banking information.

## Installation

Use the read_pdf.py.

```python
import sys
import os
sys.path.append(os.path.abspath("/path"))
from read_pdf import *
```

## Usage

```python
csv_file = convert_statementPDF_to_statementeCSV(pdf_dir, pdf_name)
```

## Contributing


<!-- Please make sure to update tests as appropriate. -->


## License
[MIT](https://choosealicense.com/licenses/mit/)
