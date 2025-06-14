from flask import jsonify


def does_exist(model, column_name, value, label):
    field = getattr(model, column_name)
    exist = model.query.filter(field==value).first()
    if exist:
        return jsonify({"status":False, "message":f"{label} already exist"}), 409
    
    return None
    
    