
import os
import logging

from alerta.app import app
from alerta.plugins import PluginBase

from influxdb import InfluxDBClient

LOG = logging.getLogger('alerta.plugins.influxdb')

DEFAULT_INFLUXDB_DSN = 'influxdb://user:pass@localhost:8086/alerta'  # 'influxdb://username:password@localhost:8086/databasename'

INFLUXDB_DSN = os.environ.get('INFLUXDB_DSN') or app.config.get('INFLUXDB_DSN', DEFAULT_INFLUXDB_DSN)
INFLUXDB_DATABASE = os.environ.get('INFLUXDB_DATABASE') or app.config.get('INFLUXDB_DATABASE', None)

# Specify the name of a combined measurement to which all alerts will be logged
INFLUXDB_SINGLE_MEASUREMENT = os.environ.get('INFLUXDB_SINGLE_MEASUREMENT') or app.config.get('INFLUXDB_SINGLE_MEASUREMENT', False)

# Specify True or False to log alerts to individual measurements (defaults to True)
INFLUXDB_SEPARATE_MEASUREMENT = True if os.environ.get('INFLUXDB_SEPARATE_MEASUREMENT', 'False') == 'True' else app.config.get('INFLUXDB_SEPARATE_MEASUREMENT', True)


class InfluxDBWrite(PluginBase):

    def __init__(self, name=None):

        self.client = InfluxDBClient.from_DSN(INFLUXDB_DSN, timeout=2)

        dbname = INFLUXDB_DATABASE or self.client._database
        try:
            if dbname:
                self.client.switch_database(dbname)
                self.client.create_database(dbname)
        except Exception as e:
            LOG.error('InfluxDB: ERROR - %s' % e)

        super(InfluxDBWrite, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        # event data
        points = []
        if INFLUXDB_SEPARATE_MEASUREMENT:
            points += [
                {
                    "measurement": alert.event,
                    "tags": {
                        "resource": alert.resource,
                        "environment": alert.environment,
                        "severity": alert.severity
                    },
                    "time": alert.last_receive_time,
                    "fields": {
                        "value": str(alert.value)
                    }
                }
            ]
        if INFLUXDB_SINGLE_MEASUREMENT:
            points += [
                {
                    "measurement": INFLUXDB_SINGLE_MEASUREMENT,
                    "tags": {
                        "event": alert.event,
                        "resource": alert.resource,
                        "environment": alert.environment,
                        "severity": alert.severity
                    },
                    "time": alert.last_receive_time,
                    "fields": {
                        "value": str(alert.value)
                    }
                }
            ]

        # common tags
        tags = {"service": ','.join(alert.service)}
        if alert.customer:
            tags.update(customer=alert.customer)

        LOG.debug('InfluxDB: points=%s, tags=%s', points, tags)

        try:
            if points:
                self.client.write_points(points, time_precision='ms', tags=tags)
        except Exception as e:
            raise RuntimeError("InfluxDB: ERROR - %s" % e)

    def status_change(self, alert, status, text):
        return
