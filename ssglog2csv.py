import argparse
import html.parser
import datetime
import pathlib
import csv

class Parser(html.parser.HTMLParser):
    STATE_OTHER = 0
    STATE_DATE = 1
    STATE_ITEM = 2

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs:
                if attr[0] == 'class':
                    if attr[1].startswith('TrainingItem_Date_'):
                        self.state = self.STATE_DATE
                    elif attr[1].startswith('TrainingItem_ExerciseItem_') or attr[1].startswith('TrainingItem_Exercise_'):
                        self.state = self.STATE_ITEM
                    elif attr[1].startswith('TrainingItem_Row_'):
                        self.state = self.STATE_OTHER
                        self.rows.append([self.date.date().isoformat()])
                    else:
                        self.state = self.STATE_OTHER

    def handle_endtag(self, tag):
        self.state = self.STATE_OTHER

    def handle_data(self, data):
        if self.state == self.STATE_DATE:
            self.date = datetime.datetime.strptime(data, '%a, %b %d, %Y')
        if self.state == self.STATE_ITEM:
            self.rows[-1].append(data.strip())

    def parse_page(self, page):
        self.state = self.STATE_OTHER
        self.date = datetime.datetime.now()
        self.rows = []
        self.feed(page)
        return self.rows

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('logbooks', nargs='*')
    args = arg_parser.parse_args()
    for logbook in args.logbooks:
        logbook_path = pathlib.Path(logbook)
        csv_path = logbook_path.with_suffix('.csv')
        with open(logbook_path, 'rb') as logbook_file:
            rows = Parser().parse_page(logbook_file.read().decode(encoding='UTF-8'))
        with open(csv_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in rows:
                csv_writer.writerow(row)
