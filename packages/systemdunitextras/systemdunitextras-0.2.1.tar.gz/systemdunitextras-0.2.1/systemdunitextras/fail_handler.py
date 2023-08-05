#!/usr/bin/python3
import os
import datetime
import argparse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker

from gymail.core import send_mail
from .settings import instance_hour, default_hour, log, db_path

Base = declarative_base()


class SystemdInstance(Base):  # (2)
    __tablename__ = 'systemd_instances'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time = Column(DateTime, default=datetime.datetime.utcnow)


class FailHandler():

    def __init__(self, instance, hour, hostname):
        self.instance = instance
        self.hour = hour
        self.hostname = hostname
        engine = create_engine('sqlite:///{0}'.format(db_path), echo=True)
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)  # (1)
        self.session = DBSession()

    def run(self):
        last_event = self.session.query(SystemdInstance).filter(SystemdInstance.name == self.instance).order_by(SystemdInstance.time.desc())
        if last_event.count() == 0:
            self.notify()
        elif last_event.count() > 0 and (datetime.datetime.utcnow() - last_event.first().time) > datetime.timedelta(hours=self.hour):
            self.notify()
        else:
            log.info('< {0} hours. Not firing notification again.'.format(self.hour))

    def notify(self):
        send_mail(event="error", subject=os.path.basename(__file__), message="systemd unit entered failed state. Instance: {0} Hostname: {1}".format(self.instance, self.hostname))
        event = SystemdInstance(name=self.instance)
        self.session.add(event)
        self.session.commit()


def argparse_entry():
    parser = argparse.ArgumentParser(
        description="fail_handler is triggered for service units that point to its unit service file in the OnFailure= setting. It checks \
                     if a notification for the failed service was sent within the time (in hours) specified in settings.py. If no, it sends \
                     a notification, else it does nothing."
    )
    parser.add_argument('-i', '--instance', help='systemd instance specifier: %I', required=True)
    parser.add_argument('-host', '--hostname', help='systemd hostname specifier: %H', required=True)
    args = parser.parse_args()
    if args.instance in instance_hour:
        hour = instance_hour[args.instance]
    else:
        hour = default_hour
    fh = FailHandler(args.instance, hour, args.hostname)
    fh.run()


# Notes:
# (1) A DBSession() instance establishes all conversations with the database and represents a "staging zone" for all the objects loaded into the
#     database session object. Any change made against the objects in the session won't be persisted into the database until you call session.commit().
#     If you're not happy about the changes, you can revert all of them back to the last commit by calling session.rollback()
# (2) SQLAlchemist model declaration.
