from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from xhtml2pdf import pisa
import io
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

def create_pdf(email):
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(email.encode('utf-8')), dest=buffer)
    if pisa_status.err:
        return None
    buffer.seek(0)
    return buffer.getvalue()

@app.route('/', methods=['GET', 'POST'])
def email_create():
    if request.method == 'POST':
        name = request.form['name']
        terms = request.form['terms']
        signature = request.form['signature']
        date = request.form['date']
        time = request.form['time']

        if not all([name, terms, signature, date, time]):
            flash('Please fill out all fields!.')
            return redirect(url_for('cliente_create'))

        email = render_template('email_template.html', name=name, terms=terms, signature=signature, date=date, time=time)

        pdf = create_pdf(email)
        if pdf is None:
            flash('Error PDF.')
            return redirect(url_for('email_create'))

        msg = Message('Terms of Service',
                      sender=os.getenv('MAIL_USERNAME'),
                      recipients=[os.getenv('MAIL_USERNAME')]
                      )

        msg.body = 'Terms of Service'
        msg.attach('terms.pdf', 'application/pdf', pdf)

        try:
            mail.send(msg)
            flash('success!')
        except Exception as e:
            flash(f'Error message: {str(e)}')
            return redirect(url_for('cliente_create'))

    return render_template('contract_form.html')

if __name__ == '__main__':
    app.run(debug=True)
