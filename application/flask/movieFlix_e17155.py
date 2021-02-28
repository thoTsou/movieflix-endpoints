from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json, os ,sys



# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose MovieFlix database
db = client['MovieFlix']
users = db['Users']
movies = db['Movies']
ratings = db['Ratings']

# Initiate Flask App
app = Flask(__name__)


#!!! FOR USER!!!

# register user
@app.route('/registerUser', methods=['POST'])
def registerUser():
    # Request JSON data
    data = None 
    
    data = json.loads(request.data.decode('utf-8'))
    
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    if users.find({"email":data["email"]}).count() == 0 :
        user = {"username": data['username'], "email": data['email'],  "password":data['password'] , "comments": [] , "category":"simple"}
        # Add user to the Users collection
        users.insert_one(user)
        return Response(data['username']+" was added to the MongoDB",status=200,mimetype='application/json') 
    else:
        return Response("A user with the given email already exists",status=200,mimetype='application/json')


# sign in
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "username" in data or not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    
    if users.find({"email":data["email"]}).count() == 0 :
        return Response("Wrong credentials .Please try again",status=200,mimetype='application/json')

    
    user = users.find_one({"email":data["email"]})
    if (  ( user["username"] == data["username"] ) and  ( user["email"] == data["email"] ) and ( user["password"] == data["password"] ) ) :
        return Response(data['username']+" Signed in",status=200,mimetype='application/json') 
    else:
        return Response("Wrong credentials .Please try again",status=200,mimetype='application/json')


# Find movie by title
@app.route('/searchMovie_title', methods=['POST'])
def searchMovie_title():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json contentt",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")


    movie = movies.find_one({"title":data["title"]})
    if movie !=None:
        movie = {'title':movie["title"],'year':movie["year"], 'description':movie["description"] ,'actors':movie["actors"] , 'rating':movie["rating"] ,'comments':movie["comments"]}
        return jsonify(movie)
    
    return Response('No movie with this name was found',status=500,mimetype='application/json')


  
# Get movies by year
@app.route('/searchMovie_year', methods=['POST'])
def searchMovie_year():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "year" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    iterable = movies.find({"year":data["year"]})
    output = []
    for movie in iterable:
        movie['_id'] = None 
        output.append(movie)
    return jsonify(output)
    

# Get movies based on actors starred
@app.route('/searchMovie_actor', methods=['POST'])
def searchMovie_actor():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "actor" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    iterable = movies.find()
    output = []
    for movie in iterable:
        for element in movie["actors"] :
            if (element["name"] == data["actor"] ) : 
                movie['_id'] = None 
                output.append(movie)
    return jsonify(output)
    


# Get movie details
@app.route('/movieDetails', methods=['POST'])
def movieDetails():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    movie = movies.find_one({"title":data["title"]})
    if movie !=None:
        movie = {'title':movie["title"],'year':movie["year"], 'description':movie["description"] ,'actors':movie["actors"] }
        return jsonify(movie)
    return Response('No movie with this name was found',status=500,mimetype='application/json')
    


# Get movie comments
@app.route('/movie_comments', methods=['POST'])
def movie_comments():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    movie = movies.find_one({"title":data["title"]})
    output=[]
    for element in movie["comments"] :  
        output.append( element )
    return jsonify(output)



# Find movie and rate
@app.route('/rateMovie', methods=['POST'])
def rateMovie():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data or not "rating" in data or not "username" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

     
    rating = {"username": data['username'], "title": data['title'],  "rating":data['rating']}
     # Add rating into Ratings Collection
    ratings.insert_one(rating)
    return Response("Rating was added to the MongoDB",status=200,mimetype='application/json') 
    


#delete rating using arguments title and username
@app.route('/deleteRating', methods=['DELETE'])
def deleteRating():
    title = request.args.get('title')
    username = request.args.get('username')

    if (title == None)  or (username == None):
        return Response("Bad request", status=500, mimetype='application/json')
   

    ratings.delete_one( {"title": title } , {"username": username } )
    return Response("Rating deleted successfuly", status=200, mimetype='application/json')   



