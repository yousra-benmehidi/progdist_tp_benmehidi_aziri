def test_available_books_contains_seed_book(client):
    response = client.get("/availablebooks")
    assert response.status_code == 200
    titles = [b["title"] for b in response.get_json().values()]
    assert titles == ["The Poppy War"]


def test_get_unknown_book_returns_404(client):
    response = client.get("/books/999")
    assert response.status_code == 404


def test_add_book(client):
    response = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
    assert response.status_code == 201
    new_id = response.get_json()["id"]

    # Read it back to prove it was really saved in the database.
    book = client.get(f"/books/{new_id}").get_json()
    assert book == {"title": "Dune", "author": "Frank Herbert", "rented": False}


def test_add_book_without_author_returns_400(client):
    response = client.post("/books", json={"title": "Dune"})
    assert response.status_code == 400


RENTAL = {"rental_date": "2026-11-01", "return_date": "2026-11-15"}


def test_rent_book(client):
    response = client.put("/rentedbooks/1?rent=true", json=RENTAL)
    assert response.status_code == 200

    # The book is now rented and no longer listed as available.
    assert client.get("/books/1").get_json()["rented"] is True
    assert client.get("/availablebooks").get_json() == {}


def test_rent_already_rented_book_returns_409(client):
    client.put("/rentedbooks/1?rent=true", json=RENTAL)
    response = client.put("/rentedbooks/1?rent=true", json=RENTAL)
    assert response.status_code == 409


def test_return_book(client):
    client.put("/rentedbooks/1?rent=true", json=RENTAL)
    response = client.put("/rentedbooks/1?rent=false")
    assert response.status_code == 200

    # Back on the shelf, with the rental dates cleared.
    assert client.get("/books/1").get_json()["rented"] is False
    available = client.get("/availablebooks").get_json()
    assert available["1"]["rental_date"] is None
    assert available["1"]["return_date"] is None


def test_return_book_that_is_not_rented_returns_409(client):
    response = client.put("/rentedbooks/1?rent=false")
    assert response.status_code == 409


def test_rent_unknown_book_returns_404(client):
    response = client.put("/rentedbooks/999?rent=true", json=RENTAL)
    assert response.status_code == 404


def test_rent_without_dates_returns_400(client):
    response = client.put("/rentedbooks/1?rent=true", json={})
    assert response.status_code == 400
    # The failed request must not have changed anything.
    assert client.get("/books/1").get_json()["rented"] is False


def test_invalid_rent_parameter_returns_400(client):
    response = client.put("/rentedbooks/1?rent=maybe")
    assert response.status_code == 400
