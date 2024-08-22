import io
import os
from flask import render_template, request, flash, redirect, url_for
from flask_mail import Message
from xhtml2pdf import pisa
from app import app, mail

def create_pdf(email):
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(email.encode('utf-8')), dest=buffer)
    if pisa_status.err:
        return None
    buffer.seek(0)
    return buffer.getvalue()

@app.route('/', methods=['GET', 'POST'])
def email_create():
    signature_image = 'https://i.postimg.cc/XYpLLmB2/signature.png'

    if request.method == 'POST':
        name = request.form['name']
        terms_content = request.form['terms']
        signature = request.form['signature']
        date = request.form['date']
        time = request.form['time']

        if not all([name, terms_content, signature, date, time]):
            flash('Please fill out all fields!')
            return redirect(url_for('email_create'))

        # Passar a assinatura e outros dados para o template
        email = render_template(
            'email_template.html',
            name=name,
            terms_content=terms_content,
            signature=signature,
            date=date,
            time=time,
            signature_image=signature_image
        )

        pdf = create_pdf(email)
        if pdf is None:
            flash('Error creating PDF.')
            return redirect(url_for('email_create'))

        msg = Message('Terms of Service',
                      sender=os.getenv('MAIL_USERNAME'),
                      recipients=[os.getenv('MAIL_USERNAME')]
                      )

        msg.body = 'Terms of Service'
        msg.attach('terms.pdf', 'application/pdf', pdf)

        try:
            mail.send(msg)
            flash('Email sent successfully!')
        except Exception as e:
            flash(f'Error sending email: {str(e)}')
            return redirect(url_for('email_create'))

    return render_template('contract_form.html', signature_image=signature_image)
