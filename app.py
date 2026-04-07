from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from supabase import create_client
from flask_mail import Mail, Message
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('ADMIN_PASSWORD', 'fallback-secret')

# Cloudinary 
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key    = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

# Flask-Mail 
app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

def get_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))



@app.route('/')
def index():
    try:
        client = get_supabase()
        result = client.table('images').select('*').order('created_at', desc=True).execute()
        images = result.data
    except Exception as e:
        print("Supabase error:", e)
        images = []
    return render_template('index.html', images=images)


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        name        = request.form['name']
        title       = request.form['title']
        description = request.form['description']
        price       = request.form['price']
        date        = request.form['date']
        email       = request.form['email']
        place       = request.form['place']
        file        = request.files['image']

        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']

        client = get_supabase()
        client.table('images').insert({
            'title':       title,
            'description': description,
            'price':       price,
            'date':        date,
            'email':       email,
            'place':       place,
            'url':         image_url
        }).execute()

        return redirect(url_for('index'))

    return render_template('upload.html')


@app.route('/delete/<image_id>', methods=['POST'])
def delete(image_id):
    if not session.get('admin'):
        return redirect(url_for('index'))
    client = get_supabase()
    client.table('images').delete().eq('id', image_id).execute()
    return redirect(url_for('admin'))


import requests as http_requests

N8N_WEBHOOK_URL = "YOUR_N8N_LOCALHOST_URL_HERE"  # ← paste your n8n webhook URL here

@app.route('/interested', methods=['POST'])
def interested():
    data = request.get_json()
    seller_email  = data.get('seller_email')
    product_title = data.get('product_title')
    seller_name   = data.get('seller_name')

    try:
        http_requests.post(N8N_WEBHOOK_URL, json={
            'seller_email':  seller_email,
            'product_title': product_title,
            'seller_name':   seller_name
        })
        return {'status': 'ok'}, 200
    except Exception as e:
        print("n8n error:", e)
        return {'status': 'error'}, 500



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success = False
    if request.method == 'POST':
        name    = request.form['name']
        email   = request.form['email']
        message = request.form['message']
        try:
            msg = Message(
                subject=f"New Contact Message from {name}",
                sender=os.getenv('MAIL_EMAIL'),
                recipients=[os.getenv('MAIL_EMAIL')],
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            success = True
        except Exception as e:
            print("Mail error:", e)
            success = False
    return render_template('contact.html', success=success)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None
    if request.method == 'POST':
        if request.form['password'] == os.getenv('ADMIN_PASSWORD'):
            session['admin'] = True
            return redirect(url_for('admin'))
        error = 'Wrong password.'
    if not session.get('admin'):
        return render_template('admin_login.html', error=error)
    try:
        client = get_supabase()
        result = client.table('images').select('*').order('created_at', desc=True).execute()
        images = result.data
    except Exception as e:
        print("Supabase error:", e)
        images = []
    return render_template('admin.html', images=images)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/shop')
def shop():
    try:
        client = get_supabase()
        result = client.table('images').select('*').order('created_at', desc=True).execute()
        products = result.data
    except Exception as e:
        print("Supabase error:", e)
        products = []
    return render_template('shop.html', products=products)


@app.route('/about')
def about():
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)