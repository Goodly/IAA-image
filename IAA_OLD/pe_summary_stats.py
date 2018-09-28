import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("pe_data/pe_2018-01-04T18+0000--quiztaskruns.csv")
    print("Unique contributor_ids")
    print(df['contributor_id'].unique())

    print("Number of rows (answers) by contributor")
    print(df['contributor_id'].groupby(df['contributor_id']).count())

    print("Number of answers per article, per contributor")
    grouped = df.groupby(['contributor_id', 'taskrun_article_number'])
    summary = grouped.size()
    print(summary)
    header = ['answer_count']
    summary.to_csv("pe_data/pe_webconf_answer_counts_by_user_article.csv",
                   header=header)

    
