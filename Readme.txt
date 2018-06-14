README
The IAA file checks for the degree to which different annotators 
agree on the answer to questions in the schema and which sections
of text to highlight.  It is based on Klaus Krippendorff's 
Alpha Agreement algorithm, however there are a few things for 
users to be aware of that may (and should) affect how they use
the data output by this file.

1) Krippendorff's alpha adjusts for what he calls the expected 
disagreement between annotators based on the distribution of
responses across multiple questions. For our purposes we are
only concerned with consistency across a single question, The
data will be consistent across questions,however it mmay be different
than Krippendorff intended
