# StarTrek-Transcripts-Search
Enables the search of the fields series, episode, character, and quote in the star trek transcripts created by [StarTrek-Transcripts](https://github.com/BirkoRuzicka/Star-Trek-Transcripts) in json format. Only working on linux since ansi escape codes are used for text highlighting.

Before you can search the database you need to create the serach index via `starTrek_transcript_search.py -u -j StarTrekDialogue_v2.json`. This command must be called everytime the database is updated.

The query `python starTrek_transcript_search.py -q 'series:TOS, character:khan captain'` provides the following output:

![](https://github.com/rainbowsend/Star-Trek-Transcripts-Search/blob/main/search_output_example.png)
