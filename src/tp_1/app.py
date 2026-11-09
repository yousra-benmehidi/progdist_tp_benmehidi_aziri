import flask
from flask import request
from flasgger import Swagger

app = flask.Flask(__name__)
swagger = Swagger(app)

books ={
    '1': {'title':'The Poppy War', 'author':'R. F. Kuang', 'rented': False, 'rental_date': None, 'return_date': None},
}

@app.get('/availablebooks')
def get_available_books():
    """
    Get all available books.
    ---
    responses:
      200:
        description: A list of available books
    """
    available_books ={}
    for book_id, book in books.items():
        if book['rented']==False:
            available_books[book_id] = book
    return available_books

@app.put('/rentedbooks/<book_id>')
def rent_book(book_id):
    rent = request.args.get('rent')
    if book_id not in books:
        return {'message': f'Book {book_id} does not exist'}, 404
    if rent=='true':
        if books[book_id]['rented']==True:
            return {'message':'Book is already rented'}, 409
        body =request.get_json()
        books[book_id]['rental_date'] = body['rental_date']
        books[book_id]['return_date'] = body['return_date']
        books[book_id]['rented'] = True
        return {'message':f'Book {book_id} is rented successfully the {books[book_id]["rental_date"]}, and should be returned by {books[book_id]["return_date"]}'}
    if rent=='false':
        if books[book_id]['rented']==False:
            return {'message': f'the book {book_id} isnt rented so it cannot be returned'}, 409
        books[book_id]['rental_date'] = None
        books[book_id]['return_date'] = None
        books[book_id]['rented'] = False
        return {'message': f"the book {book_id} has been returned successfully"}  

    

@app.get('/books/<book_id>')
def get_book(book_id):
    return {'title': books[book_id]['title'], 'author': books[book_id]['author'], 'rented': books[book_id]['rented']}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