# Find movie and update its comments 
@app.route('/update_comments', methods=['PUT'])
def update_comments():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data or not "comment" in data or not "username" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    try: 
        comment = {"user":data["username"] , "comment" : data["comment"]}
        movie = movies.find_one({"title":data["title"]})
        New_comments = movie["comments"].append(comment)
        movie = movies.update_one({"title":data["title"]}, 
        {"$set":
            {
                "comments" : New_comments
            }
        })
    except Exception as e:
        return Response({'error inserting comment'},status=500,mimetype='application/json')


# Get user comments
@app.route('/user_comments', methods=['POST'])
def user_comments():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "username" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")

    iterable = movies.find()
    output = []
    for movie in iterable:
        for element in movie["comments"]:
           if( element["user"] == data["username"]) :
                comment = { movie["title"] : element["comment"] }
                output.append(comment)
    return jsonify(output)


# Get user's ratings
@app.route('/userRatings', methods=['POST'])
def userRatings():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "username" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")

    iterable = ratings.find({"username":data["username"]})
    output = []
    for rating in iterable:
        if ( rating["username"] == data["username"]) :
             output.append(rating)
    return jsonify(output)


#delete comment from movie 
@app.route('/deleteComment', methods=['PUT'])
def deleteComment():
     # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data or not "username" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    movie = movies.find_one({"title":data["title"]})
    output = []
    for element in movie["comments"]:
        if (element["user"] == data["username"]):
            new_comments = movie["comments"].remove(element)
            movies.update_one({"title":data["title"]}, 
            {"$set":
                {
                  "comments" : new_comments
                }
            })
    return Response("Comment deleted successfuly", status=200, mimetype='application/json')
            



#delete account from DB using arguments username , email and password
@app.route('/deleteAccount', methods=['DELETE'])
def deleteAccount():
    email = request.args.get('email')
    username = request.args.get('username')
    password = request.args.get('password')

    if (email == None)  or (username == None) or (password == None):
        return Response("Bad request", status=500, mimetype='application/json')

    if users.find({"email":email}).count() == 0 :
        return Response("No user with given email",status=200,mimetype='application/json')

    user = users.find_one({"email":email})
    if (  ( user["username"] == username ) and  ( user["email"] == email ) and ( user["password"] == password ) ) :
        users.delete_one({"email": email})
        return Response("Account deleted successfuly", status=200, mimetype='application/json')



#!!! FOR ADMINS !!!

# INSERT NEW MOVIE
@app.route('/insertMovie_Admin', methods=['POST'])
def insertMovie_Admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "title" in data or not "actors" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    if movies.find({"title":data["title"]}).count() == 0 :
        movie = {"title": data['title'], "year": 0,  "description":"" , "actors":data["actors"] , "rating": 0 , "comments": []  }
        # Add movie to the Movies collection
        movies.insert_one(movie)
        return Response(data['title']+" was added to the MongoDB",status=200,mimetype='application/json') 
    else:
        return Response("A movie with given title already exists",status=200,mimetype='application/json')


#DELETE MOVIE USING ARGUMENT TITLE
@app.route('/deleteMovie_Admin', methods=['DELETE'])
def deleteMovie_Admin():
    title = request.args.get('title')

    if (title == None) :
        return Response("Bad request", status=500, mimetype='application/json')


    iterable = movies.find({"title": title})
    output = []
    x=3000
    for movie in iterable:
        if (movie["year"] < x):
            x = year
            ID = movie["_id"] 
            
    movies.delete_one({"_id": ID} )
    return Response("Movie deleted successfuly", status=200, mimetype='application/json')


# Find movie by title and update its title 
@app.route('/updateMovieTitle_Admin', methods=['PUT'])
def updateMovieTitle_Admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "title" in data or not "newTitle" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    movie = movies.find_one({"title":data["title"]})
    if movie == None:
        return Response('No movie found with that title  was found',status=500,mimetype='application/json')

    ID = movie["_id"] 
    try: 
        movies.update_one({"_id":ID}, 
        {"$set":
            {
                "title" : data["newTitle"]
            }
        })
        return Response({'Movie title changed successfuly '},status=200,mimetype='application/json')
    except Exception as e:
        return Response({'Movie title could not be updated'},status=500,mimetype='application/json')


