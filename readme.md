# Credit Card Extractor

A Python script that extracts credit card information from a given text.

## Usage

To use the `credit_card_extractor.py` script in other Python scripts, you can import it as a module and call its functions directly. Here's an example:

```python
from extractor import extract_credit_card_info
```



### JSON Format

To get the results in JSON format, use the `.get('json')`:

```bash
pextract_credit_card_info(raw_text).get('json')
```

### List Format

To get the results in list format, use the `.get('list')`:

```bash
extract_credit_card_info(raw_text).get('list')
```

