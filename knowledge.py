from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='0.1', title='Knowledge Graph API',
    description='A simple Knowledge Graph API using flask rest plus',
)

ns = api.namespace('maps', description='Maps operations')

map = api.model('Map', {
    'id': fields.Integer(readonly=True, description='The unique identifier'),
    'source_node': fields.String(required=True, description='source node details'),
    'relation': fields.String(required=True, description='relationship details'),
    'target_node': fields.String(required=True, description='target node details')
})


class MapDAO(object):
    def __init__(self):
        self.counter = 0
        self.maps = []

    def get(self, id):
        for map in self.maps:
            if map['id'] == id:
                return map
        api.abort(404, "Map {} doesn't exist".format(id))

    def create(self, data):
        map = data
        map['id'] = self.counter = self.counter + 1
        self.maps.append(map)
        return map

    def update(self, id, data):
        map = self.get(id)
        map.update(data)
        return map

    def delete(self, id):
        map = self.get(id)
        self.maps.remove(map)


DAO = MapDAO()
DAO.create({'source_node': 'cow' ,'relation': 'helps','target_node':'formar'})
DAO.create({'source_node': 'sun' ,'relation': 'feed','target_node':'plants'})
DAO.create({'source_node': 'plants' ,'relation': 'need','target_node':'water'})

@ns.route('/')

class MapList(Resource):
    '''Shows a list of all maps, and lets you POST to add new maps'''
    @ns.doc('list_maps')
    @ns.marshal_list_with(map)
    def get(self):
        '''List all maps'''
        return DAO.maps

    @ns.doc('create_map')
    @ns.expect(map)
    @ns.marshal_with(map, code=201)
    def post(self):
        '''Create a new map'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Map not found')
@ns.param('id', 'The map identifier')
class Map(Resource):
    '''Show a single map item and lets you delete them'''
    @ns.doc('get_map')
    @ns.marshal_with(map)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_map')
    @ns.response(204, 'map deleted')
    def delete(self, id):
        '''Delete a map given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(map)
    @ns.marshal_with(map)
    def put(self, id):
        '''Update a map given its identifier'''
        return DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)
