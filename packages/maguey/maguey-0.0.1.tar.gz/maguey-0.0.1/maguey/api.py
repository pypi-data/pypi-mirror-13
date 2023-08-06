import os, requests, json

AGAVE_TENANT_BASEURL = os.environ.get('AGAVE_TENANT_BASEURL', 'https://agave.iplantc.org/')

class Files(object):
    pass

class Notifications(object):
    pass

class Meta(object):
    @staticmethod
    def list(token, uuid=None, query=None):
        """Returns json list of metadata.

        Parameters:
            token   (required)  -   bearer token
            uuid    (optional)  -   get metadata by uuid
            query   (optional)  -   must be valid mongodb query

            Example query:
                query = '{"uuid":"2258583735108243941-ee4acae9fffff7a7-0001-012"}'

        Returns:
            List of JSON metadata objects with the following fields:

            associationIds - IDs of associated metadata objects
            owner - most likely the user who created the metadata
            name - often used to refer to the type of object the metadata describes
            schemaId - ...
            value - usually contains another JSON object
        """
        if not token or token == '':
            raise ValueError("token is a required parameter")

        method_path = "meta/v2/data"
        parameters = None

        if query:
            if type(query) == 'dict':
                query = json.dumps(query)
            parameters = {'q': query}

        url = "{base}/{method}/{uuid}".format(
            base = AGAVE_TENANT_BASEURL,
            method = method_path,
            uuid = uuid if uuid else ''
        )

        headers = {'Authorization': 'Bearer {}'.format(token)}

        result = requests.get(url, headers=headers, params=parameters)
        return result.json()

    @staticmethod
    def _add_update(token, body, uuid=None):
        """Internal: Adds or updates a metadata object.

        Parameters:
            token   (required)  -   bearer token
            body    (required)  -   must be valid json with 'name' and 'value' fields
            uuid    (optional)  -   metadata object to update

        Returns:
            JSON message with the following fields:

            status - success or error
            message - error message
            result - newly created metadata object
        """
        if not token or token == '':
            raise ValueError("token is a required parameter")

        if not body or body == '':
            raise ValueError("body is a required parameter")

        method_path = "meta/v2/data"

        url = "{base}/{method}/{uuid}".format(
            base = AGAVE_TENANT_BASEURL,
            method = method_path,
            uuid = uuid if uuid else ''
        )

        headers = {'Authorization': 'Bearer {}'.format(token),
                   'content-type': 'application/json'}

        result = requests.post(url, headers=headers, data=body)
        return result.json()

    @staticmethod
    def add(token, body):
        """Creates a metadata object.

        Parameters:
            token   (required)  -   bearer token
            body    (required)  -   must be valid json with 'name' and 'value' fields

        Returns:
            JSON message with the following fields:

            status - success or error
            message - error message
            result - newly created metadata object
        """
        if not token or token == '':
            raise ValueError("token is a required parameter")

        if not body or body == '':
            raise ValueError("body is a required parameter")

        return Meta._add_update(token, body)

    @staticmethod
    def update(token, uuid, body):
        """Updates a metadata object.

        Parameters:
            token   (required)  -   bearer token
            uuid    (required)  -   metadata object to update
            body    (required)  -   must be valid json with 'name' and 'value' fields

        Returns:
            JSON message with the following fields:

            status - success or error
            message - error message
            result - newly created metadata object
        """
        if not token or token == '':
            raise ValueError("token is a required parameter")

        if not uuid or uuid == '':
            raise ValueError("uuid is a required parameter")

        if not body or body == '':
            raise ValueError("body is a required parameter")

        return Meta._add_update(token, body, uuid)

    @staticmethod
    def delete(token, uuid):
        """Deletes a metadata object.

        Parameters:
            token   (required)  -   bearer token
            uuid    (required)  -   metadata object to update

        Returns:
            JSON message with the following fields:

            status - success or error
            message - error message
        """
        if not token or token == '':
            raise ValueError("token is a required parameter")

        if not uuid or uuid == '':
            raise ValueError("uuid is a required parameter")

        method_path = "meta/v2/data"

        url = "{base}/{method}/{uuid}".format(
            base = AGAVE_TENANT_BASEURL,
            method = method_path,
            uuid = uuid
        )

        headers = {'Authorization': 'Bearer {}'.format(token)}

        result = requests.delete(url, headers=headers)
        return result.json()

class Postits(object):
    pass

class Profiles(object):
    pass

class Systems(object):
    pass
