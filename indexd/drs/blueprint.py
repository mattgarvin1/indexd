import flask
from indexd.errors import AuthError
from indexd.errors import UserError
from indexd.index.errors import NoRecordFound as IndexNoRecordFound
from indexd.errors import UnexpectedError
# from indexd.index.blueprint import get_index
from indexd.index.blueprint import get_index

blueprint = flask.Blueprint("drs", __name__)

blueprint.config = dict()
blueprint.index_driver = None


@blueprint.route("/ga4gh/drs/v1/objects/<path:object_id>", methods=["GET"])
def get_drs_object(object_id, list_drs=True, expand=False):
    """
    Returns a specific DRSobject with object_id
    """
    expand = True if flask.request.args.get("expand") == "true" else False

    ret = blueprint.index_driver.get(object_id)

    print("---------------from indexd---------------------------------")
    print(ret["bundle_id"])

    data = indexd_to_drs(ret, list_drs=True) if expand else indexd_to_drs(ret, list_drs=False, expand=True)

    return flask.jsonify(data), 200


@blueprint.route("/ga4gh/drs/v1/objects", methods=["GET"])
def list_drs_records():
    records = get_index()[0].json["records"]
    ret = {"drs_objects": [indexd_to_drs(record, True) for record in records]}

    return flask.jsonify(ret), 200


@blueprint.route(
    "/ga4gh/drs/v1/objects/<path:object_id>/access",
    defaults={"access_id": None},
    methods=["GET"],
)
@blueprint.route(
    "/ga4gh/drs/v1/objects/<path:object_id>/access/<path:access_id>", methods=["GET"]
)
def get_signed_url(object_id, access_id):
    if not access_id:
        raise (UserError("Access ID/Protocol is required."))
    res = flask.current_app.fence_client.get_signed_url_for_object(
        object_id=object_id, access_id=access_id
    )
    if not res:
        raise IndexNoRecordFound("No signed url found")

    return res, 200


def indexd_to_drs(record, list_drs=False, expand=False):
    bearer_token = flask.request.headers.get("AUTHORIZATION")
    print("-----------------------------------indexd to drs --------------------------------")
    print(list_drs)
    print(expand)
    print(record)
    # print(record.get("bundle_id"))

    
    did = record["did"] if "did" in record else record["bundle_id"]

    self_uri = "drs://" + flask.current_app.hostname + "/" + did

    name = record["file_name"] if "file_name" in record else record["name"]

    created_time = record["created_date"] if "created_date" in record else record["created_time"]

    version = record["rev"] if "rev" in record else ""

    updated_date = record["updated_date"] if "updated_date" in record else ""

    drs_object = {
        "id": did,
        "description": "",
        "mime_type": "application/json",
        "name": name,
        "created_time": created_time,
        "updated_time": updated_date,
        "size": record["size"],
        "aliases": [],
        "contents": [],
        "self_uri": self_uri,
        "version": version,
    }

    if "description" in record:
        drs_object["description"] = record["description"]
    if "alias" in record:
        drs_object["aliases"].append(record["alias"])

    if "bundle_data" in record:
        bundle_data = record["bundle_data"]
        for bundle in bundle_data:
            print("-----------------------------------------")
            print(bundle)
            drs_object["contents"].append(bundle_to_drs(bundle, expand=expand))

    # access_methods mapping
    if "urls" in record:
        drs_object["access_methods"] = []
        for location in record["urls"]:
            location_type = location.split(":")[
                0
            ]  # (s3, gs, ftp, gsiftp, globus, htsget, https, file)

            drs_object["access_methods"].append(
                {
                    "type": location_type,
                    "access_url": flask.current_app.fence_client.get_signed_url_for_object(
                        record["did"], ""
                    )
                    if bearer_token and not list_drs
                    else {"url": location},
                    "access_id": location_type,
                    "region": "",
                }
            )
        print(drs_object)

    # parse out checksums
    drs_object["checksums"] = []
    if "hashes" in record:
        for k in record["hashes"]:
            drs_object["checksums"].append({"checksum": record["hashes"][k], "type": k})
    else:
        drs_object["checksums"].append({"checksum": record["checksum"], "type": "md5"})

    return drs_object


def bundle_to_drs(record, expand):
    did = record["did"] if "did" in record else record["bundle_id"]

    self_uri = "drs://" + flask.current_app.hostname + "/" + did
    
    name = record["file_name"] if "file_name" in record else record["name"]
    
    created_time = record["created_date"] if "created_date" in record else record["created_time"]

    drs_object = {
        "id": did,
        "name": name,
        "created_time": created_time,
        "self_uri": self_uri,
    }
    contents = record["contents"] if "contents" in record else record["bundle_data"]
    if expand and len(contents) > 1:
        drs_object["contents"] = bundle_to_drs(contents, expand=True)

    return drs_object






@blueprint.errorhandler(UserError)
def handle_user_error(err):
    ret = {"msg": str(err), "status_code": 400}
    return flask.jsonify(ret), 400


@blueprint.errorhandler(AuthError)
def handle_auth_error(err):
    ret = {"msg": str(err), "status_code": 401}
    return flask.jsonify(ret), 401


@blueprint.errorhandler(AuthError)
def handle_requester_auth_error(err):
    ret = {"msg": str(err), "status_code": 403}
    return flask.jsonify(ret), 403


@blueprint.errorhandler(IndexNoRecordFound)
def handle_no_index_record_error(err):
    ret = {"msg": str(err), "status_code": 404}
    return flask.jsonify(ret), 404


@blueprint.errorhandler(UnexpectedError)
def handle_unexpected_error(err):
    ret = {"msg": str(err), "status_code": 500}
    return flask.jsonify(ret), 500


@blueprint.record
def get_config(setup_state):
    index_config = setup_state.app.config["INDEX"]
    blueprint.index_driver = index_config["driver"]
