from ufvrag.config.messenger_config import create_urls_producer, create_urls_consumer, create_embeddings_producer

from . import webcrawler
from ufvrag.utils.interrupt import safe_interrupt_loop, ShouldStopFn

consumer = create_urls_consumer()
producer = create_urls_producer()
embeddings_producer = create_embeddings_producer()


@safe_interrupt_loop  # type: ignore
def process_messages(should_stop: ShouldStopFn) -> None:
    with consumer as consumer_instante:
        while True:
            msg = consumer_instante.consume(10)
            if msg:
                #print(f"Consumed message: {msg}")
                crawl_response = webcrawler.craw_url(url=msg)
                if crawl_response.url_for_embbeding is not None:
                    print(f"\tUrl sent to embedding: {crawl_response.url_for_embbeding}")
                    embeddings_producer.produce(crawl_response.url_for_embbeding)
                    embeddings_producer.flush()
                if crawl_response.links is not None:
                    for link in crawl_response.links:
                        # print(f"\tUrl sent for crawling: {link}")
                        producer.produce(message=link)
                        producer.flush()
                print(f"\tFinished item: {msg}")
            else:
                print("No messages consumed.")

            if should_stop():
                print("Loop interrupted")
                break


if __name__ == "__main__":

    print("Started crawling...")
    process_messages()
    print("Finished Crawling")
