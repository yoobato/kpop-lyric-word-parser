# Melon Lyric Scraper
Scraps song details from Melon(K-pop music) with Keyword
- Options
  - Search keyword
  - Search by **artist name**, **song title**, **album name**, or **all**
  - Output format either **CSV** or **JSON**


## Get Started
```sh
python main.py {SearchKeyword} -s {SearchFilter} -o {OutputFormat}
# For more information, type "python main.py -h"

# Ex) Get songs with the word "가을" exists in song title and output as json file.
python main.py 가을 -s song -o json
```


## TODO
- Add Genre filter (currently only Ballad(GN0101) is supported.)
- Validate `requirements.txt`
- Use `venv`, `pipenv`, or somthing like that


## Special Thanks to
- :woman_teacher:	[@chum.my](https://www.instagram.com/chum.my/)
