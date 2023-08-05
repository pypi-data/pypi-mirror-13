# -*- coding: utf-8 -*-
# gthnk (c) 2014-2016 Ian Dennis Miller

import datetime
from flask.ext.diamond.utils.mixins import CRUDMixin
from .. import db
import flask


class Entry(db.Model, CRUDMixin):
    """
    An entry is an individual chunk of content in the Journal.
    An entry has a day, hour, and minute.  Seconds is always 0.
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Unicode(2**32))
    # tags = db.Column(db.String(2**16))

    # track the Day
    day_id = db.Column(db.Integer, db.ForeignKey("day.id"), nullable=False)
    day = db.relationship('Day', backref=db.backref('entries', lazy='dynamic'))

    def save(self, _commit):
        # see if this entry is a duplicate before creating it.
        existing_entries = self.query.filter_by(timestamp=self.timestamp)\
            .filter_by(content=self.content).count()
        if existing_entries and existing_entries > 0:  # if it exists
            flask.current_app.logger.info("skipping entry because entry already exists")
            return

        if not self.day_id:
            # find the day if it exists
            from day import Day
            this_date = datetime.date.fromordinal(self.timestamp.toordinal())
            this_day = Day.find(date=this_date)
            if not this_day:  # else create the day right now
                this_day = Day.create(date=this_date)
            # now assign a value to this Entry's day
            self.day = this_day

        super(Entry, self).save()

    def date_str(self):
        this_date = datetime.date.fromordinal(self.timestamp.toordinal())
        return datetime.datetime.strftime(this_date, "%Y-%m-%d")

    def hhmm(self):
        return datetime.datetime.strftime(self.timestamp, "%H%M")

    def __repr__(self):
        return '<Entry {} "{}">'.format(self.timestamp, self.content)
        #return '<Entry {} ({}) "{}">'.format(self.timestamp, self.tags, self.content)

    def __unicode__(self):
        return "\n\n{}\n\n{}".format(
            datetime.datetime.strftime(self.timestamp, "%H%M"), self.content
        )
