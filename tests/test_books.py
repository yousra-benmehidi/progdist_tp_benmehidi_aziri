def test_available_books_contains_seed_book(client):
    response = client.get("/availablebooks")
    assert response.status_code == 200
    titles = [b["title"] for b in response.get_json().values()]
    assert titles == ["The Poppy War"]


def test_get_unknown_book_returns_404(client):
    response = client.get("/books/999")
    assert response.status_code == 404
