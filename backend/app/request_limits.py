"""Count actual request bytes, including chunked bodies, before multipart/JSON parsing."""
from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    def __init__(self,app,limit=16*1024*1024):
        self.app,self.limit=app,limit

    async def __call__(self,scope,receive,send):
        if scope['type']!='http' or scope['method'] not in {'POST','PUT','PATCH'}:
            return await self.app(scope,receive,send)
        headers=dict(scope.get('headers',[]))
        try:length=int(headers.get(b'content-length',b'0'))
        except ValueError:
            return await JSONResponse({'detail':'Invalid request length.'},status_code=400)(scope,receive,send)
        if length<0:return await JSONResponse({'detail':'Invalid request length.'},status_code=400)(scope,receive,send)
        if length>self.limit:return await JSONResponse({'detail':'Request exceeds the16MiB local-demo limit.'},status_code=413)(scope,receive,send)
        chunks=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            data=message.get('body',b'');size+=len(data)
            if size>self.limit:
                return await JSONResponse({'detail':'Request exceeds the16MiB local-demo limit.'},status_code=413)(scope,receive,send)
            chunks.append(data)
            if not message.get('more_body'):break
        body=b''.join(chunks);sent=False
        async def replay():
            nonlocal sent
            if not sent:
                sent=True;return {'type':'http.request','body':body,'more_body':False}
            return await receive()
        await self.app(scope,replay,send)
