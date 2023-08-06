from affirmpy.api import API
from affirmpy.charge_event import ChargeEvent
from affirmpy.errors.charge_error import ChargeError


class Charge(object):

    @classmethod
    def retrieve(cls, id, client=API.client()):
        return cls(attrs={"id":id},client=client).refresh()

    @classmethod
    def create(cls, checkout_token, client=API.client()):
        response = client.make_request("/charges", "post", checkout_token=checkout_token)
        if response.is_success():
            return cls(attrs=response.body(), client=client)
        else:
            raise ChargeError.from_response(response)


    def void(self):
        return self._api_request("/charges/{0}/void".format(self.id), "post")


    def refund(self, amount=None):
        return self._api_request("/charges/{0}/refund".format(self.id), "post", {
            amount:amount
        })

    def capture(self, order_id=None, shipping_carrier=None, shipping_confirmation=None):
        return self._api_request("/charges/{0}/capture".format(self.id), "post", {
            order_id:order_id,
            shipping_carrier:shipping_carrier,
            shipping_confirmation:shipping_confirmation
        })


    def is_void(self):
        return self.void

    def refresh(self):
        response = self.client.make_request("/charges/{0}".format(self.id), "get")
        self._do_attributes(response.body())
        return self


    def __init__(self, attrs={}, client=API.client()):
        self.client = client
        self._do_attributes(attrs)


    def _api_request(self, url, method, params={}):
        response = self.client.make_request(url, method, params)
        if response.is_success():
            event = ChargeEvent(response.body)
            self.events.append(event)
            return event
        else:
            raise ChargeError.from_response(response)

    def _do_attributes(self, attrs):
        for k,v in attrs:
            if k is "events":
                self.events = self._parse_events(v)
            else:
                setattr(self, k, v)

    def _parse_events(self, events_attributes):
        if events_attributes:
            return map(ChargeEvent, events_attributes)
        else:
            return []
