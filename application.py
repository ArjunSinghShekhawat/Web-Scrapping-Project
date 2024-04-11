from flask import Flask,render_template,request,jsonify
import requests
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup
from urllib.request import urlopen
import logging

logging.basicConfig(filename='scrapper.log',level=logging.DEBUG)

application = Flask(__name__)
app = application


@app.route('/',methods=['GET'])
def home_page():
    return render_template('index.html')

@app.route('/review',methods=['GET','POST'])
def index():
    if request.method=='POST':
        try:
            searchString = request.form.get('content').replace(" ","")
            flipkart_url = 'https://www.flipkart.com/search?q='+searchString
            uClient = urlopen(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html = BeautifulSoup(flipkart_page,'html.parser')
            item_box = flipkart_html.find_all('div',{'class':'_1AtVbE col-12-12'})
            del item_box[0:3]
            item = item_box[0]
            product_link = 'https://www.flipkart.com'+item.div.div.div.a['href']
            product_Req = requests.get(product_link)
            product_Req.encoding='utf-8'
            product_html = BeautifulSoup(product_Req.text,'html.parser')
            print(product_html)
            commentBoxes = product_html.find_all('div',{'class':'_16PBlm'})

            filename = searchString+'.csv'
            f = open(filename,'w')
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            f.write(headers)
            reviews = []

            for comment in commentBoxes:
                try:
                    name = comment.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    logging.info(name)
                
                try:
                    rating = comment.div.div.div.div.text
                except:
                    rating='No rating'
                    logging.info(rating)

                try:
                    commentHead = comment.div.div.div.p.text
                except:
                    commentHead='No Comment head'
                    logging.info(commentHead)
                
                try:
                    comtag = comment.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                
                mydict = {'Product':searchString,'Name':name,"Rating":rating,"CommentHead":commentHead,'Comment':custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html',reviews=reviews[0:len(reviews)-1])
            
        except Exception as e:
            logging.info(e)
            return "Something went wrong"

    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run(host='0.0.0.0')