import json
import time
import requests
from six.moves import urllib

EVENT_DROPPING_TRANSFORM_CODE = "def transform(event):\n\treturn None"
DEFAULT_TRANSFORM_CODE = "def transform(event):\n\treturn event"

DEFAULT_SETTINGS_EMAIL_NOTIFICATIONS = {
    "digestInfo": True,
    "digestWarning": True,
    "digestError": True,
    "digestFrequency": "DAILY",
    "recipientsChanged": False,
    "recipients": []
}

DEFAULT_ENCODING = 'utf-8'

RESTREAM_QUEUE_TYPE_NAME = "RESTREAM"
METRICS_LIST = [
    'EVENT_SIZE_AVG',
    'EVENT_SIZE_TOTAL',
    'EVENT_PROCESSING_RATE',
    'CPU_USAGE',
    'MEMORY_CONSUMED',
    'MEMORY_LEFT',
    'INCOMING_EVENTS',
    'RESTREAMED_EVENTS',
    'UNMAPPED_EVENTS',
    'IGNORED_EVENTS',
    'ERROR_EVENTS',
    'LOADED_EVENTS_RATE',
    'LATENCY_AVG',
    'LATENCY_PERCENTILE_50',
    'LATENCY_PERCENTILE_95',
    'LATENCY_MAX',
    'EVENTS_IN_PIPELINE',
    'EVENTS_IN_TRANSIT'
]


class FailedToCreateInputException(Exception):
    pass


