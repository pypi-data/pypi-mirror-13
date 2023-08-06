from serverdensity import Response
from serverdensity.wrapper.crud import CRUD
from serverdensity.wrapper.jsonobject import JsonObject


class Alert(JsonObject, CRUD):

    _schemapath = '/schema/alerts.json'

    PATHS = {
        'create': '/alerts/configs',
        'delete': '/alerts/configs/{}',
        'list': '/alerts/configs',
        'list_by_subject': '/alerts/configs/{}',
        'update': '/alerts/configs/{}',
        'view': '/alerts/configs/{}',
        'triggered': '/alerts/triggered',
        'device_metrics': '/alerts/device_alerts.json',
        'service_metrics': '/alerts/service_alerts.json'
    }

    def triggered(self, _id=None, subject_type=None, closed=None, **kwargs):
        if _id and subject_type:
            url = self.PATHS['triggered'] + '/{}'.format(_id)
            kwargs.setdefault('params', {})['subjectType'] = subject_type
        else:
            url = self.PATHS
        if closed:
            kwargs.setdefault('params', {})['closed'] = closed
        result = self.api.get(url=url, **kwargs)
        return [self.__class__(item) for item in result]

    def device_metrics(self, **kwargs):
        return Response(self.api.get(url=self.PATHS['device_metrics'], **kwargs))

    def service_metrics(self, **kwargs):
        return Response(self.api.get(url=self.PATHS['service_metrics'], **kwargs))
