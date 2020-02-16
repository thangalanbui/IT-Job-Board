import markdown
from flask import Flask, render_template, Markup, current_app
from sqlalchemy import create_engine, MetaData, Table
from flask_paginate import Pagination, get_page_args
from datetime import datetime

engine = create_engine('sqlite:///jobs.db',
                       connect_args={'check_same_thread': False},
                       convert_unicode=True,
                       echo=True)
metadata = MetaData(bind=engine)
jobs = Table('jobs', metadata, autoload=True)
conn = engine.connect()

app = Flask(__name__)


@app.route('/')
def show_all_jobs(page=1):
    query = 'select count(*) from jobs'
    job = conn.execute(query)
    total = job.fetchone()[0]
    page, per_page, offset = get_page_args()
    sql = 'select title, postdate, issuesid from jobs '\
          'order by postdate desc limit {}, {}'\
          .format(offset, per_page)
    data = conn.execute(sql)
    getdate = (datetime.strptime(d[1], '%Y-%m-%d') for d in data)
    postdates = (d.strftime('%d-%m-%Y') for d in getdate)
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='jobs',
                                format_total=True,
                                format_number=True,
                                )

    return render_template('show-all-jobs.html',
                           jobs=data,
                           dates=postdates,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/jobs/<string:id>')
def jobs_details(id=None):
    query = 'select * from jobs where issuesid == {0}'.format(id)
    job = conn.execute(query)
    row = job.fetchone()
    content = Markup(markdown.markdown(row['content']))
    postdate = datetime.strptime(row['postdate'], '%Y-%m-%d')
    return render_template('job-detail.html',
                           job=row,
                           date='{:%d-%m-%Y}'.format(postdate),
                           content=content)


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )


if __name__ == '__main__':
    app.run(debug=True)