class Alooma(object):
    def __init__(self, hostname, username, password, port=8443,
                 server_prefix=''):

        self.hostname = hostname
        self.rest_url = 'https://%s:%d%s/rest/' % (hostname,
                                                   port,
                                                   server_prefix)
        self.username = username
        self.password = password
        self.requests_params = None
        self.cookie = None
        self.__login()
        if not self.cookie:
            raise Exception('Failed to obtain cookie')

    def __send_request(self, func, url, is_recheck=False, **kwargs):
        params = self.requests_params.copy()
        params.update(kwargs)
        response = func(url, **params)

        if response_is_ok(response):
            return response

        if response.status_code == 401 and not is_recheck:
            self.__login()

            return self.__send_request(func, url, True, **kwargs)

        raise Exception("The rest call to {url} failed: {error_message}".format(
                url=response.url, error_message=response.reason))

    def __login(self):
        url = self.rest_url + 'login'
        login_data = {"email": self.username, "password": self.password}
        response = requests.post(url, json=login_data)
        if response.status_code == 200:
            self.cookie = response.cookies
            self.requests_params = {
                    'timeout': 20,
                    'cookies': self.cookie,
                    'verify': False
            }
        else:
            raise Exception('Failed to login to {} with username: '
                            '{}'.format(self.hostname, self.username))

    def get_config(self):
        url_get = self.rest_url + 'config/export'
        response = self.__send_request(requests.get, url=url_get)
        config_export = parse_response_to_json(response)
        return config_export

    def get_structure(self):
        url_get = self.rest_url + 'plumbing/?resolution=1min'
        response = self.__send_request(requests.get, url_get)
        return parse_response_to_json(response)

    def get_mapping_mode(self):
        url = self.rest_url + 'mapping-mode'
        res = self.__send_request(requests.get, url)
        return res.content

    def set_mapping_mode(self, flexible):
        url = self.rest_url + 'mapping-mode'
        res = requests.post(url, json='FLEXIBLE' if flexible else 'STRICT',
                            **self.requests_params)
        return res

    def get_mapping(self, event_type):
        event_type = self.get_event_type(event_type)
        mapping = remove_stats(event_type)
        return mapping

    def create_s3_input(self, name, key, secret, bucket, prefix,
                        load_files, transform_id):
        post_data = {
            'source': None,
            'target': str(transform_id),
            'name': name,
            'type': 'S3',
            'configuration': {
                'awsAccessKeyId': key,
                'awsBucketName': bucket,
                'awsSecretAccessKey': secret,
                'filePrefix': prefix,
                'loadFiles': load_files
            }
        }
        return self.create_input(input_post_data=post_data)

    def create_mixpanel_input(self, mixpanel_api_key, mixpanel_api_secret,
                              from_date, name, transform_id):
        post_data = {
            "source": None,
            "target": str(transform_id),
            "name": name,
            "type": "MIXPANEL",
            "configuration": {
                "mixpanelApiKey": mixpanel_api_key,
                "mixpanelApiSecret": mixpanel_api_secret,
                "fromDate": from_date
            }
        }
        return self.create_input(input_post_data=post_data)

    def create_input(self, input_post_data):
        structure = self.get_structure()
        previous_nodes = [x for x in structure['nodes']
                          if x['name'] == input_post_data['name']]

        url = self.rest_url + 'plumbing/nodes'

        self.__send_request(requests.post, url, json=input_post_data)

        new_id = None
        retries_left = 10
        while retries_left > 0:
            retries_left -= 1
            structure = self.get_structure()
            input_type_nodes = [x for x in structure['nodes'] if x['name'] ==
                                input_post_data["name"]]
            if len(input_type_nodes) == len(previous_nodes) + 1:
                old_ids = set([x['id'] for x in previous_nodes])
                current_ids = set([x['id'] for x in input_type_nodes])
                try:
                    new_id = current_ids.difference(old_ids).pop()
                except KeyError:
                    pass

                return new_id
            time.sleep(1)

        raise FailedToCreateInputException(
            'Failed to create {type} input'.format(
                type=input_post_data["type"]))

    def get_transform_node_id(self):
        transform_node = self._get_node_by('type', 'TRANSFORMER')
        if transform_node:
            return transform_node['id']

        raise Exception('Could not locate transform id for %s' %
                        self.hostname)

    def remove_input(self, input_id):
        url = "{rest_url}plumbing/nodes/remove/{input_id}".format(
            rest_url=self.rest_url, input_id=input_id)
        self.__send_request(requests.post, url)

    def set_transform_to_default(self):
        transform = DEFAULT_TRANSFORM_CODE
        self.set_transform(transform=transform)

    def set_mapping(self, mapping, event_type):
        event_type = urllib.parse.quote(event_type)
        url = self.rest_url + 'event-types/{event_type}/mapping'.format(
            event_type=event_type)
        res = self.__send_request(requests.post, url, json=mapping)
        return res

    def discard_event_type(self, event_type):
        event_type_json = {
            "name": event_type,
            "mapping": {
                "isDiscarded": True,
                "tableName": ""
            },
            "fields": [], "mappingMode": "STRICT"
        }
        self.set_mapping(event_type_json, event_type)

    def discard_field(self, mapping, field_path):
        """
        :param mapping: this is the mapping json
        :param field_path:  this would use us to find the keys

        for example:
                        1.  mapping == {"a":1, b:{c:3}}
                        2.  the "c" field_path == a.b.c
        :return: new mapping JSON that the last argument would be discarded
        for example:
                        1.  mapping == {"a":1, b:{c:3}}
                        2.  field_path == "a.b.c"
                        3.  then the mapping would be as the old but the "c"
                            field that would be discarded
        """

        field = self.find_field_name(mapping, field_path)
        if field:
            field["mapping"]["isDiscarded"] = True
            field["mapping"]["columnName"] = ""
            field["mapping"]["columnType"] = None

    def unmap_field(self, mapping, field_path):
        """
        :param mapping: this is the mapping json
        :param field_path:  this would use us to find the keys

        for example:
                        1.  mapping == {"a":1, b:{c:3}}
                        2.  the "c" field_path == a.b.c
        :return: new mapping JSON that the last argument would be removed
        for example:
                        1.  mapping == {"a":1, b:{c:3}}
                        2.  field_path == "a.b.c"
                        3.  then the mapping would be as the old but the "c"
                            field that would be removed -> {"a":1, b:{}}
        """
        field = self.find_field_name(mapping, field_path)
        if field:
            mapping["fields"].remove(field)

    @staticmethod
    def map_field(schema, field_path, column_name, field_type, non_null,
                  **type_attributes):
        """
        :param  schema: this is the mapping json
        :param  field_path: this would use us to find the keys
        :param  field_type: the field type (VARCHAR, INT, FLOAT...)
        :param  type_attributes:    some field type need different attributes,
                                    for example:
                                        1. INT doesn't need any attributes.
                                        2. VARCHAR need the max column length
        :param column_name: self descriptive
        :param non_null: self descriptive
        :return: new mapping dict with new argument
        """

        field = Alooma.find_field_name(schema, field_path, True)
        Alooma.set_mapping_for_field(field, column_name, field_type,
                                     non_null, **type_attributes)

    @staticmethod
    def set_mapping_for_field(field, column_name,
                              field_type, non_null, **type_attributes):
        column_type = {"type": field_type, "nonNull": non_null}
        column_type.update(type_attributes)
        field["mapping"] = {
            "columnName": column_name,
            "columnType": column_type,
            "isDiscarded": False
        }

    @staticmethod
    def add_field(parent_field, field_name):
        field = {
            "fieldName": field_name,
            "fields": [],
            "mapping": None
        }
        parent_field["fields"].append(field)
        return field

    @staticmethod
    def find_field_name(schema, field_path, add_if_missing=False):
        """
        :param schema:  this is the dict that this method run over ot
                        recursively
        :param field_path: this would use us to find the keys
        :param add_if_missing: add the field if missing
        :return:    the field that we wanna find and to do on it some changes.
                    if the field is not found then raise exception
        """

        fields_list = field_path.split('.', 1)
        if not fields_list:
            return None

        current_field = fields_list[0]
        remaining_path = fields_list[1:]

        field = next((field for field in schema["fields"]
                      if field['fieldName'] == current_field), None)
        if field:
            if not remaining_path:
                return field
            return Alooma.find_field_name(field, remaining_path[0])
        elif add_if_missing:
            parent_field = schema
            for field in fields_list:
                parent_field = Alooma.add_field(parent_field, field)
            return parent_field
        else:
            # raise this if the field is not found,
            # not standing with the case ->
            # field["fieldName"] == field_to_find
            raise Exception("Could not find field path")

    def get_input_sleep_time(self, input_id):
        """
        :param input_id:    ID of the input whose sleep time to return
        :return:            sleep time of the input with ID input_id
        """
        url = self.rest_url + 'inputSleepTime/%s' % input_id
        res = requests.get(url, **self.requests_params)
        return float(json.loads(res.content).get('inputSleepTime'))

    def set_input_sleep_time(self, input_id, sleep_time):
        """
        :param input_id:    ID of the input whose sleep time to change
        :param sleep_time:  new sleep time to set for input with ID input_id
        :return:            result of the REST request
        """
        url = self.rest_url + 'inputSleepTime/%s' % input_id
        res = requests.put(url, str(sleep_time), **self.requests_params)
        return res

    def get_samples_status_codes(self):
        """
        :return:    a list of status codes each event in Alooma may be tagged
                    with. As Alooma supports more processing capabilities,
                    status codes may be added. These status codes are used for
                    sampling events according to the events' type & status.
        """
        url = self.rest_url + 'status-types'
        res = requests.get(url, **self.requests_params)
        return json.loads(res.content)

    def get_samples_stats(self):
        """
        :return:    a dictionary where the keys are names of event types,
                    and each value is another dictionary which maps from status
                    code to the amount of samples for that event type & status
        """
        url = self.rest_url + 'samples/stats'
        res = requests.get(url, **self.requests_params)
        return json.loads(res.content.decode())

    def get_samples(self, event_type=None, error_codes=None):
        """
        :param event_type:  optional string containing an event type name
        :param error_codes: optional list of strings containing event status
                            codes. status codes may be any string returned by
                            `get_sample_status_codes()`
        :return:    a list of 10 samples. if event_type is passed, only samples
                    of that event type will be returned. if error_codes is given
                    only samples of those status codes are returned.
        """
        url = self.rest_url + 'samples'
        if event_type:
            url += '?eventType=%s' % event_type
        if error_codes and isinstance(error_codes, list):
            url += ''.join(['&status=%s' % ec for ec in error_codes])
        res = requests.get(url, **self.requests_params)
        return json.loads(res.content)

    def get_transform(self):
        url = self.rest_url + 'transform/functions/main'
        res = self.__send_request(requests.get, url)
        return parse_response_to_json(res)["code"]

    def set_transform(self, transform):
        data = {'language': 'PYTHON', 'code': transform,
                'functionName': 'main'}
        url = self.rest_url + 'transform/functions/main'
        res = self.__send_request(requests.post, url, json=data)
        return res

    def test_transform(self, sample, temp_transform=None):
        """
        :param sample:  a json string or a dict, representing a sample event
        :param temp_transform: optional string containing transform code. if
                        not provided, the currently deployed transform will be
                        used.
        :return:        the results of a test run of the temp_transform on the
                        given sample. This returns a dictionary with the
                        following keys:
                            'output' - strings printed by the transform function
                            'result' - the resulting event
                            'runtime' - millis it took the function to run
        """
        url = self.rest_url + 'transform/functions/run'
        if temp_transform is None:
            temp_transform = self.get_transform()
        if not isinstance(sample, dict):
            sample = json.loads(sample)
        data = {
            'language': 'PYTHON',
            'functionName': 'test',
            'code': temp_transform,
            'sample': sample
        }
        res = requests.post(url, json=data, **self.requests_params)
        return json.loads(res.content)

    def test_transform_all_samples(self, event_type=None, status_code=None):
        """
        test many samples on the current transform at once
        :param event_type:  optional string containing event type name
        :param status_code: optional status code string
        :return:    a list of samples (filtered by the event type & status code
                    if provided), for each sample, a 'result' key is added which
                    includes the result of the current transform function after
                    it was run with the sample.
        """
        curr_transform = self.get_transform()
        samples_stats = self.get_samples_stats()
        results = []
        event_types = [event_type] if event_type else samples_stats.keys()
        for event_type in event_types:
            status_codes = [status_code] if status_code \
                else samples_stats[event_type].keys()
            for sc in status_codes:
                if samples_stats[event_type][sc] > 0:
                    samples = self.get_samples(event_type, sc)
                    for s in samples:
                        s['result'] = self.test_transform(s['sample'],
                                                          curr_transform)
                        results.append(s)
        return results

    def get_metrics_by_names(self, metric_names, minutes):
        if type(metric_names) != list and type(metric_names) == str:
            metric_names = [metric_names]
        elif type(metric_names) != str and type(metric_names) != list:
            raise Exception("metric_names can be only from type `str` or "
                            "`list`")
        for metric_name in metric_names:
            if metric_name not in METRICS_LIST:
                raise Exception("Metrics '{name}' not exists, please use one or"
                                " more of those: {metrics}".format(
                                 name=metric_names, metrics=METRICS_LIST))

        metrics_string = ",".join(metric_names)
        url = self.rest_url + 'metrics?metrics=%s&from=-%dmin&resolution=%dmin'\
                              '' % (metrics_string, minutes, minutes)
        res = self.__send_request(requests.get, url)

        response = parse_response_to_json(res)
        return response

    def get_incoming_queue_metric(self, minutes):
        response = self.get_metrics_by_names("EVENTS_IN_PIPELINE", minutes)
        incoming = non_empty_datapoint_values(response)
        if incoming:
            return max(incoming)
        else:
            return 0

    def get_outputs_metrics(self, minutes):
        """
        Returns the number of events erred / unmapped / discarded / loaded in
        the last X minutes
        :param minutes - number of minutes to check
        """
        response = self.get_metrics_by_names(['UNMAPPED_EVENTS',
                                              'IGNORED_EVENTS',
                                              'ERROR_EVENTS',
                                              'LOADED_EVENTS_RATE'],
                                             minutes)
        return tuple([sum(non_empty_datapoint_values([r])) for r in response])

    def get_restream_queue_metrics(self, minutes):
        response = self.get_metrics_by_names("EVENTS_IN_TRANSIT", minutes)
        return non_empty_datapoint_values(response)[0]

    def get_throughput_by_name(self, name):
        structure = self.get_structure()
        return [x['stats']['throughput'] for x in structure['nodes']
                if x['name'] == name and not x['deleted']]

    def get_incoming_events_count(self, minutes):
        response = self.get_metrics_by_names("INCOMING_EVENTS", minutes)
        return sum(non_empty_datapoint_values(response))

    def get_average_event_size(self, minutes):
        response = self.get_metrics_by_names("EVENT_SIZE_AVG", minutes)
        values = non_empty_datapoint_values(response)
        if not values:
            return 0

        return sum(values)/len(values)

    def get_max_latency(self, minutes):
        try:
            response = self.get_metrics_by_names("LATENCY_MAX", minutes)
            latencies = non_empty_datapoint_values(response)
            if latencies:
                return max(latencies) / 1000
            else:
                return 0
        except Exception as e:
            raise Exception("Failed to get max latency, returning 0. "
                            "Reason: %s", e)

    def create_table(self, table_name, columns):
        """
        :param table_name: self descriptive
        :param columns: self descriptive
        columns example:
        columns = [
        {
            'columnName': 'price', 'distKey': False, 'primaryKey': False,
            'sortKeyIndex': -1,
            'columnType': {'type': 'FLOAT', 'nonNull': False}
        }, {
            'columnName': 'event', 'distKey': True, 'primaryKey': False,
            'sortKeyIndex': 0,
            'columnType': {
                'type': 'VARCHAR', 'length': 256, 'nonNull': False
            }
        }
        ]
        """
        url = self.rest_url + 'tables/' + table_name

        res = self.__send_request(requests.post, url, json=columns)

        return parse_response_to_json(res)

    def alter_table(self, table_name, columns):
        """
        :param table_name: self descriptive
        :param columns: self descriptive
        columns example:
        columns = [
        {
            'columnName': 'price', 'distKey': False, 'primaryKey': False,
            'sortKeyIndex': -1,
            'columnType': {'type': 'FLOAT', 'nonNull': False}
        }, {
            'columnName': 'event', 'distKey': True, 'primaryKey': False,
            'sortKeyIndex': 0,
            'columnType': {
                'type': 'VARCHAR', 'length': 256, 'nonNull': False
            }
        }
        ]
        """
        url = self.rest_url + 'tables/' + table_name

        res = self.__send_request(requests.put, url, json=columns)

        return parse_response_to_json(res)


