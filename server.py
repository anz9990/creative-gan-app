from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO
import sys
from pathlib import Path
import csv
import time

from fastai import *
from fastai.text import *

#model_file_name = 'lyrics_gan_reinforce_txl'
model_file_name = 'guten'
export_file_name = "export"
path = Path(__file__).parent
app = Starlette()
model_file_id = "1FdyQQMoeIYmwnapniwIzPJAsGUeoulpR"
export_file_id = "1Ka11WI8bmxGp04LHbYbPESRyNF1OKq9e"
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount("/static", StaticFiles(directory='./static'))


async def download_file_from_google_drive(id, destination):
    if destination.exists(): 
        print("model file found")
        return
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)
    
def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner(arch=AWD_LSTM):
    #await download_file(model_file_url, path/'static/'/f'{model_file_name}.pth')
    await download_file_from_google_drive(model_file_id,path/'static/models'/f'{model_file_name}.pth')
    await download_file_from_google_drive(export_file_id,path/'static'/f'{export_file_name}.pkl')
    data_lm = TextLMDataBunch.load_empty(path/"static/",export_file_name+".pkl")
    if arch is TransformerXL:
        config = tfmerXL_lm_config.copy()
        config['mem_len'] = 150
        config['output_p'] = 0.1
        config['embed_p'] = 0.1
        config['ff_p'] = 0.1
        config['resid_p'] = 0.1
        config['d_inner'] = 1024
        config['d_model'] = 128
    if arch is AWD_LSTM:
        config = awd_lstm_lm_config.copy()
    #    config["n_hid"] = 1150

    learn = language_model_learner(data_lm, arch, config=config,pretrained=False)
    learn.load(model_file_name)
    return learn

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/analyze', methods=['GET'])
async def analyze(request):
    data = request.query_params["seed"]

    return JSONResponse({'result': textResponse(data)})

def textResponse(data):
    csv_string = learn.predict(data, 20,temperature=1.1)
    #csv_string = learn.beam_search(data, 20)
    time.sleep(2)
    #return csv_string.replace(data,"");
    csv_string = csv_string.replace(data,"")
    
    words = csv_string.split()
    for i, word in enumerate(words):
        if word == 'xxbos':
            words[i] = '<br/>'
        elif word == 'xxmaj':
            words[i+1] = words[i+1][0].upper() + words[i+1][1:]
            words[i] = ''
        elif word == 'xxup':
            words[i+1] = words[i+1].upper()
            words[i] = ''     
        elif word == 'xxunk' or word == '(' or word == ')' or word == '"':
            words[i] = ''   
        elif word == ',':
            words[i] = ''
        elif word == '.' or word == '?' or word == '!' or word == ';':
            words[i-1]+= words[i]
            words[i] = ''
        elif word[0] == "'":
            words[i-1]+= words[i]
            words[i] = ''

    return ' '.join(words)

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app, host='0.0.0.0', port=8899)
