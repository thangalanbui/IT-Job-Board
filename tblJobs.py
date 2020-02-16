'''
Làm một website tuyển dụng.
Lấy dữ liệu các job từ:
https://github.com/awesome-jobs/vietnam/issues
Lưu dữ liệu vào một bảng jobs trong SQLite.
Xem ví dụ: https://docs.python.org/3/library/sqlite3.html
Dùng Flask tạo website hiển thị danh sách các jobs khi vào đường dẫn /.
Khi bấm vào mỗi job (1 link), sẽ mở ra trang chi tiết về jobs
(giống như trên
các trang web tìm viêc).
'''
import requests
from sqlalchemy import Column, Integer, String, DATE, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from math import ceil
from urllib.parse import urljoin
from datetime import date

Base = declarative_base()


class Jobs(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(String(1000), nullable=False)
    postdate = Column(DATE)
    issuesid = Column(Integer)

    def __init__(self, title=None, content=None, postdate=None, issuesid=None):
        self.title = title
        self.content = content
        self.postdate = postdate
        self.issuesid = issuesid

    def __repr__(self):
        return "Jobs(%r, %r, %r, %r)" % (self.title,
                                         self.content,
                                         self.postdate,
                                         self.issuesid)


engine = create_engine('sqlite:///jobs.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

TOKEN = '387dd9c070473002738cb865db1c656b29500e0d'

# get open_issues
repos_url = 'https://api.github.com/users/awesome-jobs/repos'
repos_token = urljoin(repos_url, '?access_token={0}'.format(TOKEN))
repo = requests.get(repos_token)
open_issues = repo.json()[1]['open_issues']

# get issues
issues_url = 'https://api.github.com/repos/awesome-jobs/vietnam/issues'
url_token = urljoin(issues_url, '?access_token={0}'.format(TOKEN))
issues = requests.get(url_token)
per_page = len(issues.json())
paged = ceil(open_issues / per_page)


issuess = session.query(Jobs.issuesid).all()
all_id = [int(issues[0]) for issues in issuess]

for page in range(1, paged + 1):
    parameters = [url_token, '&page={0}'.format(page)]
    page_issues = ''.join(parameters)
    jobpages = requests.get(page_issues)
    for job in jobpages.json():
        postdate = job['updated_at']
        dt = date(int(postdate.split('-')[0]),
                  int(postdate.split('-')[1]),
                  int(postdate.split('-')[2][:2]))
        # postdate = '{:%d-%m-%Y}'.format(dt)
        if job['id'] in all_id:
            continue
        else:
            jobs = Jobs(job['title'], job['body'], dt, job['id'])
            try:
                session.add(jobs)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
