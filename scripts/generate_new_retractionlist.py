# This script will first read the retraction_notices list file,
# then for each row's title name and authors column, it will generate a new column
# for publication year and as many author name columns as the number of authors
# into a new file, then the original file without year and single author column will be
# removed, the file with new columns will replace the old one

from General_browser_function_handle import *

CONINFO = ConfigData("","")

def read_from_config():
    global CONINFO
    with open(CONFIGRATION_FILE_NAME, "r+") as my_config:
        for line in my_config:
            line = line.replace('=', ' ').replace('/n', ' ').split()
            if line[0] == "RETRACTION_NOTICES_FILE_PATH":
                CONINFO.retraction_notices_path= "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])

def generate_more_column(original_file_path):
    is_head = 1
    out_file = "{}\data\copy{}".format(os.path.dirname(os.getcwd()),original_file_path.rsplit("\\", 1)[-1])
    print out_file
    #column index value init
    take_out_col_num = 1
    author_col = 0
    title_col = 0
    with open(original_file_path, "rb") as in_txt:
        read_in = csv.reader(in_txt)
        with open(out_file, "wb") as out_csv:
            write_to = csv.writer(out_csv)
            for row in read_in:
                if take_out_col_num == 1:
                    for i, coltext in enumerate (row):
                        if coltext == "AU":
                            author_col = i
                        if coltext == "TI":
                            title_col = i
                    take_out_col_num = 0
                if is_head == 1:
                    is_head = 0
                    row.append("")
                    row.append("year")
                    write_to.writerow(row)
                else:
                    article_title =  row[title_col]
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
                    authors = row[author_col]
                    authorlist = authors.split(";")
                    for single_author in authorlist:
                        row.append(single_author)
                    write_to.writerow(row)
    return out_file

if __name__ == '__main__':
    read_from_config()
    out_file = generate_more_column(CONINFO.retraction_notices_path)
    os.remove(CONINFO.retraction_notices_path)
    os.rename(out_file,CONINFO.retraction_notices_path)
    sys.exit(0)



