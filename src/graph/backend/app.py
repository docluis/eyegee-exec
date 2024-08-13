# app.py
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS
from src.graph.backend.src.graph import Graph

def init_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    api = Api(app)

    graph = Graph("siteinfo.pkl")


    class ExampleResource(Resource):
        def get(self):
            return {"message": "Hello, world!"}


    class GraphEndpoint(Resource):
        def get(self):
            return {
                "nodes": graph.nodes,
                "links": graph.links,
            }


    api.add_resource(ExampleResource, "/example")
    api.add_resource(GraphEndpoint, "/graph")

    return app