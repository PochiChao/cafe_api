import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    cafes = Cafe.query.all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


# HTTP GET - Read Record
@app.route("/all")
def get_all():
    cafes = Cafe.query.all()
    all_cafes = [cafe.to_dict() for cafe in cafes]
    return jsonify(all_cafes=all_cafes)


@app.route("/search")
def search():
    request_location = request.args.get("location")
    print(request_location)
    # ALTERNATE METHOD:
    # cafes = Cafe.query.all()
    # search_result = [cafe.to_dict() for cafe in cafes if cafe.to_dict()["location"] == request_location

    search_result = [cafe.to_dict() for cafe in Cafe.query.filter_by(location=request_location)]
    if search_result:
        return jsonify(cafe=search_result)
    else:
        return jsonify(error={"Not Found": "Sorry, didn't find anything at that location."})


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    # ALTERNATIVE METHOD BELOW FOR MULTIPLE CAFES BEING SUBMITTED
    # cafe_response = request.form.to_dict()
    # for key, value in cafe_response.items():
    #     if value.lower() == "true":
    #         cafe_response[key] = bool('True')
    #     elif value.lower() == "false":
    #         # if no values given to bool() it will return false
    #         cafe_response[key] = bool('')
    #         print(cafe_response[key])
    #
    # new_cafe = Cafe(**cafe_response)
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        seats=request.form["seats"],
        has_toilet=bool(request.form["has_toilet"]),
        has_wifi=bool(request.form["has_wifi"]),
        has_sockets=bool(request.form["has_sockets"]),
        can_take_calls=bool(request.form["can_take_calls"]),
        coffee_price=request.form["coffee_price"],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry, no cafe with that id was found in the database."}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.values.get("api_key")
    if api_key == "API_KEY":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted that cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