# Find movie by title and update its year 
@app.route('/updateMovieYear_Admin', methods=['PUT'])
def updateMovieYear_Admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "title" in data or not "newYear" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    movie = movies.find_one({"title":data["title"]})
    if movie == None:
        return Response('No movie found with that title  was found',status=500,mimetype='application/json')

    ID = movie["_id"] 
    try: 
        movies.update_one({"_id":ID}, 
        {"$set":
            {
                "year" : data["newYear"]
            }
        })
        return Response({'Movie year changed successfuly '},status=200,mimetype='application/json')
    except Exception as e:
        return Response({'Movie year could not be updated'},status=500,mimetype='application/json')


# Find movie by title and update its plot(description) 
@app.route('/updateMovieDescr_Admin', methods=['PUT'])
def updateMovieDescr_Admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "title" in data or not "newDescription" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    movie = movies.find_one({"title":data["title"]})
    if movie == None:
        return Response('No movie found with that title  was found',status=500,mimetype='application/json')

    ID = movie["_id"] 
    try: 
        movies.update_one({"_id":ID}, 
        {"$set":
            {
                "description" : data["newDescription"]
            }
        })
        return Response({'Movie plot changed successfuly '},status=200,mimetype='application/json')
    except Exception as e:
        return Response({'Movie plot could not be updated'},status=500,mimetype='application/json')


# Find movie by title and update its actors array 
@app.route('/updateMovieActors_Admin', methods=['PUT'])
def updateMovieActors_Admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "title" in data or not "newActorsArray" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    movie = movies.find_one({"title":data["title"]})
    if movie == None:
        return Response('No movie found with that title  was found',status=500,mimetype='application/json')

    ID = movie["_id"] 
    try: 
        movies.update_one({"_id":ID}, 
        {"$set":
            {
                "description" : data["newActorsArray"]
            }
        })
        return Response({'Movie actors array changed successfuly '},status=200,mimetype='application/json')
    except Exception as e:
        return Response({'Movie actors array could not be updated'},status=500,mimetype='application/json')


#DELETE COMMENT FROM MOVIE
@app.route('/deleteComment_Admin', methods=['PUT'])
def deleteComment_Admin():
     # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "title" in data or not "username" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    movie = movies.find_one({"title":data["title"]})
    ID = movie["_id"] 
    for element in movie["comments"]:
        if (element["user"] == data["username"]):
            new_comments = movie["comments"].remove(element)
            movies.update_one({"_id": ID }, 
            {"$set":
                {
                     "comments" : new_comments
                }
            })
    return Response("Comment deleted successfuly", status=200, mimetype='application/json')



# UPGRADE USER TO ADMIN 
@app.route('/upgradeUser_Admin', methods=['PUT'])
def upgradeUser_Admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    if not "email" in data  :
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    user = users.find_one({"email": data["email"] })
    if user == None:
        return Response('User with given email does not exist ',status=500,mimetype='application/json')

    try: 
        users.update_one({"email":data["email"]}, 
        {"$set":
            {
                "category" : "admin"
            }
        })
        return Response({'User upgraded to Admin'},status=200,mimetype='application/json')
    except Exception as e:
        return Response({'User could not be upgaded'},status=500,mimetype='application/json')


#DELETE USER USING ARGUMENT EMAIL
@app.route('/deleteUser_Admin', methods=['DELETE'])
def deleteUser_Admin():
    email = request.args.get('email')

    if (email == None) :
        return Response("Bad request", status=500, mimetype='application/json')

    user = users.find_one({"email": email})
    
    if ( ( user["email"] == email )  and (user["category"] == "simple") ):
        users.delete_one({"email": email} )
        return Response("User deleted successfuly", status=200, mimetype='application/json')
    else:
        return Response("You can not delete an ADMIN",status=500,mimetype="application/json")



# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
