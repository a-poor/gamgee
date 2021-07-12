import json
import gamgee


def test_basic():
    event = {
        "queryStringParameters": {"name": "samwise"},
        "body": json.dumps({"hello": "world"})
    }
    
    @gamgee.sam(body=json.loads, queryString=True)
    def lambda_handler(body, query):
        assert isinstance(body, dict), "`body` param is the wrong type"
        assert isinstance(query, dict), "`query` param is the wrong type"
        
        assert body["hello"] == "world", f"`body` has the wrong values: {body['hello']}"
        assert query["name"] == "samwise", f"`body` has the wrong values: {query['name']}"

    res = lambda_handler(event=event, context=None)
    res_body = json.loads(res["body"])
    assert res_body["success"], f"Error with response: {json.dumps(res)}"

