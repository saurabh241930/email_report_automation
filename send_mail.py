# importing libraries
from flask import Flask
from flask_mail import Mail, Message
from mail_utils import get_daily_footfall,convert_to_HTML_table


app = Flask(__name__)
mail = Mail(app) # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sherlindhubia@gmail.com'
app.config['MAIL_PASSWORD'] = 'ozzvczngalbpuoke'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)




def create_report_email(report_type,report_frequency,user_preference_sites):
    output = ""

    if report_type == "ATTENDANCE":
        if report_frequency == "DAILY":
            daily_footfall_data = get_daily_footfall(user_preference_sites)
            HTML = convert_to_HTML_table(daily_footfall_data,column_names=["SITE","FOOTFALL"])

            output = output + HTML


    return output
    

# message object mapped to a particular URL ‘/’
@app.route("/")
def index():
    msg = Message(
    'SWATI INTERIOR ERP automated report system',
    sender ='sherlindhubia@gmail.com',
    recipients = ['sp241930@gmail.com']
    # recipients=["herezeon@gmail.com","sp241930@gmail.com","chiragprajapati781@gmail.com","yash@swatiinterior.com "]
    )

    # print(create_report_email("ATTENDANCE","DAILY",user_preference_sites=['DLF LIMITED','INDIABULLS BLU-PENT HOUSE']))

    msg.html = create_report_email("ATTENDANCE","DAILY",user_preference_sites=['DLF LIMITED','INDIABULLS BLU-PENT HOUSE'])
    
    # with app.open_resource("chart.png") as fp:
    #     msg.attach("chart.png", "image/png", fp.read())

    mail.send(msg)
    return 'Sent'

if __name__ == '__main__':
    app.run(debug = True)
