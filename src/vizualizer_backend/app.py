# app.py
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS
from src.vizualizer_backend.src.graph import Graph

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app)

graph = Graph("siteinfo.pkl")


class ExampleResource(Resource):
    def get(self):
        return {"message": "Hello, world!"}


class Graph(Resource):
    def get(self):
        return {
            "site_nodes": graph.site_nodes,
            "api_nodes": graph.api_nodes,
            "site_links": graph.site_links,
            "api_links": graph.api_links,
        }


api.add_resource(ExampleResource, "/example")
api.add_resource(Graph, "/graph")


if __name__ == "__main__":
    app.run(debug=True)
