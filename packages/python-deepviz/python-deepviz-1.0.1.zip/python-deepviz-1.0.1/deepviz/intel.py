import requests
import simplejson
import inspect

URL_INTEL_IP = "https://api.deepviz.com/intel/network/ip"
URL_INTEL_DOMAIN = "https://api.deepviz.com/intel/network/domain"
URL_INTEL_SEARCH = "https://api.deepviz.com/intel/search"
URL_INTEL_SEARCH_ADVANCED = "https://api.deepviz.com/intel/search/advanced"


class Result:
    status = None
    msg = None

    def __init__(self, status, msg):
        self.status = status
        self.msg = msg

    def __repr__(self):
        return "Result(status='{status}', msg='{data}')".format(status=self.status, data=self.msg)


class ResultError(Result):
    def __init__(self, msg):
        Result.__init__(self, 'error', msg)


class ResultSuccess(Result):
    def __init__(self, msg):
        Result.__init__(self, 'success', msg)


class Intel:
    def ip_info(self, api_key=None, ip=None, timestamp=None, history=False):
        if not ip and not timestamp and not api_key:
            msg = "Invalid or missing parameters. Please try again!"
            return ResultError(msg=msg)

        if ip and timestamp:
            msg = "You must specify either a list of IPs or timestamp. Please try again!"
            return ResultError(msg=msg)

        if history:
            _history = "true"
        else:
            _history = "false"

        if ip:
            if not isinstance(ip, list):
                msg = "You must provide one or more IPs in a list. Please try again!"
                return ResultError(msg=msg)

            body = simplejson.dumps(
                    {
                        "api_key": api_key,
                        "ip": ip,
                        "history": _history
                    }
            )
        elif timestamp:
            body = simplejson.dumps(
                    {
                        "api_key": api_key,
                        "timestamp": timestamp,
                        "history": _history
                    }
            )

        try:
            r = requests.post(URL_INTEL_IP, data=body)
        except Exception as e:
            msg = "Error while connecting to Deepviz. (%s)" % e
            return ResultError(msg=msg)

        data = simplejson.loads(r.content)

        if r.status_code == 200:
            msg = data['data']
            return ResultSuccess(msg=msg)
        else:
            msg = "(%s) Error while connecting to Deepviz. (%s)" % (r.status_code, data['errmsg'])
            return ResultError(msg=msg)

    def domain_info(self, api_key=None, domain=None, timestamp=None, history=False, filters=None):
        if not domain and not timestamp and not api_key:
            msg = "Invalid or missing parameters. Please try again!"
            return ResultError(msg=msg)

        if domain and timestamp:
            msg = "You must specify either a list of domains or timestamp. Please try again!"
            return ResultError(msg=msg)

        if history:
            _history = "true"
        else:
            _history = "false"

        if filters:
            if not isinstance(filters, list):
                msg = "You must provide one or more output filters in a list. Please try again!"
                return ResultError(msg=msg)

        if domain:
            if not isinstance(domain, list):
                msg = "You must provide one or more IPs in a list. Please try again!"
                return ResultError(msg=msg)

            if filters:
                body = simplejson.dumps(
                        {
                            "api_key": api_key,
                            "domain": domain,
                            "history": _history,
                            "output_filters": filters
                        }
                )
            else:
                body = simplejson.dumps(
                        {
                            "api_key": api_key,
                            "domain": domain,
                            "history": _history
                        }
                )

        elif timestamp:
            if filters:
                body = simplejson.dumps(
                        {
                            "api_key": api_key,
                            "time_delta": timestamp,
                            "history": _history,
                            "output_filters": filters
                        }
                )
            else:
                body = simplejson.dumps(
                        {
                            "api_key": api_key,
                            "time_delta": timestamp,
                            "history": _history
                        }
                )

        try:
            r = requests.post(URL_INTEL_DOMAIN, data=body)
        except Exception as e:
            msg = "Error while connecting to Deepviz. (%s)" % e
            return ResultError(msg=msg)

        data = simplejson.loads(r.content)

        if r.status_code == 200:
            msg = data['data']
            return ResultSuccess(msg=msg)
        else:
            msg = "(%s) Error while connecting to Deepviz. (%s)" % (r.status_code, data['errmsg'])
            return ResultError(msg=msg)

    def search(self, api_key=None, search_string=None, start_offset=None, elements=None):
        if not search_string and not api_key:
            msg = "Invalid or missing parameters. Please try again!"
            return ResultError(msg=msg)

        if start_offset is not None and elements is not None:

            result_set = ["start=%d" % start_offset, "rows=%d" % elements]
            body = simplejson.dumps(
                    {
                        "api_key": api_key,
                        "string": search_string,
                        "result_set": result_set
                    }
            )
        else:
            body = simplejson.dumps(
                    {
                        "api_key": api_key,
                        "string": search_string
                    }
            )

        try:
            r = requests.post(URL_INTEL_SEARCH, data=body)
        except Exception as e:
            msg = "Error while connecting to Deepviz. (%s)" % e
            return ResultError(msg=msg)

        data = simplejson.loads(r.content)

        if r.status_code == 200:
            msg = data['data']
            return ResultSuccess(msg=msg)
        else:
            msg = "(%s) Error while connecting to Deepviz. (%s)" % (r.status_code, data['errmsg'])
            return ResultError(msg=msg)

    def advanced_search(self, api_key=None, sim_hash=None, created_files=None, imp_hash=None, url=None, strings=None,
                        ip=None, asn=None, classification=None, rules=None, country=None, new_sample=None,
                        time_delta=None, result_set=None, ip_range=None, domain=None):
        if not api_key:
            msg = "Invalid or missing parameters. Please try again!"
            return ResultError(msg=msg)

        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)

        body = {}

        body['api_key'] = api_key
        for i in args:
            if values[i] and i != "self" and i != "api_key":
                if i == "sim_hash" or i == "created_files" or i == "imp_hash" or i == "url" or i == "strings" or i == "ip" or i == "asn" or i == "rules" or i == "country" or i == "result_set" or i == "domain":
                    if isinstance(values[i], list):
                        body[i] = values[i]
                    else:
                        msg = "Value '%s' must be in a list form. Please try again!" % i
                        return ResultError(msg=msg)
                else:
                    if isinstance(values[i], str):
                        body[i] = values[i]
                    else:
                        msg = "Value '%s' must be in a string form. Please try again!" % i
                        return ResultError(msg=msg)

        final_body = simplejson.dumps(body)

        try:
            r = requests.post(URL_INTEL_SEARCH_ADVANCED, data=final_body)
        except Exception as e:
            msg = "Error while connecting to Deepviz. (%s)" % e
            return ResultError(msg=msg)

        data = simplejson.loads(r.content)

        if r.status_code == 200:
            msg = data['data']
            return ResultSuccess(msg=msg)
        else:
            msg = "(%s) Error while connecting to Deepviz. (%s)" % (r.status_code, data['errmsg'])
            return ResultError(msg=msg)
