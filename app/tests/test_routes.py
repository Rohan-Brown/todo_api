def test_say_hello(
    client,
):  # Simple test only used for testing if the most basic endpoint works
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello and welcome to my TaskListApp!"}
