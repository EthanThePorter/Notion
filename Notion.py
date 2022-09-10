import requests
import json
import asyncio
import aiohttp

# Access to Notion database requires security key. Refer to https://developers.notion.com/docs/getting-started
from notion_key import key


class Notion:

    def __init__(self, database_id, name_text='Name'):
        """
        Gets data on initialization
        :param database_id: Notion database ID. Refer to https://developers.notion.com/docs/getting-started
        :param name_text: Text used as identifier for 'title' type column. Default is Name
        """
        # Initialize text for Name column
        self.name_text = name_text
        # Initialize URL and authorization headers
        self.URL = f'https://api.notion.com/v1/databases/{database_id}/query'
        self.database_id = database_id
        self.headers = {
            'Authorization': f'Bearer {key}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }
        # Send POST to server
        response = requests.post(self.URL, headers=self.headers)
        # Format response as JSON
        self.data = response.json()

    def refresh(self):
        """
        Function to refresh data with most recent changes
        :return: Data from Notion database in JSON format
        """
        # Send POST to server
        response = requests.post(self.URL, headers={
            'Authorization': f'Bearer {key}',
            'Notion-Version': '2022-06-28'
        })
        # Format response as JSON
        self.data = response.json()
        return self.data

    def save(self, filename):
        """
        Save self.data JSON to file
        :param filename: Format: 'fileName.json'
        """
        # Write JSON to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def save_dict(dictionary, filename):
        """
        Saves python dictionary to JSON file
        """
        # Write JSON to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)

    def id_all(self):
        """
        Returns ordered list of IDs
        """
        id_list = []
        for item in self.data['results']:
            id_list.append(item['id'])
        return id_list

    def id(self, item_name):
        """
        Gets ID of item
        """
        index = self.get(self.name_text).index(item_name)
        return self.id_all()[index]

    def get(self, column_name):
        """
        Function to get all data from a specified column.
        For configuring properties, refer to https://developers.notion.com/reference/property-value-object.
        :return: Returns column as a list
        """
        # Get type of column
        column_type = self.data['results'][0]['properties'][column_name]['type']
        # Initialize list to save elements to
        elements = []
        # Use type to get data path
        match column_type:
            case 'title':
                for element in self.data['results']:
                    try:
                        elements.append(element['properties'][column_name]['title'][0]['plain_text'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'rich_text':
                for element in self.data['results']:
                    try:
                        elements.append(element['properties'][column_name]['rich_text'][0]['plain_text'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'number':
                for element in self.data['results']:
                    try:
                        elements.append(element['properties'][column_name]['number'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'select':
                for element in self.data['results']:
                    try:
                        elements.append(element['properties'][column_name]['select']['name'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'date':
                for element in self.data['results']:
                    try:
                        elements.append(element['properties'][column_name]['date']['start'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'rollup':
                return self.get_rollup_column(column_name)


    def index(self, index_column_name, index_value, target_column_name):
        """
        Gets list of all indexes for a specified value
        :param index_column_name: Column being used as index
        :param index_value: Value in index column to
        :param target_column_name: Column being searched
        :return: Returns value from target column at index
        """
        # Gets column being used for index
        index_column = self.get(index_column_name)
        # Checks if column contains index value
        if not index_column.__contains__(index_value):
            print(f'List does not contain any occurrences of "{index_value}".')
            return None
        # Gets list of all indexes that contain value
        indices = []
        indexed = False
        while indexed is False:
            # Get index
            index = index_column.index(index_value)
            # Append index to indices list
            indices.append(index)
            # Change value at index
            index_column[index] = None
            # Check if column contains any other occurrences of the index value
            if not index_column.__contains__(index_value):
                indexed = True
        # Get target column
        target_column = self.get(target_column_name)
        # Get values at indices and return
        values = []
        for i in indices:
            values.append(target_column[i])
        return values

    def set(self, name, column_name, value):
        """
        Function to update values in Notion database.
        For general setup, refer to https://developers.notion.com/reference/patch-page.
        For configuring properties, refer to https://developers.notion.com/reference/property-value-object.
        """
        # Get ID for name
        ID = self.id(name)
        # Get URL to send request to
        URL = f'https://api.notion.com/v1/pages/{ID}'
        # Get type of column
        column_type = self.data['results'][0]['properties'][column_name]['type']

        # Use type to get data path
        match column_type:
            case 'number':
                data = json.dumps({
                    'properties': {
                        column_name: {
                            'number': value
                        }
                    }
                })
            case 'title':
                data = json.dumps({
                    'properties': {
                        column_name: {
                            "title": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": value
                                    }
                                }
                            ]
                        }
                    }
                })
            case 'rich_text':
                data = json.dumps({
                    'properties': {
                        column_name: {
                            'rich_text': [
                                {
                                    'type': 'text',
                                    'text': {
                                        'content': value
                                    }
                                }
                            ]
                        }
                    }
                })
            case 'select':
                data = json.dumps({
                    'properties': {
                        column_name: {
                            'select': {
                                'name': value
                            }
                        }
                    }
                })
            case 'status':
                data = json.dumps({
                    'properties': {
                        column_name: {
                            'status': {
                                'name': value
                            }
                        }
                    }
                })
            case 'date':
                data = json.dumps({
                    'properties': {
                        column_name: {
                            'date': {
                                'start': value
                            }
                        }
                    }
                })
            # Need to implement Multi-Select, Formula, Relation, Rollup
        # Send request to API
        response = requests.request("PATCH", URL, headers=self.headers, data=data)
        print(response.status_code)
        print(response.text)
        # Refresh data
        self.refresh()

    def add(self, properties):
        """
        NOT YET FUNCTIONAL
        Creates new page and adds page to database. Reference https://developers.notion.com/reference/post-page
        """
        # Path to send request to
        URL = f'https://api.notion.com/v1/pages/'
        # Initialize Data to send
        newData = {
            'parent': {
                "type": "database_id",
                "database_id": self.database_id
            },
            'properties': properties,
        }
        # Format data to JSON
        newData = json.dumps(newData)
        # Send Request to server
        response = requests.request("POST", URL, headers=self.headers, data=newData)
        print(response.status_code)
        print(response.text)

    def delete(self, name):
        # Get ID for name
        page_id = self.id(name)
        # Initialize URL to send delete request to
        URL = f'https://api.notion.com/v1/pages/{page_id}'
        # Initialize request
        data = json.dumps({
            'archived': True
        })
        # Send request to server
        response = requests.request("PATCH", URL, headers=self.headers, data=data)
        print(response.status_code)
        print(response.text)

    def get_property_id(self, item_property):
        return self.data['results'][0]['properties'][item_property]['id']

    def get_rollup_column(self, column_name):
        # Get list of items
        items = self.get(self.name_text)
        # Get IDs for each item
        item_ids = []
        for item in items:
            item_ids.append(self.id(item))
        # Get column ID - "Property ID" in Notion terms
        column_id = self.get_property_id(column_name)
        # Initialize URLs for each request
        URLs = []
        for i in range(len(items)):
            URLs.append(f'https://api.notion.com/v1/pages/{item_ids[i]}/properties/{column_id}')
        # Send requests to API and output results - save first result to file
        responses = asyncio.run(self.request_urls(URLs))
        for response in responses:
            print(json.dumps(response))
        self.save_dict(responses[0], 'response.json')
        # Get rollup column type
        column_type = responses[0]['results'][0]['type']
        print('Column Type:', column_type)
        # Initialize list to save elements to
        elements = []
        # Use type to get data path
        match column_type:
            case 'title':
                for element in responses:
                    try:
                        elements.append(element['results'][0]['title']['plain_text'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'rich_text':
                for element in responses:
                    try:
                        elements.append(element['results'][0]['rich_text']['plain_text'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'number':
                for element in responses:
                    try:
                        elements.append(element['results'][0]['number'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'select':
                for element in responses:
                    try:
                        elements.append(element['results'][0]['select']['name'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements
            case 'date':
                for element in responses:
                    try:
                        elements.append(element['results'][0]['date']['start'])
                    except (TypeError, IndexError):
                        elements.append(None)
                return elements

    async def request_urls(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(
                    asyncio.ensure_future(
                        self.get_url(session, url)
                    )
                )
            return await asyncio.gather(*tasks)

    async def get_url(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url, headers=self.headers) as response:
            return await response.json()



if __name__ == '__main__':

    # Initialize Database ID
    database_id = '087ed092c10f4535a91b7849b6f61928'
    # Initialize Notion object and save to file
    N = Notion(database_id)
    N.save('data.json')

    # N.set('Number', 117, 247)
    # N.save('data.json')

    # names = N.get('Name')
    # print(names)

    N.set('Item 8', 'Select', 'Started')

    elements = N.get('Rollup')
    names = N.get('Name')
    print(names)
    print(elements)


