#!/usr/bin/python3

import json
import textwrap
import argparse
import os.path
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import *
from whoosh import highlight

class EscapeSeqFormatter(highlight.Formatter):
    """ highlights with unicode escape sequence (bold)
    """

    def format_token(self, text, token, replace=False):
        # Use the get_text function to get the text corresponding to the
        # token
        tokentext = highlight.get_text(text, token, replace)

        # Return the text as you want it to appear in the highlighted
        # string
        return "\x1b[1;4m%s\x1b[22;24m" % tokentext


def updateIndex( ix, transcript_json_file ):
  """
  reads the transcript in json format and adds the entries to the whoosh index
  :param ix: whoosh index object
  :param cat_path: path to the catalog
  """

  wrapper = textwrap.TextWrapper(width=60, subsequent_indent='\t')

  writer = ix.writer()

  with open(transcript_json_file,'r') as f:
    print('parsing '+ transcript_json_file)
    transcript=json.load(f)

    for series,ts in transcript.items():
      for episode,ts in ts.items():
        print('%s %s' % (series,episode), end="\r")
        for character,quotes in ts.items():
          for quote in quotes:
            writer.add_document(series = series,
                                episode = episode,
                                character = character,
                                quote = wrapper.fill(text=quote))

  print(' '*11, end="\r")
  writer.commit()

def hf(res,field):
    """
    returns the contnet of a filed where the matching part is highlighted
    :param res: whoosh hit object
    :param filed: field name
    """
    return res.highlights(field, minscore=0)

if __name__ == '__main__':

  scriptPath = os.path.dirname(os.path.realpath(__file__))

  # parse input arguments ---------------------------------------------------
  parser = argparse.ArgumentParser(description='searches the star trek transcript')

  parser.add_argument('-q', action="store", help='query in fields: "series","episode","character","quotes"\
                      Query syntax: https://whoosh.readthedocs.io/en/latest/querylang.html \
                      e.g. series:tos character:khan captain')
  parser.add_argument('-u', action="store_true", help='update the index')
  parser.add_argument('-j', action="store", help='path to jason db', default = scriptPath+'/StarTrekDialogue_v2.json')
  parser.add_argument('-i', action="store", help='path to index', default = scriptPath+'/index')
  parser.add_argument('-n', action="store", help='maximal number of printed results (default=20)', default = 20)

  args = parser.parse_args()

  # define index schema-- ---------------------------------------------------
  schema = Schema(series=TEXT(stored=True),
                  episode=TEXT(stored=True),
                  character=NGRAM(stored=True,minsize=1, maxsize=20),
                  quote=TEXT(stored=True)
                  )

  # create or open existing index

  if args.u:
      if not os.path.exists(args.i):
          os.mkdir(args.i)
      ix = create_in(args.i, schema)
      updateIndex(ix, args.j)
  else:
      ix = open_dir(args.i)

  # perform search ---------------------------------------------------------

  if args.q:

    with ix.searcher() as searcher:

      parser = MultifieldParser(["series","episode","character","quote"], ix.schema)

      parser.add_plugin(FuzzyTermPlugin())

      myquery = parser.parse(args.q)

      results = searcher.search(myquery, limit=int(args.n))

      results.fragmenter = highlight.WholeFragmenter(charlimit = None)
      results.formatter = EscapeSeqFormatter()

      print('-'*60)
      print( 'found \x1b[0;1m%u\x1b[0;0m matching entries for query:\x1b[92;2m %s\x1b[0m\n' % ( len(results), args.q ) )
      for i,res in enumerate( results, start = 1) :
          print( '\x1b[0;1m(%u) \x1b[94;22m%s \x1b[0m%s \x1b[92;22m%s\x1b[0m:' % ( i, hf(res,"series"), hf(res,"episode"), hf(res,"character") ))
          print( '\t%s\x1b[0m\x1b[0m' % (hf(res,"quote")))
          print('\x1b[0m')