# TODO standardize the responses (handling of error code etc)
    def get_tables(self):
        url = self.rest_url + 'tables'
        res = self.__send_request(requests.get, url)
        return res

    def get_notifications(self, epoch_time):
        url = self.rest_url + "notifications?from={epoch_time}". \
            format(epoch_time=epoch_time)
        res = self.__send_request(requests.get, url)
        return parse_response_to_json(res)

    def get_plumbing(self):
        url = self.rest_url + "plumbing?resolution=30sec"
        res = self.__send_request(requests.get, url)
        return parse_response_to_json(res)

    def get_redshift_node(self):
        return self._get_node_by('name', 'Redshift')

    def set_redshift_config(self, hostname, port, schema_name, database_name,
                            username, password, skip_validation=False):
        redshift_node = self.get_redshift_node()
        payload = {
            'configuration': {
                'hostname': hostname,
                'port': port,
                'schemaName': schema_name,
                'databaseName': database_name,
                'username': username,
                'password': password,
                'skipValidation': skip_validation
                },
            'category': 'OUTPUT',
            'id': redshift_node['id'],
            'name': 'Redshift',
            'type': 'REDSHIFT',
            'deleted': False
        }
        url = self.rest_url + 'plumbing/nodes/'+redshift_node['id']

        res = self.__send_request(requests.put, url, json=payload)
        return parse_response_to_json(res)

    def get_redshift_config(self):
        redshift_node = self.get_redshift_node()
        if redshift_node:
            return redshift_node['configuration']
        return None

    @staticmethod
    def parse_notifications_errors(notifications):
        messages_to_str = "".join(
            [
                notification["typeDescription"] + "\n\t"
                for notification in notifications["messages"]
                if notification["severity"] == "error"
            ]
        )
        return messages_to_str

    def clean_system(self):
        self.set_transform_to_default()
        self.clean_restream_queue()
        self.remove_all_inputs()
        self.delete_all_event_types()
        self.set_settings_email_notifications(
            DEFAULT_SETTINGS_EMAIL_NOTIFICATIONS)
        self.delete_s3_retention()

    def remove_all_inputs(self):
        plumbing = self.get_plumbing()
        for node in plumbing["nodes"]:
            if node["category"] == "INPUT" \
                    and node["type"] not in ["RESTREAM", "AGENT"]:
                self.remove_input(node["id"])

    def delete_all_event_types(self):
        res = self.get_event_types()
        for event_type in res:
            self.delete_event_type(event_type["name"])

    def delete_event_type(self, event_type):
        event_type = urllib.parse.quote(event_type)
        url = self.rest_url + 'event-types/{event_type}'\
            .format(event_type=event_type)

        self.__send_request(requests.delete, url)

    def get_event_types(self):
        url = self.rest_url + 'event-types'
        res = self.__send_request(requests.get, url)
        return parse_response_to_json(res)

    def get_event_type(self, event_type):
        event_type = urllib.parse.quote(event_type)
        url = self.rest_url + 'event-types/' + event_type

        res = self.__send_request(requests.get, url)
        return parse_response_to_json(res)

    def set_settings_email_notifications(self, email_settings_json):
        url = self.rest_url + "settings/email-notifications"
        self.__send_request(requests.post, url, json=email_settings_json)

    def delete_s3_retention(self):
        url = self.rest_url + "settings/s3-retention"
        self.__send_request(requests.delete, url)

    def clean_restream_queue(self):
        event_types = self.get_event_types()
        for event_type in event_types:
            self.discard_event_type(event_type["name"])

        self.start_restream()
        queue_depth = self.get_restream_queue_size()
        while queue_depth != 0:
            queue_depth = self.get_restream_queue_size()
            time.sleep(1)

    def start_restream(self):
        restream_node = self._get_node_by('type', RESTREAM_QUEUE_TYPE_NAME)

        if restream_node:
            restream_id = restream_node["id"]
            url = self.rest_url + "plumbing/nodes/{restream_id}".format(
                restream_id=restream_id)
            restream_click_button_json = {
                "id": restream_id,
                "name": "Restream",
                "type": RESTREAM_QUEUE_TYPE_NAME,
                "configuration": {
                    "streaming": "true"
                },
                "category": "INPUT",
                "deleted": False,
                "state": None
            }
            self.__send_request(requests.put, url,
                                json=restream_click_button_json)
        else:
            raise Exception("Could not find '{restream_type}' type".format(
                    restream_type=RESTREAM_QUEUE_TYPE_NAME))

    def get_restream_queue_size(self):
        restream_node = self._get_node_by("type", RESTREAM_QUEUE_TYPE_NAME)
        return restream_node["stats"]["availbleForRestream"]

    def _get_node_by(self, field, value):
        """
        Get the node by (id, name, type, etc...)
        e.g. _get_node_by("type", "RESTREAM") ->
        :param field: the field to look the node by it
        :param value: tha value of the field
        :return: first node that found, if no node found for this case return
        None
        """
        plumbing = self.get_plumbing()
        for node in plumbing["nodes"]:
            if node[field] == value:
                return node
        return None


def response_is_ok(response):
    return 200 <= response.status_code < 300


def parse_response_to_json(response):
    return json.loads(response.content.decode(DEFAULT_ENCODING))


def non_empty_datapoint_values(data):
    """
    From a graphite like response, return the values of the non-empty datapoints
    """
    if data:
        return [t[0] for t in data[0]['datapoints'] if t[0]]
    return []


def remove_stats(mapping):
    if mapping['stats']:
        del mapping['stats']

    if mapping['fields']:
        for index, field in enumerate(mapping['fields']):
            mapping['fields'][index] = remove_stats(field)
    return mapping
