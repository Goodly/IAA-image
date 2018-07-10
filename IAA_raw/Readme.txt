These files contain everything necessary to utilize the
inter-annotator agreement algorithm.  This will not
calculate any kind of user-reliability scores.
Recommended use:
in the IAA.py file on line 5, change path to be the path to the data 
you're trying to calculate the agreement of
Must be a csv, must have the fields, taskrun_article_number,contributor_id,
	question_number, answer_number, start_pos, end_pos,source_text_length,
	answer_type, question_text
answer_type must be either: 'nominal', 'ordinal', 'checklist', or 'interval', 
	with interval referring to questions that only ask users to highlight
	and don't require any categorization
question_text isn't used for any calculations, but something needs to be there

When it's done running, the new data will be in a csv called 
	'agreement_scores.csv', you can change the name of the output file
	on line 30 of the IAA.py file

In the output:
	the article and question number are the article and question
		number of the question scores are being provided

	Agreed Answer is the number of the category that was 
		most frequently chosen by annotators (for ordinal questions
		the calculation is different but this column will still 
		return the 'winning' answer)
	
	Coding Score is the agreement score for the category selection.  It 
		is the percentage of annotators who selected a certain category,
		except for ordinal data which uses its own distance metric

	HighlightedIndices is an array of all indices that were highlighted
		by enough users to pass the threshold (calculated only among
		users who categorized the same way as the majority)
	
	
	Alpha Unitizing Score is the agreement score for the highlighting among
		users who both chose the majority category and highlighted something
		that passed the threshold. Calculated using Klaus Krippendorff's 
		alpha unitizing agreement 

	Alpha Unitizing Score Inclusive is the agreement score for the highlighting among
		users who chose the majority category (didn't necessarily highlighted 
		anything that passed the threshold). Calculated using Klaus Krippendorff's 
		alpha unitizing agreement. This value isn't utilized in calculating the 
		overall agreement score for the article because it commonly will be 
		deflated by users highlighting sloppily, seeing something drastically
		different than the majority, or other kinds of outliers

Notes on Threshold Matrix:
Output will be 'U' if there are too few users, 'L' if the score is too low to be
evaluated, 'M' if more annotators could lead to sufficient agreement, or will
be a number if agreement is above the threshold.
As soon as one part of the algorithm does not pass the threshold test, the rest 
of the output will just be the output from the threshold.  It is possible for
the categorization portion of a question to pass the threshold, and then the 
unitizing won't pass, in this instance the answer and score for the coding will
be displayed while the unitizing outputs will be the threshold output.  While this
leads to a lower overall agreement score, we recommend that any work based off of
this algorithm that is especially concerned with categorization being linked to 
unitization verify that both thresholds have been passed before using the overall
agreement score
