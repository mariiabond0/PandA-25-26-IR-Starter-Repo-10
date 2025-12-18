BANNER = """PandA IR — Part 6 (PoetryDB + Caching + Timing)
Type :help for commands. Type :quit to exit."""

HELP = """Commands:
  :help                   Show this help text
  :quit                   Exit the program
  :highlight on|off       Toggle highlighting of matches
  :search-mode AND|OR     Switch search mode (carry-over from Part 4/5)
  :hl-mode DEFAULT|GREEN  Switch highlight mode between default and green

Usage:
  Enter one or more words to search. Examples:
    love
    summer day

Notes:
  - Case-insensitive search
  - Print only matching sonnets
  - Use ANSI escape codes for highlighting when enabled
  - Load Shakespeare's sonnets via PoetryDB (with local caching)
  - Print how long loading and each query took
"""

POETRYDB_URL = "https://poetrydb.org/author,title/Shakespeare;Sonnet"

CACHE_FILENAME = "sonnets.json"