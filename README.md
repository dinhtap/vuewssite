# vuewssite
Simple Vue site using websocket to get data from fastapi server<br />
First run fastapi server by `fastapi run` to run at localhost:8000 (the server should run at this address, or you can change it in vuesrc/src/App.vue, just find and replace localhost:8000). <br />
Then go to vuesrc, run client by `npm run preview`. Client gets images from server.<br />
You can add new images by API entry localhost:8000/newimage. In client you will see a new image by clicking refresh button on site (not the one by browser, ofc you can but it's not that efficient)<br />
