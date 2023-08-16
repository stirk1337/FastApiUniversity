from conftest import client


def test_register():
    response = client.post("user/", json={
        "name": "abcefg",
        "surname": "string",
        "email": 'xd1338@gmail.com',
    })

    assert response.status_code == 200
