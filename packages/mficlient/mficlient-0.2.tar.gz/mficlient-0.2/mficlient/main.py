import argparse
import os
import pprint

from mficlient import client


class Application(object):
    def main(self):
        try:
            requests.packages.urllib3.disable_warnings()
        except:
            pass
        commands = [x[4:] for x in dir(self) if x.startswith('cmd')]
        command_list = os.linesep + os.linesep.join(commands)

        parser = argparse.ArgumentParser()
        parser.add_argument('command',
                            help='One of: %s' % command_list)
        parser.add_argument('--device',
                            help='Specific device')
        parser.add_argument('--state',
                            help='State to set (on or off)')
        parser.add_argument('--every', type=int, default=0,
                            help='Repeat (interval in seconds)')
        parser.add_argument('--since', type=int, default=60,
                            metavar='SECS',
                            help='Show data since SECS seconds ago')
        parser.add_argument('--column-headers', default=False,
                            action='store_true',
                            help='Show CSV column headers')
        args = parser.parse_args()

        if not hasattr(self, 'cmd_%s' % args.command):
            print('No such command `%s\'' % args.command)
            return 1

        host, port, user, _pass, path, = client.get_auth_from_env()
        self._client = client.MFiClient(host, user, _pass, port=port)

        while True:
            getattr(self, 'cmd_%s' % args.command)(args)
            if not args.every:
                break
            time.sleep(args.every)

    def cmd_dump_sensors(self, options):
        devices = self._client.get_devices()

        fmt = '%20s | %20s | %15s | %10s | %s'
        print(fmt % ('Model', 'Label', 'Tag', 'Value', 'Extra'))
        print('-' * 78)
        for device in devices:
            for port in device.ports.values():
                print(fmt % (port.model, port.label,
                             port.tag, port.value,
                             port.output))

    def cmd_raw_sensors(self, options):
        data = self._client.get_raw_sensors()
        pprint.pprint(data)

    def cmd_raw_status(self, options):
        data = self._client.get_raw_status()
        pprint.pprint(data)

    def cmd_raw_sensor(self, options):
        if not options.device:
            print('Must specify a device')
            return
        data = self._client.get_raw_sensors()
        for sensor in data:
            if data['label'] == options.device:
                pprint.pprint(data)
                return

    def cmd_control_device(self, options):
        if not options.device:
            print('Must specify a device')
            return
        if not options.state:
            print('Must specify a state')
            return
        port = self._client.get_port(label=options.device)
        port.control(options.state == 'on')

    def cmd_get_data(self, options):
        if not options.device:
            print('Must specify a device')
            return

        devices = self._client.get_devices()
        port = None
        for dev in devices:
            for port in dev.ports:
                if port.label == options.device:
                    break
        if port is None:
            print('No such port %s' % options.device)
            return

        if options.column_headers:
            print('time,min,max')

        for sample in data:
            dt = datetime.datetime.fromtimestamp(sample['time'] / 1000)
            print('%s,%s,%s' % (dt.strftime(TIME_FORMAT),
                                sample['min'],
                                sample['max']))

    def cmd_sensors_csv(self, options):
        if not options.device:
            print('Must specify a device')
            return
        sensors = self._client.get_raw_sensors()
        keys = ['active_pwr', 'energy_sum', 'i_rms', 'v_rms',
                'label', 'model', 'output', 'output_val', 'pf',
                'port', 'tag', 'val', 'wattHours', 'wattHoursBase']
        the_sensor = None
        for sensor in sensors:
            if sensor['label'] == options.device:
                the_sensor = sensor
                break

        if not the_sensor:
            print('No such device `%s\'' % options.device)
            return

        rpt_time = datetime.datetime.fromtimestamp(
            sensor['rpt_time'] / 1000)
        try:
            wh_rpt_time = datetime.datetime.fromtimestamp(
                sensor['wh_rpt_time'] / 1000)
        except KeyError:
            wh_rpt_time = ''

        vals = [str(sensor.get(k, '')) for k in keys]
        vals.insert(0, rpt_time.strftime(TIME_FORMAT))
        vals.append(wh_rpt_time and wh_rpt_time.strftime(TIME_FORMAT) or '')
        keys.insert(0, 'time')
        keys.append('wh_rpt_time')

        if options.column_headers:
            print(','.join(keys))

        print(','.join(vals))
