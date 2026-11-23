from elasticsearch import Elasticsearch

from app.config import get_settings


settings = get_settings()
client = Elasticsearch(settings.elasticsearch_url)
