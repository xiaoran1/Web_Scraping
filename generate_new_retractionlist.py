import sys
import re
import csv

RETRACTION_LIST_PATH="retractionlist.csv"

def generate_more_column(original_file_path):
    is_head = 1
    out_file = "final_retractionlist.csv"
    with open(original_file_path, "rb") as in_txt:
        read_in = csv.reader(in_txt)
        with open(out_file, "wb") as out_csv:
            write_to = csv.writer(out_csv)
            for row in read_in:
                if is_head == 1:
                    is_head = 0
                    row.append("year")
                    write_to.writerow(row)
                else:
                    article_title =  row[9]
                    article_title = unicode(article_title, errors='ignore')
                    m = re.findall(r"\((.*?)\)", article_title)
                    if len(m) > 0 :
                        snew = m.pop()
                        snew = snew.split()
                        if len(snew)>0 and len(snew[len(snew) - 1]) == 4:
                            row.append(snew.pop())
                        else:
                            row.append("")
                    else:
                        row.append("")
                    authors = row[1]
                    authorlist = authors.split(";")
                    print authorlist
                    for single_author in authorlist:
                        row.append(single_author)
                    write_to.writerow(row)
    return out_file

if __name__ == '__main__':
    generate_more_column(RETRACTION_LIST_PATH)
    sys.exit(0)



