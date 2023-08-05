Known Issues & Planned Improvements
===================================

- Implement a DateRange class and replace all occurences of fromdate,
  todate, dateformat.
  
- Implement find_files() without dateranges at all. It should be
  possible to simply process all files within a directory (also
  recursively)
  
- TwistML currently assumes raw twitter data to be avaialble as one
  json file per day. Make sure the internet-archive's file scheme is
  supported as well
  
- Add support for hourly time resolution instead of daily only.

- Evaluation subpackage can only deal with binary classification.
  Possibly explore adding multiclass.
  
- The way logging is currently set up is weird and should be reworked.

- gensim's LabeledSentence is deprecated, use TaggedDocument instead
