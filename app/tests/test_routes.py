def test_say_hello(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello and welcome to my TaskListApp!"}
