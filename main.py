from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor
import time


uri = "bolt://localhost:7687"
username = "neo4j"
password = "56565656"
driver = GraphDatabase.driver(uri, auth=(username, password))


def reset_likes(tx):
    query = """
    MATCH (i:Item {id: 1})
    SET i.likes = 0
    """
    tx.run(query)


def increment_likes(tx):
    query = """
    MATCH (i:Item {id: 1})
    SET i.likes = i.likes + 1
    RETURN i.likes AS current_likes
    """
    result = tx.run(query)
    return result.single()["current_likes"]


def task():
    with driver.session() as session:
        for _ in range(10000):
            session.execute_write(increment_likes)


if __name__ == "__main__":
    NUM_CLIENTS = 10


    with driver.session() as session:
        session.execute_write(reset_likes)


    start_time = time.time()


    with ThreadPoolExecutor(max_workers=NUM_CLIENTS) as executor:
        futures = [executor.submit(task) for _ in range(NUM_CLIENTS)]
        for future in futures:
            future.result()


    with driver.session() as session:
        result = session.run("MATCH (i:Item {id: 1}) RETURN i.likes AS likes")
        final_likes = result.single()["likes"]

    end_time = time.time()


    print(f"Фінальне значення likes для Item 1: {final_likes}")
    print(f"Час виконання: {end_time - start_time:.2f} секунд")


    driver.close()
