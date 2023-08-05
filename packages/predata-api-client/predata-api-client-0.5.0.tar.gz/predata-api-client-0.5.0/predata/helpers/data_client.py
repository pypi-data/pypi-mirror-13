import urllib

from generic_client import PredataGenericClient


class PredataDataClient(PredataGenericClient):

    """
    Client for requesting Predata data information.
    """

    def list_source(self, country_code=None, topic_id=None):
        """
        List all signals within a domain.
        """
        endpoint = "data/sources/"
        query_dict = {
            "iso3": country_code,
            "topic_id": topic_id
        }
        params = urllib.urlencode({k: query_dict[k] for k in query_dict.keys() if query_dict[k]})
        if params:
            endpoint += "?%s" % params
        return {
            "country_code": country_code,
            "topic_id": topic_id,
            "result": self.make_request(endpoint)
        }

    def get_source(self, source_id):
        """
        Get source information.
        """
        endpoint = "data/sources/?source_id=%s" % source_id
        return {
            "source_id": source_id,
            "result": self.make_request(endpoint)
        }

    def list_country(self, footprint_id=None):
        """
        List all countries.
        """
        endpoint = "data/countries/"
        query_dict = {
            "footprint_id": footprint_id
        }
        params = urllib.urlencode({k: query_dict[k] for k in query_dict.keys() if query_dict[k]})
        if params:
            endpoint += "?%s" % params
        return {
            "footprint_id": footprint_id,
            "result": self.make_request(endpoint)
        }

    def get_country(self, country_code):
        """
        Get country data.
        """
        endpoint = "data/countries/%s/" % country_code
        return {
            "country_code": country_code,
            "result": self.make_request(endpoint)
        }

    def list_topic(self):
        """
        List all topics
        """
        endpoint = "data/topics/"
        return {
            "result": self.make_request(endpoint)
        }

    def get_topic(self, topic_id):
        """
        Get topic data.
        """
        endpoint = "data/topics/%s/" % topic_id
        return {
            "topic_id": topic_id,
            "result": self.make_request(endpoint)
        }

    def list_event(self, country_code=None, topic_id=None, tag_id="all"):
        """
        List all events in country by tag.
        """
        endpoint = "data/events/"
        query_dict = {
            "iso3": country_code,
            "topic_id": topic_id,
            "tag_id": tag_id
        }
        params = urllib.urlencode({k: query_dict[k] for k in query_dict.keys() if query_dict[k]})
        if params:
            endpoint += "?%s" % params
        return {
            "country_code": country_code,
            "topic_id": topic_id,
            "tag_id": tag_id,
            "result": self.make_request(endpoint)
        }

    def get_event(self, event_pk):
        """
        Get event data.
        """
        endpoint = "data/events/%s/" % event_pk
        return {
            "event": event_pk,
            "result": self.make_request(endpoint)
        }

    def new_event(self, event_data):
        """
        Add a new event.
        """
        endpoint = "data/events/new/"
        return {
            "event_data": event_data,
            "result": self.make_request(endpoint, method="PUT", data=event_data)
        }

    def new_event_tag(self, event_tag_data):
        """
        Add a new event tag to tag an event with a tag and a tier.
        """
        endpoint = "data/eventtags/new/"
        return {
            "event_tag_data": event_tag_data,
            "result": self.make_request(endpoint, method="PUT", data=event_tag_data)
        }

    def list_tag(self, tag_category=None, country_code=None, topic_id=None):
        """
        List all tags.

        Filter by tag_category, country, or topic. Filtering by country or topic
        returns tags for which events are populated in those domains.
        """
        endpoint = "data/tags/"
        query_dict = {
            "tag_category_id": tag_category,
            "iso3": country_code,
            "topic_id": topic_id,
        }
        params = urllib.urlencode({k: query_dict[k] for k in query_dict.keys() if query_dict[k]})
        endpoint += "?%s" % params
        return {
            "tag_category": tag_category,
            "country_code": country_code,
            "topic_id": topic_id,
            "result": self.make_request(endpoint)
        }

    def get_tag(self, tag_id):
        """
        Get tag data.
        """
        endpoint = "data/tags/%s/" % tag_id
        return {
            "tag_id": tag_id,
            "result": self.make_request(endpoint)
        }

    def list_tag_categories(self, tag_category_id=None):
        """
        List all tag categories.
        """
        endpoint = "data/tagcategories/"
        return {
            "tag_category_id": tag_category_id,
            "result": self.make_request(endpoint)
        }

    def get_tag_category(self, tag_category_id):
        """
        Get tag category.
        """
        endpoint = "data/tagcategories/%s/" % tag_category_id
        return {
            "tag_category_id": tag_category_id,
            "result": self.make_request(endpoint)
        }

    def list_asset(self, asset_type=None, country_code=None, topic_id=None):
        """
        List all assets.
        """
        endpoint = "data/assets/"
        query_dict = {
            "asset_type": asset_type,
            "iso3": country_code,
            "topic_id": topic_id,
        }
        params = urllib.urlencode({k: query_dict[k] for k in query_dict.keys() if query_dict[k]})
        endpoint += "?%s" % params
        return {
            "asset_type": asset_type,
            "country_code": country_code,
            "topic_id": topic_id,
            "result": self.make_request(endpoint)
        }

    def get_asset(self, asset_id):
        """
        Get asset data.
        """
        endpoint = "data/assets/%s/" % asset_id
        return {
            "asset_id": asset_id,
            "result": self.make_request(endpoint)
        }
