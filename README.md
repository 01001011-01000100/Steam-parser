# Steam Parser

This is a Python script that fetches the current price of items from the Steam Community Market. It uses the BeautifulSoup library to parse the HTML content of the Steam Community Market website and the requests library to send HTTP requests.

---

## Prerequisites

Before running the [script](main.py), make sure you have the following Python packages installed:

> - `requests`
> - `beautifulsoup4`
> - `fake_useragent`



You can install these packages using pip:

```bash
pip install requests beautifulsoup4 fake_useragent
```

---

## Usage

Before you run the script, you will need to fill in a txt file that contains the URLs of the items that you want to find and is located in your input folder.
Every url should be in a new line. This is content of the [sample](input/sample.txt) file:

```
https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case
https://steamcommunity.com/market/listings/730/Kilowatt%20Case
```

---

After that, you can run the script using the following command:

```bash
python main.py
```
---

The script accepts command-line arguments:  

>`--items_data`: Name of the item you want to search for. Default is __sample.txt__.
>
>`--currency`: Currency in which the price will be displayed. Default is __USD__. For more information about the currencies, please visit: [Steam Pricing Currencies](https://partner.steamgames.com/doc/store/pricing/currencies)
> 
>`--delay`: Delay between end of one request and start of another. Default is __1.5 second__.

---

You can run the script with the specified arguments by using the following command:

```bash
python main.py --items_data sample.txt --currency USD --delay 1.5
```

---

After running the script, the output will be saved in txt files in the output folder.
The name of the output file will be the same as the input file + date and time of the script execution.
The output will contain the name of the item, url, lowest sell and highest buy price.

---

## License
This project, like the libraries it uses, is under MIT license. See the [LICENSE](LICENSE) file for details.
