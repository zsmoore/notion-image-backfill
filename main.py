import os

from dotenv import load_dotenv
from notion import NotionClient
from google_images_search import GoogleImagesSearch

NOTION_TOKEN = 'NOTION_TOKEN'
DATABASE_ID = 'DATABASE_ID'
GCS_DEVELOPER_KEY = 'GCS_DEVELOPER_KEY'
GCS_CX = 'GCS_CX'


def initialize_client(notion_token):
    return NotionClient(notion_token)


def get_image_url(gcs_api_key, gcs_cx, title):
    gis = GoogleImagesSearch(gcs_api_key, gcs_cx)
    params = {
        'q': title,
        'num': 1,
    }
    gis.search(search_params=params)
    for image in gis.results():
        return image.url


def get_pages_without_image(notion_client, database_id):
    return notion_client.databases.query(database_id, **{
        'filter': {
            'property': 'Cover',
            'files': {
                'is_empty': True
            }
        }
    }).results


def update_page_properties(notion_client, page_id, properties):
    return notion_client.pages.update(
        page_id=page_id,
        properties=properties)


def build_page_properties(image_url):
    return {
        'Cover': {
            'files': [
                {
                    'type': 'external',
                    'name': 'cover image',
                    'external': {
                        'url': image_url
                    }
                }
            ]
        }
    }


def main():
    load_dotenv()
    notion_token = os.getenv(NOTION_TOKEN)
    database_id = os.getenv(DATABASE_ID)
    gcs_api_key = os.getenv(GCS_DEVELOPER_KEY)
    gcs_cx = os.getenv(GCS_CX)

    notion_client = initialize_client(notion_token)
    pages_without_images = get_pages_without_image(notion_client, database_id)
    page_ids_and_titles = map(lambda x: [x.id, x.properties['Name'].title[0].plain_text], pages_without_images)
    page_ids_and_image_urls = map(lambda x: [x[0], get_image_url(gcs_api_key, gcs_cx, x[1])], page_ids_and_titles)
    for page_tup in page_ids_and_image_urls:
        update_page_properties(notion_client, page_tup[0], build_page_properties(page_tup[1]))


if __name__ == "__main__":
    main()