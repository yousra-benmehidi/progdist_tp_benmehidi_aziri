import flask
from flask import request
from flasgger import Swagger

from tp_1 import db

app = flask.Flask(__name__)
swagger = Swagger(app)

db.init_db()


@app.get('/availablebooks')
def get_available_books():
    """
    Get all available books.
    ---
    responses:
      200:
        description: A list of available books
    """
    return {str(b['id']): b for b in db.list_books(available_only=True)}


@app.post('/books')
def add_book():
    """
    Add a new book.
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [title, author]
          properties:
            title: {type: string}
            author: {type: string}
    responses:
      201:
        description: Book created
      400:
        description: Missing title or author
    """
    body = request.get_json(silent=True) or {}
    if not body.get('title') or not body.get('author'):
        return {'message': 'title and author are required'}, 400
    book_id = db.add_book(body['title'], body['author'])
    return {'message': 'Book created', 'id': book_id}, 201


@app.put('/rentedbooks/<int:book_id>')
def rent_book(book_id):
    book = db.get_book(book_id)
    if book is None:
        return {'message': f'Book {book_id} does not exist'}, 404
    rent = request.args.get('rent')
    if rent == 'true':
        if book['rented']:
            return {'message': 'Book is already rented'}, 409
        body = request.get_json(silent=True) or {}
        if 'rental_date' not in body or 'return_date' not in body:
            return {'message': 'rental_date and return_date are required'}, 400
        db.set_rental(book_id, True, body['rental_date'], body['return_date'])
        return {'message': f'Book {book_id} is rented successfully the {body["rental_date"]}, and should be returned by {body["return_date"]}'}
    if rent == 'false':
        if not book['rented']:
            return {'message': f'the book {book_id} isnt rented so it cannot be returned'}, 409
        db.set_rental(book_id, False)
        return {'message': f'the book {book_id} has been returned successfully'}
    return {'message': "query parameter 'rent' must be 'true' or 'false'"}, 400


@app.get('/books/<int:book_id>')
def get_book(book_id):
    book = db.get_book(book_id)
    if book is None:
        return {'message': f'Book {book_id} does not exist'}, 404
    return {'title': book['title'], 'author': book['author'], 'rented': book['rented']}


@app.put('/books/<int:book_id>')
def edit_book(book_id):
    """
    Edit a book's title and/or author.
    ---
    parameters:
      - in: path
        name: book_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title: {type: string}
            author: {type: string}
    responses:
      200:
        description: Book updated
      400:
        description: Nothing valid to update
      404:
        description: Book does not exist
    """
    if db.get_book(book_id) is None:
        return {'message': f'Book {book_id} does not exist'}, 404
    body = request.get_json(silent=True) or {}
    title = body.get('title') or None
    author = body.get('author') or None
    if title is None and author is None:
        return {'message': 'provide a non-empty title and/or author'}, 400
    db.update_book(book_id, title, author)
    return {'message': f'Book {book_id} updated'}


@app.delete('/books/<int:book_id>')
def delete_book(book_id):
    """
    Delete a book (it must not be currently rented).
    ---
    parameters:
      - in: path
        name: book_id
        type: integer
        required: true
    responses:
      200:
        description: Book deleted
      404:
        description: Book does not exist
      409:
        description: Book is currently rented
    """
    book = db.get_book(book_id)
    if book is None:
        return {'message': f'Book {book_id} does not exist'}, 404
    if book['rented']:
        return {'message': 'A rented book cannot be deleted'}, 409
    db.delete_book(book_id)
    return {'message': f'Book {book_id} deleted'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
