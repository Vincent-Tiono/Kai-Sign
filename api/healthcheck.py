from http.server import BaseHTTPRequestHandler

def handler(request):
    return {
        'statusCode': 200,
        'body': '{"status": "ok", "message": "API is running"}',
        'headers': {
            'Content-Type': 'application/json'
        }
    } 