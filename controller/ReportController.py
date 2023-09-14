import json
from exception.ExceptionHandler import IllegalArgument
from service.ReportService import *
from server import server
from flask_expects_json import expects_json

service = ReportService()
app = server.app


@app.route('/report/<string:token>/<int:id_usuario>', methods=['GET'])
def executar_relatorio(token, id_usuario):
    response = app.response_class(
        response=json.dumps(service.gerar_relatorio(token, id_usuario)),
        status=200,
        mimetype='application/json'
    )
    return response